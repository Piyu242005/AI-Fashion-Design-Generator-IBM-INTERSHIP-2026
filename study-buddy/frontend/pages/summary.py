"""Summary Page — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import list_documents, generate_summary
from utils.session_state import init_session

def render():
    init_session()
    token = st.session_state.get("token","")
    st.markdown('<div class="page-header"><h1>📄 Smart Summary</h1>'
                '<p>Get AI-generated summaries of your study materials in seconds.</p></div>',
                unsafe_allow_html=True)
    try: docs = list_documents(token)
    except Exception: docs = []
    if not docs:
        st.markdown('<div class="custom-warning">📂 No documents found. Upload a document first.</div>',
                    unsafe_allow_html=True); return

    col_ctrl, col_out = st.columns([1,2])
    with col_ctrl:
        st.markdown("#### ⚙️ Options")
        doc_map = {d["filename"]: d["id"] for d in docs}
        chosen_name = st.selectbox("Select document", list(doc_map.keys()), key="sum_doc")
        chosen_id   = doc_map[chosen_name]
        style   = st.radio("Style", ["🔵 Bullet Points","📝 Paragraph"], key="sum_style")
        style_k = "bullet" if "Bullet" in style else "paragraph"
        detail  = st.select_slider("Detail", ["Brief","Standard","Detailed"], value="Standard", key="sum_detail")
        gen_btn = st.button("✨  Generate Summary", use_container_width=True)

    with col_out:
        st.markdown("#### 📋 Output")
        if gen_btn:
            with st.spinner(f"Summarising '{chosen_name}'…"):
                try:
                    r = generate_summary(token, chosen_id, style=style_k)
                    st.session_state["last_summary"] = r.get("summary","")
                    st.session_state["last_summary_name"] = chosen_name
                except RuntimeError as e:
                    st.error(f"Summary failed: {e}"); return
        s = st.session_state.get("last_summary")
        n = st.session_state.get("last_summary_name","")
        if s:
            st.markdown(
                f'<div class="content-card"><h4>📄 {n}</h4>'
                f'<div style="color:var(--text);font-size:14px;line-height:1.8;white-space:pre-wrap;">{s}</div></div>',
                unsafe_allow_html=True)
            st.download_button("⬇️  Download (.txt)", data=s,
                               file_name=f"summary_{n}.txt", mime="text/plain", use_container_width=True)
        else:
            st.markdown(
                '<div style="text-align:center;padding:60px 20px;color:var(--text-faint);">'
                '<div style="font-size:48px;">📄</div>'
                '<div style="font-size:15px;margin-top:12px;">Select a document and click '
                '<strong style="color:var(--accent);">Generate Summary</strong></div></div>',
                unsafe_allow_html=True)
