"""
Chat Page — AI-Powered Study Buddy
=====================================
Multi-turn RAG-powered chat interface.
- Select documents to query against
- Send questions; stream AI answers
- Display source citations
- Clear conversation history
"""

from __future__ import annotations

import streamlit as st

from components.file_uploader import render_file_uploader
from utils.api_client import list_documents, send_chat_message
from utils.session_state import init_session, add_chat_message, clear_chat


def render() -> None:
    init_session()

    token = st.session_state.get("token", "")

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>💬 AI Chat</h1>
            <p>Ask anything about your uploaded study materials — powered by RAG + Gemini.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Layout: chat (left 2/3) + controls (right 1/3) ────────────────────
    col_chat, col_ctrl = st.columns([2, 1])

    # ────────────────────────── Right: Controls ───────────────────────────
    with col_ctrl:
        st.markdown("#### 📂 Select Documents")

        # Fetch documents
        try:
            docs = list_documents(token)
            st.session_state["documents"] = docs
        except Exception:
            docs = st.session_state.get("documents", [])

        if not docs:
            st.markdown(
                '<div class="custom-warning">No documents yet. '
                "Upload one below.</div>",
                unsafe_allow_html=True,
            )
            render_file_uploader(token)
        else:
            doc_options = {d["filename"]: d["id"] for d in docs}
            selected_names = st.multiselect(
                "Choose documents to query",
                options=list(doc_options.keys()),
                default=list(doc_options.keys())[:1],
                label_visibility="collapsed",
            )
            st.session_state["selected_doc_ids"] = [
                doc_options[n] for n in selected_names
            ]

            st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
            st.markdown("#### ⬆️ Upload New")
            render_file_uploader(token)

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        # Clear history
        if st.button("🗑️  Clear Chat", use_container_width=True):
            clear_chat()
            st.rerun()

        # Chat stats
        history = st.session_state.get("chat_history", [])
        user_msgs = sum(1 for m in history if m["role"] == "user")
        st.markdown(
            f"""
            <div class="content-card">
                <h4>📊 Session Stats</h4>
                <div style="font-size:13px;color:#94a3b8;">
                    Questions asked: <strong style="color:#3b82f6;">{user_msgs}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ────────────────────────── Left: Chat ────────────────────────────────
    with col_chat:
        history = st.session_state.get("chat_history", [])

        # ── Chat history display ───────────────────────────────────────────
        chat_container = st.container()
        with chat_container:
            if not history:
                st.markdown(
                    """
                    <div style="text-align:center;padding:60px 20px;color:#475569;">
                        <div style="font-size:48px;margin-bottom:12px;">🤖</div>
                        <div style="font-size:16px;color:#64748b;">
                            Hello! I'm your AI Study Buddy.<br>
                            Select a document and ask me anything!
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                for msg in history:
                    if msg["role"] == "user":
                        st.markdown(
                            f'<div class="chat-user">👤 {msg["content"]}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        # Parse source citations if present
                        content = msg["content"]
                        sources_html = ""
                        if "**Sources:**" in content:
                            parts = content.split("**Sources:**")
                            content = parts[0].strip()
                            src_text = parts[1].strip() if len(parts) > 1 else ""
                            sources_html = (
                                f'<div style="margin-top:10px;padding-top:8px;'
                                f'border-top:1px solid #2d3748;font-size:11px;'
                                f'color:#64748b;">📎 <strong>Sources:</strong> {src_text}</div>'
                            )
                        st.markdown(
                            f'<div class="chat-assistant">🤖 {content}{sources_html}</div>',
                            unsafe_allow_html=True,
                        )

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # ── Input bar ─────────────────────────────────────────────────────
        with st.form("chat_form", clear_on_submit=True):
            q_col, btn_col = st.columns([5, 1])
            with q_col:
                question = st.text_input(
                    "Ask a question",
                    placeholder="e.g. What is Newton's third law?",
                    label_visibility="collapsed",
                )
            with btn_col:
                send = st.form_submit_button("Send ➤", use_container_width=True)

        if send and question.strip():
            doc_ids = st.session_state.get("selected_doc_ids", [])
            if not doc_ids:
                st.warning("Please select at least one document to query.")
            else:
                add_chat_message("user", question.strip())
                with st.spinner("Thinking…"):
                    try:
                        result = send_chat_message(token, question.strip(), doc_ids)
                        answer  = result.get("answer", "Sorry, I couldn't generate an answer.")
                        sources = result.get("sources", [])
                        if sources:
                            answer += f"\n\n**Sources:** {', '.join(sources)}"
                        add_chat_message("assistant", answer)
                    except RuntimeError as e:
                        add_chat_message("assistant", f"⚠️ Error: {e}")
                st.rerun()
