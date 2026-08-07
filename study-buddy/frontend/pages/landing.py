"""Landing Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st

def render() -> None:
    st.markdown(
        '<div style="text-align:center;padding:60px 24px 40px;animation:fadeInUp .5s ease;">'
        '<div style="font-size:72px;margin-bottom:16px;">🎓</div>'
        '<h1 style="font-size:40px;font-weight:900;color:var(--text);line-height:1.15;margin-bottom:12px;">'
        'AI-Powered<br><span style="color:var(--accent);">Study Buddy</span></h1>'
        '<p style="font-size:17px;color:var(--text-faint);max-width:480px;margin:0 auto 32px;line-height:1.7;">'
        'Upload your study materials. Ask questions. Get instant AI answers, summaries, '
        'quizzes and flashcards — powered by RAG + Gemini.</p></div>',
        unsafe_allow_html=True)

    _, c1, c2, _ = st.columns([2, 1, 1, 2])
    with c1:
        if st.button("🚀  Get Started", use_container_width=True):
            st.session_state["landing_tab"] = "register"
            st.session_state["show_auth"] = True
            st.rerun()
    with c2:
        if st.button("🔑  Sign In", use_container_width=True):
            st.session_state["landing_tab"] = "login"
            st.session_state["show_auth"] = True
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:40px 0;'>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center;color:var(--text);margin-bottom:24px;">✨ Everything You Need to Study Smarter</h2>', unsafe_allow_html=True)

    features = [
        ("🔍","RAG-Powered Q&A","Ask questions about your own documents. Answers grounded in your material."),
        ("📄","Smart Summaries","Get concise bullet-point or paragraph summaries in seconds."),
        ("❓","Quiz Generator","Auto-generate MCQ, True/False and Short Answer quizzes."),
        ("🃏","Flashcards","Extract key terms as interactive flip cards."),
        ("💡","Concept Explainer","Explain any concept simply with analogies and examples."),
        ("📊","Study Dashboard","Track scores, weak topics, and AI-powered revision recommendations."),
    ]

    c1, c2, c3 = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(
                f'<div class="content-card" style="text-align:center;padding:24px;">'
                f'<div style="font-size:36px;margin-bottom:10px;">{icon}</div>'
                f'<div style="font-weight:700;color:var(--text);font-size:15px;margin-bottom:8px;">{title}</div>'
                f'<div style="font-size:13px;color:var(--text-faint);line-height:1.6;">{desc}</div></div>',
                unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:40px 0;'>", unsafe_allow_html=True)
    techs = ["Google Gemini","LangChain","ChromaDB","Sentence Transformers","FastAPI","Streamlit"]
    badges = "".join(f'<span class="badge badge-blue">{t}</span> ' for t in techs)
    st.markdown(
        f'<div style="text-align:center;">'
        f'<div style="font-size:12px;color:var(--text-faint);text-transform:uppercase;'
        f'letter-spacing:.1em;margin-bottom:14px;">Powered By</div>{badges}</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;padding:32px 0 8px;color:var(--text-faint);font-size:12px;">'
        'AI-Powered Study Buddy · IBM SkillsBuild Final Project 2025</div>',
        unsafe_allow_html=True)
