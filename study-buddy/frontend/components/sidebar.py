"""Sidebar Component — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.session_state import is_logged_in, logout
from themes.design_system import THEMES, inject_theme

NAV_ITEMS = [
    ("Dashboard","🏠","dashboard"), ("Chat","💬","chat"),
    ("Summary","📄","summary"),    ("Quiz","❓","quiz"),
    ("Flashcards","🃏","flashcards"), ("Profile","👤","profile"),
    ("Settings","⚙️","settings"),  ("Help","❓","help"),
]

def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:16px 0 8px;">'
            '<div style="font-size:32px;">🎓</div>'
            '<div style="font-size:18px;font-weight:800;color:var(--accent);">Study Buddy</div>'
            '<div style="font-size:11px;color:var(--text-faint);text-transform:uppercase;'
            'letter-spacing:.08em;">AI-Powered Learning</div></div>'
            '<hr style="border:none;border-top:1px solid var(--border);margin:8px 0 16px;">',
            unsafe_allow_html=True)

        if is_logged_in():
            labels = [f"{e}  {l}" for l, e, _ in NAV_ITEMS]
            keys   = [k for _, _, k in NAV_ITEMS]
            current = st.session_state.get("current_page", "dashboard")
            idx = keys.index(current) if current in keys else 0
            sel_label = st.radio("Navigate", labels, index=idx,
                                 label_visibility="collapsed", key="sidebar_nav")
            sel_page = keys[labels.index(sel_label)]
            st.session_state["current_page"] = sel_page

            # Theme selector
            theme_names = list(THEMES.keys())
            cur_theme = st.session_state.get("user_preferences", {}).get("theme", "Dark")
            chosen = st.selectbox("🎨 Theme", theme_names,
                                  index=theme_names.index(cur_theme) if cur_theme in theme_names else 0,
                                  key="sidebar_theme")
            if chosen != cur_theme:
                prefs = st.session_state.get("user_preferences", {})
                prefs["theme"] = chosen
                st.session_state["user_preferences"] = prefs
                inject_theme(chosen)
                st.rerun()

            # Streak
            streak = (st.session_state.get("user") or {}).get("study_streak", 0)
            st.markdown(
                f'<div style="background:var(--surface);border:1px solid var(--border);'
                f'border-radius:10px;padding:12px;margin:16px 0;text-align:center;">'
                f'<div style="font-size:22px;">🔥</div>'
                f'<div style="font-size:20px;font-weight:800;color:var(--warning);">{streak}</div>'
                f'<div style="font-size:11px;color:var(--text-faint);text-transform:uppercase;">'
                f'Day Streak</div></div>', unsafe_allow_html=True)

            # User info
            user = st.session_state.get("user") or {}
            if user:
                name = user.get("name","Student")
                email = user.get("email","")
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:10px;'
                    f'background:var(--surface2);border-radius:10px;margin-bottom:12px;">'
                    f'<div style="width:36px;height:36px;border-radius:50%;background:var(--accent);'
                    f'display:flex;align-items:center;justify-content:center;font-weight:800;'
                    f'color:#fff;font-size:14px;">{name[0].upper()}</div>'
                    f'<div><div style="font-weight:700;color:var(--text);font-size:13px;">{name}</div>'
                    f'<div style="color:var(--text-faint);font-size:11px;">{email}</div>'
                    f'</div></div>', unsafe_allow_html=True)

            if st.button("🚪  Logout", use_container_width=True):
                logout()
                st.rerun()
            return sel_page
        else:
            st.markdown('<p style="color:var(--text-faint);font-size:13px;text-align:center;">Please log in.</p>',
                        unsafe_allow_html=True)
            return "login"
