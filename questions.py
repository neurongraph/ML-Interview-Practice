import json
import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from config import QUESTIONS_FILE, TOTAL_QUESTIONS


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
    def __init__(self, file_path=QUESTIONS_FILE):
        self.questions: List[Question] = []
        self.question_pool: List[Question] = []
        self._load_questions(file_path)

    def _load_questions(self, file_path):
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

    def get_question(self, index: int) -> Optional[Question]:
        if 0 <= index < len(self.questions):
            return self.questions[index]
        return None

    def get_total_count(self) -> int:
        return len(self.questions)

    def get_by_topic(self, topic: str) -> List[Question]:
        return [q for q in self.question_pool if q.topic == topic]

    def get_topics(self) -> List[str]:
        return sorted(set(q.topic for q in self.question_pool))

    def get_random_interview(self) -> List[Question]:
        """Get a random sample of questions for a new interview.

        Ensures balanced representation across topics and difficulty levels.
        """
        topics = self.get_topics()
        questions_per_topic = TOTAL_QUESTIONS // len(topics)

        selected_questions = []
        for topic in topics:
            topic_questions = self.get_by_topic(topic)
            sample_size = min(questions_per_topic, len(topic_questions))
            selected = random.sample(topic_questions, sample_size)
            selected_questions.extend(selected)

        # If we need more questions to reach TOTAL_QUESTIONS
        remaining = TOTAL_QUESTIONS - len(selected_questions)
        if remaining > 0:
            available = [q for q in self.question_pool if q not in selected_questions]
            selected_questions.extend(random.sample(available, min(remaining, len(available))))

        # Shuffle to avoid topic clustering
        random.shuffle(selected_questions)
        self.questions = selected_questions[:TOTAL_QUESTIONS]
        return self.questions

    def get_by_ids(self, question_ids: List[int]) -> List[Question]:
        """Retrieve questions by their IDs, maintaining the order of IDs."""
        id_to_question = {q.id: q for q in self.question_pool}
        return [id_to_question[qid] for qid in question_ids if qid in id_to_question]
