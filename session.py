import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import DEFAULT_PROFILE, PROFILES_DIR, SCORES_DIR, TOTAL_QUESTIONS


@dataclass
class Session:
    session_id: str
    current_question_idx: int
    answers: List[Dict] = field(default_factory=list)
    question_ids: List[int] = field(default_factory=list)
    profile_name: str = DEFAULT_PROFILE
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None

    # ─── Paths ───────────────────────────────────────────────────────────────

    def get_session_file(self) -> Path:
        return SCORES_DIR / f"{self.session_id}.md"

    # ─── Persistence ─────────────────────────────────────────────────────────

    def _save_all(self):
        """Write both markdown (human-readable) and JSON (machine-readable)."""
        self.save()
        json_file = SCORES_DIR / f"{self.session_id}.json"
        with open(json_file, "w") as f:
            json.dump(self._to_dict(), f, indent=2)

    def _to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "current_question_idx": self.current_question_idx,
            "answers": self.answers,
            "question_ids": self.question_ids,
            "profile_name": self.profile_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def save(self):
        """Write the markdown score file."""
        self.get_session_file().write_text(self._generate_markdown())

    def _generate_markdown(self) -> str:
        summary = self.get_summary()
        md = f"# Interview Session: {self.session_id}\n\n"
        md += f"**Profile:** {self.profile_name}\n"
        md += f"**Date:** {self.start_time[:10]}\n"
        md += f"**Start Time:** {self.start_time[11:19]}\n"
        if self.end_time:
            md += f"**End Time:** {self.end_time[11:19]}\n"
        else:
            md += f"**Last Updated:** {datetime.now().isoformat()[11:19]}\n"

        md += f"\n## Overall Score: {summary['overall_score']}/100\n\n"

        md += "## Score by Topic\n\n"
        for topic in sorted(summary["by_topic"].keys()):
            score = summary["by_topic"][topic]
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            md += f"- **{topic}**: {score}/100 `[{bar}]`\n"

        md += f"\n## Progress\n\n"
        md += f"- Completed: {summary['completed']}/{summary['total_questions']} questions\n"

        if self.answers:
            md += "\n## Detailed Answers\n\n"
            questions_data = {q["id"]: q for q in self.get_questions_data()}
            for idx, answer in enumerate(self.answers, 1):
                question = questions_data.get(answer["question_id"], {})
                md += f"### Question {idx}: {question.get('topic', 'Unknown')}\n\n"
                md += f"**Score:** {answer['score']}/100\n\n"
                md += f"**Feedback:** {answer['feedback']}\n\n"
                snippet = answer["user_answer"][:500]
                truncated = "...[truncated]" if len(answer["user_answer"]) > 500 else ""
                md += f"**Your Answer:**\n```\n{snippet}{truncated}\n```\n\n"
        return md

    # ─── Static constructors ──────────────────────────────────────────────────

    @staticmethod
    def create_new(profile_name: str = DEFAULT_PROFILE) -> "Session":
        return Session(
            session_id=str(uuid.uuid4()),
            current_question_idx=0,
            profile_name=profile_name,
        )

    @staticmethod
    def load(session_id: str) -> Optional["Session"]:
        """Load from JSON backup (single source of truth for data)."""
        json_backup = SCORES_DIR / f"{session_id}.json"
        if not json_backup.exists():
            return None
        with open(json_backup) as f:
            data = json.load(f)
        data.setdefault("profile_name", DEFAULT_PROFILE)  # backward compat
        return Session(**data)

    @staticmethod
    def list_sessions() -> List[str]:
        return [f.stem for f in SCORES_DIR.glob("*.md")]

    @staticmethod
    def get_latest_session() -> Optional["Session"]:
        sessions = Session.list_sessions()
        if not sessions:
            return None
        latest_id = max(
            sessions,
            key=lambda sid: (SCORES_DIR / f"{sid}.md").stat().st_mtime,
        )
        return Session.load(latest_id)

    # ─── Mutation ─────────────────────────────────────────────────────────────

    def set_questions(self, questions: List) -> None:
        self.question_ids = [q.id for q in questions]
        self._save_all()

    def record_answer(self, question_id: int, answer: str, score: int, feedback: str):
        self.answers.append(
            {
                "question_id": question_id,
                "user_answer": answer,
                "score": score,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.current_question_idx += 1
        self._save_all()

    def mark_complete(self):
        self.end_time = datetime.now().isoformat()
        self._save_all()

    # ─── Queries ──────────────────────────────────────────────────────────────

    def _total_questions(self) -> int:
        return len(self.question_ids) if self.question_ids else TOTAL_QUESTIONS

    def is_complete(self) -> bool:
        return self.current_question_idx >= self._total_questions()

    def get_progress(self) -> str:
        return f"{len(self.answers)}/{self._total_questions()}"

    def get_summary(self) -> Dict:
        total = self._total_questions()
        if not self.answers:
            return {"total_questions": total, "completed": 0, "overall_score": 0, "by_topic": {}}

        completed = len(self.answers)
        overall_score = int(sum(a["score"] for a in self.answers) / completed)

        # Build per-topic scores using question metadata
        questions_data = {q["id"]: q for q in self.get_questions_data()}
        by_topic: Dict[str, Dict] = {}
        for answer in self.answers:
            q = questions_data.get(answer["question_id"], {})
            topic = q.get("topic", "Unknown")
            if topic not in by_topic:
                by_topic[topic] = {"count": 0, "total": 0}
            by_topic[topic]["count"] += 1
            by_topic[topic]["total"] += answer["score"]

        topic_scores = {
            topic: int(data["total"] / data["count"])
            for topic, data in by_topic.items()
        }

        return {
            "total_questions": total,
            "completed": completed,
            "overall_score": overall_score,
            "by_topic": topic_scores,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def get_questions_data(self) -> List[Dict]:
        """Load raw question dicts from the profile's questions.json."""
        questions_path = PROFILES_DIR / self.profile_name / "questions.json"
        with open(questions_path) as f:
            return json.load(f)["questions"]
