import requests
import re
from typing import Dict
from config import OLLAMA_HOST, OLLAMA_MODEL, OLLAMA_TIMEOUT, EVALUATION_PROMPT_TEMPLATE, CODING_EVALUATION_PROMPT


class OllamaClient:
    def __init__(self, host: str = OLLAMA_HOST, model: str = OLLAMA_MODEL, timeout: int = OLLAMA_TIMEOUT):
        self.host = host
        self.model = model
        self.timeout = timeout
        self.endpoint = f"{host}/api/generate"

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def generate(self, prompt: str, stream: bool = False) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
        }

        try:
            response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
            response.raise_for_status()

            if stream:
                result = ""
                for line in response.iter_lines():
                    if line:
                        import json
                        chunk = json.loads(line)
                        result += chunk.get("response", "")
                        if chunk.get("done"):
                            break
                return result
            else:
                import json
                return response.json().get("response", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to call Ollama: {e}")

    def evaluate_open_ended(self, question: str, answer: str, criteria: str) -> Dict:
        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            question=question, answer=answer, criteria=criteria
        )
        response = self.generate(prompt)
        return self._parse_evaluation(response)

    def evaluate_coding(self, question: str, answer: str) -> Dict:
        prompt = CODING_EVALUATION_PROMPT.format(question=question, answer=answer)
        response = self.generate(prompt)
        return self._parse_evaluation(response)

    def _parse_evaluation(self, response: str) -> Dict:
        """Parse evaluation response with support for multi-line fields."""
        result = {
            "score": 0,
            "feedback": "",
            "strengths": "",
            "improvements": "",
        }

        # Extract SCORE
        score_match = re.search(r'SCORE:\s*(\d+)', response, re.IGNORECASE)
        if score_match:
            try:
                score = int(score_match.group(1))
                result["score"] = max(0, min(100, score))
            except ValueError:
                result["score"] = 50

        # Extract FEEDBACK (until next section)
        feedback_match = re.search(
            r'FEEDBACK:\s*(.*?)(?=STRENGTHS:|IMPROVEMENTS:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if feedback_match:
            result["feedback"] = feedback_match.group(1).strip()

        # Extract STRENGTHS (until next section)
        strengths_match = re.search(
            r'STRENGTHS?:\s*(.*?)(?=IMPROVEMENTS?:|$)',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if strengths_match:
            result["strengths"] = strengths_match.group(1).strip()

        # Extract IMPROVEMENTS (until end)
        improvements_match = re.search(
            r'IMPROVEMENTS?:\s*(.*?)$',
            response,
            re.IGNORECASE | re.DOTALL
        )
        if improvements_match:
            result["improvements"] = improvements_match.group(1).strip()

        return result
