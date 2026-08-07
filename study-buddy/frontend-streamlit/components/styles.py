"""
Shared CSS Styles — AI-Powered Study Buddy (Luxury Red Theme)
==============================================================
Provides GLOBAL_CSS matching the Deep Black (#050505) and Luxury Red (#FF003C) palette.
"""

GLOBAL_CSS = """
<style>
/* ── Reset & Base ─────────────────────────────────────────── */
.stApp {
    background-color: #050505 !important;
    background-image:
      radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255, 0, 60, 0.08) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 85% 90%, rgba(193, 18, 31, 0.05) 0%, transparent 50%) !important;
}

#MainMenu, footer, header { visibility: hidden; height: 0; }
.stDeployButton { display: none !important; }

/* ── Custom Scrollbar ─────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #050505; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #FF003C; }

/* ── Typography ───────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
}
p, li, span, label { color: #B3B3B3; font-size: 14px; }

/* ── KPI Cards ────────────────────────────────────────────── */
.kpi-card {
    background: #181818;
    border: 1px solid #2A2A2A;
    border-radius: 18px;
    padding: 22px 20px;
    text-align: center;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.kpi-card:hover {
    border-color: #3D3D3D;
    transform: translateY(-3px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.6), 0 0 20px rgba(255,0,60,0.12);
}
.kpi-value {
    font-size: 36px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.04em;
    line-height: 1.1;
}
.kpi-label {
    font-size: 11px;
    font-weight: 700;
    color: #666666;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: .08em;
}

/* ── Content Cards ────────────────────────────────────────── */
.content-card {
    background: #181818;
    border: 1px solid #2A2A2A;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.35);
    transition: all 0.2s ease;
}
.content-card:hover { border-color: #3D3D3D; }

/* ── Chat Bubbles ─────────────────────────────────────────── */
.chat-user {
    background: linear-gradient(135deg, #FF003C 0%, #C1121F 100%);
    color: #FFFFFF !important;
    padding: 14px 18px;
    border-radius: 20px 20px 4px 20px;
    margin: 10px 0 10px auto;
    max-width: 80%;
    font-size: 14px;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(255,0,60,0.25);
}
.chat-assistant {
    background: #181818;
    border: 1px solid #2A2A2A;
    color: #FFFFFF;
    padding: 18px 20px;
    border-radius: 4px 20px 20px 20px;
    margin: 10px 0;
    max-width: 88%;
    font-size: 14px;
    line-height: 1.7;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}

/* ── Badges ───────────────────────────────────────────────── */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}
.badge-blue   { background: rgba(255,0,60,0.12); color: #FF003C; border: 1px solid rgba(255,0,60,0.3); }
.badge-green  { background: rgba(0,200,83,0.12); color: #00C853; border: 1px solid rgba(0,200,83,0.3); }
.badge-red    { background: rgba(244,67,54,0.12); color: #F44336; border: 1px solid rgba(244,67,54,0.3); }
.badge-orange { background: rgba(255,193,7,0.12); color: #FFC107; border: 1px solid rgba(255,193,7,0.3); }
.badge-purple { background: rgba(193,18,31,0.15); color: #FF335F; border: 1px solid rgba(193,18,31,0.35); }

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    background: #FF003C !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 16px rgba(255,0,60,0.35) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stButton > button:hover {
    background: #FF335F !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(255,0,60,0.5) !important;
}

/* ── File Upload Zone ─────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #2A2A2A !important;
    border-radius: 18px !important;
    padding: 24px !important;
    background: #111111 !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: #FF003C !important;
    box-shadow: 0 0 30px rgba(255,0,60,0.15);
}

/* ── Page Header ──────────────────────────────────────────── */
.page-header {
    border-bottom: 1px solid #2A2A2A;
    padding-bottom: 18px;
    margin-bottom: 24px;
}
.page-header h1 { font-size: 28px; margin: 0; }
.page-header p  { color: #B3B3B3; font-size: 13px; margin: 4px 0 0; }

.custom-divider {
    border: none;
    border-top: 1px solid #2A2A2A;
    margin: 24px 0;
}
</style>
"""

def inject_css() -> str:
    """Return the global CSS block."""
    return GLOBAL_CSS
