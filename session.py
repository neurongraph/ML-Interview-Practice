import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config import SCORES_DIR, TOTAL_QUESTIONS


@dataclass
class Session:
    session_id: str
    current_question_idx: int
    answers: List[Dict] = field(default_factory=list)
    question_ids: List[int] = field(default_factory=list)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None

    def get_session_file(self) -> Path:
        return SCORES_DIR / f"{self.session_id}.md"

    def save(self):
        """Save session as a markdown file with scores."""
        file_path = self.get_session_file()
        md_content = self._generate_markdown()
        with open(file_path, "w") as f:
            f.write(md_content)

    def _generate_markdown(self) -> str:
        """Generate markdown content for the session."""
        summary = self.get_summary()

        md = f"# Interview Session: {self.session_id}\n\n"
        md += f"**Date:** {self.start_time[:10]}\n"
        md += f"**Start Time:** {self.start_time[11:19]}\n"

        if self.end_time:
            md += f"**End Time:** {self.end_time[11:19]}\n"

        md += f"\n## Overall Score: {summary['overall_score']}/100\n\n"

        # Topic breakdown
        md += "## Score by Topic\n\n"
        for topic in sorted(summary['by_topic'].keys()):
            score = summary['by_topic'][topic]
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            md += f"- **{topic}**: {score}/100 `[{bar}]`\n"

        # Progress
        md += f"\n## Progress\n\n"
        md += f"- Completed: {summary['completed']}/{summary['total_questions']} questions\n"

        # Answers detail
        if self.answers:
            md += f"\n## Detailed Answers\n\n"
            questions_data = {q["id"]: q for q in self.get_questions_data()}

            for idx, answer in enumerate(self.answers, 1):
                q_id = answer["question_id"]
                question = questions_data.get(q_id, {})

                md += f"### Question {idx}: {question.get('topic', 'Unknown')}\n\n"
                md += f"**Score:** {answer['score']}/100\n\n"
                md += f"**Feedback:** {answer['feedback']}\n\n"

                md += f"**Your Answer:**\n```\n{answer['user_answer'][:500]}"
                if len(answer['user_answer']) > 500:
                    md += "...[truncated]"
                md += "\n```\n\n"

        return md

    @staticmethod
    def load(session_id: str) -> Optional["Session"]:
        """Load session from markdown file (reconstructs from saved markdown)."""
        file_path = SCORES_DIR / f"{session_id}.md"
        if not file_path.exists():
            return None

        # Load from JSON backup for data reconstruction
        json_backup = SCORES_DIR / f"{session_id}.json"
        if json_backup.exists():
            with open(json_backup) as f:
                data = json.load(f)
                return Session(**data)

        return None

    @staticmethod
    def create_new() -> "Session":
        return Session(session_id=str(uuid.uuid4()), current_question_idx=0)

    def set_questions(self, questions: List) -> None:
        """Store the question IDs for this session."""
        self.question_ids = [q.id for q in questions]
        self._save_all()

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

    def is_complete(self) -> bool:
        return self.current_question_idx >= TOTAL_QUESTIONS

    def mark_complete(self):
        self.end_time = datetime.now().isoformat()
        self._save_all()

    def _save_all(self):
        """Save both markdown (for display) and JSON (for data)."""
        # Save markdown for display
        self.save()

        # Save JSON backup for data reconstruction
        json_file = SCORES_DIR / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "current_question_idx": self.current_question_idx,
            "answers": self.answers,
            "question_ids": self.question_ids,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_summary(self) -> Dict:
        if not self.answers:
            return {
                "total_questions": TOTAL_QUESTIONS,
                "completed": 0,
                "overall_score": 0,
                "by_topic": {},
            }

        completed = len(self.answers)
        total_score = sum(a["score"] for a in self.answers)
        overall_score = int(total_score / completed) if completed > 0 else 0

        by_topic = {}
        for answer in self.answers:
            for q in self.get_questions_data():
                if q["id"] == answer["question_id"]:
                    topic = q["topic"]
                    if topic not in by_topic:
                        by_topic[topic] = {"count": 0, "total_score": 0}
                    by_topic[topic]["count"] += 1
                    by_topic[topic]["total_score"] += answer["score"]
                    break

        topic_scores = {
            topic: int(data["total_score"] / data["count"])
            for topic, data in by_topic.items()
        }

        return {
            "total_questions": TOTAL_QUESTIONS,
            "completed": completed,
            "overall_score": overall_score,
            "by_topic": topic_scores,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    @staticmethod
    def get_questions_data() -> List[Dict]:
        from config import QUESTIONS_FILE

        with open(QUESTIONS_FILE) as f:
            return json.load(f)["questions"]

    def get_progress(self) -> str:
        total = TOTAL_QUESTIONS
        completed = len(self.answers)
        return f"{completed}/{total}"
