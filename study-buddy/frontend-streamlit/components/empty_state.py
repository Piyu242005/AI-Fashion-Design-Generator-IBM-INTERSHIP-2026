"""
Empty State Components — AI-Powered Study Buddy
================================================
Consistent, friendly empty-state illustrations for every page.
Each empty state guides the user toward the next action.
"""

from __future__ import annotations

import streamlit as st


def _empty(icon: str, title: str, subtitle: str, cta_label: str = "",
           cta_page: str = "") -> None:
    st.markdown(
        f"""
        <div style="text-align:center;padding:72px 24px;animation:fadeInUp .3s ease;">
            <div style="font-size:64px;margin-bottom:16px;opacity:.85;">{icon}</div>
            <div style="font-size:18px;font-weight:700;color:var(--text);
                        margin-bottom:8px;">{title}</div>
            <div style="font-size:14px;color:var(--text-faint);
                        max-width:320px;margin:0 auto;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if cta_label and cta_page:
        _, col_btn, _ = st.columns([2, 1, 2])
        with col_btn:
            if st.button(cta_label, use_container_width=True):
                st.session_state["current_page"] = cta_page
                st.rerun()


# ---------------------------------------------------------------------------
# Named empty states
# ---------------------------------------------------------------------------

def no_documents() -> None:
    _empty(
        "📂",
        "No Documents Yet",
        "Upload your first PDF, DOCX, PPTX or TXT to get started.",
        "⬆️  Upload Document",
        "chat",
    )


def no_chat_history() -> None:
    _empty(
        "💬",
        "No Chats Yet",
        "Upload a document and ask your first question to the AI.",
        "💬  Start Chatting",
        "chat",
    )


def no_quiz() -> None:
    _empty(
        "❓",
        "No Quiz Yet",
        "Select a document and generate a quiz to test your knowledge.",
        "❓  Generate Quiz",
        "quiz",
    )


def no_flashcards() -> None:
    _empty(
        "🃏",
        "No Flashcards Yet",
        "Generate flashcards from any uploaded document.",
        "🃏  Generate Flashcards",
        "flashcards",
    )


def no_summary() -> None:
    _empty(
        "📄",
        "No Summary Yet",
        "Select a document and click Generate Summary.",
    )


def search_no_results(query: str) -> None:
    _empty(
        "🔍",
        "No Results Found",
        f'No matches for "{query}". Try a different keyword.',
    )
