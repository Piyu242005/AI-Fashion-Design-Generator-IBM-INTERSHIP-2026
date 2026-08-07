"""
Dashboard Page — AI-Powered Study Buddy (Upgraded)
====================================================
Full expanded dashboard:
  Row 1  — Personalised AI greeting + Daily Goal ring
  Row 2  — KPI cards: Documents, Study Time, Quiz Score, Streak
  Row 3  — Weak Topics | Strong Topics | AI Recommendations
  Row 4  — Topic progress bars | Quick Actions
  Row 5  — Recent Activity feed | Recent Chats
Uses skeleton loaders while stats are fetching.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from utils.api_client import get_dashboard_stats
from utils.session_state import init_session
from components.skeleton import skeleton_kpi_row, skeleton_text_block
from components.empty_state import no_chat_history


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi(value: str, label: str, icon: str, color: str = "var(--accent)") -> str:
    return f"""
    <div class="kpi-card" style="animation:fadeInUp .35s ease;">
        <div style="font-size:28px;margin-bottom:4px;">{icon}</div>
        <div class="kpi-value" style="color:{color};">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


def _topic_bar(topic: str, score: int) -> str:
    color = "var(--success)" if score >= 80 else "var(--warning)" if score >= 60 else "var(--danger)"
    return f"""
    <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;
                    font-size:13px;color:var(--text-muted);margin-bottom:4px;">
            <span>{topic}</span>
            <span style="color:{color};font-weight:700;">{score}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width:{score}%;background:{color};"></div>
        </div>
    </div>
    """


def _activity_item(icon: str, text: str, time: str) -> str:
    return f"""
    <div style="display:flex;align-items:center;gap:10px;
                padding:10px 0;border-bottom:1px solid var(--border);">
        <div style="font-size:20px;width:32px;text-align:center;">{icon}</div>
        <div style="flex:1;">
            <div style="font-size:13px;color:var(--text);">{text}</div>
            <div style="font-size:11px;color:var(--text-faint);">{time}</div>
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
    return f'{period}, <strong style="color:var(--accent);">{name}</strong>! {emoji}'


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    init_session()

    user  = st.session_state.get("user", {}) or {}
    token = st.session_state.get("token", "")
    name  = user.get("name", "Student")

    # ── Page header with greeting ──────────────────────────────────────────
    st.markdown(
        f"""
        <div class="page-header">
            <h1>🏠 Dashboard</h1>
            <p>{_greeting(name)} Here's your study overview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch stats (with skeleton while loading) ──────────────────────────
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

    # Refresh button
    col_h1, col_h2 = st.columns([6, 1])
    with col_h2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state[stats_key] = None
            st.rerun()

    # ── Row 1: KPI cards ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi(str(stats.get("document_count", 0)), "Documents", "📄"),
                    unsafe_allow_html=True)
    with c2:
        mins = stats.get("total_study_mins", 0)
        h, m = divmod(mins, 60)
        label = f"{h}h {m}m" if h else f"{m}m"
        st.markdown(_kpi(label, "Study Time", "⏱", "var(--secondary)"),
                    unsafe_allow_html=True)
    with c3:
        score = stats.get("avg_quiz_score", 0)
        color = "var(--success)" if score >= 70 else "var(--warning)"
        st.markdown(_kpi(f"{score}%", "Avg Quiz Score", "🎯", color),
                    unsafe_allow_html=True)
    with c4:
        streak = stats.get("study_streak", user.get("study_streak", 0))
        st.markdown(_kpi(str(streak), "Day Streak", "🔥", "var(--warning)"),
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 2: Daily Goal progress ─────────────────────────────────────────
    goal_pct = min(int(stats.get("daily_goal_pct", 0)), 100)
    daily_goal_mins = st.session_state.get("user_preferences", {}).get("daily_goal", 30)
    st.markdown(
        f"""
        <div class="content-card" style="margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;
                        align-items:center;margin-bottom:8px;">
                <h4 style="margin:0;">🎯 Daily Goal — {daily_goal_mins} minutes</h4>
                <span style="font-weight:700;color:var(--accent);font-size:15px;">
                    {goal_pct}%</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width:{goal_pct}%;"></div>
            </div>
            <div style="font-size:12px;color:var(--text-faint);margin-top:6px;">
                {"🏆 Goal reached! Great work today." if goal_pct >= 100
                 else f"Keep going — {100 - goal_pct}% remaining"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Row 3: Topics + AI Suggestions ────────────────────────────────────
    col_weak, col_strong, col_ai = st.columns(3)

    with col_weak:
        st.markdown("#### ⚠️ Weak Topics")
        weak = stats.get("weak_topics", [])
        if weak:
            for t in weak[:5]:
                st.markdown(f'<span class="badge badge-red">{t}</span> ',
                            unsafe_allow_html=True)
        else:
            st.caption("No weak topics yet — take a quiz!")

    with col_strong:
        st.markdown("#### ✅ Strong Topics")
        strong = stats.get("strong_topics", [])
        if strong:
            for t in strong[:5]:
                st.markdown(f'<span class="badge badge-green">{t}</span> ',
                            unsafe_allow_html=True)
        else:
            st.caption("No strong topics yet.")

    with col_ai:
        st.markdown("#### 🤖 AI Recommendations")
        suggestions = stats.get("ai_suggestions", [])
        if suggestions:
            for s in suggestions[:3]:
                st.markdown(f'<div class="custom-info">{s}</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="custom-info">Upload documents and take quizzes '
                'to receive personalised AI recommendations.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 4: Topic progress + Quick Actions ──────────────────────────────
    col_progress, col_actions = st.columns([2, 1])

    with col_progress:
        st.markdown("#### 📊 Topic Progress")
        topic_scores: dict = stats.get("topic_scores", {})
        if topic_scores:
            bars_html = "".join(
                _topic_bar(topic, score)
                for topic, score in sorted(topic_scores.items(), key=lambda x: x[1])
            )
            st.markdown(f'<div class="content-card">{bars_html}</div>',
                        unsafe_allow_html=True)
        else:
            skeleton_text_block(4)
            st.caption("Topic progress appears here after you take quizzes.")

    with col_actions:
        st.markdown("#### ⚡ Quick Actions")
        actions = [
            ("💬  Start Chat",        "chat"),
            ("❓  Generate Quiz",      "quiz"),
            ("📄  Summarize Notes",    "summary"),
            ("🃏  Review Flashcards",  "flashcards"),
        ]
        for label, page in actions:
            if st.button(label, use_container_width=True, key=f"qa_{page}"):
                st.session_state["current_page"] = page
                st.session_state["dashboard_stats"] = None
                st.rerun()

        # Flashcards reviewed counter
        fc_count = stats.get("flashcards_reviewed", 0)
        st.markdown(
            f"""
            <div class="content-card" style="margin-top:12px;text-align:center;">
                <div style="font-size:22px;">🃏</div>
                <div style="font-size:20px;font-weight:800;color:var(--accent);">
                    {fc_count}</div>
                <div style="font-size:11px;color:var(--text-faint);
                            text-transform:uppercase;">Flashcards Reviewed</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 5: Recent Activity + Recent Chats ──────────────────────────────
    col_activity, col_chats = st.columns(2)

    with col_activity:
        st.markdown("#### 📋 Recent Activity")
        activity = stats.get("recent_activity", [])
        if activity:
            items_html = "".join(
                _activity_item(a.get("icon", "📌"), a.get("text", ""), a.get("time", ""))
                for a in activity[:6]
            )
            st.markdown(
                f'<div class="content-card" style="padding:12px 16px;">{items_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="custom-info">No activity yet. '
                'Upload a document to get started!</div>',
                unsafe_allow_html=True,
            )

    with col_chats:
        st.markdown("#### 💬 Recent Chats")
        recent = stats.get("recent_chats", [])
        if recent:
            for item in recent[:4]:
                q = item.get("question", "")
                a = (item.get("answer", "")[:100] + "…") if len(item.get("answer","")) > 100 else item.get("answer","")
                st.markdown(
                    f"""
                    <div class="content-card" style="margin-bottom:8px;padding:12px 16px;">
                        <div style="font-weight:700;color:var(--text);font-size:13px;">
                            Q: {q}</div>
                        <div style="color:var(--text-faint);font-size:12px;margin-top:4px;">
                            A: {a}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            no_chat_history()
