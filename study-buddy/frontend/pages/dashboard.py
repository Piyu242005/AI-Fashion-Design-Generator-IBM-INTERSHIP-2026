"""Dashboard Page — AI-Powered Study Buddy"""
from __future__ import annotations
from datetime import datetime
import streamlit as st
from utils.api_client import get_dashboard_stats
from utils.session_state import init_session
from components.skeleton import skeleton_kpi_row, skeleton_text_block
from components.empty_state import no_chat_history

def _kpi(value, label, icon, color="var(--accent)"):
    return (f'<div class="kpi-card" style="animation:fadeInUp .35s ease;">'
            f'<div style="font-size:28px;margin-bottom:4px;">{icon}</div>'
            f'<div class="kpi-value" style="color:{color};">{value}</div>'
            f'<div class="kpi-label">{label}</div></div>')

def _bar(topic, score):
    c = "var(--success)" if score>=80 else "var(--warning)" if score>=60 else "var(--danger)"
    return (f'<div style="margin-bottom:12px;">'
            f'<div style="display:flex;justify-content:space-between;font-size:13px;'
            f'color:var(--text-muted);margin-bottom:4px;"><span>{topic}</span>'
            f'<span style="color:{c};font-weight:700;">{score}%</span></div>'
            f'<div class="progress-bar-bg"><div class="progress-bar-fill" '
            f'style="width:{score}%;background:{c};"></div></div></div>')

def _greeting(name):
    h = datetime.now().hour
    p,e = ("Good morning","☀️") if h<12 else ("Good afternoon","🌤️") if h<17 else ("Good evening","🌙")
    return f'{p}, <strong style="color:var(--accent);">{name}</strong>! {e}'

def render():
    init_session()
    user  = st.session_state.get("user") or {}
    token = st.session_state.get("token","")
    name  = user.get("name","Student")

    st.markdown(f'<div class="page-header"><h1>🏠 Dashboard</h1>'
                f'<p>{_greeting(name)} Here\'s your study overview.</p></div>',
                unsafe_allow_html=True)

    key = "dashboard_stats"
    if st.session_state.get(key) is None:
        skeleton_kpi_row()
        try:
            st.session_state[key] = get_dashboard_stats(token)
        except Exception:
            st.session_state[key] = {}
        st.rerun()

    stats = st.session_state.get(key) or {}
    _, c_ref = st.columns([6,1])
    with c_ref:
        if st.button("🔄 Refresh"):
            st.session_state[key] = None
            st.rerun()

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(_kpi(stats.get("document_count",0),"Documents","📄"), unsafe_allow_html=True)
    with c2:
        mins = stats.get("total_study_mins",0); h,m = divmod(mins,60)
        st.markdown(_kpi(f"{h}h {m}m" if h else f"{m}m","Study Time","⏱","var(--secondary)"), unsafe_allow_html=True)
    with c3:
        sc = stats.get("avg_quiz_score",0)
        st.markdown(_kpi(f"{sc}%","Avg Quiz Score","🎯","var(--success)" if sc>=70 else "var(--warning)"), unsafe_allow_html=True)
    with c4:
        st.markdown(_kpi(stats.get("study_streak",0),"Day Streak","🔥","var(--warning)"), unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    goal = min(int(stats.get("daily_goal_pct",0)),100)
    dg   = st.session_state.get("user_preferences",{}).get("daily_goal",30)
    st.markdown(
        f'<div class="content-card" style="margin-bottom:20px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'<h4 style="margin:0;">🎯 Daily Goal — {dg} minutes</h4>'
        f'<span style="font-weight:700;color:var(--accent);font-size:15px;">{goal}%</span></div>'
        f'<div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{goal}%;"></div></div>'
        f'<div style="font-size:12px;color:var(--text-faint);margin-top:6px;">'
        f'{"🏆 Goal reached!" if goal>=100 else f"Keep going — {100-goal}% remaining"}</div></div>',
        unsafe_allow_html=True)

    cw,cs,ca = st.columns(3)
    with cw:
        st.markdown("#### ⚠️ Weak Topics")
        for t in stats.get("weak_topics",[])[:5]:
            st.markdown(f'<span class="badge badge-red">{t}</span> ', unsafe_allow_html=True)
        if not stats.get("weak_topics"):
            st.caption("No weak topics yet — take a quiz!")
    with cs:
        st.markdown("#### ✅ Strong Topics")
        for t in stats.get("strong_topics",[])[:5]:
            st.markdown(f'<span class="badge badge-green">{t}</span> ', unsafe_allow_html=True)
        if not stats.get("strong_topics"):
            st.caption("No strong topics yet.")
    with ca:
        st.markdown("#### 🤖 AI Recommendations")
        for s in stats.get("ai_suggestions",[])[:3]:
            st.markdown(f'<div class="custom-info">{s}</div>', unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    cp,cact = st.columns([2,1])
    with cp:
        st.markdown("#### 📊 Topic Progress")
        ts = stats.get("topic_scores",{})
        if ts:
            bars = "".join(_bar(t,s) for t,s in sorted(ts.items(),key=lambda x:x[1]))
            st.markdown(f'<div class="content-card">{bars}</div>', unsafe_allow_html=True)
        else:
            skeleton_text_block(4)
    with cact:
        st.markdown("#### ⚡ Quick Actions")
        for label,pg in [("💬  Start Chat","chat"),("❓  Generate Quiz","quiz"),
                          ("📄  Summarize","summary"),("🃏  Flashcards","flashcards")]:
            if st.button(label, use_container_width=True, key=f"qa_{pg}"):
                st.session_state["current_page"] = pg
                st.session_state[key] = None
                st.rerun()

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    cl,cr = st.columns(2)
    with cl:
        st.markdown("#### 📋 Recent Activity")
        for a in stats.get("recent_activity",[])[:5]:
            st.markdown(
                f'<div style="display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);">'
                f'<div style="font-size:18px;">{a.get("icon","📌")}</div>'
                f'<div><div style="font-size:13px;color:var(--text);">{a.get("text","")}</div>'
                f'<div style="font-size:11px;color:var(--text-faint);">{a.get("time","")}</div>'
                f'</div></div>', unsafe_allow_html=True)
    with cr:
        st.markdown("#### 💬 Recent Chats")
        chats = stats.get("recent_chats",[])
        if chats:
            for c in chats[:4]:
                q = c.get("question",""); a = c.get("answer","")
                st.markdown(
                    f'<div class="content-card" style="margin-bottom:8px;padding:12px 16px;">'
                    f'<div style="font-weight:700;color:var(--text);font-size:13px;">Q: {q}</div>'
                    f'<div style="color:var(--text-faint);font-size:12px;margin-top:4px;">'
                    f'A: {(a[:100]+"…") if len(a)>100 else a}</div></div>',
                    unsafe_allow_html=True)
        else:
            no_chat_history()
