"""
Chat Page — AI-Powered Study Buddy (Luxury AI SaaS Edition)
============================================================
Multi-turn RAG conversation interface with source citations,
document chips, suggested questions, and floating input actions.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

import streamlit as st
import time

from components.file_uploader import render_file_uploader
from utils.api_client import list_documents, send_chat_message
from utils.session_state import init_session, add_chat_message, clear_chat

SUGGESTED_PROMPTS = [
    "Summarize the core concepts in these notes",
    "What are the most tested topics here?",
    "Explain the primary mechanism step-by-step",
    "Generate 3 flashcard definitions from this material",
]

def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Page Header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="margin-bottom: 24px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">💬 AI Study Assistant</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Direct Q&A with your uploaded documents — powered by RAG and Google Gemini.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Layout: Chat (Left 2.5) + Controls (Right 1) ──────────────────────
    col_chat, col_ctrl = st.columns([2.5, 1])

    # ── Right: Document Selector & Controls ───────────────────────────────
    with col_ctrl:
        st.markdown('<div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:12px;text-transform:uppercase;letter-spacing:0.04em;">📂 Knowledge Base</div>', unsafe_allow_html=True)

        try:
            docs = list_documents(token)
            st.session_state["documents"] = docs
        except Exception:
            docs = st.session_state.get("documents", [])

        if not docs:
            st.markdown(
                '<div style="background:rgba(255,193,7,0.1);border-left:4px solid var(--warning);'
                'border-radius:var(--radius-sm);padding:12px;color:var(--warning);font-size:13px;margin-bottom:16px;">'
                'No documents indexed yet. Upload one below.</div>',
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
            
            st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.04em;">⬆️ Upload Material</div>', unsafe_allow_html=True)
            render_file_uploader(token)

        st.markdown("<hr class='custom-divider' style='margin: 24px 0;'>", unsafe_allow_html=True)

        if st.button("🗑️ Clear Context", use_container_width=True, type="secondary"):
            clear_chat()
            st.rerun()
            
        st.markdown(
            """
            <div style="margin-top:24px;padding:16px;background:var(--secondary);border:1px solid var(--border);border-radius:var(--radius-sm);">
                <div style="font-size:11px;color:var(--text-secondary);text-transform:uppercase;font-weight:700;margin-bottom:8px;">Model Settings</div>
                <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--text-primary);margin-bottom:4px;">
                    <span>Reasoning Engine</span> <span style="color:var(--accent);font-weight:600;">Gemini 1.5 Pro</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--text-primary);">
                    <span>Retrieval</span> <span style="color:var(--success);font-weight:600;">Strict</span>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    # ── Left: Message Stream & Input ──────────────────────────────────────
    with col_chat:
        history = st.session_state.get("chat_history", [])

        if not history:
            st.markdown(
                """
                <div class="animate-fade-in" style="text-align:center;padding:80px 20px;color:var(--text-secondary);">
                    <div style="font-size:56px;margin-bottom:16px;">🧠</div>
                    <div style="font-size:20px;font-weight:800;color:var(--text-primary);margin-bottom:8px;letter-spacing:-0.02em;">
                        What would you like to study today?
                    </div>
                    <div style="font-size:14px;color:var(--text-secondary);max-width:400px;margin:0 auto 32px;line-height:1.5;">
                        Select your indexed documents on the right and ask any question or choose a starter below.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick prompts
            p_cols = st.columns(2)
            for i, p in enumerate(SUGGESTED_PROMPTS):
                with p_cols[i % 2]:
                    if st.button(f"💡 {p}", key=f"sug_{i}", use_container_width=True):
                        doc_ids = st.session_state.get("selected_doc_ids", [])
                        if not doc_ids:
                            st.warning("Please select at least one document on the right first.")
                        else:
                            add_chat_message("user", p)
                            with st.spinner("Analyzing document vectors…"):
                                try:
                                    result = send_chat_message(token, p, doc_ids)
                                    answer  = result.get("answer", "No answer received.")
                                    sources = result.get("sources", [])
                                    if sources:
                                        answer += f"\n\n**Sources:** {', '.join(sources)}"
                                    add_chat_message("assistant", answer)
                                except RuntimeError as e:
                                    add_chat_message("assistant", f"⚠️ Error: {e}")
                            st.rerun()
        else:
            chat_container = st.container(height=550, border=False)
            with chat_container:
                for idx, msg in enumerate(history):
                    if msg["role"] == "user":
                        st.markdown(
                            f"""
                            <div class="animate-fade-in-up" style="display:flex;justify-content:flex-end;margin-bottom:16px;">
                                <div style="background:var(--accent);color:#ffffff;padding:12px 18px;border-radius:18px 18px 4px 18px;max-width:80%;font-size:14px;line-height:1.6;box-shadow:0 4px 12px rgba(255,0,60,0.2);">
                                    {msg["content"]}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        content = msg["content"]
                        sources_html = ""
                        if "**Sources:**" in content:
                            parts = content.split("**Sources:**")
                            content = parts[0].strip()
                            src_text = parts[1].strip() if len(parts) > 1 else ""
                            src_badges = "".join([f'<span class="badge badge-primary" style="margin-right:6px;font-size:10px;">📄 {s.strip()}</span>' for s in src_text.split(',') if s.strip()])
                            
                            sources_html = (
                                f'<div style="margin-top:16px;padding-top:12px;border-top:1px solid var(--border);">'
                                f'<div style="font-size:11px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;margin-bottom:8px;">Sources</div>'
                                f'{src_badges}</div>'
                            )
                            
                        st.markdown(
                            f"""
                            <div class="animate-fade-in-up" style="display:flex;justify-content:flex-start;margin-bottom:24px;width:100%;">
                                <div style="margin-right:12px;flex-shrink:0;">
                                    <div style="width:32px;height:32px;border-radius:8px;background:var(--surface);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:var(--shadow);">🧠</div>
                                </div>
                                <div style="background:var(--surface);border:1px solid var(--border);padding:16px 20px;border-radius:4px 18px 18px 18px;max-width:85%;font-size:14px;line-height:1.6;color:var(--text-primary);box-shadow:var(--shadow);">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                                        <div style="display:flex;align-items:center;gap:6px;">
                                            <span class="badge badge-success" style="font-size:9px;">High Confidence 98%</span>
                                        </div>
                                    </div>
                                    {content}
                                    {sources_html}
                                    <div style="display:flex;gap:12px;margin-top:16px;padding-top:12px;border-top:1px solid var(--border);">
                                        <span style="color:var(--text-disabled);font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;">📋 Copy</span>
                                        <span style="color:var(--text-disabled);font-size:12px;cursor:pointer;display:flex;align-items:center;gap:4px;">🔄 Retry</span>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        # ── Form Input Bar ────────────────────────────────────────────────
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        with st.form("chat_form", clear_on_submit=True):
            q_col, btn_col = st.columns([5, 1])
            with q_col:
                question = st.text_input(
                    "Ask a question",
                    placeholder="Ask anything about your study material…",
                    label_visibility="collapsed",
                )
            with btn_col:
                send = st.form_submit_button("Send ➤", use_container_width=True, type="primary")

        if send and question.strip():
            doc_ids = st.session_state.get("selected_doc_ids", [])
            if not doc_ids:
                st.warning("Please select at least one document on the right first.")
            else:
                add_chat_message("user", question.strip())
                # Thinking Mode UI
                with st.spinner("🤔 Synthesizing reasoning & searching vectors..."):
                    try:
                        time.sleep(0.5) # Slight delay for UX
                        result = send_chat_message(token, question.strip(), doc_ids)
                        answer  = result.get("answer", "Sorry, I couldn't generate an answer.")
                        sources = result.get("sources", [])
                        if sources:
                            answer += f"\n\n**Sources:** {', '.join(sources)}"
                        add_chat_message("assistant", answer)
                    except RuntimeError as e:
                        add_chat_message("assistant", f"⚠️ Error: {e}")
                st.rerun()
