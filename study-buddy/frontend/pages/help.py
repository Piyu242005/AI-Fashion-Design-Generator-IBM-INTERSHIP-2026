"""Help Center Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.session_state import init_session

FAQS = [
    ("What file types can I upload?","PDF, DOCX, PPTX and TXT up to 50 MB."),
    ("How accurate are AI answers?","Answers are grounded in your documents via RAG, targeting >90% accuracy."),
    ("How many quiz questions?","3–15 per quiz. MCQ, True/False, or Short Answer."),
    ("Is my data secure?","Files stored locally. PII scanned before indexing."),
    ("Why is the first response slow?","Render free tier has ~30s cold-start. Subsequent calls are fast."),
    ("Can I delete documents?","Yes — Profile → My Documents → 🗑️ button."),
    ("What is RAG?","Retrieval-Augmented Generation — your question is matched to document chunks, then sent to Gemini."),
    ("How is streak calculated?","Any AI activity (chat/quiz/summary/flashcards) within 24 hours counts as a streak day."),
]

def render():
    init_session()
    st.markdown('<div class="page-header"><h1>❓ Help Center</h1>'
                '<p>FAQs, feature guides, feedback, and project information.</p></div>',
                unsafe_allow_html=True)
    tab_faq, tab_guide, tab_feedback, tab_about = st.tabs(["📋 FAQs","📖 Feature Guide","💬 Feedback","ℹ️ About"])

    with tab_faq:
        st.markdown("#### Frequently Asked Questions")
        for q, a in FAQS:
            with st.expander(q):
                st.write(a)

    with tab_guide:
        st.markdown("#### 📖 Quick Feature Guide")
        for feature, steps in {
            "💬 Chat (RAG Q&A)": ["Upload a document","Go to Chat → select document","Type your question","AI retrieves relevant passages and answers"],
            "📄 Summary":        ["Go to Summary → select document","Choose Bullet or Paragraph style","Click Generate Summary","Download as .txt"],
            "❓ Quiz":           ["Go to Quiz → select document","Choose question type and count","Click Generate Quiz","Answer and submit to see score"],
            "🃏 Flashcards":     ["Go to Flashcards → select document","Click Generate Flashcards","Flip each card","Mark Known or Review"],
        }.items():
            with st.expander(feature):
                for i, s in enumerate(steps, 1):
                    st.markdown(f"**{i}.** {s}")

    with tab_feedback:
        st.markdown("#### 💬 Send Feedback")
        with st.form("feedback_form"):
            ftype   = st.radio("Type",["Bug Report 🐛","Feature Request ✨","General Feedback 💬"],horizontal=True)
            message = st.text_area("Message", placeholder="Describe the issue or idea…", height=120)
            sub     = st.form_submit_button("📤  Send Feedback", use_container_width=True)
        if sub:
            if message.strip():
                st.success("Thank you for your feedback! 🙏")
            else:
                st.warning("Please write a message before submitting.")

    with tab_about:
        st.markdown("#### ℹ️ About Study Buddy")
        st.markdown(
            '<div class="content-card"><h4>🎓 AI-Powered Study Buddy</h4>'
            '<p style="color:var(--text);">IBM SkillsBuild Final Project 2025 — '
            'Generative AI study assistant with RAG, LangChain, and Google Gemini.</p>'
            '<p style="color:var(--text);">Version 1.0 &nbsp;·&nbsp; MIT License</p></div>',
            unsafe_allow_html=True)
