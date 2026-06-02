from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ministral-3:14b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))  # seconds

# Storage paths (local to project)
SCORES_DIR = Path(__file__).parent / "scores"
SCORES_DIR.mkdir(parents=True, exist_ok=True)

PROFILES_DIR = Path(__file__).parent / "profiles"
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# Defaults
DEFAULT_PROFILE = "ml-engineering"
TOTAL_QUESTIONS = 15  # fallback when no profile config found

# Scoring Rubric for LLM Evaluation
EVALUATION_PROMPT_TEMPLATE = """You are an expert technical interviewer. Rate this answer from 0-100.

SCORING GUIDELINES:
- 90-100: Excellent - Complete, accurate, well-explained with examples
- 70-89: Good - Mostly correct with minor gaps or clarity issues
- 50-69: Fair - Shows understanding but missing key details or has errors
- 30-49: Poor - Incomplete or contains significant errors
- 0-29: Very Poor - Irrelevant, completely incorrect, or no effort (e.g., "I don't know", "I can't answer")

Question: {question}

Candidate's Answer: {answer}

Evaluation Criteria: {criteria}

You MUST respond with EXACTLY this format (fill each section completely):

SCORE: [number 0-100]
FEEDBACK: [1-2 sentences explaining the score]
STRENGTHS: [1-2 specific things done well]
IMPROVEMENTS: [2-3 specific areas to improve]"""

CODING_EVALUATION_PROMPT = """You are an expert code reviewer. Evaluate this code solution.

SCORING GUIDELINES:
- 90-100: Excellent - Works correctly, clean code, handles edge cases, follows best practices
- 70-89: Good - Works mostly correctly, minor issues or style problems
- 50-69: Fair - Has the right idea but missing implementation, lacks error handling
- 30-49: Poor - Significant errors, incomplete solution, poor practices
- 0-29: Very Poor - Doesn't work, doesn't attempt the task, or trivial responses

Task: {question}

Candidate's Code/Solution: {answer}

You MUST respond with EXACTLY this format (fill each section completely):

SCORE: [number 0-100]
FEEDBACK: [1-2 sentences on correctness and code quality]
STRENGTHS: [1-2 specific strengths of the implementation]
IMPROVEMENTS: [2-3 specific improvements needed]"""
