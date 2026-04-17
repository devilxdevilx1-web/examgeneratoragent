import requests
import json


PROMPT_TEMPLATE = """You are an expert exam question generator.

Generate EXACTLY {n} multiple-choice questions.

STRICT RULES:
- Output ONLY valid JSON
- No explanations
- No extra text
- No markdown

FORMAT:

[
  {
    "question": "string",
    "options": {
      "A": "string",
      "B": "string",
      "C": "string",
      "D": "string"
    },
    "answer": "A"
  }
]

CONSTRAINTS:
- Only ONE correct answer
- No ambiguous questions
- Questions must be exam-level (concept-based)
- Avoid repetition

Now generate questions.
"""



class QuestionGenerator:
    def __init__(self, model: str = "phi3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"

    def generate(self, syllabus_text: str, examples: str, n: int = 50) -> list[str]:
        prompt = PROMPT_TEMPLATE.format(
            syl=syllabus_text.strip(),
            examples=examples.strip(),
            n=n
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            raw_output = data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.api_url}.\n"
                "Make sure Ollama is running: `ollama serve`"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out. The model may be too slow or overloaded.")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"API error: {e}")

        questions = self._parse_questions(raw_output)
        return questions[:n]

    def _parse_questions(self, raw: str) -> list[str]:
        lines = raw.splitlines()
        questions = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match lines starting with a number followed by . or )
            if line[0].isdigit():
                # Strip leading number + punctuation (e.g. "1.", "1)", "12.")
                for sep in ['. ', ') ', '.\t']:
                    idx = line.find(sep)
                    if idx != -1 and idx <= 3:
                        question = line[idx + len(sep):].strip()
                        if question:
                            questions.append(question)
                        break
                else:
                    # Fallback: strip digits and punctuation from front
                    stripped = line.lstrip('0123456789.)- ').strip()
                    if stripped:
                        questions.append(stripped)

        return questions