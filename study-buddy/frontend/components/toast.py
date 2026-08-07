"""
Toast Notifications — AI-Powered Study Buddy
==============================================
Modern, auto-dismissing toast messages injected via st.markdown.
Types: success ✓ | warning ⚠ | error ✗ | info ℹ
"""

from __future__ import annotations

import streamlit as st


def _toast_html(message: str, kind: str, icon: str) -> str:
    return f"""
    <div class="toast {kind}" role="alert" aria-live="polite">
        {icon}&nbsp; {message}
    </div>
    """


def toast_success(message: str) -> None:
    """Green bordered success toast — auto-dismisses after ~3 s."""
    st.markdown(_toast_html(message, "success", "✓"), unsafe_allow_html=True)


def toast_warning(message: str) -> None:
    """Orange bordered warning toast."""
    st.markdown(_toast_html(message, "warning", "⚠"), unsafe_allow_html=True)


def toast_error(message: str) -> None:
    """Red bordered error toast."""
    st.markdown(_toast_html(message, "error", "✗"), unsafe_allow_html=True)


def toast_info(message: str) -> None:
    """Blue bordered info toast."""
    st.markdown(_toast_html(message, "info", "ℹ"), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Convenience wrappers used across pages
# ---------------------------------------------------------------------------

UPLOAD_SUCCESS   = lambda fname, chunks: toast_success(f"'{fname}' uploaded — {chunks} chunks indexed")
QUIZ_SUCCESS     = lambda n: toast_success(f"{n} quiz questions generated")
SUMMARY_SUCCESS  = lambda: toast_success("Summary ready")
FLASHCARD_SUCCESS = lambda n: toast_success(f"{n} flashcards created")
DELETED_SUCCESS  = lambda fname: toast_success(f"'{fname}' deleted")
LOGIN_SUCCESS    = lambda name: toast_success(f"Welcome back, {name}!")
REGISTER_SUCCESS = lambda: toast_success("Account created — please sign in")
