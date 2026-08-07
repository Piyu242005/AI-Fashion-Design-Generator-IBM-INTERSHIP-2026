"""
Summary Page — AI-Powered Study Buddy (Luxury AI SaaS Edition)
===============================================================
AI-powered document summarizer supporting:
- Bullet Points
- Paragraph
- Detailed / Executive Breakdown
- Mind Map (Outline)
Features: Word counter, Download, and formatted markdown rendering.
Uses Design Tokens from design_system.py.
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import list_documents, generate_summary
from utils.session_state import init_session

def render() -> None:
    init_session()
    token = st.session_state.get("token", "")

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="animate-fade-in-up" style="margin-bottom: 32px;">
            <h1 style="font-size:32px;font-weight:800;letter-spacing:-0.03em;margin:0;">📝 AI Document Summarizer</h1>
            <p style="color:var(--text-secondary);font-size:14px;margin-top:6px;">
                Distill 100-page documents into structured, actionable study summaries in seconds.
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
            '📂 No documents found. Please upload study material to generate summaries.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Configuration Card ─────────────────────────────────────────────────
    doc_map = {d["filename"]: d["id"] for d in docs}

    st.markdown(
        '<div class="animate-fade-in-up" style="font-weight:700;color:var(--text-primary);font-size:13px;text-transform:uppercase;letter-spacing:0.04em;margin-bottom:12px;">'
        '⚙️ Summary Parameters</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([2, 1.2, 1.2])

    with c1:
        chosen_name = st.selectbox("Target Document", list(doc_map.keys()), key="sum_doc")
        chosen_id   = doc_map[chosen_name]

    with c2:
        style_label = st.selectbox(
            "Summary Format",
            ["Bullet Points", "Paragraph", "Deep Dive", "Mind Map Outline"],
            key="sum_style",
        )
        style_map = {
            "Bullet Points": "bullet",
            "Paragraph":     "paragraph",
            "Deep Dive":     "detailed",
            "Mind Map Outline": "bullet" # Backend mapped
        }

    with c3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        gen_btn = st.button("✨ Generate", use_container_width=True, type="primary", key="gen_sum_btn")

    if gen_btn:
        with st.spinner("Synthesizing document vectors with Gemini…"):
            try:
                res = generate_summary(token, chosen_id, style=style_map[style_label])
                st.session_state["summary_text"] = res.get("summary", "")
                st.session_state["summary_doc"]  = chosen_name
                st.session_state["summary_words"] = len(res.get("summary", "").split())
            except RuntimeError as e:
                st.error(f"Summary generation failed: {e}")

    # ── Summary Output Card ────────────────────────────────────────────────
    summary = st.session_state.get("summary_text", "")
    doc_name = st.session_state.get("summary_doc", "")
    words   = st.session_state.get("summary_words", 0)

    if summary:
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="animate-fade-in-up" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <div style="display:flex;gap:12px;align-items:center;">
                    <span class="badge badge-primary" style="font-size:12px;">AI Summary</span>
                    <span class="badge badge-success" style="font-size:12px;">📄 {doc_name}</span>
                </div>
                <div style="font-size:13px;color:var(--text-secondary);font-weight:600;">
                    {words} words
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="content-card animate-fade-in-up" style="line-height:1.75;font-size:14px;color:var(--text-primary);margin-bottom:16px;">
                {summary}
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Actions
        a1, a2, a3, _ = st.columns([1, 1, 1, 3])
        with a1:
            st.download_button("📥 Download", data=summary, file_name=f"Summary_{doc_name}.md", use_container_width=True)
        with a2:
            if st.button("📋 Copy", use_container_width=True):
                st.toast("Summary copied (placeholder)!")
    else:
        st.markdown(
            """
            <div class="animate-fade-in" style="text-align:center;padding:80px 20px;color:var(--text-secondary);">
                <div style="font-size:48px;margin-bottom:16px;">📝</div>
                <div style="font-size:16px;color:var(--text-primary);font-weight:700;margin-bottom:8px;">
                    No summary generated yet
                </div>
                <div style="font-size:14px;color:var(--text-disabled);">
                    Select your document above and click <strong>Generate</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
