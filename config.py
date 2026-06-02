from pathlib import Path

# Ollama Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "mistral"

# Scores Storage (local to project)
SCORES_DIR = Path(__file__).parent / "scores"
SCORES_DIR.mkdir(parents=True, exist_ok=True)

# Interview Configuration
TOTAL_QUESTIONS = 15
QUESTIONS_FILE = Path(__file__).parent / "questions_data.json"

# Scoring Rubric for LLM Evaluation
EVALUATION_PROMPT_TEMPLATE = """You are an expert evaluator for a technical interview.
Evaluate the candidate's answer on a scale of 0-100 based on the following criteria:
- Correctness and accuracy
- Depth of understanding
- Clarity of explanation
- Relevant details and examples

Question: {question}
Candidate's Answer: {answer}
Evaluation Criteria: {criteria}

Provide your evaluation in the following format:
SCORE: [0-100]
FEEDBACK: [Brief explanation of the score]
STRENGTHS: [What the candidate did well]
IMPROVEMENTS: [What could be improved]"""

CODING_EVALUATION_PROMPT = """You are an expert Python/Databricks code reviewer.
Evaluate the candidate's code on a scale of 0-100 based on:
- Correctness (does it work?)
- Code quality (readability, maintainability)
- Performance (efficiency, optimization)
- Best practices (following conventions and patterns)

Question/Task: {question}
Candidate's Code: {answer}

Provide your evaluation in the following format:
SCORE: [0-100]
FEEDBACK: [Brief explanation]
STRENGTHS: [What the code does well]
IMPROVEMENTS: [Specific suggestions for improvement]"""
