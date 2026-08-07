"""
Toast Notifications — AI-Powered Study Buddy
==============================================
Modern, auto-dismissing toast messages injected via st.markdown.
Types: success ✓ | warning ⚠ | error ✗ | info ℹ
"""

from __future__ import annotations

import streamlit as st

def _toast_html(message: str, kind: str, icon: str) -> str:
    color_map = {
        "success": "var(--success)",
        "warning": "var(--warning)",
        "error": "var(--danger)",
        "info": "var(--accent)"
    }
    bg_map = {
        "success": "rgba(0, 200, 83, 0.1)",
        "warning": "rgba(255, 193, 7, 0.1)",
        "error": "rgba(244, 67, 54, 0.1)",
        "info": "rgba(255, 0, 60, 0.1)"
    }
    
    color = color_map.get(kind, "var(--text-primary)")
    bg = bg_map.get(kind, "var(--surface)")

    # The auto-dismiss animation is achieved via standard Streamlit reruns usually,
    # but we can add a simple CSS animation here for appearance.
    return f"""
    <div style="
        background: {bg};
        border-left: 4px solid {color};
        color: {color};
        padding: 12px 16px;
        border-radius: var(--radius-sm);
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 12px;
        box-shadow: var(--shadow);
        animation: fadeInRight 0.3s ease-out forwards;
        display: flex;
        align-items: center;
        gap: 12px;
    " role="alert" aria-live="polite">
        <div style="font-size:18px;">{icon}</div>
        <div>{message}</div>
    </div>
    <style>
    @keyframes fadeInRight {{
        from {{ opacity: 0; transform: translateX(20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    </style>
    """


def toast_success(message: str) -> None:
    """Green bordered success toast."""
    st.markdown(_toast_html(message, "success", "✓"), unsafe_allow_html=True)


def toast_warning(message: str) -> None:
    """Orange bordered warning toast."""
    st.markdown(_toast_html(message, "warning", "⚠"), unsafe_allow_html=True)


def toast_error(message: str) -> None:
    """Red bordered error toast."""
    st.markdown(_toast_html(message, "error", "✗"), unsafe_allow_html=True)


def toast_info(message: str) -> None:
    """Accent bordered info toast."""
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
