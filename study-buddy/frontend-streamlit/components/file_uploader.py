"""
File Uploader Component — AI-Powered Study Buddy
=================================================
Reusable file-upload widget that:
- Accepts PDF, DOCX, PPTX, TXT (up to 50 MB)
- Shows upload progress
- Calls the FastAPI upload endpoint
- Displays success / error feedback
"""

from __future__ import annotations

import streamlit as st

from utils.api_client import upload_document


ALLOWED_TYPES = ["pdf", "docx", "pptx", "txt"]
MAX_SIZE_MB   = 50


def render_file_uploader(token: str, on_success: callable | None = None) -> None:
    """
    Render a styled file uploader widget.

    Args:
        token: JWT auth token for the upload API call.
        on_success: Optional callback invoked after successful upload.
    """
    st.markdown(
        """
        <div style="background:#1e2130;border:2px dashed #2d3748;
                    border-radius:12px;padding:24px;margin-bottom:16px;">
            <div style="text-align:center;color:#64748b;font-size:13px;">
                <div style="font-size:32px;margin-bottom:8px;">📂</div>
                <strong style="color:#94a3b8;">Upload Study Material</strong><br>
                PDF · DOCX · PPTX · TXT &nbsp;|&nbsp; Max 50 MB
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=ALLOWED_TYPES,
        label_visibility="collapsed",
        key="file_upload_widget",
    )

    if uploaded_file is not None:
        # Size guard
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > MAX_SIZE_MB:
            st.error(f"File too large ({size_mb:.1f} MB). Maximum is {MAX_SIZE_MB} MB.")
            return

        # File info display
        ext = uploaded_file.name.rsplit(".", 1)[-1].upper()
        st.markdown(
            f"""
            <div style="background:#161b27;border:1px solid #2d3748;
                        border-radius:8px;padding:12px 16px;
                        display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="font-size:24px;">
                    {"📕" if ext=="PDF" else "📘" if ext=="DOCX" else "📙" if ext=="PPTX" else "📄"}
                </div>
                <div>
                    <div style="font-weight:700;color:#e2e8f0;font-size:13px;">
                        {uploaded_file.name}</div>
                    <div style="color:#64748b;font-size:12px;">
                        {ext} &nbsp;·&nbsp; {size_mb:.2f} MB</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⬆️  Upload & Process", use_container_width=True, key="upload_btn"):
            with st.spinner("Uploading and processing… This may take a moment for large files."):
                try:
                    file_bytes = uploaded_file.getvalue()
                    result = upload_document(token, file_bytes, uploaded_file.name)
                    st.success(
                        f"✅ **{uploaded_file.name}** uploaded successfully! "
                        f"({result.get('chunk_count', '?')} chunks indexed)"
                    )
                    if on_success:
                        on_success(result)
                except RuntimeError as e:
                    st.error(f"Upload failed: {e}")
