"""Auth Forms Component — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import login_user, register_user, get_profile
from utils.session_state import set_user

def render_login_form() -> None:
    st.markdown(
        '<div style="text-align:center;margin-bottom:32px;">'
        '<div style="font-size:48px;margin-bottom:8px;">🎓</div>'
        '<h1 style="font-size:26px;color:var(--text);margin:0;">Welcome Back</h1>'
        '<p style="color:var(--text-faint);font-size:14px;margin-top:6px;">'
        'Sign in to your Study Buddy account</p></div>',
        unsafe_allow_html=True)
    with st.form("login_form"):
        email    = st.text_input("📧  Email", placeholder="student@example.com")
        password = st.text_input("🔒  Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
            return
        with st.spinner("Authenticating…"):
            try:
                token_data = login_user(email, password)
                token = token_data["access_token"]
                user  = get_profile(token)
                set_user(token, user)
                st.success(f"Welcome back, {user.get('name','Student')}! 🎉")
                st.rerun()
            except RuntimeError as e:
                st.error(f"Login failed: {e}")

def render_register_form() -> None:
    st.markdown(
        '<div style="text-align:center;margin-bottom:32px;">'
        '<div style="font-size:48px;margin-bottom:8px;">✨</div>'
        '<h1 style="font-size:26px;color:var(--text);margin:0;">Create Account</h1>'
        '<p style="color:var(--text-faint);font-size:14px;margin-top:6px;">'
        'Start your AI-powered learning journey</p></div>',
        unsafe_allow_html=True)
    with st.form("register_form"):
        name     = st.text_input("👤  Full Name", placeholder="Jane Smith")
        email    = st.text_input("📧  Email", placeholder="jane@example.com")
        password = st.text_input("🔒  Password", type="password", placeholder="Min 8 characters")
        confirm  = st.text_input("🔒  Confirm Password", type="password")
        submitted = st.form_submit_button("Create Account", use_container_width=True)
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
