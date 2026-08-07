"""
Landing Page — AI-Powered Study Buddy
=======================================
Public-facing hero page shown before login.
Features: Hero banner, Feature grid, How-it-works, CTA buttons.
No login required — navigates to Login/Register tabs.
"""

from __future__ import annotations

import streamlit as st


def render() -> None:
    # ── Hero Section ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:60px 24px 40px;
                    animation:fadeInUp .5s ease;">
            <div style="font-size:72px;margin-bottom:16px;">🎓</div>
            <h1 style="font-size:40px;font-weight:900;color:var(--text);
                       line-height:1.15;margin-bottom:12px;">
                AI-Powered<br>
                <span style="color:var(--accent);">Study Buddy</span>
            </h1>
            <p style="font-size:17px;color:var(--text-faint);max-width:480px;
                      margin:0 auto 32px;line-height:1.7;">
                Upload your study materials. Ask questions. Get instant AI answers,
                summaries, quizzes and flashcards — powered by RAG + Gemini.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── CTA Buttons ────────────────────────────────────────────────────────
    _, c1, c2, _ = st.columns([2, 1, 1, 2])
    with c1:
        if st.button("🚀  Get Started", use_container_width=True, key="hero_cta"):
            st.session_state["landing_tab"] = "register"
            st.session_state["show_auth"]   = True
            st.rerun()
    with c2:
        if st.button("🔑  Sign In", use_container_width=True, key="hero_login"):
            st.session_state["landing_tab"] = "login"
            st.session_state["show_auth"]   = True
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:40px 0;'>",
                unsafe_allow_html=True)

    # ── Feature Grid ───────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="text-align:center;color:var(--text);margin-bottom:24px;">'
        '✨ Everything You Need to Study Smarter</h2>',
        unsafe_allow_html=True,
    )

    features = [
        ("🔍", "RAG-Powered Q&A",
         "Ask questions about your own documents. Answers are grounded in your uploaded material — not generic web knowledge."),
        ("📄", "Smart Summaries",
         "Get concise bullet-point or paragraph summaries of any PDF, DOCX, PPTX or TXT file in seconds."),
        ("❓", "Quiz Generator",
         "Auto-generate MCQ, True/False and Short Answer quizzes. Test yourself and track your weak topics."),
        ("🃏", "Flashcards",
         "Extract key terms and definitions as interactive flip cards. Mark known vs review to track progress."),
        ("💡", "Concept Explainer",
         "Ask the AI to explain any concept in simple language, with analogies and examples tailored to your level."),
        ("📊", "Study Dashboard",
         "Track study time, streak, quiz scores, weak topics, and AI-powered revision recommendations."),
    ]

    r1, r2, r3 = st.columns(3)
    cols = [r1, r2, r3, r1, r2, r3]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="content-card" style="text-align:center;padding:24px;
                     animation:fadeInUp .4s ease;">
                    <div style="font-size:36px;margin-bottom:10px;">{icon}</div>
                    <div style="font-weight:700;color:var(--text);font-size:15px;
                                margin-bottom:8px;">{title}</div>
                    <div style="font-size:13px;color:var(--text-faint);
                                line-height:1.6;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:40px 0;'>",
                unsafe_allow_html=True)

    # ── How It Works ───────────────────────────────────────────────────────
    st.markdown(
        '<h2 style="text-align:center;color:var(--text);margin-bottom:28px;">'
        '🔄 How It Works</h2>',
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "Upload", "Upload your PDF, DOCX, PPTX or TXT study material."),
        ("2", "Index",  "The AI extracts, chunks, and embeds your content into ChromaDB."),
        ("3", "Ask",    "Type any question — RAG retrieves relevant chunks from your docs."),
        ("4", "Learn",  "Gemini generates a precise, grounded answer, quiz, or summary."),
    ]

    step_cols = st.columns(4)
    for col, (num, title, desc) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align:center;padding:16px;animation:fadeInUp .5s ease;">
                    <div style="width:48px;height:48px;border-radius:50%;
                                background:var(--accent);color:#fff;
                                font-size:20px;font-weight:800;
                                display:inline-flex;align-items:center;
                                justify-content:center;margin-bottom:12px;">
                        {num}
                    </div>
                    <div style="font-weight:700;color:var(--text);
                                font-size:14px;margin-bottom:6px;">{title}</div>
                    <div style="font-size:12px;color:var(--text-faint);
                                line-height:1.6;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<hr style='border:none;border-top:1px solid var(--border);margin:40px 0;'>",
                unsafe_allow_html=True)

    # ── Tech Stack Banner ──────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:16px 0;">
            <div style="font-size:12px;color:var(--text-faint);
                        text-transform:uppercase;letter-spacing:.1em;
                        margin-bottom:14px;">Powered By</div>
            <div style="display:flex;justify-content:center;flex-wrap:wrap;gap:12px;">
        """,
        unsafe_allow_html=True,
    )
    techs = ["Google Gemini", "LangChain", "ChromaDB",
             "Sentence Transformers", "FastAPI", "Streamlit"]
    badges_html = "".join(
        f'<span class="badge badge-blue">{t}</span>' for t in techs
    )
    st.markdown(
        f'{badges_html}</div></div>',
        unsafe_allow_html=True,
    )

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:32px 0 8px;color:var(--text-faint);
                    font-size:12px;">
            AI-Powered Study Buddy &nbsp;·&nbsp; IBM SkillsBuild Final Project 2025
        </div>
        """,
        unsafe_allow_html=True,
    )
