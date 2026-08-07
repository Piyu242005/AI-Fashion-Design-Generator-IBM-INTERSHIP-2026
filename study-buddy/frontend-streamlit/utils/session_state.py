"""
Session State Helpers — AI-Powered Study Buddy
================================================
Centralised Streamlit session_state initialisation and accessors.
Prevents KeyError on first render and keeps state keys consistent.
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------------
# Initialise all session keys once
# ---------------------------------------------------------------------------

def init_session() -> None:
    """Call this at the top of every page to ensure keys exist."""
    defaults: dict = {
        # Auth
        "token": None,
        "user": None,
        "logged_in": False,
        # Chat
        "chat_history": [],          # list of {role, content}
        "selected_doc_ids": [],
        # Dashboard
        "dashboard_stats": None,
        # Documents
        "documents": [],
        # UI
        "dark_mode": True,
        "current_page": "dashboard",
        # Quiz
        "quiz_questions": [],
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_score": None,
        # Flashcards
        "flashcards": [],
        "flashcard_index": 0,
        "flashcard_flipped": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def is_logged_in() -> bool:
    return bool(st.session_state.get("logged_in", False))


def set_user(token: str, user: dict) -> None:
    st.session_state["token"] = token
    st.session_state["user"] = user
    st.session_state["logged_in"] = True


def get_profile() -> dict | None:
    """Return the current user dict stored in session state (or None)."""
    return st.session_state.get("user")


def logout() -> None:
    keys_to_clear = ["token", "user", "logged_in", "chat_history",
                     "documents", "dashboard_stats", "quiz_questions",
                     "quiz_answers", "flashcards"]
    for key in keys_to_clear:
        st.session_state[key] = None if key in ("token", "user") else []
    st.session_state["logged_in"] = False


# ---------------------------------------------------------------------------
# Chat helpers
# ---------------------------------------------------------------------------

def add_chat_message(role: str, content: str) -> None:
    st.session_state["chat_history"].append({"role": role, "content": content})


def clear_chat() -> None:
    st.session_state["chat_history"] = []
