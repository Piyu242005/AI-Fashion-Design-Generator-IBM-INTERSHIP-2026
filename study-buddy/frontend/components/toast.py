"""Toast Notifications — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st

def _toast_html(message: str, kind: str, icon: str) -> str:
    return f'<div class="toast {kind}" role="alert" aria-live="polite">{icon}&nbsp; {message}</div>'

def toast_success(message: str) -> None:
    st.markdown(_toast_html(message, "success", "✓"), unsafe_allow_html=True)

def toast_warning(message: str) -> None:
    st.markdown(_toast_html(message, "warning", "⚠"), unsafe_allow_html=True)

def toast_error(message: str) -> None:
    st.markdown(_toast_html(message, "error", "✗"), unsafe_allow_html=True)

def toast_info(message: str) -> None:
    st.markdown(_toast_html(message, "info", "ℹ"), unsafe_allow_html=True)
