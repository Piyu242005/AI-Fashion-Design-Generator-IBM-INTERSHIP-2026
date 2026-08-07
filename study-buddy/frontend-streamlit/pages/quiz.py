"""
Quiz Page — AI-Powered Study Buddy
=====================================
Generates and administers AI-created quizzes:
  - MCQ (Multiple Choice)
  - True / False
  - Short Answer
Shows score, correct answers, and feeds results into the recommendation engine.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from utils.api_client import list_documents, generate_quiz
from utils.session_state import init_session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_color(score: float) -> str:
    if score >= 80:
        return "#22c55e"
    if score >= 60:
        return "#f97316"
    return "#ef4444"


def _render_mcq(q: dict[str, Any], idx: int) -> None:
    """Render one MCQ question with radio buttons."""
    st.markdown(
        f"""
        <div class="content-card">
            <div style="font-weight:700;color:#e2e8f0;font-size:14px;
                        margin-bottom:12px;">
                Q{idx + 1}. {q.get("question", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    options = q.get("options", [])
    key = f"quiz_q_{idx}"
    chosen = st.radio(
        f"q{idx}",
        options,
        key=key,
        label_visibility="collapsed",
    )
    st.session_state["quiz_answers"][idx] = chosen


def _render_truefalse(q: dict[str, Any], idx: int) -> None:
    """Render a True/False question."""
    st.markdown(
        f"""
        <div class="content-card">
            <div style="font-weight:700;color:#e2e8f0;font-size:14px;
                        margin-bottom:12px;">
                Q{idx + 1}. {q.get("question", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    key = f"quiz_q_{idx}"
    chosen = st.radio(
        f"tf{idx}", ["True", "False"],
        key=key,
        label_visibility="collapsed",
        horizontal=True,
    )
    st.session_state["quiz_answers"][idx] = chosen


def _render_short_answer(q: dict[str, Any], idx: int) -> None:
    """Render a short-answer text input."""
    st.markdown(
        f"""
        <div class="content-card">
            <div style="font-weight:700;color:#e2e8f0;font-size:14px;
                        margin-bottom:8px;">
                Q{idx + 1}. {q.get("question", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    key = f"quiz_q_{idx}"
    answer = st.text_input(
        f"sa{idx}",
        key=key,
        placeholder="Type your answer…",
        label_visibility="collapsed",
    )
    st.session_state["quiz_answers"][idx] = answer


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>❓ Quiz Generator</h1>
            <p>Auto-generate quizzes from your study material and test your knowledge.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Fetch documents ────────────────────────────────────────────────────
    try:
        docs = list_documents(token)
    except Exception:
        docs = []

    if not docs:
        st.markdown(
            '<div class="custom-warning">📂 No documents found. '
            'Upload a document first.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Configuration panel ────────────────────────────────────────────────
    col_cfg, col_spacer = st.columns([1, 2])
    with col_cfg:
        st.markdown("#### ⚙️ Quiz Settings")
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="quiz_doc")
        chosen_id   = doc_map[chosen_name]

        qtype = st.selectbox(
            "Question type",
            ["MCQ", "True/False", "Short Answer"],
            key="quiz_qtype",
        )
        num_q = st.slider("Number of questions", 3, 15, 5, key="quiz_num")

        generate_btn = st.button(
            "🎲  Generate Quiz", use_container_width=True, key="gen_quiz_btn"
        )

    if generate_btn:
        st.session_state["quiz_questions"] = []
        st.session_state["quiz_answers"]   = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_score"]     = None

        type_map = {"MCQ": "mcq", "True/False": "true_false", "Short Answer": "short_answer"}
        with st.spinner(f"Generating {num_q} {qtype} questions…"):
            try:
                result = generate_quiz(
                    token, chosen_id,
                    num_questions=num_q,
                    qtype=type_map[qtype],
                )
                st.session_state["quiz_questions"] = result.get("questions", [])
                st.session_state["quiz_doc_name"]  = chosen_name
            except RuntimeError as e:
                st.error(f"Quiz generation failed: {e}")
                return

    # ── Quiz display ───────────────────────────────────────────────────────
    questions = st.session_state.get("quiz_questions", [])

    if not questions:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;color:#475569;">
                <div style="font-size:48px;margin-bottom:12px;">❓</div>
                <div style="font-size:15px;color:#64748b;">
                    Configure settings and click<br>
                    <strong style="color:#3b82f6;">Generate Quiz</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    doc_name = st.session_state.get("quiz_doc_name", "")
    st.markdown(
        f"""
        <div style="margin-bottom:20px;">
            <span class="badge badge-blue">Quiz</span>&nbsp;
            <span class="badge badge-purple">{doc_name}</span>&nbsp;
            <span class="badge badge-orange">{len(questions)} Questions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    submitted = st.session_state.get("quiz_submitted", False)

    for idx, q in enumerate(questions):
        q_type = q.get("type", "mcq")
        if not submitted:
            if q_type == "mcq":
                _render_mcq(q, idx)
            elif q_type == "true_false":
                _render_truefalse(q, idx)
            else:
                _render_short_answer(q, idx)
        else:
            # Show result after submission
            user_ans    = st.session_state["quiz_answers"].get(idx, "")
            correct_ans = q.get("answer", "")
            is_correct  = str(user_ans).strip().lower() == str(correct_ans).strip().lower()
            border = "#22c55e" if is_correct else "#ef4444"
            icon   = "✅" if is_correct else "❌"
            st.markdown(
                f"""
                <div class="content-card" style="border-color:{border};">
                    <div style="font-weight:700;color:#e2e8f0;font-size:14px;">
                        {icon} Q{idx+1}. {q.get("question","")}
                    </div>
                    <div style="font-size:13px;margin-top:8px;">
                        <span style="color:#94a3b8;">Your answer:</span>
                        <strong style="color:{'#22c55e' if is_correct else '#ef4444'};">
                            {user_ans}</strong>
                    </div>
                    <div style="font-size:13px;">
                        <span style="color:#94a3b8;">Correct answer:</span>
                        <strong style="color:#22c55e;">{correct_ans}</strong>
                    </div>
                    {"" if is_correct else f'<div style="font-size:12px;color:#94a3b8;margin-top:6px;">💡 {q.get("explanation","")}</div>'}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Submit / Results ───────────────────────────────────────────────────
    if not submitted:
        if st.button("📤  Submit Quiz", use_container_width=True):
            st.session_state["quiz_submitted"] = True
            answers = st.session_state.get("quiz_answers", {})
            correct = sum(
                1
                for idx, q in enumerate(questions)
                if str(answers.get(idx, "")).strip().lower()
                == str(q.get("answer", "")).strip().lower()
            )
            st.session_state["quiz_score"] = round((correct / len(questions)) * 100)
            st.rerun()
    else:
        score = st.session_state.get("quiz_score", 0)
        color = _score_color(score)
        st.markdown(
            f"""
            <div class="content-card" style="text-align:center;
                 border-color:{color};margin-top:20px;">
                <div style="font-size:48px;">{
                    "🏆" if score >= 80 else "👍" if score >= 60 else "📚"
                }</div>
                <div style="font-size:32px;font-weight:800;color:{color};
                            margin:8px 0;">{score}%</div>
                <div style="color:#94a3b8;font-size:14px;">
                    {"Excellent!" if score >= 80
                     else "Good job! Review weak topics."
                     if score >= 60
                     else "Keep studying — you'll get there!"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔄  Retake Quiz", use_container_width=True):
            st.session_state["quiz_submitted"] = False
            st.session_state["quiz_answers"]   = {}
            st.session_state["quiz_score"]     = None
            st.rerun()
