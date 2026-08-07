"""File Uploader Component — AI-Powered Study Buddy"""
from __future__ import annotations
import streamlit as st
from utils.api_client import upload_document

ALLOWED_TYPES = ["pdf", "docx", "pptx", "txt"]
MAX_SIZE_MB   = 50

def render_file_uploader(token: str, on_success=None) -> None:
    st.markdown(
        '<div style="background:var(--surface);border:2px dashed var(--border);'
        'border-radius:12px;padding:24px;margin-bottom:16px;text-align:center;'
        'color:var(--text-faint);font-size:13px;">'
        '<div style="font-size:32px;margin-bottom:8px;">📂</div>'
        '<strong style="color:var(--text-muted);">Upload Study Material</strong><br>'
        'PDF · DOCX · PPTX · TXT &nbsp;|&nbsp; Max 50 MB</div>',
        unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a file", type=ALLOWED_TYPES,
                                label_visibility="collapsed", key="file_upload_widget")
    if uploaded is not None:
        size_mb = uploaded.size / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            st.error(f"File too large ({size_mb:.1f} MB). Maximum is {MAX_SIZE_MB} MB.")
            return
        ext  = uploaded.name.rsplit(".", 1)[-1].upper()
        icon = {"PDF":"📕","DOCX":"📘","PPTX":"📙"}.get(ext, "📄")
        st.markdown(
            f'<div style="background:var(--surface2);border:1px solid var(--border);'
            f'border-radius:8px;padding:12px 16px;display:flex;align-items:center;'
            f'gap:12px;margin-bottom:12px;">'
            f'<div style="font-size:24px;">{icon}</div>'
            f'<div><div style="font-weight:700;color:var(--text);font-size:13px;">{uploaded.name}</div>'
            f'<div style="color:var(--text-faint);font-size:12px;">{ext} · {size_mb:.2f} MB</div>'
            f'</div></div>', unsafe_allow_html=True)
        if st.button("⬆️  Upload & Process", use_container_width=True, key="upload_btn"):
            with st.spinner("Uploading and processing…"):
                try:
                    result = upload_document(token, uploaded.getvalue(), uploaded.name)
                    st.success(f"✅ '{uploaded.name}' uploaded — {result.get('chunk_count','?')} chunks indexed")
                    if on_success:
                        on_success(result)
                except RuntimeError as e:
                    st.error(f"Upload failed: {e}")
