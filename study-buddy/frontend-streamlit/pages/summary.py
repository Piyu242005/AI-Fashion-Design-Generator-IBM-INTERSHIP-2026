"""
Summary Page — AI-Powered Study Buddy
=======================================
Generates concise summaries of uploaded documents.
Supports bullet-point and paragraph styles.
Allows export of summary as plain text.
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import list_documents, generate_summary
from utils.session_state import init_session


def render() -> None:
    init_session()

    token = st.session_state.get("token", "")

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1>📄 Smart Summary</h1>
            <p>Get AI-generated summaries of your study materials in seconds.</p>
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
            'Please upload a document first from the Chat page.</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Controls ───────────────────────────────────────────────────────────
    col_ctrl, col_out = st.columns([1, 2])

    with col_ctrl:
        st.markdown("#### ⚙️ Options")

        doc_map = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox(
            "Select document",
            options=list(doc_map.keys()),
            key="summary_doc_select",
        )
        chosen_id = doc_map[chosen_name]

        style = st.radio(
            "Summary style",
            ["🔵 Bullet Points", "📝 Paragraph"],
            key="summary_style",
        )
        style_key = "bullet" if "Bullet" in style else "paragraph"

        detail = st.select_slider(
            "Detail level",
            options=["Brief", "Standard", "Detailed"],
            value="Standard",
            key="summary_detail",
        )

        generate_btn = st.button(
            "✨  Generate Summary", use_container_width=True, key="gen_summary_btn"
        )

    with col_out:
        st.markdown("#### 📋 Summary Output")

        if generate_btn:
            with st.spinner(f"Summarising *{chosen_name}*…"):
                try:
                    result  = generate_summary(token, chosen_id, style=style_key)
                    summary = result.get("summary", "No summary returned.")
                    st.session_state["last_summary"]      = summary
                    st.session_state["last_summary_name"] = chosen_name
                except RuntimeError as e:
                    st.error(f"Summary failed: {e}")
                    return

        last_summary = st.session_state.get("last_summary")
        last_name    = st.session_state.get("last_summary_name", "")

        if last_summary:
            st.markdown(
                f"""
                <div class="content-card">
                    <h4>📄 {last_name}</h4>
                    <div style="color:#e2e8f0;font-size:14px;line-height:1.8;
                                white-space:pre-wrap;">{last_summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── Export ─────────────────────────────────────────────────────
            st.download_button(
                label="⬇️  Download Summary (.txt)",
                data=last_summary,
                file_name=f"summary_{last_name}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.markdown(
                """
                <div style="text-align:center;padding:60px 20px;color:#475569;">
                    <div style="font-size:48px;margin-bottom:12px;">📄</div>
                    <div style="font-size:15px;color:#64748b;">
                        Select a document and click<br>
                        <strong style="color:#3b82f6;">Generate Summary</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
