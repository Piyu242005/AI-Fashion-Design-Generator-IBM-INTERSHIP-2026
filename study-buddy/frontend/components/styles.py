"""
styles.py — AI-Powered Study Buddy
=====================================
Legacy compatibility shim.
The design system has moved to themes/design_system.py.
This module re-exports inject_theme for any existing imports.
"""
from themes.design_system import get_theme_css, inject_theme  # noqa: F401

def inject_css() -> str:
    """Return default Dark theme CSS. Kept for backward compatibility."""
    return get_theme_css("Dark")
