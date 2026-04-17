from loguru import logger
from answer_agent import AnswerAgent
import sys

# Clean log format
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


class Orchestrator:
    def __init__(self, model: str = "mistral"):
        self.agent = AnswerAgent(model=model)
        logger.info(f"Orchestrator ready | model={model}")

    def generate_exam(self, syllabus: str, examples: str, n: int = 30) -> dict:
        """
        Main entry point.
        Returns: { "questions": [...], "count": int, "error": str | None }
        """
        result = {"questions": [], "count": 0, "error": None}

        # Validate inputs
        if not syllabus.strip():
            result["error"] = "Syllabus text is required."
            return result

        if not examples.strip():
            result["error"] = "Example questions are required."
            return result

        n = max(5, min(n, 50))

        try:
            logger.info(f"Starting exam generation | n={n}")
            questions = self.agent.generate_exam_questions(
                syllabus=syllabus,
                examples=examples,
                n=n
            )

            if not questions:
                result["error"] = "Model returned no valid MCQs. Try again or switch model."
                return result

            result["questions"] = questions
            result["count"] = len(questions)
            logger.success(f"Exam generation complete | {len(questions)} MCQs ready")

        except ConnectionError as e:
            logger.error(str(e))
            result["error"] = str(e)
        except TimeoutError as e:
            logger.error(str(e))
            result["error"] = str(e)
        except RuntimeError as e:
            logger.error(str(e))
            result["error"] = str(e)
        except Exception as e:
            logger.exception("Unexpected error")
            result["error"] = f"Unexpected error: {e}"

        return result