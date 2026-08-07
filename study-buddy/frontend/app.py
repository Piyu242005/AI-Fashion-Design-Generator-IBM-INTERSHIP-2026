"""
app.py — AI-Powered Study Buddy
=================================
Main Streamlit entry point.
Handles routing between Login/Register and authenticated pages.
All pages are rendered inline (no st.switch_page) for broad compatibility.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import sys
import os

# Ensure local modules are importable regardless of working directory
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from components.styles import inject_css
from components.sidebar import render_sidebar
from components.auth_forms import render_login_form, render_register_form
from utils.session_state import init_session, is_logged_in

# ---------------------------------------------------------------------------
# Page configuration — must be FIRST Streamlit call
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
# Inject global CSS
# ---------------------------------------------------------------------------
st.markdown(inject_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Initialise session state
# ---------------------------------------------------------------------------
init_session()

# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
if not is_logged_in():
    # ── Unauthenticated: show Login / Register ─────────────────────────────
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_center:
        tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Register"])
        with tab_login:
            render_login_form()
        with tab_register:
            render_register_form()

else:
    # ── Authenticated: show sidebar + page ────────────────────────────────
    page = render_sidebar()

    # Lazy import pages to keep startup fast
    if page == "dashboard":
        from pages import dashboard
        dashboard.render()

    elif page == "chat":
        from pages import chat
        chat.render()

    elif page == "summary":
        from pages import summary
        summary.render()

    elif page == "quiz":
        from pages import quiz
        quiz.render()

    elif page == "flashcards":
        from pages import flashcards
        flashcards.render()

    elif page == "profile":
        from pages import profile
        profile.render()

    elif page == "settings":
        from pages import settings
        settings.render()
