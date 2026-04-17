import requests
import json
import re
from loguru import logger


EXAM_PROMPT = """You are a Kalvium-style exam question setter.

SYLLABUS:
{syllabus}

EXAMPLE QUESTIONS (style reference):
{examples}

TASK: Generate exactly {n} MCQ exam questions.

STRICT RULES:
1. Each question tests ONLY ONE concept
2. Exactly 4 options: A, B, C, D
3. Only ONE correct answer per question
4. No explanations anywhere
5. No coding questions — scenario and concept based only
6. Wrong options must be conceptually similar (not obviously wrong)
7. No repeated patterns or similar questions
8. Difficulty mix: 30% easy, 40% medium, 30% hard
9. Short, sharp, scenario-based questions
10. Match the style and tone of the example questions exactly

OUTPUT FORMAT (follow exactly, no deviation):
Q: <question text>
A. <option>
B. <option>
C. <option>
D. <option>
Answer: <A or B or C or D>

Generate all {n} questions now. No preamble. No explanation. Just the questions.
"""


class AnswerAgent:
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        logger.info(f"AnswerAgent initialized | model={model}")

    def generate_exam_questions(self, syllabus: str, examples: str, n: int = 30) -> list[dict]:
        prompt = EXAM_PROMPT.format(
            syllabus=syllabus.strip(),
            examples=examples.strip(),
            n=n
        )

        logger.info(f"Generating {n} exam questions...")

        try:
            response = requests.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=300
            )
            response.raise_for_status()
            raw = response.json().get("response", "").strip()
            logger.info("Raw response received from Ollama")
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Cannot connect to Ollama. Run: ollama serve")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama request timed out. Try fewer questions.")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {e}")

        questions = self._parse_mcqs(raw)
        logger.info(f"Parsed {len(questions)} valid MCQs")
        return questions

    def _parse_mcqs(self, raw: str) -> list[dict]:
        questions = []
        # Split on Q: to get individual question blocks
        blocks = re.split(r'\n(?=Q:)', raw.strip())

        for block in blocks:
            block = block.strip()
            if not block.startswith("Q:"):
                continue

            lines = [l.strip() for l in block.splitlines() if l.strip()]
            mcq = {"question": "", "A": "", "B": "", "C": "", "D": "", "answer": ""}

            for line in lines:
                if line.startswith("Q:"):
                    mcq["question"] = line[2:].strip()
                elif line.startswith("A."):
                    mcq["A"] = line[2:].strip()
                elif line.startswith("B."):
                    mcq["B"] = line[2:].strip()
                elif line.startswith("C."):
                    mcq["C"] = line[2:].strip()
                elif line.startswith("D."):
                    mcq["D"] = line[2:].strip()
                elif line.startswith("Answer:"):
                    mcq["answer"] = line.split(":", 1)[1].strip().upper()

            # Only keep fully formed MCQs
            if all([mcq["question"], mcq["A"], mcq["B"], mcq["C"], mcq["D"], mcq["answer"]]):
                if mcq["answer"] in ("A", "B", "C", "D"):
                    questions.append(mcq)
            else:
                logger.warning(f"Skipped malformed MCQ: {mcq['question'][:60]}")

        return questions