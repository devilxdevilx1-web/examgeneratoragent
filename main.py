import sys
from generator import QuestionGenerator


def read_multiline(prompt: str) -> str:
    """Read multiline input until the user enters a blank line twice or EOF."""
    print(prompt)
    print("(Press Enter twice when done)\n")
    lines = []
    blank_count = 0

    while True:
        try:
            line = input()
        except EOFError:
            break

        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)

    return "\n".join(lines).strip()


def print_questions(questions: list[str]) -> None:
    print("\n" + "=" * 60)
    print("           GENERATED EXAM QUESTIONS")
    print("=" * 60 + "\n")

    if not questions:
        print("No questions were generated. Check model output.")
        return

    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")

    print(f"\n{'=' * 60}")
    print(f"Total: {len(questions)} questions generated.")
    print("=" * 60)


def main():
    print("\n╔══════════════════════════════════════╗")
    print("║     Exam Question Generator           ║")
    print("╚══════════════════════════════════════╝\n")

    # Get syllabus input
    syllabus_text = read_multiline("📚 Paste your SYLLABUS TEXT below:")

    if not syllabus_text:
        print("Error: Syllabus text cannot be empty.")
        sys.exit(1)

    print()

    # Get example questions input
    example_questions = read_multiline("📝 Paste your EXAMPLE QUESTIONS below:")

    if not example_questions:
        print("Error: Example questions cannot be empty.")
        sys.exit(1)

    # Optional: ask for number of questions
    print()
    try:
        n_input = input("🔢 How many questions to generate? (default: 50): ").strip()
        n = int(n_input) if n_input else 50
        n = max(1, min(n, 50))  # clamp between 1 and 50
    except ValueError:
        n = 50

    print(f"\n⚙️  Generating {n} exam questions using phi3 model...")
    print("This may take a moment...\n")

    generator = QuestionGenerator(model="mistral")

    try:
        questions = generator.generate(
            syllabus_text=syllabus_text,
            examples=example_questions,
            n=n
        )
        print_questions(questions)

    except ConnectionError as e:
        print(f"\n❌ Connection Error:\n{e}")
        sys.exit(1)
    except TimeoutError as e:
        print(f"\n❌ Timeout Error:\n{e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Runtime Error:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()