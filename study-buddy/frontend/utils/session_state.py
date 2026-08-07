"""Session State Helpers — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st

def init_session() -> None:
    defaults: dict = {
        "token": None, "user": None, "logged_in": False,
        "chat_history": [], "selected_doc_ids": [],
        "dashboard_stats": None, "documents": [],
        "dark_mode": True, "current_page": "dashboard",
        "quiz_questions": [], "quiz_answers": {},
        "quiz_submitted": False, "quiz_score": None,
        "flashcards": [], "flashcard_index": 0,
        "flashcard_flipped": False, "show_auth": False,
        "landing_tab": "login", "user_preferences": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in", False))

def set_user(token: str, user: dict) -> None:
    st.session_state["token"] = token
    st.session_state["user"] = user
    st.session_state["logged_in"] = True

def logout() -> None:
    for key in ["token", "user", "chat_history", "documents", "dashboard_stats",
                "quiz_questions", "quiz_answers", "flashcards"]:
        st.session_state[key] = None if key in ("token", "user") else []
    st.session_state["logged_in"] = False
    st.session_state["show_auth"] = False

def add_chat_message(role: str, content: str) -> None:
    st.session_state["chat_history"].append({"role": role, "content": content})

def clear_chat() -> None:
    st.session_state["chat_history"] = []
