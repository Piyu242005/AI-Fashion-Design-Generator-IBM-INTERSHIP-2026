"""
Design System — AI-Powered Study Buddy (Luxury AI SaaS Design)
===============================================================
A token-driven, premium AI platform design system.
Adheres strictly to Minimal, Functional, Premium, Accessible, AI-first principles.

Brand Personality: Luxury, Intelligent, Focused, Professional, Confident, Modern, Minimal, AI Native
"""

from __future__ import annotations
import streamlit as st

# Design Tokens (Strictly enforcing consistency)
THEMES: dict[str, dict[str, str]] = {
    "Luxury Dark": {
        "primary": "#050505",       # Core app background
        "secondary": "#111111",     # Sidebars, deeper panels
        "surface": "#181818",       # Default card background
        "surface_hover": "#1F1F1F", # Card hover background
        "accent": "#FF003C",        # Primary CTA, active states
        "accent_hover": "#FF335F",  # Hover for accent
        "accent_pressed": "#C1121F",# Pressed/Active state for accent
        "border": "#2A2A2A",        # Default border
        "border_hover": "#3D3D3D",  # Stronger border on hover
        "text_primary": "#FFFFFF",  # Main text
        "text_secondary": "#B3B3B3",# Supporting text
        "text_disabled": "#666666", # Disabled states
        "success": "#00C853",       # Positive states
        "warning": "#FFC107",       # Caution
        "danger": "#F44336",        # Destructive
        "radius": "16px",           # Consistent border radius
        "radius_sm": "8px",         # Smaller elements
        "shadow": "0 4px 20px rgba(0,0,0,0.4)",
        "shadow_hover": "0 8px 30px rgba(0,0,0,0.6)",
        "blur": "12px",             # Glassmorphism backdrop blur
    }
}

THEMES["Dark"] = THEMES["Luxury Dark"]
THEMES["System"] = THEMES["Luxury Dark"]

def get_theme_css(theme_name: str = "Luxury Dark") -> str:
    """Generate comprehensive CSS injection block."""
    t = THEMES.get(theme_name, THEMES["Luxury Dark"])
    
    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════
   PREMIUM AI SAAS THEME (TOKEN-DRIVEN)
   ═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
  /* Colors */
  --primary:        {t["primary"]};
  --secondary:      {t["secondary"]};
  --surface:        {t["surface"]};
  --surface-hover:  {t["surface_hover"]};
  --accent:         {t["accent"]};
  --accent-hover:   {t["accent_hover"]};
  --accent-pressed: {t["accent_pressed"]};
  --border:         {t["border"]};
  --border-hover:   {t["border_hover"]};
  --text-primary:   {t["text_primary"]};
  --text-secondary: {t["text_secondary"]};
  --text-disabled:  {t["text_disabled"]};
  --success:        {t["success"]};
  --warning:        {t["warning"]};
  --danger:         {t["danger"]};
  
  /* Geometry & Effects */
  --radius:         {t["radius"]};
  --radius-sm:      {t["radius_sm"]};
  --shadow:         {t["shadow"]};
  --shadow-hover:   {t["shadow_hover"]};
  --blur:           {t["blur"]};
  
  /* Motion Tokens */
  --duration-fast:  150ms;
  --duration-med:   200ms;
  --duration-slow:  300ms;
  --duration-xslow: 500ms;
  --ease-out:       cubic-bezier(0, 0, 0.2, 1);
  --ease-spring:    cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-in-out:    cubic-bezier(0.4, 0, 0.2, 1);
  --hover-scale:    1.02;
  --card-lift:      -4px;
}}

/* ── App Canvas ────────────────────────────────────────────── */
.stApp {{
  background-color: var(--primary) !important;
  font-family: 'Inter', -apple-system, sans-serif !important;
  color: var(--text-primary) !important;
}}

/* ── Typography ────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {{
  font-family: 'Inter', sans-serif !important;
  color: var(--text-primary) !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
}}

p, span, li, label {{
  color: var(--text-secondary) !important;
  font-size: 14px;
  line-height: 1.6;
}}

strong {{ color: var(--text-primary) !important; font-weight: 600; }}

/* ── Native Streamlit Overrides ────────────────────────────── */

/* Buttons - States: Default, Hover, Pressed, Disabled */
.stButton > button {{
  background: var(--accent) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 10px 20px !important;
  transition: all var(--duration-med) var(--ease-out) !important;
  box-shadow: 0 2px 10px rgba(255, 0, 60, 0.2) !important;
}}

.stButton > button:hover {{
  background: var(--accent-hover) !important;
  transform: scale(var(--hover-scale)) !important;
  box-shadow: 0 4px 14px rgba(255, 0, 60, 0.3) !important;
}}

.stButton > button:active {{
  background: var(--accent-pressed) !important;
  transform: scale(0.98) !important;
}}

.stButton > button:disabled {{
  background: var(--surface) !important;
  color: var(--text-disabled) !important;
  border: 1px solid var(--border) !important;
  box-shadow: none !important;
  transform: none !important;
  cursor: not-allowed !important;
}}

/* Inputs - States: Default, Hover, Focus */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {{
  background: var(--secondary) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-size: 14px !important;
  transition: all var(--duration-fast) var(--ease-out) !important;
}}

.stTextInput input:hover, .stTextArea textarea:hover {{
  border-color: var(--border-hover) !important;
}}

.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(255,0,60,0.15) !important;
  background: var(--primary) !important;
}}

/* Checkbox & Radio */
.stRadio label, .stCheckbox label {{
  color: var(--text-primary) !important;
  font-weight: 500 !important;
}}

/* ── Custom Component Classes ──────────────────────────────── */

/* Glassmorphism Card */
.content-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
  transition: all var(--duration-med) var(--ease-out);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
}}

.content-card:hover {{
  background: var(--surface-hover);
  border-color: var(--border-hover);
  transform: translateY(var(--card-lift));
  box-shadow: var(--shadow-hover);
}}

/* KPI Card */
.kpi-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  text-align: left;
  transition: all var(--duration-med) var(--ease-out);
  box-shadow: var(--shadow);
  backdrop-filter: blur(var(--blur));
  -webkit-backdrop-filter: blur(var(--blur));
}}

.kpi-card:hover {{
  background: var(--surface-hover);
  border-color: var(--border-hover);
  transform: translateY(var(--card-lift));
  box-shadow: var(--shadow-hover);
}}

.kpi-value {{
  font-size: 32px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
  margin-top: 8px;
}}

.kpi-label {{
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}}

/* Badges */
.badge {{
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  border: 1px solid transparent;
}}

.badge-primary {{ background: rgba(255,0,60,0.1); color: var(--accent); border-color: rgba(255,0,60,0.2); }}
.badge-success {{ background: rgba(0,200,83,0.1); color: var(--success); border-color: rgba(0,200,83,0.2); }}
.badge-warning {{ background: rgba(255,193,7,0.1); color: var(--warning); border-color: rgba(255,193,7,0.2); }}
.badge-danger {{ background: rgba(244,67,54,0.1); color: var(--danger); border-color: rgba(244,67,54,0.2); }}

/* Skeletons (Loading States) */
.skeleton {{
  background: linear-gradient(90deg, var(--surface) 25%, var(--border) 50%, var(--surface) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}}

@keyframes shimmer {{
  0% {{ background-position: -200% 0; }}
  100% {{ background-position: 200% 0; }}
}}

/* Animations */
@keyframes fadeIn {{
  from {{ opacity: 0; }}
  to   {{ opacity: 1; }}
}}

@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

.animate-fade-in {{
  animation: fadeIn var(--duration-slow) var(--ease-out) forwards;
}}

.animate-fade-in-up {{
  animation: fadeInUp var(--duration-med) var(--ease-out) forwards;
}}

/* ── Progress Track ────────────────────────────────────────── */
.progress-bar-bg {{
  background: var(--border);
  border-radius: 999px;
  height: 6px;
  width: 100%;
  margin: 8px 0;
  overflow: hidden;
}}

.progress-bar-fill {{
  background: var(--accent);
  border-radius: 999px;
  height: 100%;
  transition: width var(--duration-xslow) var(--ease-in-out);
}}

/* ── Divider ───────────────────────────────────────────────── */
.custom-divider {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 32px 0;
}}

/* ── Scrollbars & Utilities ────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 999px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--border-hover); }}

/* Hide deploy button and extra headers */
#MainMenu, footer, header {{ visibility: hidden; height: 0; }}
.stDeployButton {{ display: none !important; }}
div[data-testid="stDecoration"] {{ display: none !important; }}

</style>
"""

def inject_theme(theme_name: str = "Luxury Dark") -> None:
    """Inject custom styles into the active Streamlit app view."""
    st.markdown(get_theme_css(theme_name), unsafe_allow_html=True)
