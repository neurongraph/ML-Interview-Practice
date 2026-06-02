from dataclasses import dataclass
from questions import Question, QuestionType
from ollama_client import OllamaClient


@dataclass
class EvaluationResult:
    score: int
    feedback: str
    strengths: str
    improvements: str


class Evaluator:
    def __init__(self):
        self.ollama = OllamaClient()

    def evaluate(self, question: Question, answer: str) -> EvaluationResult:
        if question.type == QuestionType.MULTIPLE_CHOICE:
            return self._evaluate_multiple_choice(question, answer)
        elif question.type == QuestionType.OPEN_ENDED:
            return self._evaluate_open_ended(question, answer)
        elif question.type == QuestionType.CODING:
            return self._evaluate_coding(question, answer)
        else:
            raise ValueError(f"Unknown question type: {question.type}")

    def _evaluate_multiple_choice(
        self, question: Question, answer: str
    ) -> EvaluationResult:
        try:
            user_choice = int(answer.strip())
            if user_choice == question.correct_answer:
                return EvaluationResult(
                    score=100,
                    feedback="Correct answer!",
                    strengths="You selected the correct option.",
                    improvements="",
                )
            else:
                correct_text = question.options[question.correct_answer]
                return EvaluationResult(
                    score=0,
                    feedback=f"Incorrect. The correct answer is: {correct_text}",
                    strengths="",
                    improvements=f"Review the concept and study: {question.evaluation_criteria}",
                )
        except (ValueError, IndexError):
            return EvaluationResult(
                score=0,
                feedback="Invalid input. Please enter a valid option number.",
                strengths="",
                improvements="",
            )

    def _evaluate_open_ended(self, question: Question, answer: str) -> EvaluationResult:
        if not answer.strip():
            return EvaluationResult(
                score=0,
                feedback="No answer provided.",
                strengths="",
                improvements="Please provide a thoughtful answer.",
            )

        # Check for obviously low-effort responses
        low_effort_phrases = ["i can't", "i don't", "dunno", "no idea", "idk", "pass", "skip"]
        answer_lower = answer.lower().strip()

        if any(phrase in answer_lower for phrase in low_effort_phrases) and len(answer.strip()) < 50:
            return EvaluationResult(
                score=5,
                feedback="Insufficient effort - appears to be a low-effort response without genuine attempt.",
                strengths="",
                improvements="Please attempt to answer the question by providing your knowledge or reasoning.",
            )

        result = self.ollama.evaluate_open_ended(
            question.text, answer, question.evaluation_criteria
        )

        return EvaluationResult(
            score=result["score"],
            feedback=result["feedback"],
            strengths=result["strengths"],
            improvements=result["improvements"],
        )

    def _evaluate_coding(self, question: Question, answer: str) -> EvaluationResult:
        if not answer.strip():
            return EvaluationResult(
                score=0,
                feedback="No code provided.",
                strengths="",
                improvements="Please provide a code solution.",
            )

        # Check for obviously low-effort responses
        low_effort_phrases = ["i can't", "i don't", "dunno", "no idea", "idk", "pass", "skip"]
        answer_lower = answer.lower().strip()

        if any(phrase in answer_lower for phrase in low_effort_phrases) and len(answer.strip()) < 50:
            return EvaluationResult(
                score=5,
                feedback="Insufficient effort - no code attempt provided.",
                strengths="",
                improvements="Please write functional code or pseudocode to solve the problem.",
            )

        result = self.ollama.evaluate_coding(question.text, answer)

        return EvaluationResult(
            score=result["score"],
            feedback=result["feedback"],
            strengths=result["strengths"],
            improvements=result["improvements"],
        )
