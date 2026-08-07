"""Quiz Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import list_documents, generate_quiz
from utils.session_state import init_session

def render():
    init_session()
    token = st.session_state.get("token","")
    st.markdown('<div class="page-header"><h1>❓ Quiz Generator</h1>'
                '<p>Auto-generate quizzes from your study material and test your knowledge.</p></div>',
                unsafe_allow_html=True)
    try: docs = list_documents(token)
    except Exception: docs = []
    if not docs:
        st.markdown('<div class="custom-warning">📂 No documents. Upload one first.</div>',
                    unsafe_allow_html=True); return

    col_cfg, _ = st.columns([1,2])
    with col_cfg:
        st.markdown("#### ⚙️ Quiz Settings")
        doc_map     = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Document", list(doc_map.keys()), key="quiz_doc")
        chosen_id   = doc_map[chosen_name]
        qtype       = st.selectbox("Question type", ["MCQ","True/False","Short Answer"], key="quiz_qtype")
        num_q       = st.slider("Questions", 3, 15, 5, key="quiz_num")
        gen_btn     = st.button("🎲  Generate Quiz", use_container_width=True)

    if gen_btn:
        st.session_state.update({"quiz_questions":[], "quiz_answers":{},
                                  "quiz_submitted":False, "quiz_score":None})
        type_map = {"MCQ":"mcq","True/False":"true_false","Short Answer":"short_answer"}
        with st.spinner(f"Generating {num_q} {qtype} questions…"):
            try:
                r = generate_quiz(token, chosen_id, num_questions=num_q, qtype=type_map[qtype])
                st.session_state["quiz_questions"] = r.get("questions",[])
                st.session_state["quiz_doc_name"]  = chosen_name
            except RuntimeError as e:
                st.error(f"Quiz generation failed: {e}"); return

    questions = st.session_state.get("quiz_questions",[])
    if not questions:
        st.markdown(
            '<div style="text-align:center;padding:60px 20px;color:var(--text-faint);">'
            '<div style="font-size:48px;">❓</div>'
            '<div style="font-size:15px;margin-top:12px;">Configure settings and click '
            '<strong style="color:var(--accent);">Generate Quiz</strong></div></div>',
            unsafe_allow_html=True); return

    submitted = st.session_state.get("quiz_submitted", False)
    st.markdown(
        f'<div style="margin-bottom:20px;">'
        f'<span class="badge badge-blue">Quiz</span> '
        f'<span class="badge badge-orange">{len(questions)} Questions</span></div>',
        unsafe_allow_html=True)

    for idx, q in enumerate(questions):
        qtype_q = q.get("type","mcq")
        opts    = q.get("options",[])
        if not submitted:
            st.markdown(
                f'<div class="content-card"><div style="font-weight:700;color:var(--text);font-size:14px;">'
                f'Q{idx+1}. {q.get("question","")}</div></div>', unsafe_allow_html=True)
            key = f"quiz_q_{idx}"
            if qtype_q == "true_false":
                ans = st.radio(f"tf{idx}", ["True","False"], key=key,
                               label_visibility="collapsed", horizontal=True)
            elif opts:
                ans = st.radio(f"mc{idx}", opts, key=key, label_visibility="collapsed")
            else:
                ans = st.text_input(f"sa{idx}", key=key, placeholder="Your answer…",
                                    label_visibility="collapsed")
            st.session_state["quiz_answers"][idx] = ans
        else:
            user_ans   = st.session_state["quiz_answers"].get(idx,"")
            correct    = q.get("answer","")
            is_correct = str(user_ans).strip().lower() == str(correct).strip().lower()
            border     = "var(--success)" if is_correct else "var(--danger)"
            icon       = "✅" if is_correct else "❌"
            st.markdown(
                f'<div class="content-card" style="border-color:{border};">'
                f'<div style="font-weight:700;color:var(--text);">{icon} Q{idx+1}. {q.get("question","")}</div>'
                f'<div style="font-size:13px;margin-top:6px;color:var(--text-muted);">'
                f'Your: <strong style="color:{border};">{user_ans}</strong> &nbsp;|&nbsp; '
                f'Correct: <strong style="color:var(--success);">{correct}</strong></div>'
                + (f'<div style="font-size:12px;color:var(--text-faint);margin-top:4px;">'
                   f'💡 {q.get("explanation","")}</div>' if not is_correct and q.get("explanation") else "")
                + '</div>', unsafe_allow_html=True)

    if not submitted:
        if st.button("📤  Submit Quiz", use_container_width=True):
            answers = st.session_state.get("quiz_answers",{})
            correct = sum(1 for i,q in enumerate(questions)
                          if str(answers.get(i,"")).strip().lower()==str(q.get("answer","")).strip().lower())
            st.session_state["quiz_submitted"] = True
            st.session_state["quiz_score"] = round((correct/len(questions))*100)
            st.rerun()
    else:
        score = st.session_state.get("quiz_score",0)
        color = "var(--success)" if score>=80 else "var(--warning)" if score>=60 else "var(--danger)"
        st.markdown(
            f'<div class="content-card" style="text-align:center;border-color:{color};margin-top:20px;">'
            f'<div style="font-size:48px;">{"🏆" if score>=80 else "👍" if score>=60 else "📚"}</div>'
            f'<div style="font-size:32px;font-weight:800;color:{color};margin:8px 0;">{score}%</div>'
            f'<div style="color:var(--text-muted);">{"Excellent!" if score>=80 else "Good job! Review weak topics." if score>=60 else "Keep studying!"}</div>'
            f'</div>', unsafe_allow_html=True)
        if st.button("🔄  Retake Quiz", use_container_width=True):
            st.session_state.update({"quiz_submitted":False,"quiz_answers":{},"quiz_score":None})
            st.rerun()
