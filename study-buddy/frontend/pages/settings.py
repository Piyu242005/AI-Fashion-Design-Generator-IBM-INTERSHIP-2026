"""
Settings Page — AI-Powered Study Buddy (Upgraded)
===================================================
Full settings panel:
  - Theme (Dark / Light / Blue / Purple / System)
  - Language
  - AI Style (Concise / Standard / Detailed)
  - Explanation level
  - Quiz preferences
  - Summary length
  - Chat memory depth
  - Daily goal
  - Accessibility (High Contrast, Large Fonts)
  - Export preferences
  - Delete Account (UI placeholder)
"""

from __future__ import annotations

import streamlit as st

from utils.session_state import init_session
from themes.design_system import THEMES, inject_theme
from components.toast import toast_success


def render() -> None:
    init_session()
    prefs: dict = st.session_state.get("user_preferences", {})

    st.markdown(
        """
        <div class="page-header">
            <h1>⚙️ Settings</h1>
            <p>Personalise every aspect of your Study Buddy experience.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_appear, tab_ai, tab_quiz, tab_access, tab_account = st.tabs([
        "🎨 Appearance", "🤖 AI & Learning", "❓ Quiz", "♿ Accessibility", "🔐 Account"
    ])

    # ─────────────────────────── Appearance ──────────────────────────────
    with tab_appear:
        st.markdown("#### 🎨 Theme")
        theme_cols = st.columns(5)
        theme_options = list(THEMES.keys())
        current_theme = prefs.get("theme", "Dark")

        for col, theme_name in zip(theme_cols, theme_options):
            with col:
                selected = current_theme == theme_name
                border = "var(--accent)" if selected else "var(--border)"
                t = THEMES[theme_name]
                st.markdown(
                    f"""
                    <div style="background:{t['bg']};border:2px solid {border};
                                border-radius:10px;padding:12px 8px;text-align:center;
                                cursor:pointer;transition:.2s;">
                        <div style="width:24px;height:24px;border-radius:50%;
                                    background:{t['accent']};margin:0 auto 6px;"></div>
                        <div style="font-size:11px;color:{t['text']};font-weight:700;">
                            {theme_name}</div>
                        {"<div style='font-size:9px;color:#3b82f6;'>✓ Active</div>" if selected else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(theme_name, key=f"theme_{theme_name}",
                             use_container_width=True):
                    prefs["theme"] = theme_name
                    st.session_state["user_preferences"] = prefs
                    inject_theme(theme_name)
                    toast_success(f"{theme_name} theme applied")
                    st.rerun()

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🔤 Typography")
            font_size = st.select_slider(
                "Font size",
                options=["Small (12px)", "Medium (14px)", "Large (16px)"],
                value=prefs.get("font_size", "Medium (14px)"),
                key="set_font",
            )
            prefs["font_size"] = font_size

        with col_r:
            st.markdown("#### 📐 Layout")
            sidebar_default = st.radio(
                "Default sidebar state",
                ["Expanded", "Collapsed"],
                index=0 if prefs.get("sidebar", "Expanded") == "Expanded" else 1,
                horizontal=True,
                key="set_sidebar",
            )
            prefs["sidebar"] = sidebar_default

    # ─────────────────────────── AI & Learning ───────────────────────────
    with tab_ai:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("#### 🤖 Response Style")
            ai_style = st.radio(
                "AI verbosity",
                ["Concise", "Standard", "Detailed"],
                index=["Concise","Standard","Detailed"].index(
                    prefs.get("ai_style", "Standard")),
                key="set_ai_style",
            )
            prefs["ai_style"] = ai_style

            st.markdown("#### 🌐 Language")
            lang = st.selectbox(
                "Response language",
                ["English", "Hindi", "Spanish", "French"],
                index=["English","Hindi","Spanish","French"].index(
                    prefs.get("language", "English")),
                key="set_lang",
                help="Multi-language support in v2.0",
            )
            prefs["language"] = lang

        with col_r:
            st.markdown("#### 💡 Explanation Level")
            explain = st.selectbox(
                "Concept explanation depth",
                ["Beginner (ELI5)", "Intermediate", "Advanced"],
                index=["Beginner (ELI5)","Intermediate","Advanced"].index(
                    prefs.get("explain_level", "Intermediate")),
                key="set_explain",
            )
            prefs["explain_level"] = explain

            st.markdown("#### 🧠 Chat Memory Depth")
            memory = st.slider(
                "Number of previous turns to remember",
                min_value=2, max_value=20, value=prefs.get("memory_depth", 10),
                step=2, key="set_memory",
            )
            prefs["memory_depth"] = memory

        st.markdown("#### 📄 Summary Length")
        sum_len = st.select_slider(
            "Default summary length",
            options=["Brief (3–5 bullets)", "Standard (5–8 bullets)", "Detailed (8–12 bullets)"],
            value=prefs.get("summary_len", "Standard (5–8 bullets)"),
            key="set_sum_len",
        )
        prefs["summary_len"] = sum_len

    # ─────────────────────────── Quiz ────────────────────────────────────
    with tab_quiz:
        col_l, col_r = st.columns(2)
        with col_l:
            quiz_diff = st.select_slider(
                "Default difficulty",
                options=["Easy", "Medium", "Hard"],
                value=prefs.get("quiz_diff", "Medium"),
                key="set_quiz_diff",
            )
            prefs["quiz_diff"] = quiz_diff

            qtype = st.radio(
                "Default question type",
                ["MCQ", "True/False", "Short Answer", "Mixed"],
                index=["MCQ","True/False","Short Answer","Mixed"].index(
                    prefs.get("qtype", "MCQ")),
                horizontal=False,
                key="set_qtype",
            )
            prefs["qtype"] = qtype

        with col_r:
            qcount = st.slider(
                "Default question count",
                3, 15, prefs.get("qcount", 5),
                key="set_qcount",
            )
            prefs["qcount"] = qcount

            daily_goal = st.slider(
                "Daily study goal (minutes)",
                10, 180, prefs.get("daily_goal", 30),
                step=5, key="set_daily_goal",
            )
            prefs["daily_goal"] = daily_goal

            streak_reminder = st.toggle(
                "Show streak reminder",
                value=prefs.get("streak_reminder", True),
                key="set_streak",
            )
            prefs["streak_reminder"] = streak_reminder

    # ─────────────────────────── Accessibility ───────────────────────────
    with tab_access:
        col_l, col_r = st.columns(2)
        with col_l:
            high_contrast = st.toggle(
                "High Contrast Mode",
                value=prefs.get("high_contrast", False),
                key="set_hc",
                help="Increases border and text contrast ratios.",
            )
            prefs["high_contrast"] = high_contrast

            large_fonts = st.toggle(
                "Large Font Mode",
                value=prefs.get("large_fonts", False),
                key="set_lf",
                help="Sets base font size to 16px.",
            )
            prefs["large_fonts"] = large_fonts

        with col_r:
            reduce_motion = st.toggle(
                "Reduce Motion",
                value=prefs.get("reduce_motion", False),
                key="set_rm",
                help="Disables fade-in and card hover animations.",
            )
            prefs["reduce_motion"] = reduce_motion

        st.markdown(
            """
            <div class="custom-info">
                <strong>Keyboard Shortcuts (v1.0)</strong><br>
                <code>Ctrl + /</code> — Focus search bar<br>
                <code>Ctrl + K</code> — Open chat input<br>
                <code>→ / ←</code> — Navigate flashcards<br>
                <code>Space</code> — Flip flashcard
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ─────────────────────────── Account ─────────────────────────────────
    with tab_account:
        st.markdown("#### 🔐 Security")
        st.markdown(
            """
            <div class="custom-info">
                • JWT tokens expire after <strong>30 minutes</strong>.<br>
                • Passwords are hashed with <strong>bcrypt</strong>.<br>
                • API keys stored in <strong>environment variables only</strong>.<br>
                • Uploaded files scanned for <strong>PII</strong> before indexing.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("#### 📤 Export Data")
        if st.button("⬇️  Export My Data (JSON)", use_container_width=False):
            st.info("Data export will be available in v1.5 — adds GDPR compliance.")

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("#### 🗑️ Danger Zone")
        st.markdown(
            '<div class="custom-warning">Deleting your account is permanent '
            'and cannot be undone.</div>',
            unsafe_allow_html=True,
        )
        if st.button("🗑️  Delete My Account", type="primary"):
            st.warning("This will be fully implemented in v1.5 with confirmation flow.")

    # ─────────────────────────── Save ────────────────────────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button("💾  Save All Settings", use_container_width=True, key="save_settings"):
            st.session_state["user_preferences"] = prefs
            toast_success("Settings saved!")
            st.rerun()
