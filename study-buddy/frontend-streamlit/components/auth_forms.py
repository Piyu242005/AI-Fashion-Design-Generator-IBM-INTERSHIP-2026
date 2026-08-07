"""
Auth Forms Component — AI-Powered Study Buddy
==============================================
Login and Registration forms rendered as Streamlit widgets.
Uses the Luxury AI SaaS Design System.
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import login_user, register_user
from utils.session_state import set_user, get_profile


def render_login_form() -> None:
    """Render the login form. Sets session on success."""
    st.markdown(
        """
        <div class="animate-fade-in-up" style="text-align:center;margin-bottom:32px;padding-top:24px;">
            <div style="width:56px;height:56px;border-radius:14px;background:var(--accent);
                        display:flex;align-items:center;justify-content:center;margin:0 auto 16px;
                        font-size:24px;box-shadow:0 0 24px rgba(255,0,60,0.5);">
                🧠
            </div>
            <h1 style="font-size:28px;color:var(--text-primary);margin:0;font-weight:800;letter-spacing:-0.03em;">Welcome Back</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:8px;">
                Sign in to your Study Buddy workspace
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        email    = st.text_input("Email", placeholder="student@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
            return
        with st.spinner("Authenticating…"):
            try:
                token_data = login_user(email, password)
                token = token_data["access_token"]
                # Fetch user profile
                from utils.api_client import get_profile as _gp
                user = _gp(token)
                set_user(token, user)
                st.success(f"Welcome back, {user.get('name', 'Student')}! 🎉")
                st.rerun()
            except RuntimeError as e:
                st.error(f"Login failed: {e}")


def render_register_form() -> None:
    """Render the registration form."""
    st.markdown(
        """
        <div class="animate-fade-in-up" style="text-align:center;margin-bottom:32px;padding-top:24px;">
            <div style="width:56px;height:56px;border-radius:14px;background:var(--surface);
                        border:1px solid var(--border);
                        display:flex;align-items:center;justify-content:center;margin:0 auto 16px;
                        font-size:24px;box-shadow:var(--shadow);">
                ✨
            </div>
            <h1 style="font-size:28px;color:var(--text-primary);margin:0;font-weight:800;letter-spacing:-0.03em;">Create Account</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:8px;">
                Start your AI-powered learning journey
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("register_form", clear_on_submit=False):
        name     = st.text_input("Full Name", placeholder="Jane Smith")
        email    = st.text_input("Email", placeholder="jane@example.com")
        password = st.text_input("Password", type="password", placeholder="Min 8 characters")
        confirm  = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

    if submitted:
        if not all([name, email, password, confirm]):
            st.error("Please fill in all fields.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return
        if len(password) < 8:
            st.error("Password must be at least 8 characters.")
            return
        with st.spinner("Creating your account…"):
            try:
                register_user(name, email, password)
                st.success("Account created! Please sign in. 🎉")
            except RuntimeError as e:
                st.error(f"Registration failed: {e}")
