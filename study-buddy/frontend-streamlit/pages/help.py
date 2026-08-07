"""
Help Center Page — AI-Powered Study Buddy
==========================================
FAQs, feature guide, bug report link, feedback form, and About section.
Uses Design Tokens from design_system.py.
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
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">❓ Help Center</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                FAQs, feature guides, feedback, and project information.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_faq, tab_guide, tab_feedback, tab_about = st.tabs(
        ["📋 FAQs", "📖 Feature Guide", "💬 Feedback", "ℹ️ About"]
    )

    # ── FAQs ───────────────────────────────────────────────────────────────
    with tab_faq:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;margin-top:16px;">Frequently Asked Questions</div>', unsafe_allow_html=True)
        for q, a in FAQS:
            with st.expander(q):
                st.write(a)

    # ── Feature Guide ──────────────────────────────────────────────────────
    with tab_guide:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;margin-top:16px;">📖 Quick Feature Guide</div>', unsafe_allow_html=True)
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
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;margin-top:16px;">💬 Send Feedback</div>', unsafe_allow_html=True)
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
            submitted = st.form_submit_button("📤 Send Feedback", use_container_width=True, type="primary")

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
            <div class="content-card" style="margin-top:16px;font-size:13px;">
                You can also open a GitHub Issue directly at:<br>
                <a href="https://github.com/your-repo/study-buddy/issues"
                   style="color:var(--accent);font-weight:600;text-decoration:none;">
                   github.com/your-repo/study-buddy/issues</a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── About ──────────────────────────────────────────────────────────────
    with tab_about:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;margin-top:16px;">ℹ️ About Study Buddy</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="content-card">
                <h4 style="color:var(--text-primary);margin-bottom:12px;">🎓 AI-Powered Study Buddy</h4>
                <p style="color:var(--text-secondary);font-size:14px;">
                    A production-grade Generative AI study assistant built as an
                    <strong>IBM SkillsBuild Final Project (2026)</strong>.
                </p>
                <p style="color:var(--text-secondary);font-size:14px;margin-bottom:0;">
                    Uses <strong>Retrieval-Augmented Generation (RAG)</strong> to answer
                    questions grounded in the student's own uploaded documents, eliminating
                    hallucinations and providing personalised, context-aware learning.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        tech_col1, tech_col2 = st.columns(2)
        with tech_col1:
            st.markdown('<div style="color:var(--text-primary);font-weight:700;font-size:13px;margin-bottom:8px;">Frontend</div>', unsafe_allow_html=True)
            for t in ["Streamlit 1.32", "Custom CSS Token System", "Luxury AI SaaS Theme"]:
                st.markdown(f'<div style="color:var(--text-secondary);font-size:13px;margin-bottom:4px;">• {t}</div>', unsafe_allow_html=True)
            
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="color:var(--text-primary);font-weight:700;font-size:13px;margin-bottom:8px;">AI / ML</div>', unsafe_allow_html=True)
            for t in ["Google Gemini 1.5 Pro", "LangChain RAG", "Sentence Transformers"]:
                st.markdown(f'<div style="color:var(--text-secondary);font-size:13px;margin-bottom:4px;">• {t}</div>', unsafe_allow_html=True)

        with tech_col2:
            st.markdown('<div style="color:var(--text-primary);font-weight:700;font-size:13px;margin-bottom:8px;">Backend</div>', unsafe_allow_html=True)
            for t in ["FastAPI", "SQLAlchemy + SQLite", "JWT Auth"]:
                st.markdown(f'<div style="color:var(--text-secondary);font-size:13px;margin-bottom:4px;">• {t}</div>', unsafe_allow_html=True)
                
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="color:var(--text-primary);font-weight:700;font-size:13px;margin-bottom:8px;">Vector DB</div>', unsafe_allow_html=True)
            for t in ["ChromaDB (cosine similarity)", "all-MiniLM-L6-v2 embeddings"]:
                st.markdown(f'<div style="color:var(--text-secondary);font-size:13px;margin-bottom:4px;">• {t}</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align:center;margin-top:32px;color:var(--text-disabled);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;">
                Version 2.0 &nbsp;·&nbsp; MIT License &nbsp;·&nbsp; IBM SkillsBuild 2026
            </div>
            """,
            unsafe_allow_html=True,
        )
