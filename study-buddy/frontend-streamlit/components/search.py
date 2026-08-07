"""
Search Component — AI-Powered Study Buddy
==========================================
Reusable search bar and filtering logic for:
  - Documents (by filename)
  - Chat history (by question/answer text)
  - Flashcards (by term/definition)
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

import streamlit as st
from components.empty_state import search_no_results


def search_bar(placeholder: str = "Search…", key: str = "search_bar") -> str:
    """
    Render a styled search input and return the current query string.
    """
    st.markdown(
        """
        <style>
        div[data-testid="stTextInput"].search-wrap > div > div > input {
            background: var(--secondary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
            padding-left: 36px !important;
            color: var(--text-primary) !important;
            box-shadow: var(--shadow) !important;
        }
        div[data-testid="stTextInput"].search-wrap > div > div > input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(255,0,60,0.15) !important;
            background: var(--primary) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    query = st.text_input(
        "🔍",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
    )
    return query.strip().lower()


# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------

def filter_documents(docs: list[dict], query: str) -> list[dict]:
    """Return documents whose filename contains the query."""
    if not query:
        return docs
    return [d for d in docs if query in d.get("filename", "").lower()]


def filter_chat_history(history: list[dict], query: str) -> list[dict]:
    """Return chat messages whose content contains the query."""
    if not query:
        return history
    return [
        m for m in history
        if query in m.get("content", "").lower()
    ]


def filter_flashcards(cards: list[dict], query: str) -> list[dict]:
    """Return flashcards whose term or definition contains the query."""
    if not query:
        return cards
    return [
        c for c in cards
        if query in c.get("term", "").lower()
        or query in c.get("definition", "").lower()
    ]


def render_search_results_or_empty(
    items: list,
    query: str,
    render_fn: callable,
) -> None:
    """
    Render filtered items, or show an empty state if none match.

    Args:
        items:     Pre-filtered list.
        query:     Current search string (for empty-state message).
        render_fn: Function(item) -> None that renders one item.
    """
    if not items:
        search_no_results(query) if query else None
        return
    for item in items:
        render_fn(item)
