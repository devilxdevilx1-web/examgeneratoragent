import streamlit as st
import sys
import os

# Allow import of orchestrator from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orchestrator import Orchestrator

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kalvium Exam Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    model = st.selectbox(
        "Ollama Model",
        ["mistral", "phi3", "llama3", "gemma"],
        index=0,
        help="Make sure this model is pulled via `ollama pull <model>`"
    )
    n_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=50,
        value=30,
        step=5
    )
    st.markdown("---")
    st.markdown("**Ollama must be running:**")
    st.code("ollama serve", language="bash")
    st.markdown("**Pull a model:**")
    st.code(f"ollama pull {model}", language="bash")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎯 Kalvium-Style Exam Question Generator")
st.caption("Paste syllabus + example questions → get exam-ready MCQs instantly")
st.markdown("---")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Syllabus")
    syllabus_text = st.text_area(
        label="syllabus",
        height=320,
        placeholder=(
            "Paste your syllabus here — messy or structured, both work.\n\n"
            "e.g.\n"
            "- HTML5 semantic elements\n"
            "- CSS Flexbox and Grid layout\n"
            "- JavaScript: closures, event loop, promises\n"
            "- React: useState, useEffect, useContext\n"
            "- DOM manipulation, browser APIs"
        ),
        label_visibility="collapsed"
    )

with col2:
    st.subheader("📋 Example Questions")
    example_questions = st.text_area(
        label="examples",
        height=320,
        placeholder=(
            "Paste 5–20 example exam questions here.\n\n"
            "e.g.\n"
            "Q: What does the 'key' prop do in React lists?\n"
            "A. Adds CSS styling\n"
            "B. Helps React identify changed elements\n"
            "C. Binds event listeners\n"
            "D. Prevents re-renders\n"
            "Answer: B"
        ),
        label_visibility="collapsed"
    )

st.markdown("---")

# ── Generate button ───────────────────────────────────────────────────────────
generate = st.button(
    f"🚀 Generate {n_questions} Exam Questions",
    use_container_width=True,
    type="primary"
)

# ── Generation logic ──────────────────────────────────────────────────────────
if generate:
    if not syllabus_text.strip():
        st.error("⚠️ Please enter syllabus text.")
    elif not example_questions.strip():
        st.error("⚠️ Please enter example questions.")
    else:
        with st.spinner(f"Generating {n_questions} MCQs with {model}... this may take 30–90 seconds."):
            orchestrator = Orchestrator(model=model)
            result = orchestrator.generate_exam(
                syllabus=syllabus_text,
                examples=example_questions,
                n=n_questions
            )

        if result["error"]:
            st.error(f"❌ {result['error']}")

        elif result["questions"]:
            questions = result["questions"]
            st.success(f"✅ Generated {result['count']} exam-ready MCQs")
            st.markdown("---")
            st.subheader("📝 Exam Questions")

            # Build plain text for download
            lines = []

            for i, q in enumerate(questions, 1):
                # Display card
                with st.container():
                    st.markdown(f"**Q{i}. {q['question']}**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"&nbsp;&nbsp;A. {q['A']}")
                        st.markdown(f"&nbsp;&nbsp;B. {q['B']}")
                    with col_b:
                        st.markdown(f"&nbsp;&nbsp;C. {q['C']}")
                        st.markdown(f"&nbsp;&nbsp;D. {q['D']}")

                    ans_label = q['answer']
                    ans_text = q.get(ans_label, "")
                    st.markdown(
                        f"<span style='color:#2ecc71;font-weight:600'>✔ Answer: {ans_label}. {ans_text}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown("---")

                # Accumulate text for download
                lines.append(f"Q{i}. {q['question']}")
                lines.append(f"A. {q['A']}")
                lines.append(f"B. {q['B']}")
                lines.append(f"C. {q['C']}")
                lines.append(f"D. {q['D']}")
                lines.append(f"Answer: {q['answer']}")
                lines.append("")

            # Download button
            st.download_button(
                label="⬇️ Download as .txt",
                data="\n".join(lines),
                file_name="exam_questions.txt",
                mime="text/plain",
                use_container_width=True
            )