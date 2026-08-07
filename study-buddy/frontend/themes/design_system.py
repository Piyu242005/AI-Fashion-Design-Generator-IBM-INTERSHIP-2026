"""
Design System — AI-Powered Study Buddy
========================================
Single source of truth for color tokens (5 themes), spacing, radii,
shadows, and full CSS injection per theme.
"""
from __future__ import annotations

THEMES: dict[str, dict[str, str]] = {
    "Dark": {
        "bg": "#0f1117", "surface": "#1e2130", "surface2": "#161b27",
        "border": "#2d3748", "text": "#e2e8f0", "text_muted": "#94a3b8",
        "text_faint": "#475569", "accent": "#3b82f6", "accent_hover": "#2563eb",
        "accent_light": "#1d4ed8", "accent_bg": "#1e3a5f", "secondary": "#8b5cf6",
        "success": "#22c55e", "success_bg": "#14532d", "warning": "#f97316",
        "warning_bg": "#7c2d12", "danger": "#ef4444", "danger_bg": "#7f1d1d",
    },
    "Light": {
        "bg": "#f8fafc", "surface": "#ffffff", "surface2": "#f1f5f9",
        "border": "#e2e8f0", "text": "#1e293b", "text_muted": "#64748b",
        "text_faint": "#94a3b8", "accent": "#2563eb", "accent_hover": "#1d4ed8",
        "accent_light": "#3b82f6", "accent_bg": "#eff6ff", "secondary": "#7c3aed",
        "success": "#16a34a", "success_bg": "#dcfce7", "warning": "#ea580c",
        "warning_bg": "#fff7ed", "danger": "#dc2626", "danger_bg": "#fee2e2",
    },
    "Blue": {
        "bg": "#06091f", "surface": "#0d1535", "surface2": "#0a1128",
        "border": "#1e3a6e", "text": "#dbeafe", "text_muted": "#93c5fd",
        "text_faint": "#60a5fa", "accent": "#60a5fa", "accent_hover": "#3b82f6",
        "accent_light": "#2563eb", "accent_bg": "#1e3a5f", "secondary": "#a78bfa",
        "success": "#4ade80", "success_bg": "#14532d", "warning": "#fb923c",
        "warning_bg": "#7c2d12", "danger": "#f87171", "danger_bg": "#7f1d1d",
    },
    "Purple": {
        "bg": "#0d0a1a", "surface": "#1a1030", "surface2": "#130c24",
        "border": "#3b2d6e", "text": "#ede9fe", "text_muted": "#c4b5fd",
        "text_faint": "#a78bfa", "accent": "#a78bfa", "accent_hover": "#8b5cf6",
        "accent_light": "#7c3aed", "accent_bg": "#2e1a5e", "secondary": "#f472b6",
        "success": "#4ade80", "success_bg": "#14532d", "warning": "#fb923c",
        "warning_bg": "#7c2d12", "danger": "#f87171", "danger_bg": "#7f1d1d",
    },
}
THEMES["System"] = THEMES["Dark"].copy()


def get_theme_css(theme_name: str = "Dark") -> str:
    t = THEMES.get(theme_name, THEMES["Dark"])
    return f"""
<style>
*,*::before,*::after{{box-sizing:border-box;}}
:root{{
  --bg:{t['bg']};--surface:{t['surface']};--surface2:{t['surface2']};
  --border:{t['border']};--text:{t['text']};--text-muted:{t['text_muted']};
  --text-faint:{t['text_faint']};--accent:{t['accent']};
  --accent-hover:{t['accent_hover']};--secondary:{t['secondary']};
  --success:{t['success']};--warning:{t['warning']};--danger:{t['danger']};
}}
.stApp{{background:var(--bg)!important;}}
#MainMenu,footer,header{{visibility:hidden;}}
.stDeployButton{{display:none!important;}}
body{{font-family:-apple-system,"Segoe UI",system-ui,sans-serif;font-size:14px;line-height:1.6;color:var(--text);}}
h1,h2,h3,h4,h5,h6{{color:var(--text);font-weight:700;}}
p,li,span{{color:var(--text-muted);}}
::-webkit-scrollbar{{width:6px;height:6px;}}
::-webkit-scrollbar-track{{background:var(--surface);}}
::-webkit-scrollbar-thumb{{background:var(--accent);border-radius:6px;}}
[data-testid="stSidebar"]{{background:var(--surface2)!important;border-right:1px solid var(--border);}}
.kpi-card{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px 24px;text-align:center;transition:border-color .2s,transform .2s;}}
.kpi-card:hover{{border-color:var(--accent);transform:translateY(-2px);}}
.kpi-value{{font-size:34px;font-weight:800;color:var(--accent);line-height:1.1;}}
.kpi-label{{font-size:12px;color:var(--text-faint);margin-top:4px;text-transform:uppercase;letter-spacing:.06em;}}
.content-card{{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:20px;margin-bottom:16px;transition:border-color .2s;}}
.content-card h4{{color:var(--accent);margin-bottom:8px;font-size:15px;}}
.chat-user{{background:var(--accent-light);color:#fff;padding:12px 16px;border-radius:18px 18px 4px 18px;margin:8px 0 8px auto;max-width:75%;font-size:14px;line-height:1.55;animation:fadeInRight .25s ease;}}
.chat-assistant{{background:var(--surface);border:1px solid var(--border);color:var(--text);padding:12px 16px;border-radius:18px 18px 18px 4px;margin:8px 0;max-width:85%;font-size:14px;line-height:1.55;animation:fadeInLeft .25s ease;}}
@keyframes shimmer{{0%{{background-position:-700px 0;}}100%{{background-position:700px 0;}}}}
.skeleton{{background:linear-gradient(90deg,var(--surface) 25%,var(--border) 50%,var(--surface) 75%);background-size:700px 100%;animation:shimmer 1.4s infinite linear;border-radius:10px;}}
.toast{{position:fixed;bottom:24px;right:24px;background:var(--surface);border-left:4px solid var(--accent);border-radius:10px;padding:12px 20px;color:var(--text);font-size:14px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.5);}}
.toast.success{{border-color:var(--success);}}
.toast.warning{{border-color:var(--warning);}}
.toast.error{{border-color:var(--danger);}}
.progress-bar-bg{{background:var(--border);border-radius:9999px;height:8px;width:100%;margin:6px 0;}}
.progress-bar-fill{{background:linear-gradient(90deg,var(--accent),var(--secondary));border-radius:9999px;height:8px;transition:width .6s cubic-bezier(.4,0,.2,1);}}
.flashcard{{background:var(--surface);border:2px solid var(--accent);border-radius:16px;padding:40px 32px;text-align:center;min-height:220px;display:flex;flex-direction:column;justify-content:center;transition:transform .2s,border-color .2s,box-shadow .2s;}}
.flashcard:hover{{transform:translateY(-3px);border-color:var(--secondary);}}
.badge{{display:inline-block;padding:3px 10px;border-radius:9999px;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;}}
.badge-blue{{background:var(--accent-light);color:#bfdbfe;}}
.badge-green{{background:{t['success_bg']};color:#86efac;}}
.badge-red{{background:{t['danger_bg']};color:#fca5a5;}}
.badge-orange{{background:{t['warning_bg']};color:#fdba74;}}
.badge-purple{{background:#4c1d95;color:#c4b5fd;}}
.custom-info{{background:{t['accent_bg']};border-left:4px solid var(--accent);border-radius:6px;padding:12px 16px;margin:10px 0;color:var(--text);font-size:14px;}}
.custom-success{{background:{t['success_bg']}22;border-left:4px solid var(--success);border-radius:6px;padding:12px 16px;margin:10px 0;color:#86efac;font-size:14px;}}
.custom-warning{{background:{t['warning_bg']}22;border-left:4px solid var(--warning);border-radius:6px;padding:12px 16px;margin:10px 0;color:#fdba74;font-size:14px;}}
.stButton>button{{background:var(--accent)!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:600!important;padding:8px 20px!important;transition:background .15s,transform .1s!important;}}
.stButton>button:hover{{background:var(--accent-hover)!important;transform:translateY(-1px);}}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{{border-color:var(--accent)!important;box-shadow:0 0 0 3px {t['accent']}33!important;}}
[data-testid="stFileUploader"]{{border:2px dashed var(--border)!important;border-radius:14px!important;background:var(--surface)!important;transition:border-color .2s!important;}}
[data-testid="stFileUploader"]:hover{{border-color:var(--accent)!important;}}
.page-header{{border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:24px;}}
.page-header h1{{font-size:26px;margin:0;}}
.page-header p{{color:var(--text-faint);font-size:14px;margin:4px 0 0;}}
.custom-divider{{border:none;border-top:1px solid var(--border);margin:20px 0;}}
@keyframes fadeInRight{{from{{opacity:0;transform:translateX(20px);}}to{{opacity:1;transform:translateX(0);}}}}
@keyframes fadeInLeft{{from{{opacity:0;transform:translateX(-20px);}}to{{opacity:1;transform:translateX(0);}}}}
@keyframes fadeInUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
@media(max-width:768px){{.kpi-value{{font-size:24px;}}.chat-user,.chat-assistant{{max-width:100%;}}.flashcard{{padding:24px 16px;}}}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:2px;}}
</style>"""


def inject_theme(theme_name: str = "Dark") -> None:
    import streamlit as st
    st.markdown(get_theme_css(theme_name), unsafe_allow_html=True)
