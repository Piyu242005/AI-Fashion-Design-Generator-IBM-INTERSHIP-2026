"""
Landing Page — AI-Powered Study Buddy (Luxury SaaS Edition)
============================================================
Cinematic marketing hero, animated headline with red gradient text,
interactive capability cards, 4-step workflow, stats, and CTAs.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

import streamlit as st

def render() -> None:
    # ── Hero Section ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="text-align:center;padding:60px 20px 40px;">
            <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 16px;
                        border-radius:999px;background:var(--surface);
                        border:1px solid var(--border);color:var(--text-secondary);
                        font-size:12px;font-weight:600;letter-spacing:0.04em;
                        margin-bottom:24px;box-shadow:var(--shadow);">
                <span style="width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block;box-shadow:0 0 10px var(--accent);"></span>
                Introducing Study Buddy AI OS
            </div>
            <h1 style="font-size:56px;font-weight:800;color:var(--text-primary);line-height:1.15;
                       letter-spacing:-0.04em;margin-bottom:20px;max-width:800px;margin-left:auto;margin-right:auto;">
                Study Smarter With <span style="background:linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span><br>
                That Knows Your Notes
            </h1>
            <p style="font-size:16px;color:var(--text-secondary);max-width:600px;margin:0 auto 40px;line-height:1.6;">
                Upload your course materials. Ask questions. Receive grounded, cited answers,
                instant summaries, adaptive quizzes, and active recall flashcards in milliseconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── CTA Buttons ────────────────────────────────────────────────────────
    _, c1, c2, _ = st.columns([1.5, 1, 1, 1.5])
    with c1:
        if st.button("Start for Free", use_container_width=True, type="primary", key="hero_cta"):
            st.session_state["landing_tab"] = "register"
            st.session_state["show_auth"]   = True
            st.rerun()
    with c2:
        if st.button("Sign In", use_container_width=True, type="secondary", key="hero_login"):
            st.session_state["landing_tab"] = "login"
            st.session_state["show_auth"]   = True
            st.rerun()

    # ── Live Stats Strip ───────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in" style="display:flex;justify-content:center;gap:48px;flex-wrap:wrap;
                    padding:32px 0;margin:48px 0 32px;border-top:1px solid var(--border);
                    border-bottom:1px solid var(--border);text-align:center;">
            <div>
                <div style="font-size:28px;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;">50 MB</div>
                <div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;font-weight:600;letter-spacing:0.04em;margin-top:4px;">Max File Size</div>
            </div>
            <div>
                <div style="font-size:28px;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;">&lt; 2s</div>
                <div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;font-weight:600;letter-spacing:0.04em;margin-top:4px;">RAG Latency</div>
            </div>
            <div>
                <div style="font-size:28px;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;">100%</div>
                <div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;font-weight:600;letter-spacing:0.04em;margin-top:4px;">Grounded Context</div>
            </div>
            <div>
                <div style="font-size:28px;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;">0.00$</div>
                <div style="font-size:12px;color:var(--text-secondary);text-transform:uppercase;font-weight:600;letter-spacing:0.04em;margin-top:4px;">Open Source</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Feature Grid ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="text-align:center;margin:64px 0 32px;">
            <div style="font-size:12px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">
                Core Capabilities
            </div>
            <h2 style="font-size:32px;font-weight:800;color:var(--text-primary);">
                Everything Your Brain Needs to Excel
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    features = [
        ("🔍", "RAG-Powered Chat",
         "Ask anything about your study notes. Answers are strictly grounded in your materials with exact source citations."),
        ("📝", "Instant Summaries",
         "Generate bulleted, paragraph, or executive deep-dives of 100-page chapters in seconds."),
        ("❓", "Adaptive Quizzes",
         "Auto-generate MCQ, True/False, and Short Answer questions with real-time scoring and explanations."),
        ("🃏", "Smart Flashcards",
         "Interactive flip cards with spaced repetition. Mark terms as Known or Review to maximize memory retention."),
        ("💡", "Concept Explainer",
         "Ask the Teaching Agent to explain any complex topic in plain terms with relatable real-world analogies."),
        ("📊", "Study Analytics",
         "Track study streaks, quiz accuracy per topic, and receive personalized AI recommendations."),
    ]

    r1, r2, r3 = st.columns(3)
    cols = [r1, r2, r3, r1, r2, r3]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="content-card" style="padding:28px;height:100%;">
                    <div style="font-size:32px;margin-bottom:16px;">{icon}</div>
                    <div style="font-weight:700;color:var(--text-primary);font-size:16px;margin-bottom:8px;">
                        {title}
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);line-height:1.6;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── How It Works ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="text-align:center;margin:64px 0 32px;">
            <div style="font-size:12px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">
                Simple Workflow
            </div>
            <h2 style="font-size:32px;font-weight:800;color:var(--text-primary);">
                How Study Buddy Works
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = [
        ("01", "Upload Notes", "Drop your PDF, DOCX, PPTX, or TXT study materials."),
        ("02", "Vector Indexing", "Content is chunked and stored in ChromaDB vector space."),
        ("03", "Ask & Generate", "Query with natural language or trigger 1-click quizzes."),
        ("04", "Master & Track", "Study with flashcards and watch your streak grow."),
    ]

    step_cols = st.columns(4)
    for col, (num, title, desc) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align:center;padding:24px;background:var(--surface);
                            border:1px solid var(--border);border-radius:var(--radius);
                            box-shadow:var(--shadow);height:100%;">
                    <div style="font-size:20px;font-weight:800;color:var(--accent);margin-bottom:8px;">
                        {num}
                    </div>
                    <div style="font-weight:700;color:var(--text-primary);font-size:15px;margin-bottom:8px;">
                        {title}
                    </div>
                    <div style="font-size:13px;color:var(--text-secondary);line-height:1.6;">
                        {desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:64px 0 32px;color:var(--text-disabled);font-size:13px;
                    border-top:1px solid var(--border);margin-top:64px;">
            AI-Powered Study Buddy &nbsp;·&nbsp; IBM SkillsBuild 2026 &nbsp;·&nbsp; Google Gemini 1.5 Pro &nbsp;·&nbsp; ChromaDB
        </div>
        """,
        unsafe_allow_html=True,
    )
