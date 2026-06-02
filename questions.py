import json
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from config import DEFAULT_PROFILE, PROFILES_DIR, TOTAL_QUESTIONS


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    CODING = "coding"


@dataclass
class Question:
    id: int
    topic: str
    difficulty: str
    type: QuestionType
    text: str
    evaluation_criteria: str
    options: Optional[List[str]] = None
    correct_answer: Optional[int] = None

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = QuestionType(self.type)


class QuestionBank:
    def __init__(self, profile_name: str = DEFAULT_PROFILE):
        self.profile_name = profile_name
        self.questions: List[Question] = []
        self.question_pool: List[Question] = []
        questions_path = PROFILES_DIR / profile_name / "questions.json"
        self._load_questions(questions_path)

    def _load_questions(self, file_path: Path):
        with open(file_path) as f:
            data = json.load(f)
        for q_data in data["questions"]:
            q = Question(
                id=q_data["id"],
                topic=q_data["topic"],
                difficulty=q_data["difficulty"],
                type=q_data["type"],
                text=q_data["text"],
                evaluation_criteria=q_data["evaluation_criteria"],
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer"),
            )
            self.question_pool.append(q)
        self.questions = self.question_pool.copy()

    def get_interview_size(self) -> int:
        """Return total_questions_per_interview from profile config."""
        profile_path = PROFILES_DIR / self.profile_name / "profile.json"
        if profile_path.exists():
            with open(profile_path) as f:
                return json.load(f).get("total_questions_per_interview", TOTAL_QUESTIONS)
        return TOTAL_QUESTIONS

    def get_question(self, index: int) -> Optional[Question]:
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def get_total_count(self) -> int:
        return len(self.questions)

    def get_pool_size(self) -> int:
        return len(self.question_pool)

    def get_by_topic(self, topic: str) -> List[Question]:
        return [q for q in self.question_pool if q.topic == topic]

    def get_topics(self) -> List[str]:
        return sorted(set(q.topic for q in self.question_pool))

    def get_random_interview(self) -> List[Question]:
        """Random balanced sample across topics. Size driven by profile config."""
        interview_size = self.get_interview_size()
        topics = self.get_topics()
        questions_per_topic = interview_size // len(topics)

        selected: List[Question] = []
        for topic in topics:
            pool = self.get_by_topic(topic)
            selected.extend(random.sample(pool, min(questions_per_topic, len(pool))))

        # Top-up if rounding left us short
        remaining = interview_size - len(selected)
        if remaining > 0:
            available = [q for q in self.question_pool if q not in selected]
            selected.extend(random.sample(available, min(remaining, len(available))))

        random.shuffle(selected)
        self.questions = selected[:interview_size]
        return self.questions

    def get_by_ids(self, question_ids: List[int]) -> List[Question]:
        """Retrieve questions by their IDs, preserving order."""
        lookup = {q.id: q for q in self.question_pool}
        return [lookup[qid] for qid in question_ids if qid in lookup]
