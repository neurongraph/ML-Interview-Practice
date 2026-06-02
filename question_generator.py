import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn

from ollama_client import OllamaClient

console = Console()

# ─── Prompts ─────────────────────────────────────────────────────────────────

_TYPE_REQUIREMENTS = {
    "multiple_choice": (
        "- Write a clear, unambiguous question with exactly 4 options.\n"
        "- Only ONE option is definitively correct.\n"
        "- Distractors must be plausible but clearly wrong to someone who knows the material.\n"
        "- VARY which index (0-3) holds the correct answer across questions."
    ),
    "open_ended": (
        "- Ask about design decisions, explanations, or conceptual understanding.\n"
        "- Question should require 2-3 paragraphs to answer well.\n"
        "- evaluation_criteria must list 4-6 key points a strong answer covers."
    ),
    "coding": (
        "- Provide a specific, implementable coding task with clear requirements.\n"
        "- Include any constraints (time/space complexity, edge cases to handle).\n"
        "- evaluation_criteria must describe: expected approach, edge cases, performance considerations."
    ),
}

_GENERATION_PROMPT = """\
You are an expert technical interviewer. Generate exactly {count} {difficulty}-level \
{q_type} interview questions about "{topic}".

Focus specifically on these subtopics: {subtopics}

TYPE REQUIREMENTS:
{type_requirements}

DIFFICULTY DEFINITIONS:
- beginner: Foundational concepts, definitions, basic usage patterns
- intermediate: Applied knowledge, common patterns, trade-offs, practical scenarios
- advanced: Deep internals, optimisation, architectural decisions, edge cases

RETURN ONLY a valid JSON array — no markdown, no code fences, no explanation:
[
  {{
    "text": "Full question text here",
    "type": "{q_type}",
    "difficulty": "{difficulty}",
    "topic": "{topic}",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 1,
    "evaluation_criteria": "Key points the answer must cover: ..."
  }}
]

Rules:
- For open_ended and coding questions: omit "options" and "correct_answer" entirely.
- For multiple_choice: correct_answer is 0-indexed (0 = first option).
- Every question must have a non-empty "evaluation_criteria".
- Generate exactly {count} questions — no more, no fewer.
"""


# ─── Generator ───────────────────────────────────────────────────────────────

class QuestionGenerator:
    """Generates interview questions via Ollama and saves them to a profile."""

    def __init__(self):
        self.client = OllamaClient()

    # ── Deduplication helpers ────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())

    def _hash(self, text: str) -> str:
        return hashlib.md5(self._normalize(text).encode()).hexdigest()

    # ── Single batch ─────────────────────────────────────────────────────────

    def _generate_batch(
        self,
        topic: str,
        subtopics: List[str],
        q_type: str,
        difficulty: str,
        count: int,
    ) -> List[Dict]:
        """Call Ollama and parse one batch of questions. Returns empty list on failure."""
        prompt = _GENERATION_PROMPT.format(
            count=count,
            difficulty=difficulty,
            q_type=q_type,
            topic=topic,
            subtopics=", ".join(subtopics),
            type_requirements=_TYPE_REQUIREMENTS.get(q_type, ""),
        )
        try:
            response = self.client.generate(prompt)
        except RuntimeError:
            return []

        return self._parse_response(response, q_type, topic, difficulty)

    def _parse_response(
        self, response: str, expected_type: str, topic: str, difficulty: str
    ) -> List[Dict]:
        """Extract and validate JSON from LLM response."""
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            return []
        try:
            questions = json.loads(match.group(0))
        except json.JSONDecodeError:
            return []

        valid = []
        for q in questions:
            if not isinstance(q, dict) or not q.get("text", "").strip():
                continue
            q.setdefault("type", expected_type)
            q.setdefault("topic", topic)
            q.setdefault("difficulty", difficulty)
            q.setdefault("evaluation_criteria", "Evaluate for accuracy and completeness.")
            if expected_type == "multiple_choice":
                if not q.get("options") or len(q["options"]) != 4:
                    continue
                q.setdefault("correct_answer", 0)
            else:
                q.pop("options", None)
                q.pop("correct_answer", None)
            valid.append(q)
        return valid

    # ── Batch planning ───────────────────────────────────────────────────────

    @staticmethod
    def _plan_batches(
        target: int,
        difficulty_mix: Dict[str, int],
        type_mix: Dict[str, int],
    ) -> List[Tuple[str, str, int]]:
        """Return list of (difficulty, q_type, count) for this topic."""
        total_diff = sum(difficulty_mix.values())
        total_type = sum(type_mix.values())
        batches = []
        for difficulty, d_weight in difficulty_mix.items():
            for q_type, t_weight in type_mix.items():
                count = max(1, round(target * (d_weight / total_diff) * (t_weight / total_type)))
                batches.append((difficulty, q_type, count))
        return batches

    # ── Public API ───────────────────────────────────────────────────────────

    def generate_for_profile(
        self,
        profile: Dict,
        questions_path: Path,
        augment_topic: Optional[str] = None,
        augment_count: Optional[int] = None,
    ) -> int:
        """Generate (or augment) questions for a profile.

        Args:
            profile:        Parsed profile.json dict.
            questions_path: Where to save/append questions.json.
            augment_topic:  If set, only generate for this topic name.
            augment_count:  Override question_count when augmenting.

        Returns:
            Number of new (non-duplicate) questions added.
        """
        # ── Load existing questions for deduplication ────────────────────────
        existing: List[Dict] = []
        seen_hashes: set = set()
        if questions_path.exists():
            with open(questions_path) as f:
                existing = json.load(f).get("questions", [])
            seen_hashes = {self._hash(q["text"]) for q in existing}

        next_id = max((q.get("id", 0) for q in existing), default=0) + 1

        # ── Decide which topics to process ───────────────────────────────────
        all_topics = profile.get("topics", [])
        topics = [t for t in all_topics if t["name"] == augment_topic] if augment_topic else all_topics

        # ── Pre-calculate total batches for progress bar ─────────────────────
        all_batches = []
        for tc in topics:
            dm = tc.get("difficulty_mix", {"beginner": 4, "intermediate": 8, "advanced": 4})
            tm = tc.get("type_mix", {"multiple_choice": 6, "open_ended": 6, "coding": 4})
            target = augment_count if augment_count is not None else tc.get("question_count", 16)
            for diff, qtype, cnt in self._plan_batches(target, dm, tm):
                all_batches.append((tc, diff, qtype, cnt))

        # ── Generate ─────────────────────────────────────────────────────────
        new_questions: List[Dict] = []

        with Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Starting...", total=len(all_batches))

            for tc, difficulty, q_type, count in all_batches:
                topic_name = tc["name"]
                subtopics = tc.get("subtopics", [topic_name])

                progress.update(
                    task,
                    description=f"[bold]{topic_name}[/bold]  {difficulty} · {q_type} ({count}q)",
                )

                batch = self._generate_batch(topic_name, subtopics, q_type, difficulty, count)

                for q in batch:
                    h = self._hash(q["text"])
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        q["id"] = next_id
                        next_id += 1
                        new_questions.append(q)

                progress.advance(task)

        # ── Persist ──────────────────────────────────────────────────────────
        all_questions = existing + new_questions
        with open(questions_path, "w") as f:
            json.dump({"questions": all_questions}, f, indent=2)

        return len(new_questions)
