"""
Profile Page — AI-Powered Study Buddy
=======================================
Displays user account info, study statistics, and document management.
Allows updating display name and viewing full quiz history.
Uses Design Tokens from design_system.py.
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
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">👤 My Workspace</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Manage your account and view your study documents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_info, col_docs = st.columns([1, 1.8])

    # ────────────────────────── Left: User info ───────────────────────────
    with col_info:
        name  = user.get("name", "Student")
        email = user.get("email", "—")

        # Avatar
        st.markdown(
            f"""
            <div class="content-card animate-fade-in-up" style="text-align:center;padding:32px 16px;margin-bottom:24px;">
                <div style="width:96px;height:96px;border-radius:50%;
                            background:linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
                            display:inline-flex;align-items:center;justify-content:center;
                            font-size:36px;font-weight:800;color:#fff;
                            border:4px solid var(--surface);box-shadow:0 0 24px rgba(255,0,60,0.3);margin-bottom:16px;">
                    {name[0].upper()}
                </div>
                <div style="font-size:24px;font-weight:800;color:var(--text-primary);letter-spacing:-0.03em;">{name}</div>
                <div style="font-size:14px;color:var(--text-secondary);margin-top:4px;">{email}</div>
                
                <div style="margin-top:24px;display:flex;justify-content:center;gap:12px;">
                    <span class="badge badge-primary">Pro Plan</span>
                    <span class="badge badge-success">Active</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Stats
        streak = user.get("study_streak", 0)
        st.markdown(
            f"""
            <div class="content-card animate-fade-in-up" style="padding:24px;margin-bottom:24px;">
                <div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:16px;">
                    📊 Lifetime Stats
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
                    <div style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;text-align:center;">
                        <div style="font-size:28px;font-weight:800;color:var(--accent);line-height:1;">
                            {streak}
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;font-weight:700;margin-top:8px;">Day Streak</div>
                    </div>
                    <div style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;text-align:center;">
                        <div style="font-size:28px;font-weight:800;color:var(--warning);line-height:1;">
                            {user.get("quiz_count", 0)}
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;font-weight:700;margin-top:8px;">Quizzes</div>
                    </div>
                    <div style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;text-align:center;">
                        <div style="font-size:28px;font-weight:800;color:var(--success);line-height:1;">
                            {user.get("document_count", 0)}
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;font-weight:700;margin-top:8px;">Documents</div>
                    </div>
                    <div style="background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;text-align:center;">
                        <div style="font-size:28px;font-weight:800;color:var(--text-primary);line-height:1;">
                            {user.get("avg_score", 0)}%
                        </div>
                        <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;font-weight:700;margin-top:8px;">Avg Score</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Refresh profile
        if st.button("🔄 Refresh Profile", use_container_width=True, type="secondary"):
            with st.spinner("Refreshing…"):
                try:
                    updated = get_profile(token)
                    st.session_state["user"] = updated
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ────────────────────────── Right: Documents ──────────────────────────
    with col_docs:
        st.markdown('<div style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">📂 My Documents</div>', unsafe_allow_html=True)

        try:
            docs = list_documents(token)
            st.session_state["documents"] = docs
        except Exception:
            docs = st.session_state.get("documents", [])

        if not docs:
            st.markdown(
                '<div class="animate-fade-in-up" style="background:var(--secondary);border:1px solid var(--border);padding:24px;border-radius:var(--radius);text-align:center;color:var(--text-secondary);font-size:14px;">'
                'No documents uploaded yet. Upload in the Sidebar or Chat to begin.</div>',
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
                        <div class="content-card animate-fade-in-up" style="margin-bottom:12px;padding:16px 20px;display:flex;align-items:center;gap:16px;transition:all var(--duration-fast) ease;"
                             onmouseover="this.style.borderColor='var(--accent)';" onmouseout="this.style.borderColor='var(--border)';">
                            <div style="width:40px;height:40px;background:var(--secondary);border:1px solid var(--border);
                                        border-radius:8px;display:flex;align-items:center;justify-content:center;
                                        font-size:20px;box-shadow:var(--shadow);">
                                {icon}
                            </div>
                            <div style="flex:1;">
                                <div style="font-weight:700;color:var(--text-primary);font-size:14px;margin-bottom:4px;">
                                    {filename}
                                </div>
                                <div style="color:var(--text-secondary);font-size:12px;">
                                    <span style="color:var(--accent);font-weight:600;">{ftype}</span> &nbsp;·&nbsp; {chunks} chunks
                                    {"&nbsp;·&nbsp; " + uploaded if uploaded else ""}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_del:
                    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_doc_{doc_id}", help="Delete document"):
                        with st.spinner("Deleting…"):
                            try:
                                delete_document(token, doc_id)
                                st.success(f"Deleted {filename}")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
