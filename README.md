# ExamQuestionGenerator

A minimal Python agent that generates up to 50 high-quality exam-style questions
from raw syllabus text and example questions — using a local LLM via Ollama.

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- `phi3` model pulled

---

## Setup

### 1. Install Ollama
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download from https://ollama.com/download
```

### 2. Pull the phi3 model
```bash
ollama pull phi3
```

### 3. Start Ollama (if not already running)
```bash
ollama serve
```

### 4. Install Python dependency
```bash
pip install requests
```

---

## Usage

```bash
python main.py
```

You'll be prompted to:
1. Paste your **syllabus text** (messy/unstructured is fine)
2. Paste your **example questions** (inconsistent format is fine)
3. Choose how many questions to generate (1–50, default: 50)

Press **Enter twice** to finish each input section.

---

## Example Session

```
📚 Paste your SYLLABUS TEXT below:
(Press Enter twice when done)

HTML5 semantic elements, CSS flexbox and grid layout,
JavaScript closures, event loop, promises and async/await,
React hooks - useState useEffect useContext,
DOM manipulation, browser APIs...

[blank line]
[blank line]

📝 Paste your EXAMPLE QUESTIONS below:
(Press Enter twice when done)

1. What is the output of this closure?
2. Why might this useEffect cause infinite re-renders?
...

[blank line]
[blank line]

🔢 How many questions to generate? (default: 50): 20
```

---

## Output

```
============================================================
           GENERATED EXAM QUESTIONS
============================================================

1. What happens when a flex container has no width but child elements have fixed widths?
2. Why might useEffect cause an infinite loop in React?
3. Predict the output of this closure-based function...
...

============================================================
Total: 20 questions generated.
============================================================
```

---

## Project Structure

```
ExamQuestionGenerator/
├── generator.py   # QuestionGenerator class — core logic
├── main.py        # CLI entry point — input/output
└── README.md
```

---

## How It Works

The agent uses a carefully crafted prompt that instructs the LLM to:

1. **Clean & structure** the syllabus — extract topics, subtopics, key concepts
2. **Analyze example questions** — detect patterns (conceptual, scenario-based, debugging, output prediction), infer difficulty
3. **Fuse** extracted concepts with identified question patterns
4. **Generate NEW questions** that match exam style — not generic, not copies

All intelligence is in the prompt. No databases, no embeddings, no FAISS.
