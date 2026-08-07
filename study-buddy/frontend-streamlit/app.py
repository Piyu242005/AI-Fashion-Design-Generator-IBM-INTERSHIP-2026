"""
app.py — AI-Powered Study Buddy (Upgraded)
============================================
Main Streamlit entry point.
- Shows Landing Page first (unauthenticated)
- Login / Register as modal tabs
- Routes authenticated users to all 8 pages + Help
- Injects the active theme from design system
- Initialises session and injects CSS once per render

Run:
    streamlit run app.py
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from themes.design_system import inject_theme
from components.sidebar import render_sidebar
from components.auth_forms import render_login_form, render_register_form
from utils.session_state import init_session, is_logged_in

# ---------------------------------------------------------------------------
# Page config — MUST be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/study-buddy",
        "Report a Bug": "https://github.com/your-repo/study-buddy/issues",
        "About": "**AI-Powered Study Buddy** — IBM SkillsBuild Final Project 2025",
    },
)

# ---------------------------------------------------------------------------
# Session + Theme
# ---------------------------------------------------------------------------
init_session()
active_theme = st.session_state.get("user_preferences", {}).get("theme", "Dark")
inject_theme(active_theme)

# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
if not is_logged_in():
    show_auth = st.session_state.get("show_auth", False)

    if not show_auth:
        # ── Landing Page ───────────────────────────────────────────────────
        from pages.landing import render as landing_render
        landing_render()
    else:
        # ── Auth forms ─────────────────────────────────────────────────────
        col_left, col_center, col_right = st.columns([1, 1.4, 1])
        with col_center:
            if st.button("← Back to Home", key="back_home"):
                st.session_state["show_auth"] = False
                st.rerun()

            default_tab = st.session_state.get("landing_tab", "login")
            tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Register"])
            with tab_login:
                render_login_form()
            with tab_register:
                render_register_form()

else:
    # ── Authenticated — sidebar + page routing ─────────────────────────────
    page = render_sidebar()

    PAGE_MAP = {
        "dashboard": ("pages.dashboard", "render"),
        "chat":       ("pages.chat",      "render"),
        "summary":    ("pages.summary",   "render"),
        "quiz":       ("pages.quiz",      "render"),
        "flashcards": ("pages.flashcards","render"),
        "profile":    ("pages.profile",   "render"),
        "settings":   ("pages.settings",  "render"),
        "help":       ("pages.help",      "render"),
    }

    if page in PAGE_MAP:
        module_path, fn_name = PAGE_MAP[page]
        import importlib
        mod = importlib.import_module(module_path)
        getattr(mod, fn_name)()
