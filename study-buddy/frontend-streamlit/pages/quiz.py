"""
Quiz Page — AI-Powered Study Buddy (Luxury AI SaaS Edition)
============================================================
Interactive MCQ, True/False, and Short Answer quizzes with real-time scoring,
timers, feedback cards, and gamified mastery badges.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

from typing import Any
import streamlit as st

from utils.api_client import list_documents, generate_quiz
from utils.session_state import init_session

def _score_color(score: float) -> str:
    if score >= 80:
        return "var(--success)"
    if score >= 60:
        return "var(--warning)"
    return "var(--danger)"

def _render_mcq(q: dict[str, Any], idx: int) -> None:
    st.markdown(
        f"""
        <div class="content-card animate-fade-in-up" style="margin-bottom:12px;padding:24px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:28px;height:28px;background:var(--accent);color:#ffffff;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;box-shadow:0 0 12px rgba(255,0,60,0.4);">
                    {idx + 1}
                </div>
                <div style="font-weight:700;color:var(--text-primary);font-size:15px;flex:1;line-height:1.5;">
                    {q.get("question", "")}
                </div>
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
    st.markdown(
        f"""
        <div class="content-card animate-fade-in-up" style="margin-bottom:12px;padding:24px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:28px;height:28px;background:var(--accent);color:#ffffff;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;box-shadow:0 0 12px rgba(255,0,60,0.4);">
                    {idx + 1}
                </div>
                <div style="font-weight:700;color:var(--text-primary);font-size:15px;flex:1;line-height:1.5;">
                    {q.get("question", "")}
                </div>
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
    st.markdown(
        f"""
        <div class="content-card animate-fade-in-up" style="margin-bottom:12px;padding:24px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:28px;height:28px;background:var(--accent);color:#ffffff;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:14px;box-shadow:0 0 12px rgba(255,0,60,0.4);">
                    {idx + 1}
                </div>
                <div style="font-weight:700;color:var(--text-primary);font-size:15px;flex:1;line-height:1.5;">
                    {q.get("question", "")}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    key = f"quiz_q_{idx}"
    answer = st.text_input(
        f"sa{idx}",
        key=key,
        placeholder="Type your answer here…",
        label_visibility="collapsed",
    )
    st.session_state["quiz_answers"][idx] = answer

def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Page Header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">❓ Adaptive Quiz Generator</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Test your understanding with instant, AI-graded quizzes generated from your materials.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        docs = list_documents(token)
    except Exception:
        docs = []

    if not docs:
        st.markdown(
            '<div class="animate-fade-in-up" style="background:rgba(255,193,7,0.1);border-left:4px solid var(--warning);'
            'border-radius:var(--radius-sm);padding:16px;color:var(--warning);font-size:14px;">'
            '📂 No documents found. Please upload study material to generate quizzes.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Settings Column ────────────────────────────────────────────────────
    col_cfg, col_display = st.columns([1, 2.5])

    with col_cfg:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">⚙️ Quiz Parameters</div>', unsafe_allow_html=True)
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="quiz_doc")
        chosen_id   = doc_map[chosen_name]

        qtype = st.selectbox(
            "Question format",
            ["Multiple Choice", "True / False", "Short Answer"],
            key="quiz_qtype",
        )
        num_q = st.slider("Question count", 3, 15, 5, key="quiz_num")

        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        generate_btn = st.button(
            "🎲 Generate Quiz", use_container_width=True, type="primary", key="gen_quiz_btn"
        )

    if generate_btn:
        st.session_state["quiz_questions"] = []
        st.session_state["quiz_answers"]   = {}
        st.session_state["quiz_submitted"] = False
        st.session_state["quiz_score"]     = None

        type_map = {"Multiple Choice": "mcq", "True / False": "true_false", "Short Answer": "short_answer"}
        with st.spinner(f"Generating {num_q} {qtype} questions with Gemini…"):
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

    # ── Quiz Questions & Results ───────────────────────────────────────────
    with col_display:
        questions = st.session_state.get("quiz_questions", [])

        if not questions:
            st.markdown(
                """
                <div class="animate-fade-in" style="text-align:center;padding:80px 20px;color:var(--text-secondary);">
                    <div style="font-size:56px;margin-bottom:16px;">🎯</div>
                    <div style="font-size:20px;font-weight:800;color:var(--text-primary);margin-bottom:8px;letter-spacing:-0.02em;">
                        Ready to test your knowledge?
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);max-width:400px;margin:0 auto;line-height:1.5;">
                        Configure question settings on the left and click <strong>Generate Quiz</strong>.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        doc_name = st.session_state.get("quiz_doc_name", "")
        st.markdown(
            f"""
            <div class="animate-fade-in-up" style="margin-bottom:24px;display:flex;gap:12px;flex-wrap:wrap;align-items:center;padding-left:16px;">
                <span class="badge badge-primary">Quiz Active</span>
                <span class="badge badge-success">📄 {doc_name}</span>
                <span class="badge badge-warning">🎯 {len(questions)} Questions</span>
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
                user_ans    = st.session_state["quiz_answers"].get(idx, "")
                correct_ans = q.get("answer", "")
                is_correct  = str(user_ans).strip().lower() == str(correct_ans).strip().lower()
                border = "var(--success)" if is_correct else "var(--danger)"
                icon   = "✅" if is_correct else "❌"
                
                # Explanation display for feedback
                exp_html = ""
                if not is_correct and q.get("explanation"):
                    exp_html = f'<div style="font-size:13px;color:var(--text-secondary);margin-top:12px;padding-top:12px;border-top:1px solid var(--border);">💡 {q.get("explanation","")}</div>'

                st.markdown(
                    f"""
                    <div class="content-card animate-fade-in-up" style="border:1px solid {border};padding:24px;margin-bottom:16px;">
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                            <div style="font-size:18px;">{icon}</div>
                            <div style="font-weight:700;color:var(--text-primary);font-size:15px;flex:1;line-height:1.5;">
                                Q{idx+1}. {q.get("question","")}
                            </div>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;background:var(--secondary);padding:16px;border-radius:var(--radius-sm);border:1px solid var(--border);">
                            <div>
                                <span style="font-size:11px;color:var(--text-disabled);text-transform:uppercase;font-weight:700;display:block;margin-bottom:4px;">Your Answer</span>
                                <strong style="color:{border};font-size:14px;">{user_ans if user_ans else '—'}</strong>
                            </div>
                            <div>
                                <span style="font-size:11px;color:var(--text-disabled);text-transform:uppercase;font-weight:700;display:block;margin-bottom:4px;">Correct Answer</span>
                                <strong style="color:var(--success);font-size:14px;">{correct_ans}</strong>
                            </div>
                        </div>
                        {exp_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if not submitted:
            st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
            if st.button("📤 Submit Answers for Grading", use_container_width=True, type="primary"):
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
            
            icon, title = ("🏆", "Mastery Level Achieved! 🎉") if score >= 80 else ("⚡", "Solid Performance! Review weak areas. 💪") if score >= 60 else ("💡", "Review study notes and try again. 📚")
            
            st.markdown(
                f"""
                <div class="content-card animate-fade-in-up" style="text-align:center;border:2px solid {color};margin-top:32px;padding:48px 24px;background:linear-gradient(180deg, rgba(0,0,0,0) 0%, {color}11 100%);">
                    <div style="font-size:56px;margin-bottom:12px;filter:drop-shadow(0 0 20px {color});">{icon}</div>
                    <div style="font-size:56px;font-weight:900;color:{color};margin:0;line-height:1;letter-spacing:-0.04em;">{score}%</div>
                    <div style="color:var(--text-primary);font-weight:700;font-size:18px;margin-top:16px;">
                        {title}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Retake Quiz", use_container_width=True, type="secondary"):
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_answers"]   = {}
                st.session_state["quiz_score"]     = None
                st.rerun()
