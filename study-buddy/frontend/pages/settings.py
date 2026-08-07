"""Settings Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.session_state import init_session
from themes.design_system import THEMES, inject_theme
from components.toast import toast_success

def render():
    init_session()
    prefs: dict = st.session_state.get("user_preferences",{})
    st.markdown('<div class="page-header"><h1>⚙️ Settings</h1>'
                '<p>Personalise every aspect of your Study Buddy experience.</p></div>',
                unsafe_allow_html=True)

    tab_app, tab_ai, tab_quiz, tab_access, tab_account = st.tabs([
        "🎨 Appearance","🤖 AI & Learning","❓ Quiz","♿ Accessibility","🔐 Account"])

    with tab_app:
        st.markdown("#### 🎨 Theme")
        theme_names = list(THEMES.keys())
        cur = prefs.get("theme","Dark")
        th_cols = st.columns(5)
        for col, tn in zip(th_cols, theme_names):
            with col:
                t = THEMES[tn]; sel = (cur == tn)
                border = "var(--accent)" if sel else "var(--border)"
                st.markdown(
                    f'<div style="background:{t["bg"]};border:2px solid {border};border-radius:10px;'
                    f'padding:12px 8px;text-align:center;"><div style="width:24px;height:24px;'
                    f'border-radius:50%;background:{t["accent"]};margin:0 auto 6px;"></div>'
                    f'<div style="font-size:11px;color:{t["text"]};font-weight:700;">{tn}</div>'
                    + (f'<div style="font-size:9px;color:{t["accent"]};">✓ Active</div>' if sel else "")
                    + '</div>', unsafe_allow_html=True)
                if st.button(tn, key=f"th_{tn}", use_container_width=True):
                    prefs["theme"] = tn; st.session_state["user_preferences"] = prefs
                    inject_theme(tn); toast_success(f"{tn} theme applied"); st.rerun()
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        fl, fr = st.columns(2)
        with fl:
            fs = st.select_slider("Font size",["Small (12px)","Medium (14px)","Large (16px)"],
                                  value=prefs.get("font_size","Medium (14px)"), key="set_font")
            prefs["font_size"] = fs
        with fr:
            sb = st.radio("Default sidebar",["Expanded","Collapsed"],
                          index=0 if prefs.get("sidebar","Expanded")=="Expanded" else 1,
                          horizontal=True, key="set_sb")
            prefs["sidebar"] = sb

    with tab_ai:
        cl, cr = st.columns(2)
        with cl:
            ai_style = st.radio("AI verbosity",["Concise","Standard","Detailed"],
                                index=["Concise","Standard","Detailed"].index(prefs.get("ai_style","Standard")),
                                key="set_ai"); prefs["ai_style"] = ai_style
            lang = st.selectbox("Language",["English","Hindi","Spanish","French"],
                                index=["English","Hindi","Spanish","French"].index(prefs.get("language","English")),
                                key="set_lang"); prefs["language"] = lang
        with cr:
            exp = st.selectbox("Explanation level",["Beginner (ELI5)","Intermediate","Advanced"],
                               index=["Beginner (ELI5)","Intermediate","Advanced"].index(
                                   prefs.get("explain_level","Intermediate")), key="set_exp")
            prefs["explain_level"] = exp
            mem = st.slider("Chat memory (turns)", 2, 20, prefs.get("memory_depth",10), step=2, key="set_mem")
            prefs["memory_depth"] = mem
        sl = st.select_slider("Summary length",
                              ["Brief (3–5 bullets)","Standard (5–8 bullets)","Detailed (8–12 bullets)"],
                              value=prefs.get("summary_len","Standard (5–8 bullets)"), key="set_sl")
        prefs["summary_len"] = sl

    with tab_quiz:
        cl, cr = st.columns(2)
        with cl:
            qd = st.select_slider("Difficulty",["Easy","Medium","Hard"],
                                  value=prefs.get("quiz_diff","Medium"), key="set_qd"); prefs["quiz_diff"] = qd
            qt = st.radio("Default type",["MCQ","True/False","Short Answer","Mixed"],
                          index=["MCQ","True/False","Short Answer","Mixed"].index(prefs.get("qtype","MCQ")),
                          key="set_qt"); prefs["qtype"] = qt
        with cr:
            qc = st.slider("Question count",3,15,prefs.get("qcount",5),key="set_qc"); prefs["qcount"] = qc
            dg = st.slider("Daily goal (mins)",10,180,prefs.get("daily_goal",30),step=5,key="set_dg"); prefs["daily_goal"] = dg
            sr = st.toggle("Show streak reminder",value=prefs.get("streak_reminder",True),key="set_sr"); prefs["streak_reminder"] = sr

    with tab_access:
        cl, cr = st.columns(2)
        with cl:
            hc = st.toggle("High Contrast",value=prefs.get("high_contrast",False),key="set_hc"); prefs["high_contrast"] = hc
            lf = st.toggle("Large Fonts",value=prefs.get("large_fonts",False),key="set_lf"); prefs["large_fonts"] = lf
        with cr:
            rm = st.toggle("Reduce Motion",value=prefs.get("reduce_motion",False),key="set_rm"); prefs["reduce_motion"] = rm
        st.markdown('<div class="custom-info"><strong>Keyboard Shortcuts</strong><br>'
                    '<code>→ / ←</code> Navigate flashcards &nbsp; <code>Space</code> Flip card</div>',
                    unsafe_allow_html=True)

    with tab_account:
        st.markdown('<div class="custom-info">• JWT tokens expire after <strong>30 minutes</strong><br>'
                    '• Passwords hashed with <strong>bcrypt</strong><br>'
                    '• API keys in <strong>environment variables only</strong><br>'
                    '• Files scanned for <strong>PII</strong> before indexing</div>', unsafe_allow_html=True)
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        if st.button("⬇️  Export My Data (JSON)"):
            st.info("Data export available in v1.5.")
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="custom-warning">Deleting your account is permanent.</div>', unsafe_allow_html=True)
        if st.button("🗑️  Delete My Account", type="primary"):
            st.warning("Implemented in v1.5 with confirmation flow.")

    _, cs = st.columns([3,1])
    with cs:
        if st.button("💾  Save All Settings", use_container_width=True, key="save_all"):
            st.session_state["user_preferences"] = prefs
            toast_success("Settings saved!"); st.rerun()
