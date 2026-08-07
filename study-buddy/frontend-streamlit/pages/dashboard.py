"""
Dashboard Page — AI-Powered Study Buddy (Executive SaaS Edition)
================================================================
KPI Cards, Topic Progress, AI Recommendations, Quick Actions, Activity Feed.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

from datetime import datetime
import streamlit as st

from utils.api_client import get_dashboard_stats
from utils.session_state import init_session
from components.skeleton import skeleton_kpi_row, skeleton_text_block
from components.empty_state import no_chat_history

def _kpi(value: str, label: str, icon: str, color: str = "var(--text-primary)") -> str:
    return f"""
    <div class="kpi-card animate-fade-in-up">
        <div style="font-size:24px;margin-bottom:8px;background:var(--secondary);width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;border:1px solid var(--border);">{icon}</div>
        <div class="kpi-value" style="color:{color};">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """

def _topic_bar(topic: str, score: int) -> str:
    color = "var(--success)" if score >= 80 else "var(--warning)" if score >= 60 else "var(--danger)"
    return f"""
    <div style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;
                    font-size:13px;color:var(--text-secondary);margin-bottom:6px;font-weight:600;">
            <span>{topic}</span>
            <span style="color:{color};">{score}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{score}%;background:{color};"></div>
        </div>
    </div>
    """

def _activity_item(icon: str, text: str, time: str) -> str:
    return f"""
    <div style="display:flex;align-items:flex-start;gap:12px;
                padding:12px 0;border-bottom:1px solid var(--border);">
        <div style="font-size:16px;width:32px;height:32px;background:var(--secondary);border-radius:50%;display:flex;align-items:center;justify-content:center;border:1px solid var(--border);flex-shrink:0;">{icon}</div>
        <div style="flex:1;">
            <div style="font-size:13px;color:var(--text-primary);font-weight:500;line-height:1.4;">{text}</div>
            <div style="font-size:11px;color:var(--text-disabled);margin-top:4px;">{time}</div>
        </div>
    </div>
    """

def _greeting(name: str) -> str:
    hour = datetime.now().hour
    if hour < 12:
        period, emoji = "Good morning", "☀️"
    elif hour < 17:
        period, emoji = "Good afternoon", "🌤️"
    else:
        period, emoji = "Good evening", "🌙"
    return f'{period}, <strong style="color:var(--text-primary);">{name}</strong>!'

def render() -> None:
    init_session()

    user  = st.session_state.get("user", {}) or {}
    token = st.session_state.get("token", "")
    name  = user.get("name", "Student")

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">Workspace Overview</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                {_greeting(name)} Here is your executive learning summary.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch stats ────────────────────────────────────────────────────────
    stats_key = "dashboard_stats"
    if st.session_state.get(stats_key) is None:
        with st.spinner(""):
            skeleton_kpi_row()
            try:
                stats = get_dashboard_stats(token)
                st.session_state[stats_key] = stats
            except Exception:
                stats = {}
                st.session_state[stats_key] = stats
        st.rerun()

    stats: dict = st.session_state.get(stats_key, {})

    # ── Row 1: KPI Cards ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi(str(stats.get("document_count", 0)), "Documents Analyzed", "📄", "var(--text-primary)"),
                    unsafe_allow_html=True)
    with c2:
        mins = stats.get("total_study_mins", 0)
        h, m = divmod(mins, 60)
        label = f"{h}h {m}m" if h else f"{m}m"
        st.markdown(_kpi(label, "Active Study Time", "⏱", "var(--text-primary)"),
                    unsafe_allow_html=True)
    with c3:
        score = stats.get("avg_quiz_score", 0)
        color = "var(--success)" if score >= 70 else "var(--warning)"
        st.markdown(_kpi(f"{score}%", "Accuracy Trend", "🎯", color),
                    unsafe_allow_html=True)
    with c4:
        streak = stats.get("study_streak", user.get("study_streak", 0))
        st.markdown(_kpi(str(streak), "Day Streak", "🔥", "var(--accent)"),
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 2: Charts, Progress, Activity, AI Suggestion ───────────────────
    r2c1, r2c2, r2c3 = st.columns([1.5, 1, 1.2])

    with r2c1:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">📈 Accuracy Trend</div>', unsafe_allow_html=True)
        topic_scores: dict = stats.get("topic_scores", {})
        if topic_scores:
            bars_html = "".join(
                _topic_bar(topic, score)
                for topic, score in sorted(topic_scores.items(), key=lambda x: x[1])
            )
            st.markdown(f'<div class="content-card animate-fade-in-up" style="padding:20px;">{bars_html}</div>', unsafe_allow_html=True)
        else:
            skeleton_text_block(4)
            st.caption("Topic scores appear here after quiz completions.")

    with r2c2:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">🎯 Study Goals</div>', unsafe_allow_html=True)
        goal_pct = min(int(stats.get("daily_goal_pct", 0)), 100)
        daily_goal_mins = st.session_state.get("user_preferences", {}).get("daily_goal", 30)
        st.markdown(
            f"""
            <div class="content-card animate-fade-in-up" style="padding:20px;">
                <div style="font-size:12px;color:var(--text-secondary);font-weight:600;margin-bottom:4px;">TODAY'S TARGET</div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <div style="font-size:24px;font-weight:800;color:var(--text-primary);">{daily_goal_mins}m</div>
                    <span style="font-weight:700;color:var(--accent);font-size:14px;">{goal_pct}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width:{goal_pct}%;background:var(--accent);"></div>
                </div>
                <div style="font-size:12px;color:var(--text-disabled);margin-top:12px;line-height:1.5;">
                    {"🏆 Daily goal unlocked! Outstanding session." if goal_pct >= 100
                     else f"Focus required — {100 - goal_pct}% remaining today."}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2c3:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">🤖 AI Insights</div>', unsafe_allow_html=True)
        suggestions = stats.get("ai_suggestions", [])
        if suggestions:
            insights_html = "".join(
                f'<div style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px 16px;color:var(--text-secondary);font-size:13px;margin-bottom:8px;line-height:1.5;"><span style="color:var(--accent);font-weight:700;margin-right:8px;">•</span>{s}</div>'
                for s in suggestions[:3]
            )
            st.markdown(f'<div class="animate-fade-in-up">{insights_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="animate-fade-in-up" style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;color:var(--text-secondary);font-size:13px;">Upload study materials and take quizzes to unlock personalized AI guidance.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 3: Documents, Quiz, Recent Chat, Activity ────────────────────────
    r3c1, r3c2 = st.columns([1, 1.5])

    with r3c1:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">📋 Activity Feed</div>', unsafe_allow_html=True)
        activity = stats.get("recent_activity", [])
        if activity:
            items_html = "".join(
                _activity_item(a.get("icon", "📌"), a.get("text", ""), a.get("time", ""))
                for a in activity[:5]
            )
            st.markdown(f'<div class="content-card animate-fade-in-up" style="padding:16px 20px;">{items_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="content-card animate-fade-in-up" style="padding:20px;text-align:center;color:var(--text-disabled);font-size:13px;">No activity recorded yet. Upload a document to start!</div>',
                unsafe_allow_html=True,
            )

    with r3c2:
        st.markdown('<div style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px;">💬 Recent AI Interactions</div>', unsafe_allow_html=True)
        recent = stats.get("recent_chats", [])
        if recent:
            for item in recent[:3]:
                q = item.get("question", "")
                a = (item.get("answer", "")[:120] + "…") if len(item.get("answer","")) > 120 else item.get("answer","")
                st.markdown(
                    f"""
                    <div class="content-card animate-fade-in-up" style="margin-bottom:12px;padding:16px 20px;">
                        <div style="font-weight:600;color:var(--text-primary);font-size:13px;margin-bottom:6px;"><span style="color:var(--accent);">Q:</span> {q}</div>
                        <div style="color:var(--text-secondary);font-size:13px;line-height:1.5;">{a}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            no_chat_history()

