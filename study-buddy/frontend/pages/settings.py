"""
Settings Page — AI-Powered Study Buddy
========================================
User-configurable preferences:
  - AI response style (concise / detailed)
  - Quiz difficulty (easy / medium / hard)
  - Explanation level (beginner / intermediate / advanced)
  - Daily study goal (minutes)
  - Notification preferences (UI-only in this version)
"""

from __future__ import annotations

import streamlit as st

from utils.session_state import init_session


def render() -> None:
    init_session()

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>⚙️ Settings</h1>
            <p>Personalise your AI Study Buddy experience.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_r = st.columns(2)

    # ────────────────────────── Left column ───────────────────────────────
    with col_l:
        st.markdown("#### 🤖 AI Preferences")

        ai_style = st.radio(
            "Response style",
            ["Concise", "Standard", "Detailed"],
            index=1,
            key="pref_ai_style",
            help="Controls how verbose Gemini's answers are.",
        )

        explain_level = st.selectbox(
            "Explanation level",
            ["Beginner (ELI5)", "Intermediate", "Advanced"],
            index=1,
            key="pref_explain_level",
            help="How simply concepts are explained.",
        )

        lang = st.selectbox(
            "Language",
            ["English", "Hindi", "Spanish", "French"],
            index=0,
            key="pref_language",
            help="Response language (multi-language coming in v2).",
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("#### ❓ Quiz Preferences")

        quiz_diff = st.select_slider(
            "Quiz difficulty",
            options=["Easy", "Medium", "Hard"],
            value="Medium",
            key="pref_quiz_diff",
        )

        default_qtype = st.radio(
            "Default question type",
            ["MCQ", "True/False", "Mixed"],
            index=0,
            horizontal=True,
            key="pref_qtype",
        )

        default_count = st.slider(
            "Default question count",
            3, 15, 5,
            key="pref_qcount",
        )

    # ────────────────────────── Right column ──────────────────────────────
    with col_r:
        st.markdown("#### 🎯 Study Goals")

        daily_goal = st.slider(
            "Daily study goal (minutes)",
            10, 180, 30,
            step=5,
            key="pref_daily_goal",
        )

        streak_reminder = st.toggle(
            "Show streak reminder",
            value=True,
            key="pref_streak_reminder",
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("#### 🎨 Appearance")

        dark_mode = st.toggle(
            "Dark mode",
            value=st.session_state.get("dark_mode", True),
            key="pref_dark_mode",
        )
        st.session_state["dark_mode"] = dark_mode

        font_size = st.select_slider(
            "Font size",
            options=["Small", "Medium", "Large"],
            value="Medium",
            key="pref_font",
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("#### 🔐 Security")

        st.markdown(
            """
            <div class="custom-info">
                JWT tokens expire after <strong>30 minutes</strong>.<br>
                API keys are stored securely in environment variables.<br>
                Uploaded files are scanned for PII before indexing.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Save button ────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button("💾  Save Settings", use_container_width=True):
            # Persist preferences to session state
            prefs = {
                "ai_style":     ai_style,
                "explain_level": explain_level,
                "language":     lang,
                "quiz_diff":    quiz_diff,
                "qtype":        default_qtype,
                "qcount":       default_count,
                "daily_goal":   daily_goal,
                "streak_reminder": streak_reminder,
                "dark_mode":    dark_mode,
                "font_size":    font_size,
            }
            st.session_state["user_preferences"] = prefs
            st.success("✅ Settings saved successfully!")
            st.markdown(
                '<div class="custom-info">Settings are stored for this session. '
                "Persistent user preferences will sync to the database in v1.5.</div>",
                unsafe_allow_html=True,
            )
