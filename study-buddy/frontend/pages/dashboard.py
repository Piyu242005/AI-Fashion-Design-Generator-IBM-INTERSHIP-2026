"""
Dashboard Page — AI-Powered Study Buddy
========================================
Displays:
  Row 1 — KPI cards: Documents, Study Time, Quiz Score, Streak
  Row 2 — Weak Topics | Strong Topics | AI Recommendations
  Row 3 — Recent Chat History | Quick Actions
  Row 4 — Progress bars per topic (from quiz scores)
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import get_dashboard_stats, list_documents
from utils.session_state import init_session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi(value: str, label: str, icon: str, color: str = "#3b82f6") -> str:
    return f"""
    <div class="kpi-card">
        <div style="font-size:28px;margin-bottom:4px;">{icon}</div>
        <div class="kpi-value" style="color:{color};">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


def _topic_bar(topic: str, score: int) -> str:
    color = "#22c55e" if score >= 80 else "#f97316" if score >= 60 else "#ef4444"
    return f"""
    <div style="margin-bottom:10px;">
        <div style="display:flex;justify-content:space-between;
                    font-size:13px;color:#94a3b8;margin-bottom:4px;">
            <span>{topic}</span>
            <span style="color:{color};font-weight:700;">{score}%</span>
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill"
                 style="width:{score}%;background:{color};"></div>
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    init_session()

    user  = st.session_state.get("user", {}) or {}
    token = st.session_state.get("token", "")
    name  = user.get("name", "Student")

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="page-header">
            <h1>🏠 Dashboard</h1>
            <p>Welcome back, <strong style="color:#3b82f6;">{name}</strong>!
               Here's your study overview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch stats ────────────────────────────────────────────────────────
    with st.spinner("Loading your stats…"):
        try:
            stats = get_dashboard_stats(token)
        except Exception:
            # Fallback demo data when backend is not running
            stats = {
                "document_count":  0,
                "total_study_mins": 0,
                "avg_quiz_score":  0,
                "study_streak":    user.get("study_streak", 0),
                "weak_topics":     [],
                "strong_topics":   [],
                "ai_suggestions":  ["Upload your first document to get started!"],
                "recent_chats":    [],
                "topic_scores":    {},
                "flashcards_reviewed": 0,
                "daily_goal_pct":  0,
            }

    # ── Row 1: KPI cards ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_kpi(str(stats.get("document_count", 0)),
                         "Documents", "📄"), unsafe_allow_html=True)
    with c2:
        mins = stats.get("total_study_mins", 0)
        st.markdown(_kpi(f"{mins}m", "Study Time", "⏱", "#8b5cf6"),
                    unsafe_allow_html=True)
    with c3:
        score = stats.get("avg_quiz_score", 0)
        color = "#22c55e" if score >= 70 else "#f97316"
        st.markdown(_kpi(f"{score}%", "Avg Quiz Score", "🎯", color),
                    unsafe_allow_html=True)
    with c4:
        streak = stats.get("study_streak", 0)
        st.markdown(_kpi(str(streak), "Day Streak", "🔥", "#f97316"),
                    unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 2: Topics + AI Suggestions ────────────────────────────────────
    col_weak, col_strong, col_ai = st.columns(3)

    with col_weak:
        st.markdown("#### ⚠️ Weak Topics")
        weak = stats.get("weak_topics", [])
        if weak:
            for t in weak[:5]:
                st.markdown(
                    f'<span class="badge badge-red">{t}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No weak topics yet — take a quiz!")

    with col_strong:
        st.markdown("#### ✅ Strong Topics")
        strong = stats.get("strong_topics", [])
        if strong:
            for t in strong[:5]:
                st.markdown(
                    f'<span class="badge badge-green">{t}</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No strong topics yet.")

    with col_ai:
        st.markdown("#### 🤖 AI Suggestions")
        suggestions = stats.get("ai_suggestions", [])
        if suggestions:
            for s in suggestions[:3]:
                st.markdown(
                    f'<div class="custom-info">{s}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No suggestions yet.")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 3: Topic progress + Quick Actions ──────────────────────────────
    col_progress, col_actions = st.columns([2, 1])

    with col_progress:
        st.markdown("#### 📊 Topic Progress")
        topic_scores: dict = stats.get("topic_scores", {})
        if topic_scores:
            bars_html = "".join(
                _topic_bar(topic, score)
                for topic, score in sorted(
                    topic_scores.items(), key=lambda x: x[1]
                )
            )
            st.markdown(
                f'<div class="content-card">{bars_html}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="custom-info">Take quizzes to see your topic progress here.</div>',
                unsafe_allow_html=True,
            )

    with col_actions:
        st.markdown("#### ⚡ Quick Actions")
        if st.button("💬  Start Chat", use_container_width=True):
            st.session_state["current_page"] = "chat"
            st.rerun()
        if st.button("❓  Generate Quiz", use_container_width=True):
            st.session_state["current_page"] = "quiz"
            st.rerun()
        if st.button("📄  Summarize Notes", use_container_width=True):
            st.session_state["current_page"] = "summary"
            st.rerun()
        if st.button("🃏  Review Flashcards", use_container_width=True):
            st.session_state["current_page"] = "flashcards"
            st.rerun()

        # Daily goal
        goal_pct = min(stats.get("daily_goal_pct", 0), 100)
        st.markdown(
            f"""
            <div class="content-card" style="margin-top:16px;">
                <h4>🎯 Daily Goal</h4>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill"
                         style="width:{goal_pct}%;"></div>
                </div>
                <div style="font-size:12px;color:#64748b;margin-top:6px;
                            text-align:right;">{goal_pct}% complete</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # ── Row 4: Recent chat history ─────────────────────────────────────────
    st.markdown("#### 💬 Recent Chats")
    recent = stats.get("recent_chats", [])
    if recent:
        for item in recent[:5]:
            q = item.get("question", "")
            a = item.get("answer", "")[:120] + "…"
            st.markdown(
                f"""
                <div class="content-card">
                    <div style="font-weight:700;color:#e2e8f0;font-size:13px;">
                        Q: {q}</div>
                    <div style="color:#64748b;font-size:12px;margin-top:4px;">
                        A: {a}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="custom-info">No chat history yet. '
            'Upload a document and start asking questions!</div>',
            unsafe_allow_html=True,
        )
