"""
File Uploader Component — AI-Powered Study Buddy
=================================================
Reusable file-upload widget that:
- Accepts PDF, DOCX, PPTX, TXT (up to 50 MB)
- Shows upload progress
- Calls the FastAPI upload endpoint
- Displays success / error feedback
- Styled with Luxury AI SaaS tokens
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
        <div class="animate-fade-in-up" style="background:var(--secondary);border:2px dashed var(--border);
                    border-radius:var(--radius);padding:32px 24px;margin-bottom:16px;
                    transition:all var(--duration-med) var(--ease-out);text-align:center;"
             onmouseover="this.style.borderColor='var(--accent)';this.style.background='var(--surface-hover)';"
             onmouseout="this.style.borderColor='var(--border)';this.style.background='var(--secondary)';">
            <div style="font-size:36px;margin-bottom:12px;color:var(--accent);">☁️</div>
            <div style="font-weight:700;color:var(--text-primary);font-size:15px;margin-bottom:4px;">
                Drag & Drop or Click to Upload
            </div>
            <div style="color:var(--text-secondary);font-size:12px;text-transform:uppercase;letter-spacing:0.04em;">
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
        
        icon = "📄"
        if ext == "PDF":
            icon = "📕"
        elif ext == "DOCX":
            icon = "📘"
        elif ext == "PPTX":
            icon = "📙"
            
        st.markdown(
            f"""
            <div class="animate-fade-in-up content-card" style="padding:16px;display:flex;align-items:center;gap:16px;margin-bottom:16px;">
                <div style="width:48px;height:48px;background:var(--secondary);border:1px solid var(--border);
                            border-radius:12px;display:flex;align-items:center;justify-content:center;
                            font-size:24px;box-shadow:var(--shadow);">
                    {icon}
                </div>
                <div style="flex:1;overflow:hidden;">
                    <div style="font-weight:700;color:var(--text-primary);font-size:14px;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;margin-bottom:4px;">
                        {uploaded_file.name}
                    </div>
                    <div style="display:flex;gap:12px;align-items:center;">
                        <span class="badge badge-primary">{ext}</span>
                        <span style="color:var(--text-secondary);font-size:12px;font-weight:600;">{size_mb:.2f} MB</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⬆️ Upload & Process", use_container_width=True, type="primary", key="upload_btn"):
            # Progress UI placeholder
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.markdown('<div style="color:var(--text-secondary);font-size:13px;text-align:center;margin-top:8px;">Initializing secure upload...</div>', unsafe_allow_html=True)
            
            try:
                # Simulate progress for UX
                import time
                for percent_complete in range(0, 50, 10):
                    time.sleep(0.1)
                    progress_bar.progress(percent_complete + 10)
                
                status_text.markdown('<div style="color:var(--accent);font-size:13px;text-align:center;margin-top:8px;font-weight:600;">Processing vectors and extracting text...</div>', unsafe_allow_html=True)
                
                file_bytes = uploaded_file.getvalue()
                result = upload_document(token, file_bytes, uploaded_file.name)
                
                for percent_complete in range(50, 100, 10):
                    time.sleep(0.1)
                    progress_bar.progress(percent_complete + 10)
                    
                status_text.empty()
                progress_bar.empty()
                
                st.markdown(
                    f"""
                    <div class="animate-fade-in-up" style="background:var(--success);color:#ffffff;padding:16px;border-radius:var(--radius-sm);margin-top:16px;display:flex;align-items:center;gap:12px;box-shadow:0 4px 16px rgba(0,200,83,0.3);">
                        <div style="font-size:24px;">✅</div>
                        <div>
                            <div style="font-weight:700;font-size:14px;">Upload Successful!</div>
                            <div style="font-size:12px;opacity:0.9;">{uploaded_file.name} ({result.get('chunk_count', '?')} chunks indexed)</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                if on_success:
                    on_success(result)
            except RuntimeError as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"Upload failed: {e}")
