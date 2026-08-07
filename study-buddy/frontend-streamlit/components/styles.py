"""
Shared CSS Styles — AI-Powered Study Buddy
===========================================
Single source of truth for all custom CSS injected into Streamlit.
Covers dark mode, cards, buttons, chat bubbles, badges, and animations.
"""

# ---------------------------------------------------------------------------
# Shared CSS — injected via st.markdown(..., unsafe_allow_html=True)
# ---------------------------------------------------------------------------

GLOBAL_CSS = """
<style>
/* ── Reset & base ─────────────────────────────────────────── */
.stApp { background-color: #0f1117; }

/* ── Hide default Streamlit chrome ───────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Custom scrollbar ─────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1e2130; }
::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 3px; }

/* ── Typography ───────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    color: #e2e8f0;
    font-weight: 700;
}
p, li, span, label { color: #cbd5e1; }

/* ── KPI / Metric cards ───────────────────────────────────── */
.kpi-card {
    background: #1e2130;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: border-color 0.2s;
}
.kpi-card:hover { border-color: #3b82f6; }
.kpi-value {
    font-size: 36px;
    font-weight: 800;
    color: #3b82f6;
    line-height: 1.1;
}
.kpi-label {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: .05em;
}

/* ── Content cards ────────────────────────────────────────── */
.content-card {
    background: #1e2130;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
.content-card h4 {
    color: #3b82f6;
    margin-bottom: 8px;
    font-size: 15px;
}

/* ── Chat bubbles ─────────────────────────────────────────── */
.chat-user {
    background: #1d4ed8;
    color: #fff;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    max-width: 75%;
    margin-left: auto;
    font-size: 14px;
    line-height: 1.5;
}
.chat-assistant {
    background: #1e2130;
    border: 1px solid #2d3748;
    color: #e2e8f0;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    max-width: 85%;
    font-size: 14px;
    line-height: 1.5;
}
.chat-assistant strong { color: #3b82f6; }

/* ── Badge ────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .05em;
    text-transform: uppercase;
}
.badge-blue   { background: #1d4ed8; color: #bfdbfe; }
.badge-green  { background: #14532d; color: #86efac; }
.badge-red    { background: #7f1d1d; color: #fca5a5; }
.badge-orange { background: #7c2d12; color: #fdba74; }
.badge-purple { background: #4c1d95; color: #c4b5fd; }

/* ── Progress bar ─────────────────────────────────────────── */
.progress-bar-bg {
    background: #2d3748;
    border-radius: 20px;
    height: 8px;
    width: 100%;
    margin: 6px 0;
}
.progress-bar-fill {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 20px;
    height: 8px;
}

/* ── Flashcard ────────────────────────────────────────────── */
.flashcard {
    background: #1e2130;
    border: 2px solid #3b82f6;
    border-radius: 16px;
    padding: 40px 32px;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.15s, border-color 0.2s;
}
.flashcard:hover { transform: translateY(-2px); border-color: #60a5fa; }
.flashcard-term   { font-size: 22px; font-weight: 700; color: #e2e8f0; }
.flashcard-def    { font-size: 15px; color: #94a3b8; margin-top: 12px; }
.flashcard-hint   { font-size: 12px; color: #475569; margin-top: 16px; }

/* ── Quiz option buttons ──────────────────────────────────── */
.quiz-option {
    background: #1e2130;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    cursor: pointer;
    color: #e2e8f0;
    font-size: 14px;
    transition: border-color 0.15s;
}
.quiz-option:hover  { border-color: #3b82f6; }
.quiz-option.correct { border-color: #22c55e; background: #14532d22; }
.quiz-option.wrong   { border-color: #ef4444; background: #7f1d1d22; }

/* ── File upload zone ─────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #2d3748 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    background: #1e2130 !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6 !important;
}

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #2d3748;
}
[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8;
    font-size: 14px;
    padding: 4px 0;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    background: #1d4ed8;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
    transition: background 0.15s;
}
.stButton > button:hover { background: #2563eb; }

/* ── Alert / info boxes ───────────────────────────────────── */
.custom-info {
    background: #1e3a5f;
    border-left: 4px solid #3b82f6;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #bfdbfe;
    font-size: 14px;
}
.custom-success {
    background: #14532d22;
    border-left: 4px solid #22c55e;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #86efac;
    font-size: 14px;
}
.custom-warning {
    background: #7c2d1222;
    border-left: 4px solid #f97316;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0;
    color: #fdba74;
    font-size: 14px;
}

/* ── Page header ──────────────────────────────────────────── */
.page-header {
    border-bottom: 1px solid #2d3748;
    padding-bottom: 16px;
    margin-bottom: 24px;
}
.page-header h1 { font-size: 26px; margin: 0; }
.page-header p  { color: #64748b; font-size: 14px; margin: 4px 0 0; }

/* ── Divider ──────────────────────────────────────────────── */
.custom-divider {
    border: none;
    border-top: 1px solid #2d3748;
    margin: 20px 0;
}
</style>
"""


def inject_css() -> str:
    """Return the global CSS block for use with st.markdown."""
    return GLOBAL_CSS
