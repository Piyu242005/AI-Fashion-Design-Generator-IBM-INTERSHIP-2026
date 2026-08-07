"""
Settings Page — AI-Powered Study Buddy (Luxury AI SaaS Edition)
================================================================
Full settings panel for Appearance, AI settings, Quiz defaults, 
Accessibility, and Account management.
Uses Design Tokens from design_system.py.
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
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">⚙️ Settings</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Personalise every aspect of your Study Buddy workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_appear, tab_ai, tab_quiz, tab_access, tab_account = st.tabs([
        "🎨 Appearance", "🤖 AI & Learning", "❓ Quiz", "♿ Accessibility", "🔐 Account"
    ])

    # ─────────────────────────── Appearance ──────────────────────────────
    with tab_appear:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;margin-top:16px;">🎨 Theme</div>', unsafe_allow_html=True)
        theme_cols = st.columns(3)
        # Simplify themes since we unified to Luxury Dark token engine
        theme_options = ["Luxury Dark", "Light (Coming Soon)", "System"]
        current_theme = prefs.get("theme", "Luxury Dark")

        for col, theme_name in zip(theme_cols, theme_options):
            with col:
                selected = current_theme == theme_name
                border = "var(--accent)" if selected else "var(--border)"
                st.markdown(
                    f"""
                    <div class="content-card" style="border:2px solid {border};padding:16px;text-align:center;cursor:pointer;">
                        <div style="width:32px;height:32px;border-radius:50%;background:var(--accent);margin:0 auto 12px;box-shadow:var(--shadow);"></div>
                        <div style="font-size:13px;color:var(--text-primary);font-weight:700;">{theme_name}</div>
                        {"<div style='font-size:11px;color:var(--accent);margin-top:4px;font-weight:600;'>✓ Active</div>" if selected else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(theme_name, key=f"theme_{theme_name}", use_container_width=True, disabled=theme_name == "Light (Coming Soon)"):
                    prefs["theme"] = theme_name
                    st.session_state["user_preferences"] = prefs
                    inject_theme(theme_name)
                    toast_success(f"{theme_name} theme applied")
                    st.rerun()

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🔤 Typography</div>', unsafe_allow_html=True)
            font_size = st.select_slider(
                "Font size",
                options=["Small (12px)", "Medium (14px)", "Large (16px)"],
                value=prefs.get("font_size", "Medium (14px)"),
                key="set_font",
            )
            prefs["font_size"] = font_size

        with col_r:
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">📐 Layout</div>', unsafe_allow_html=True)
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
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🤖 Response Style</div>', unsafe_allow_html=True)
            ai_style = st.radio(
                "AI verbosity",
                ["Concise", "Standard", "Detailed"],
                index=["Concise","Standard","Detailed"].index(
                    prefs.get("ai_style", "Standard")),
                key="set_ai_style",
            )
            prefs["ai_style"] = ai_style

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🌐 Language</div>', unsafe_allow_html=True)
            lang = st.selectbox(
                "Response language",
                ["English", "Hindi", "Spanish", "French"],
                index=["English","Hindi","Spanish","French"].index(
                    prefs.get("language", "English")),
                key="set_lang",
            )
            prefs["language"] = lang

        with col_r:
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">💡 Explanation Level</div>', unsafe_allow_html=True)
            explain = st.selectbox(
                "Concept explanation depth",
                ["Beginner (ELI5)", "Intermediate", "Advanced"],
                index=["Beginner (ELI5)","Intermediate","Advanced"].index(
                    prefs.get("explain_level", "Intermediate")),
                key="set_explain",
            )
            prefs["explain_level"] = explain

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🧠 Chat Memory Depth</div>', unsafe_allow_html=True)
            memory = st.slider(
                "Number of previous turns to remember",
                min_value=2, max_value=20, value=prefs.get("memory_depth", 10),
                step=2, key="set_memory",
            )
            prefs["memory_depth"] = memory

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">📄 Summary Length</div>', unsafe_allow_html=True)
        sum_len = st.select_slider(
            "Default summary length",
            options=["Brief (3–5 bullets)", "Standard (5–8 bullets)", "Detailed (8–12 bullets)"],
            value=prefs.get("summary_len", "Standard (5–8 bullets)"),
            key="set_sum_len",
        )
        prefs["summary_len"] = sum_len

    # ─────────────────────────── Quiz ────────────────────────────────────
    with tab_quiz:
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🎯 Default Difficulty</div>', unsafe_allow_html=True)
            quiz_diff = st.select_slider(
                "Default difficulty",
                options=["Easy", "Medium", "Hard"],
                value=prefs.get("quiz_diff", "Medium"),
                key="set_quiz_diff",
            )
            prefs["quiz_diff"] = quiz_diff

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">📝 Default Format</div>', unsafe_allow_html=True)
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
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🔢 Question Count</div>', unsafe_allow_html=True)
            qcount = st.slider(
                "Default question count",
                3, 15, prefs.get("qcount", 5),
                key="set_qcount",
            )
            prefs["qcount"] = qcount

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">⏱️ Study Goal</div>', unsafe_allow_html=True)
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
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
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
            <div class="content-card" style="margin-top:24px;">
                <div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">⌨️ Keyboard Shortcuts</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;font-size:14px;">
                    <div><kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">Ctrl</kbd> + <kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">/</kbd> — Focus search</div>
                    <div><kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">Ctrl</kbd> + <kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">K</kbd> — Open chat</div>
                    <div><kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">→</kbd> / <kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">←</kbd> — Flashcard Nav</div>
                    <div><kbd style="background:var(--secondary);border:1px solid var(--border);border-radius:4px;padding:2px 6px;color:var(--text-primary);font-family:monospace;">Space</kbd> — Flip card</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ─────────────────────────── Account ─────────────────────────────────
    with tab_account:
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🔐 Security</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="content-card" style="font-size:13px;line-height:1.6;color:var(--text-secondary);">
                <ul style="margin:0;padding-left:16px;">
                    <li>JWT tokens expire after <strong>30 minutes</strong>.</li>
                    <li>Passwords are hashed with <strong>bcrypt</strong>.</li>
                    <li>API keys stored in <strong>environment variables only</strong>.</li>
                    <li>Uploaded files scanned for <strong>PII</strong> before indexing.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">📤 Export Data</div>', unsafe_allow_html=True)
        if st.button("⬇️ Export My Data (JSON)", use_container_width=False):
            st.info("Data export will be available in v1.5 — adds GDPR compliance.")

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<div style="font-weight:700;color:var(--danger);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">🗑️ Danger Zone</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="background:rgba(244,67,54,0.1);border-left:4px solid var(--danger);border-radius:var(--radius-sm);padding:12px;color:var(--danger);font-size:13px;margin-bottom:16px;">'
            '<strong>Warning:</strong> Deleting your account is permanent and cannot be undone.</div>',
            unsafe_allow_html=True,
        )
        if st.button("🗑️ Delete My Account", type="primary"):
            st.warning("This will be fully implemented in v1.5 with a confirmation flow.")

    # ─────────────────────────── Save ────────────────────────────────────
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)
    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button("💾 Save All Settings", use_container_width=True, type="primary", key="save_settings"):
            st.session_state["user_preferences"] = prefs
            toast_success("Settings saved successfully!")
            st.rerun()
