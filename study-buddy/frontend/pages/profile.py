"""Profile Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import list_documents, delete_document, get_profile
from utils.session_state import init_session

def render():
    init_session()
    token = st.session_state.get("token","")
    user  = st.session_state.get("user") or {}
    st.markdown('<div class="page-header"><h1>👤 Profile</h1>'
                '<p>Manage your account and uploaded documents.</p></div>',
                unsafe_allow_html=True)
    col_info, col_docs = st.columns([1,2])

    with col_info:
        name  = user.get("name","Student")
        email = user.get("email","—")
        st.markdown(
            f'<div style="text-align:center;margin-bottom:20px;">'
            f'<div style="width:80px;height:80px;border-radius:50%;background:var(--accent);'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:32px;font-weight:800;color:#fff;border:3px solid var(--accent);">'
            f'{name[0].upper()}</div>'
            f'<div style="font-size:20px;font-weight:700;color:var(--text);margin-top:10px;">{name}</div>'
            f'<div style="font-size:13px;color:var(--text-faint);">{email}</div></div>',
            unsafe_allow_html=True)
        streak = user.get("study_streak",0)
        st.markdown(
            f'<div class="content-card"><h4>📊 Your Stats</h4>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px;">'
            f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:var(--accent);">{streak}</div>'
            f'<div style="font-size:11px;color:var(--text-faint);">Day Streak</div></div>'
            f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:var(--secondary);">{user.get("quiz_count",0)}</div>'
            f'<div style="font-size:11px;color:var(--text-faint);">Quizzes</div></div>'
            f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:var(--success);">{user.get("document_count",0)}</div>'
            f'<div style="font-size:11px;color:var(--text-faint);">Documents</div></div>'
            f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:var(--warning);">{user.get("avg_score",0)}%</div>'
            f'<div style="font-size:11px;color:var(--text-faint);">Avg Score</div></div>'
            f'</div></div>', unsafe_allow_html=True)
        if st.button("🔄  Refresh Profile", use_container_width=True):
            try:
                st.session_state["user"] = get_profile(token); st.rerun()
            except Exception as e: st.error(str(e))

    with col_docs:
        st.markdown("#### 📂 My Documents")
        try: docs = list_documents(token); st.session_state["documents"] = docs
        except Exception: docs = st.session_state.get("documents",[])
        if not docs:
            st.markdown('<div class="custom-info">No documents uploaded yet.</div>', unsafe_allow_html=True)
        else:
            for doc in docs:
                ftype = doc.get("filename","").rsplit(".",1)[-1].upper()
                icon  = {"PDF":"📕","DOCX":"📘","PPTX":"📙"}.get(ftype,"📄")
                cd, cx = st.columns([5,1])
                with cd:
                    st.markdown(
                        f'<div class="content-card" style="margin-bottom:8px;padding:12px 16px;">'
                        f'<div style="display:flex;align-items:center;gap:12px;">'
                        f'<div style="font-size:24px;">{icon}</div>'
                        f'<div><div style="font-weight:700;color:var(--text);font-size:13px;">{doc.get("filename","")}</div>'
                        f'<div style="color:var(--text-faint);font-size:11px;">{ftype} · {doc.get("chunk_count","?")} chunks</div>'
                        f'</div></div></div>', unsafe_allow_html=True)
                with cx:
                    if st.button("🗑️", key=f"del_{doc.get('id')}", help="Delete"):
                        try:
                            delete_document(token, doc["id"]); st.success("Deleted"); st.rerun()
                        except Exception as e: st.error(str(e))
