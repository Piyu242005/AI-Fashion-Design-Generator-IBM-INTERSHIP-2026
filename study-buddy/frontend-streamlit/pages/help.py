"""
Help Center Page — AI-Powered Study Buddy
==========================================
FAQs, feature guide, bug report link, feedback form, and About section.
"""

from __future__ import annotations

import streamlit as st
from utils.session_state import init_session


FAQS: list[tuple[str, str]] = [
    ("What file types can I upload?",
     "PDF, DOCX, PPTX and TXT files up to 50 MB. Images within PDFs are skipped in v1."),
    ("How accurate are the AI answers?",
     "Answers are grounded in your uploaded documents via RAG, targeting >90% accuracy. "
     "The AI will say 'I don't know' rather than hallucinate when evidence is absent."),
    ("How many questions can a quiz have?",
     "Between 3 and 15 questions per quiz. Supports MCQ, True/False, and Short Answer."),
    ("Is my data secure?",
     "Files are stored locally on the server (or your Render instance). "
     "We scan for PII before indexing and never share your data with third parties."),
    ("Why is the first response slow?",
     "Render's free tier has a cold-start delay (~30 s). Subsequent requests are fast."),
    ("Can I delete my documents?",
     "Yes — go to Profile → My Documents → click the 🗑️ button next to any document."),
    ("What is RAG?",
     "Retrieval-Augmented Generation: your question is matched against embedded chunks "
     "of your documents, and only the most relevant chunks are sent to Gemini to generate "
     "a precise, grounded answer."),
    ("How is my study streak calculated?",
     "A streak day is counted when you perform any AI activity (chat, quiz, summary, flashcards) "
     "within a 24-hour window."),
]


def render() -> None:
    init_session()

    st.markdown(
        """
        <div class="page-header">
            <h1>❓ Help Center</h1>
            <p>FAQs, feature guides, feedback, and project information.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_faq, tab_guide, tab_feedback, tab_about = st.tabs(
        ["📋 FAQs", "📖 Feature Guide", "💬 Feedback", "ℹ️ About"]
    )

    # ── FAQs ───────────────────────────────────────────────────────────────
    with tab_faq:
        st.markdown("#### Frequently Asked Questions")
        for q, a in FAQS:
            with st.expander(q):
                st.write(a)

    # ── Feature Guide ──────────────────────────────────────────────────────
    with tab_guide:
        st.markdown("#### 📖 Quick Feature Guide")
        guide = {
            "💬 Chat (RAG Q&A)": [
                "Upload at least one document first.",
                "Go to Chat → select the document(s) to query.",
                "Type your question and press Send.",
                "The AI retrieves relevant passages and generates an answer.",
                "Source document references appear below each answer.",
            ],
            "📄 Summary": [
                "Go to Summary → select a document.",
                "Choose Bullet Points or Paragraph style.",
                "Adjust the detail level (Brief / Standard / Detailed).",
                "Click Generate Summary → download as .txt if needed.",
            ],
            "❓ Quiz": [
                "Go to Quiz → select document and question type.",
                "Adjust the number of questions (3–15).",
                "Click Generate Quiz → answer all questions.",
                "Submit to see your score and correct answers.",
                "Your scores feed the recommendation engine on the Dashboard.",
            ],
            "🃏 Flashcards": [
                "Go to Flashcards → select document and card count.",
                "Click Generate Flashcards.",
                "Click Flip to reveal the definition.",
                "Mark each card as ✅ Known or ⚠️ Review.",
                "Progress is tracked in the sidebar.",
            ],
        }
        for feature, steps in guide.items():
            with st.expander(feature):
                for i, step in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {step}")

    # ── Feedback ───────────────────────────────────────────────────────────
    with tab_feedback:
        st.markdown("#### 💬 Send Feedback")
        with st.form("feedback_form"):
            feedback_type = st.radio(
                "Type",
                ["Bug Report 🐛", "Feature Request ✨", "General Feedback 💬"],
                horizontal=True,
            )
            message = st.text_area(
                "Your message",
                placeholder="Describe the issue or your idea…",
                height=140,
            )
            submitted = st.form_submit_button("📤  Send Feedback", use_container_width=True)

        if submitted:
            if message.strip():
                st.success(
                    "Thank you for your feedback! 🙏 "
                    "In production this would be submitted to a GitHub Issue or email."
                )
            else:
                st.warning("Please write a message before submitting.")

        st.markdown(
            """
            <div class="custom-info">
                You can also open a GitHub Issue directly at:<br>
                <a href="https://github.com/your-repo/study-buddy/issues"
                   style="color:var(--accent);">
                   github.com/your-repo/study-buddy/issues</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── About ──────────────────────────────────────────────────────────────
    with tab_about:
        st.markdown("#### ℹ️ About Study Buddy")
        st.markdown(
            """
            <div class="content-card">
                <h4>🎓 AI-Powered Study Buddy</h4>
                <p style="color:var(--text);">
                    A production-grade Generative AI study assistant built as an
                    <strong>IBM SkillsBuild Final Project (2025)</strong>.
                </p>
                <p style="color:var(--text);">
                    Uses <strong>Retrieval-Augmented Generation (RAG)</strong> to answer
                    questions grounded in the student's own uploaded documents, eliminating
                    hallucinations and providing personalised, context-aware learning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tech_col1, tech_col2 = st.columns(2)
        with tech_col1:
            st.markdown("**Frontend**")
            for t in ["Streamlit 1.32", "Custom CSS Design System", "5 Themes"]:
                st.markdown(f"- {t}")
            st.markdown("**AI / ML**")
            for t in ["Google Gemini 1.5 Pro", "LangChain RAG", "Sentence Transformers"]:
                st.markdown(f"- {t}")

        with tech_col2:
            st.markdown("**Backend**")
            for t in ["FastAPI", "SQLAlchemy + SQLite", "JWT Auth"]:
                st.markdown(f"- {t}")
            st.markdown("**Vector DB**")
            for t in ["ChromaDB (cosine similarity)", "all-MiniLM-L6-v2 embeddings"]:
                st.markdown(f"- {t}")

        st.markdown(
            """
            <div style="text-align:center;margin-top:24px;color:var(--text-faint);
                        font-size:12px;">
                Version 1.0 &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; IBM SkillsBuild 2025
            </div>
            """,
            unsafe_allow_html=True,
        )
