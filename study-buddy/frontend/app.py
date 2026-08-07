"""app.py — AI-Powered Study Buddy — Main Entry Point"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from themes.design_system import inject_theme
from components.sidebar import render_sidebar
from components.auth_forms import render_login_form, render_register_form
from utils.session_state import init_session, is_logged_in

st.set_page_config(
    page_title="AI Study Buddy", page_icon="🎓", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "AI-Powered Study Buddy — IBM SkillsBuild 2025"},
)

init_session()
inject_theme(st.session_state.get("user_preferences", {}).get("theme", "Dark"))

if not is_logged_in():
    if not st.session_state.get("show_auth", False):
        from pages.landing import render as landing_render
        landing_render()
    else:
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            if st.button("← Back to Home", key="back_home"):
                st.session_state["show_auth"] = False
                st.rerun()
            tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Register"])
            with tab_login:
                render_login_form()
            with tab_register:
                render_register_form()
else:
    page = render_sidebar()
    PAGE_MAP = {
        "dashboard": ("pages.dashboard",  "render"),
        "chat":      ("pages.chat",       "render"),
        "summary":   ("pages.summary",    "render"),
        "quiz":      ("pages.quiz",       "render"),
        "flashcards":("pages.flashcards", "render"),
        "profile":   ("pages.profile",    "render"),
        "settings":  ("pages.settings",   "render"),
        "help":      ("pages.help",       "render"),
    }
    if page in PAGE_MAP:
        import importlib
        mod = importlib.import_module(PAGE_MAP[page][0])
        getattr(mod, PAGE_MAP[page][1])()
