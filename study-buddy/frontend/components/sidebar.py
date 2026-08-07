"""
Sidebar Component — AI-Powered Study Buddy
===========================================
Renders the persistent left navigation sidebar with:
- App branding
- Navigation links (rendered as radio buttons)
- Logged-in user info
- Logout button
- Study streak display
"""

from __future__ import annotations

import streamlit as st
from utils.session_state import is_logged_in, logout


# ---------------------------------------------------------------------------
# Navigation items: (label, emoji, page_key)
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("Dashboard",   "🏠", "dashboard"),
    ("Chat",        "💬", "chat"),
    ("Summary",     "📄", "summary"),
    ("Quiz",        "❓", "quiz"),
    ("Flashcards",  "🃏", "flashcards"),
    ("Profile",     "👤", "profile"),
    ("Settings",    "⚙️", "settings"),
]


def render_sidebar() -> str:
    """
    Render sidebar navigation. Returns the selected page key.
    """
    with st.sidebar:
        # ── Branding ──────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="text-align:center; padding: 16px 0 8px;">
                <div style="font-size:32px;">🎓</div>
                <div style="font-size:18px; font-weight:800; color:#3b82f6;
                            letter-spacing:.02em;">Study Buddy</div>
                <div style="font-size:11px; color:#475569;
                            text-transform:uppercase; letter-spacing:.08em;">
                    AI-Powered Learning
                </div>
            </div>
            <hr style="border:none;border-top:1px solid #2d3748;margin:8px 0 16px;">
            """,
            unsafe_allow_html=True,
        )

        # ── Navigation ────────────────────────────────────────────────────
        if is_logged_in():
            labels = [f"{emoji}  {label}" for label, emoji, _ in NAV_ITEMS]
            keys   = [key for _, _, key in NAV_ITEMS]

            # Default to current page index
            current = st.session_state.get("current_page", "dashboard")
            default_idx = keys.index(current) if current in keys else 0

            selected_label = st.radio(
                "Navigate",
                labels,
                index=default_idx,
                label_visibility="collapsed",
                key="sidebar_nav",
            )

            selected_idx = labels.index(selected_label)
            selected_page = keys[selected_idx]
            st.session_state["current_page"] = selected_page

            # ── Study streak ──────────────────────────────────────────────
            streak = st.session_state.get("user", {}).get("study_streak", 0) if st.session_state.get("user") else 0
            st.markdown(
                f"""
                <div style="background:#1e2130;border:1px solid #2d3748;
                            border-radius:10px;padding:12px;margin:16px 0;
                            text-align:center;">
                    <div style="font-size:22px;">🔥</div>
                    <div style="font-size:20px;font-weight:800;color:#f97316;">
                        {streak}</div>
                    <div style="font-size:11px;color:#64748b;
                                text-transform:uppercase;letter-spacing:.06em;">
                        Day Streak</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── User info ─────────────────────────────────────────────────
            user = st.session_state.get("user", {})
            if user:
                name  = user.get("name", "Student")
                email = user.get("email", "")
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;gap:10px;
                                padding:10px;background:#161b27;
                                border-radius:10px;margin-bottom:12px;">
                        <div style="width:36px;height:36px;border-radius:50%;
                                    background:#1d4ed8;display:flex;
                                    align-items:center;justify-content:center;
                                    font-weight:800;color:#fff;font-size:14px;">
                            {name[0].upper()}
                        </div>
                        <div>
                            <div style="font-weight:700;color:#e2e8f0;
                                        font-size:13px;">{name}</div>
                            <div style="color:#64748b;font-size:11px;">
                                {email}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # ── Logout ────────────────────────────────────────────────────
            if st.button("🚪  Logout", use_container_width=True):
                logout()
                st.rerun()

            return selected_page

        else:
            st.markdown(
                '<p style="color:#64748b;font-size:13px;text-align:center;">'
                "Please log in to continue.</p>",
                unsafe_allow_html=True,
            )
            return "login"
