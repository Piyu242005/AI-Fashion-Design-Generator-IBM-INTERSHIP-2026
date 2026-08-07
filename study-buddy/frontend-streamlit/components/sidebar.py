"""
Sidebar Component — AI-Powered Study Buddy (Luxury AI SaaS Edition)
====================================================================
Renders the persistent left navigation sidebar with:
- Workspace (Branding)
- Navigation
- Quick Actions
- Storage
- User Profile
- Settings & Logout
"""

from __future__ import annotations

import streamlit as st

from utils.session_state import is_logged_in, logout

# Main navigation links
NAV_ITEMS = [
    ("Dashboard",   "🏠", "dashboard"),
    ("AI Chat",     "💬", "chat"),
    ("Documents",   "📄", "profile"), # Reusing profile page for documents for now, or could map to upload
    ("Summary",     "📝", "summary"),
    ("Quiz",        "❓", "quiz"),
    ("Flashcards",  "🃏", "flashcards"),
]

# Bottom navigation links
SETTINGS_ITEMS = [
    ("Profile",     "👤", "profile"),
    ("Settings",    "⚙️", "settings"),
    ("Help",        "💡", "help"),
]

def render_sidebar() -> str:
    """Render sidebar navigation. Returns the selected page key."""
    with st.sidebar:
        
        # ── 1. Workspace (Branding) ───────────────────────────────────────
        st.markdown(
            """
            <div style="padding: 12px 4px 20px; text-align: left;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <div style="width:32px;height:32px;border-radius:8px;background:var(--accent);
                                display:flex;align-items:center;justify-content:center;
                                font-size:16px;box-shadow:0 0 16px rgba(255,0,60,0.5);">
                        🧠
                    </div>
                    <div>
                        <div style="font-size:15px;font-weight:800;color:var(--text-primary);letter-spacing:-0.02em;line-height:1.2;">
                            Study Buddy
                        </div>
                        <div style="font-size:10px;font-weight:700;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.06em;">
                            AI Workspace
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_logged_in():
            current = st.session_state.get("current_page", "dashboard")
            
            # ── 2. Navigation ────────────────────────────────────────────────
            st.markdown('<div style="font-size:11px;font-weight:700;color:var(--text-disabled);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;padding-left:4px;">Main Menu</div>', unsafe_allow_html=True)
            
            nav_labels = [f"{emoji}  {label}" for label, emoji, _ in NAV_ITEMS]
            nav_keys   = [key for _, _, key in NAV_ITEMS]
            
            settings_labels = [f"{emoji}  {label}" for label, emoji, _ in SETTINGS_ITEMS]
            settings_keys   = [key for _, _, key in SETTINGS_ITEMS]
            
            all_labels = nav_labels + settings_labels
            all_keys = nav_keys + settings_keys
            
            default_idx = all_keys.index(current) if current in all_keys else 0
            
            # Streamlit radio doesn't support grouping well, so we use one radio for all,
            # or split them if we must. One radio is safer for Streamlit state.
            selected_label = st.radio(
                "Navigate",
                all_labels,
                index=default_idx,
                label_visibility="collapsed",
                key="sidebar_nav",
            )
            
            selected_idx = all_labels.index(selected_label)
            selected_page = all_keys[selected_idx]
            st.session_state["current_page"] = selected_page

            st.markdown("<hr class='custom-divider' style='margin: 16px 0;'>", unsafe_allow_html=True)

            # ── 3. Quick Actions ─────────────────────────────────────────────
            st.markdown('<div style="font-size:11px;font-weight:700;color:var(--text-disabled);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;padding-left:4px;">Quick Actions</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Upload", use_container_width=True, key="qa_upload"):
                    st.session_state["current_page"] = "profile" # Route to documents/profile
                    st.rerun()
            with col2:
                if st.button("⚡ Quiz", use_container_width=True, key="qa_quiz"):
                    st.session_state["current_page"] = "quiz"
                    st.rerun()
                    
            st.markdown("<hr class='custom-divider' style='margin: 16px 0;'>", unsafe_allow_html=True)

            # ── 4. Storage ───────────────────────────────────────────────────
            # Dummy storage calc for UI purposes
            storage_used = 14.2
            storage_max = 50.0
            storage_pct = int((storage_used / storage_max) * 100)
            
            st.markdown(
                f"""
                <div style="padding: 0 4px;">
                    <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-secondary);margin-bottom:6px;font-weight:500;">
                        <span>Storage</span>
                        <span>{storage_used}MB / {storage_max}MB</span>
                    </div>
                    <div class="progress-bar-bg" style="height:4px;margin-bottom:4px;">
                        <div class="progress-bar-fill" style="width:{storage_pct}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            st.markdown("<hr class='custom-divider' style='margin: 16px 0;'>", unsafe_allow_html=True)

            # ── 5. User ──────────────────────────────────────────────────────
            user = st.session_state.get("user", {}) or {}
            name  = user.get("name", "Student")
            email = user.get("email", "student@studybuddy.ai")
            
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:10px;padding:8px 4px;margin-bottom:8px;">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:var(--surface);border:1px solid var(--border);
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;color:var(--text-primary);font-size:13px;flex-shrink:0;">
                        {name[0].upper()}
                    </div>
                    <div style="overflow:hidden;">
                        <div style="font-weight:600;color:var(--text-primary);font-size:13px;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;">
                            {name}
                        </div>
                        <div style="color:var(--text-secondary);font-size:11px;white-space:nowrap;text-overflow:ellipsis;overflow:hidden;">
                            {email}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ── 6. Logout ────────────────────────────────────────────────────
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout()
                st.rerun()

            return selected_page

        else:
            st.markdown(
                '<p style="color:var(--text-disabled);font-size:13px;text-align:left;padding-left:4px;">'
                "Please sign in to unlock your workspace.</p>",
                unsafe_allow_html=True,
            )
            return "login"
