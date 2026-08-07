"""
Profile Page — AI-Powered Study Buddy
=======================================
Displays user account info, study statistics, and document management.
Allows updating display name and viewing full quiz history.
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import list_documents, delete_document, get_profile
from utils.session_state import init_session


def render() -> None:
    init_session()

    token = st.session_state.get("token", "")
    user  = st.session_state.get("user", {}) or {}

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>👤 Profile</h1>
            <p>Manage your account and view your study documents.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_info, col_docs = st.columns([1, 2])

    # ────────────────────────── Left: User info ───────────────────────────
    with col_info:
        name  = user.get("name", "Student")
        email = user.get("email", "—")

        # Avatar
        st.markdown(
            f"""
            <div style="text-align:center;margin-bottom:20px;">
                <div style="width:80px;height:80px;border-radius:50%;
                            background:#1d4ed8;display:inline-flex;
                            align-items:center;justify-content:center;
                            font-size:32px;font-weight:800;color:#fff;
                            border:3px solid #3b82f6;">
                    {name[0].upper()}
                </div>
                <div style="font-size:20px;font-weight:700;color:#e2e8f0;
                            margin-top:10px;">{name}</div>
                <div style="font-size:13px;color:#64748b;">{email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Stats
        streak = user.get("study_streak", 0)
        st.markdown(
            f"""
            <div class="content-card">
                <h4>📊 Your Stats</h4>
                <div style="display:grid;grid-template-columns:1fr 1fr;
                            gap:12px;margin-top:8px;">
                    <div style="text-align:center;">
                        <div style="font-size:24px;font-weight:800;color:#3b82f6;">
                            {streak}</div>
                        <div style="font-size:11px;color:#64748b;">Day Streak</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:24px;font-weight:800;color:#8b5cf6;">
                            {user.get("quiz_count", 0)}</div>
                        <div style="font-size:11px;color:#64748b;">Quizzes Taken</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:24px;font-weight:800;color:#22c55e;">
                            {user.get("document_count", 0)}</div>
                        <div style="font-size:11px;color:#64748b;">Documents</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:24px;font-weight:800;color:#f97316;">
                            {user.get("avg_score", 0)}%</div>
                        <div style="font-size:11px;color:#64748b;">Avg Score</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Refresh profile
        if st.button("🔄  Refresh Profile", use_container_width=True):
            with st.spinner("Refreshing…"):
                try:
                    updated = get_profile(token)
                    st.session_state["user"] = updated
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ────────────────────────── Right: Documents ──────────────────────────
    with col_docs:
        st.markdown("#### 📂 My Documents")

        try:
            docs = list_documents(token)
            st.session_state["documents"] = docs
        except Exception:
            docs = st.session_state.get("documents", [])

        if not docs:
            st.markdown(
                '<div class="custom-info">No documents uploaded yet.</div>',
                unsafe_allow_html=True,
            )
        else:
            for doc in docs:
                doc_id   = doc.get("id")
                filename = doc.get("filename", "Unknown")
                ftype    = filename.rsplit(".", 1)[-1].upper() if "." in filename else "FILE"
                chunks   = doc.get("chunk_count", "?")
                uploaded = doc.get("uploaded_at", "")[:10] if doc.get("uploaded_at") else ""

                icon = {"PDF": "📕", "DOCX": "📘", "PPTX": "📙", "TXT": "📄"}.get(ftype, "📄")

                col_doc, col_del = st.columns([5, 1])
                with col_doc:
                    st.markdown(
                        f"""
                        <div class="content-card" style="margin-bottom:8px;padding:12px 16px;">
                            <div style="display:flex;align-items:center;gap:12px;">
                                <div style="font-size:24px;">{icon}</div>
                                <div>
                                    <div style="font-weight:700;color:#e2e8f0;
                                                font-size:13px;">{filename}</div>
                                    <div style="color:#64748b;font-size:11px;">
                                        {ftype} &nbsp;·&nbsp; {chunks} chunks
                                        {"&nbsp;·&nbsp; Uploaded " + uploaded if uploaded else ""}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_del:
                    if st.button("🗑️", key=f"del_doc_{doc_id}", help="Delete document"):
                        with st.spinner("Deleting…"):
                            try:
                                delete_document(token, doc_id)
                                st.success(f"Deleted {filename}")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
