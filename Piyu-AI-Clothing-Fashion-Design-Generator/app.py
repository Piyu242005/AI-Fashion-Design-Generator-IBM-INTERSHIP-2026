"""
app.py
------
Streamlit web interface — Piyu AI Clothing Fashion Design Generator.
Premium dark-tech UI with animated GIF hero, glassmorphism cards,
custom step badges, and progress pipeline visualisation.

Running
-------
    streamlit run app.py

Secrets (Streamlit Cloud / .streamlit/secrets.toml)
----------------------------------------------------
    HF_TOKEN     Hugging Face token (required for private/gated repos).
                 Set in Streamlit secrets — never hard-code in source.

Environment variables (local / Colab fallback)
----------------------------------------------
    HF_TOKEN     Falls back to os.environ if not in st.secrets
    HF_REPO_ID   Override model repo (default: Piyu2420/AI-Fashion-Design-Generator-IBM-INTERSHIP-2026)
    MODEL_DIR    Local weight cache root (default: project root)
"""

from __future__ import annotations

import base64
import io
import logging
import os
import sys
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

# ─── Python version guard ─────────────────────────────────────────────────
# Requires Python 3.10+.  Python 3.9 and below are not supported.
# Python 3.10, 3.11, 3.12 all work — auto1111sdk was removed.
_py = sys.version_info
if _py < (3, 10):
    st.error(
        f"⛔ **Python {_py.major}.{_py.minor} is not supported.**\n\n"
        "This project requires **Python 3.10 or newer**.\n\n"
        "Please upgrade your Python environment and re-run:"
        "```\n"
        "conda create -n fashion python=3.11\n"
        "conda activate fashion\n"
        "pip install -r requirements.txt\n"
        "streamlit run app.py\n"
        "```"
    )
    st.stop()

# ─── Inject HF_TOKEN from Streamlit secrets into os.environ so that
#     src/model_manager.py (which reads os.getenv) picks it up regardless
#     of whether we are on Streamlit Cloud or running locally. ──────────
try:
    if "HF_TOKEN" in st.secrets and not os.environ.get("HF_TOKEN"):
        os.environ["HF_TOKEN"] = st.secrets["HF_TOKEN"]
except Exception:
    pass  # st.secrets not available in local runs — .env / shell export used instead

# ─── Page config — MUST be first Streamlit call ───────────────────────────
st.set_page_config(
    page_title="Piyu AI Fashion Generator",
    page_icon="🪡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Piyu242005/Piyu-AI-clothing-fashion-design-generator",
        "About": "Piyu AI Clothing Fashion Design Generator — RealVisXL · SAM · IDM-VTON",
    },
)

log = logging.getLogger(__name__)

# ─── Asset path ───────────────────────────────────────────────────────────
ASSETS_DIR = Path(__file__).parent / "assets"
GIF_PATH   = ASSETS_DIR / "hero.gif"


# ─── Inject global CSS ────────────────────────────────────────────────────
def _inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Google Font ── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Root palette ── */
        :root {
            --bg-base:       #0a0d14;
            --bg-surface:    #111520;
            --bg-card:       #151929;
            --bg-card-hover: #1b2035;
            --border:        rgba(255,255,255,0.07);
            --border-glow:   rgba(99,179,237,0.35);
            --accent-blue:   #63b3ed;
            --accent-purple: #9f7aea;
            --accent-pink:   #f687b3;
            --accent-green:  #68d391;
            --text-primary:  #f0f4ff;
            --text-muted:    #8892a4;
            --text-dim:      #4a5568;
            --radius-lg:     16px;
            --radius-md:     10px;
            --radius-sm:     6px;
        }

        /* ── Global reset ── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        .stApp {
            background: var(--bg-base) !important;
        }

        /* ── Hide default Streamlit chrome ── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        .stDeployButton { display: none; }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1117 0%, #111827 100%) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        [data-testid="stSidebarNav"] { display: none; }

        /* ── Main content padding ── */
        .main .block-container {
            padding: 0 2rem 3rem 2rem !important;
            max-width: 1400px !important;
        }

        /* ── Hero section ── */
        .hero-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2.5rem;
            padding: 2.5rem 0 1.5rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        .hero-text { flex: 1; }
        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(99,179,237,0.1);
            border: 1px solid rgba(99,179,237,0.3);
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: var(--accent-blue) !important;
            margin-bottom: 1rem;
        }
        .hero-title {
            font-size: clamp(1.9rem, 3.5vw, 2.8rem);
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.03em;
            color: var(--text-primary) !important;
            margin: 0 0 0.75rem 0;
        }
        .hero-title span {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero-subtitle {
            font-size: 0.95rem;
            color: var(--text-muted) !important;
            line-height: 1.7;
            max-width: 520px;
            margin: 0 0 1.5rem 0;
        }
        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 0.5rem;
        }
        .hero-badge {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 500;
            color: var(--text-muted) !important;
        }
        .hero-gif {
            flex: 0 0 320px;
            max-width: 320px;
        }
        .hero-gif img {
            width: 100%;
            border-radius: var(--radius-lg);
            filter: drop-shadow(0 0 40px rgba(99,179,237,0.18));
        }

        /* ── Pipeline step strip ── */
        .pipeline-strip {
            display: flex;
            align-items: center;
            gap: 0;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 0;
            margin-bottom: 2rem;
            overflow: hidden;
        }
        .pipe-step {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 13px 12px;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-dim) !important;
            border-right: 1px solid var(--border);
            transition: background 0.2s;
            cursor: default;
            letter-spacing: 0.02em;
        }
        .pipe-step:last-child { border-right: none; }
        .pipe-step.active {
            background: rgba(99,179,237,0.08);
            color: var(--accent-blue) !important;
        }
        .pipe-step.done {
            background: rgba(104,211,145,0.06);
            color: var(--accent-green) !important;
        }
        .pipe-num {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 700;
            background: rgba(255,255,255,0.07);
            color: inherit !important;
            flex-shrink: 0;
        }
        .pipe-step.active .pipe-num { background: var(--accent-blue); color: #0a0d14 !important; }
        .pipe-step.done .pipe-num   { background: var(--accent-green); color: #0a0d14 !important; }

        /* ── Section cards ── */
        .section-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.25rem;
            transition: border-color 0.2s, background 0.2s;
        }
        .section-card:hover { border-color: var(--border-glow); }
        .section-card:focus-within { border-color: var(--border-glow); }

        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 1rem;
        }
        .step-badge {
            width: 30px;
            height: 30px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: 700;
            flex-shrink: 0;
        }
        .badge-blue   { background: rgba(99,179,237,0.15);  color: var(--accent-blue)   !important; border: 1px solid rgba(99,179,237,0.3); }
        .badge-purple { background: rgba(159,122,234,0.15); color: var(--accent-purple) !important; border: 1px solid rgba(159,122,234,0.3); }
        .badge-pink   { background: rgba(246,135,179,0.15); color: var(--accent-pink)   !important; border: 1px solid rgba(246,135,179,0.3); }
        .badge-green  { background: rgba(104,211,145,0.15); color: var(--accent-green)  !important; border: 1px solid rgba(104,211,145,0.3); }

        .card-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary) !important;
            letter-spacing: -0.01em;
            margin: 0;
        }
        .card-hint {
            font-size: 0.78rem;
            color: var(--text-muted) !important;
            margin-top: 2px;
        }

        /* ── Output panel ── */
        .output-panel {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            min-height: 540px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            position: sticky;
            top: 1rem;
        }
        .output-empty {
            text-align: center;
        }
        .output-empty-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            opacity: 0.25;
            filter: grayscale(1);
        }
        .output-empty-title {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-dim) !important;
            margin-bottom: 0.4rem;
        }
        .output-empty-sub {
            font-size: 0.8rem;
            color: var(--text-dim) !important;
        }
        .output-label {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            color: var(--text-muted) !important;
            margin-bottom: 1rem;
            align-self: flex-start;
        }

        /* ── Streamlit widget overrides ── */
        /* Text area */
        .stTextArea textarea {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-size: 0.9rem !important;
            transition: border-color 0.2s !important;
        }
        .stTextArea textarea:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 3px rgba(99,179,237,0.12) !important;
        }

        /* Text input */
        .stTextInput input {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-md) !important;
            color: var(--text-primary) !important;
            font-size: 0.88rem !important;
            font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
            transition: border-color 0.2s !important;
        }
        .stTextInput input:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 3px rgba(99,179,237,0.12) !important;
        }

        /* File uploader */
        [data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.02) !important;
            border: 1.5px dashed rgba(255,255,255,0.1) !important;
            border-radius: var(--radius-md) !important;
            transition: border-color 0.2s, background 0.2s !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(99,179,237,0.4) !important;
            background: rgba(99,179,237,0.03) !important;
        }

        /* Primary action button */
        .stButton > button[kind="primary"],
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
            border: none !important;
            border-radius: var(--radius-md) !important;
            color: #fff !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.02em !important;
            padding: 0.6rem 1.5rem !important;
            transition: opacity 0.15s, transform 0.12s, box-shadow 0.15s !important;
            box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
        }
        .stButton > button:hover {
            opacity: 0.92 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 24px rgba(99,102,241,0.4) !important;
        }
        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* Download button */
        [data-testid="stDownloadButton"] > button {
            background: rgba(104,211,145,0.1) !important;
            border: 1px solid rgba(104,211,145,0.35) !important;
            color: var(--accent-green) !important;
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            box-shadow: none !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
            background: rgba(104,211,145,0.18) !important;
            transform: translateY(-1px) !important;
        }

        /* Slider */
        [data-testid="stSlider"] > div > div > div > div {
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)) !important;
        }
        [data-testid="stSlider"] [aria-valuenow] {
            background: var(--accent-blue) !important;
            border-color: var(--accent-blue) !important;
        }

        /* Radio */
        .stRadio [data-testid="stMarkdownContainer"] p {
            color: var(--text-primary) !important;
        }
        .stRadio label { cursor: pointer !important; }

        /* Number input */
        .stNumberInput input {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
        }

        /* Spinner */
        .stSpinner > div { border-top-color: var(--accent-blue) !important; }

        /* Alerts */
        .stAlert {
            border-radius: var(--radius-md) !important;
            border: none !important;
            font-size: 0.85rem !important;
        }
        .stSuccess { background: rgba(104,211,145,0.08) !important; color: var(--accent-green) !important; }
        .stError   { background: rgba(252,129,129,0.08) !important; color: #fc8181 !important; }
        .stInfo    { background: rgba(99,179,237,0.08) !important;  color: var(--accent-blue) !important; }

        /* st.image */
        [data-testid="stImage"] img {
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border) !important;
        }

        /* Caption / small text */
        .stCaption, [data-testid="stCaptionContainer"] {
            color: var(--text-muted) !important;
            font-size: 0.78rem !important;
        }

        /* Divider */
        hr { border-color: var(--border) !important; margin: 0.5rem 0 !important; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

        /* Sidebar mode selector label */
        .sidebar-mode-label {
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: var(--text-muted) !important;
            margin-bottom: 0.5rem;
            display: block;
        }

        /* Stat chips in sidebar */
        .stat-row {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
            margin: 0.75rem 0;
        }
        .stat-chip {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 10px;
            font-weight: 600;
            color: var(--text-muted) !important;
            letter-spacing: 0.3px;
        }
        .stat-chip span { color: var(--text-primary) !important; margin-left: 3px; }

        /* Column layout fix */
        [data-testid="column"] { padding: 0 0.6rem !important; }
        [data-testid="column"]:first-child { padding-left: 0 !important; }
        [data-testid="column"]:last-child  { padding-right: 0 !important; }

        /* Label overrides */
        label, .stLabel, [data-testid="stWidgetLabel"] p {
            color: var(--text-muted) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }

        /* Mode tabs look */
        .mode-tab-row {
            display: flex;
            gap: 8px;
            margin-bottom: 1.5rem;
        }
        .mode-tab {
            flex: 1;
            padding: 10px 14px;
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            background: var(--bg-surface);
            text-align: center;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-muted) !important;
            cursor: pointer;
            transition: all 0.18s;
        }
        .mode-tab.selected {
            background: rgba(99,179,237,0.08);
            border-color: rgba(99,179,237,0.35);
            color: var(--accent-blue) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─── Utility: load GIF as base64 ──────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _gif_b64(path: Path) -> str | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    return base64.b64encode(data).decode()


# ─── Cached model loaders ─────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading RealVisXL generation pipeline…")
def load_generation_pipeline():
    """Load RealVisXL via Diffusers from_single_file — no auto1111sdk needed."""
    import gc
    import torch
    from diffusers import DPMSolverSinglestepScheduler, StableDiffusionXLPipeline
    from src.model_manager import get_realvisxl_path

    model_path = get_realvisxl_path()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32

    pipe = StableDiffusionXLPipeline.from_single_file(
        model_path,
        config="stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=dtype,
        use_safetensors=True,
        safety_checker=None,
        ignore_mismatched_sizes=True,
    )
    try:
        pipe.scheduler = DPMSolverSinglestepScheduler.from_config(
            pipe.scheduler.config,
            use_karras_sigmas=True,
        )
    except Exception:
        pass

    pipe.enable_vae_slicing()
    pipe.enable_vae_tiling()
    if device == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)
    return pipe


@st.cache_resource(show_spinner="Loading SAM ViT-H…")
def load_sam_predictor():
    from src.model_manager import get_sam_path
    from segment_anything import SamPredictor, sam_model_registry
    sam = sam_model_registry["vit_h"](checkpoint=get_sam_path())
    sam.to(device="cuda")
    return SamPredictor(sam)


@st.cache_resource(show_spinner="Loading IDM-VTON pipeline…")
def load_tryon_pipeline():
    import sys
    sys.path.insert(0, "idm_vton")
    from try_on import pipe as tryon_pipe
    return tryon_pipe


# ─── Inference helpers ────────────────────────────────────────────────────
def run_sam_headless(predictor, image: Image.Image, points: list) -> Image.Image:
    import cv2 as _cv2
    arr = np.array(image.convert("RGB"))
    arr = _cv2.cvtColor(arr, _cv2.COLOR_RGB2BGR)
    arr = _cv2.cvtColor(arr, _cv2.COLOR_BGR2RGB)
    predictor.set_image(arr)
    input_point = np.array(points[:3])
    input_label = np.array([1, 1, 1])
    _, scores, logits = predictor.predict(
        point_coords=input_point, point_labels=input_label, multimask_output=True
    )
    mask_input = logits[np.argmax(scores), :, :]
    masks, _, _ = predictor.predict(
        point_coords=input_point, point_labels=input_label,
        mask_input=mask_input[None, :, :], multimask_output=False,
    )
    return Image.fromarray((masks[0].astype(np.uint8) * 255))


def generate_human_model(pipe, clothing_description: str) -> Image.Image:
    """Generate a fashion model image using the Diffusers SDXL pipeline."""
    import gc
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device="cpu").manual_seed(42)

    result = pipe(
        prompt=(
            f"centered, portrait photo of a woman, wearing {clothing_description}, "
            "natural skin, photorealistic, high detail clothing, realistic fabric, "
            "studio fashion photography, neutral background, sharp focus"
        ),
        negative_prompt=(
            "low quality, blurry, deformed, bad anatomy, bad hands, "
            "extra fingers, fused fingers, distorted face, duplicate, "
            "cropped head, text, watermark, cartoon, illustration, nsfw"
        ),
        height=1024,
        width=768,
        num_inference_steps=4,
        guidance_scale=0.0,
        generator=generator,
    )
    image = result.images[0]

    # Free VRAM so SAM can load
    del result
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return image


def run_tryon(human_image, mask_image, garment_image, cloth_type, denoise_steps=30, seed=42):
    import sys
    sys.path.insert(0, "idm_vton")
    from try_on import start_tryon
    result, _ = start_tryon(
        human_img_orig=human_image, mask_image=mask_image, garm_img=garment_image,
        garment_des=cloth_type, is_checked=False, is_checked_crop=False,
        denoise_steps=denoise_steps, seed=seed,
    )
    return result


def _parse_points(raw: str) -> list:
    vals = [int(v.strip()) for v in raw.split(",")]
    if len(vals) != 6:
        raise ValueError("Enter exactly 6 comma-separated integers (3 x,y pairs).")
    return [(vals[i], vals[i + 1]) for i in range(0, 6, 2)]


def _img_download_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════════════════════════════════════
_inject_css()

# ─── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0;">
            <div style="font-size:1.15rem; font-weight:800; color:#f0f4ff; letter-spacing:-0.02em;">
                🪡 Piyu AI Fashion
            </div>
            <div style="font-size:0.72rem; color:#8892a4; margin-top:3px; letter-spacing:0.3px;">
                AI Clothing Fashion Design Generator
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr style="border-color:rgba(255,255,255,0.07); margin:0 0 1rem 0;">', unsafe_allow_html=True)

    # Model info chips
    st.markdown(
        """
        <div class="stat-row">
            <div class="stat-chip">RealVisXL<span>v4.0</span></div>
            <div class="stat-chip">SAM<span>ViT-H</span></div>
            <div class="stat-chip">IDM-VTON<span>SDXL</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr style="border-color:rgba(255,255,255,0.07); margin:0.75rem 0;">', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-mode-label">Pipeline mode</span>', unsafe_allow_html=True)
    mode = st.radio(
        "Pipeline mode",
        options=["Generate & Try-On", "Try-On Only"],
        label_visibility="collapsed",
        help=(
            "**Generate & Try-On** — Text prompt → AI model → segment → apply garment.\n\n"
            "**Try-On Only** — Upload a person photo, apply a garment directly."
        ),
    )

    st.markdown('<hr style="border-color:rgba(255,255,255,0.07); margin:0.75rem 0;">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px; font-weight:700; letter-spacing:1.2px; '
        'text-transform:uppercase; color:#8892a4; margin-bottom:0.75rem;">Try-On Settings</div>',
        unsafe_allow_html=True,
    )
    denoise_steps = st.slider("Denoising steps", min_value=10, max_value=50, value=30, step=5)
    seed = st.number_input("Seed", min_value=0, max_value=999999, value=42)

    st.markdown('<hr style="border-color:rgba(255,255,255,0.07); margin:0.75rem 0 1rem 0;">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:0.7rem; color:#4a5568; line-height:1.6;">
            <strong style="color:#8892a4;">License notice</strong><br>
            IDM-VTON is <strong>CC BY-NC-SA 4.0</strong> — non-commercial only.<br>
            RealVisXL: CivitAI / Stability AI community terms.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Hero ─────────────────────────────────────────────────────────────────
gif_b64 = _gif_b64(GIF_PATH)
gif_html = (
    f'<img src="data:image/gif;base64,{gif_b64}" alt="AI Fashion Hero" />'
    if gif_b64
    else '<div style="width:320px;height:260px;background:rgba(255,255,255,0.03);border-radius:16px;"></div>'
)

st.markdown(
    f"""
    <div class="hero-wrapper">
        <div class="hero-text">
            <div class="hero-tag">✦ Generative AI · Computer Vision</div>
            <h1 class="hero-title">AI Clothing<br><span>Fashion Design</span><br>Generator</h1>
            <p class="hero-subtitle">
                Generate photorealistic fashion models from text, segment clothing regions
                with SAM, and apply new garments with IDM-VTON — end-to-end in minutes.
            </p>
            <div class="hero-badges">
                <span class="hero-badge">RealVisXL V4.0 Lightning</span>
                <span class="hero-badge">Segment Anything ViT-H</span>
                <span class="hero-badge">IDM-VTON SDXL</span>
                <span class="hero-badge">768 × 1024</span>
                <span class="hero-badge">float16</span>
            </div>
        </div>
        <div class="hero-gif">{gif_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Pipeline strip ───────────────────────────────────────────────────────
step_state = st.session_state.get("_pipeline_step", 0)

def _pipe_cls(n: int) -> str:
    if step_state > n:  return "pipe-step done"
    if step_state == n: return "pipe-step active"
    return "pipe-step"

def _pipe_num(n: int) -> str:
    if step_state > n: return "✓"
    return str(n + 1)

st.markdown(
    f"""
    <div class="pipeline-strip">
        <div class="{_pipe_cls(0)}">
            <span class="pipe-num">{_pipe_num(0)}</span>Describe Clothing
        </div>
        <div class="{_pipe_cls(1)}">
            <span class="pipe-num">{_pipe_num(1)}</span>Upload Garment
        </div>
        <div class="{_pipe_cls(2)}">
            <span class="pipe-num">{_pipe_num(2)}</span>Generate Model
        </div>
        <div class="{_pipe_cls(3)}">
            <span class="pipe-num">{_pipe_num(3)}</span>Segment Region
        </div>
        <div class="{_pipe_cls(4)}">
            <span class="pipe-num">{_pipe_num(4)}</span>Virtual Try-On
        </div>
        <div class="{_pipe_cls(5)}">
            <span class="pipe-num">{_pipe_num(5)}</span>Download Result
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════
#  MODE 1 — GENERATE & TRY-ON
# ══════════════════════════════════════════════════════════════════════════
if mode == "Generate & Try-On":

    col_inputs, col_output = st.columns([1.05, 0.95], gap="large")

    # ── Left: inputs ──────────────────────────────────────────────────────
    with col_inputs:

        # Step 1
        st.markdown(
            """
            <div class="section-card">
                <div class="card-header">
                    <div class="step-badge badge-blue">1</div>
                    <div>
                        <div class="card-title">Describe the clothing style</div>
                        <div class="card-hint">Describe what the model should wear</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        prompt = st.text_area(
            "Clothing description",
            placeholder="e.g. a red crop top with high-waist denim jeans",
            height=88,
            label_visibility="collapsed",
        )

        # Step 2
        st.markdown(
            """
            <div class="section-card" style="margin-top:0.25rem;">
                <div class="card-header">
                    <div class="step-badge badge-purple">2</div>
                    <div>
                        <div class="card-title">Upload garment image</div>
                        <div class="card-hint">Flat-lay or mannequin photo works best</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        garment_file = st.file_uploader(
            "Garment", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )
        if garment_file:
            st.image(Image.open(garment_file), width=160, caption="Garment preview")

        # Step 3
        st.markdown(
            """
            <div class="section-card" style="margin-top:0.25rem;">
                <div class="card-header">
                    <div class="step-badge badge-pink">3</div>
                    <div>
                        <div class="card-title">Segmentation coordinates</div>
                        <div class="card-hint">Three x,y pixel points on the clothing region</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "After generating the model, inspect the image and enter three pixel coordinates "
            "on the clothing area you want to replace — format: `x1,y1,x2,y2,x3,y3`"
        )
        points_input = st.text_input(
            "Coordinates",
            placeholder="384,300,400,450,360,500",
            label_visibility="collapsed",
        )

        # Action buttons
        st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            generate_btn = st.button("⚡  Generate Model", use_container_width=True)
        with btn_col2:
            tryon_btn = st.button("✨  Apply Garment", use_container_width=True)

    # ── Right: output ─────────────────────────────────────────────────────
    with col_output:
        has_model  = "model_image" in st.session_state
        has_result = "result_image_m1" in st.session_state

        if not has_model and not has_result:
            st.markdown(
                """
                <div class="output-panel">
                    <div class="output-empty">
                        <div class="output-empty-icon">🖼️</div>
                        <div class="output-empty-title">Output appears here</div>
                        <div class="output-empty-sub">Generate a model or apply a garment<br>to see your result</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="output-label">Result</div>', unsafe_allow_html=True)
            if has_result:
                st.image(
                    st.session_state["result_image_m1"],
                    caption="Virtual try-on result",
                    use_container_width=True,
                )
                st.download_button(
                    "⬇  Download Result",
                    data=_img_download_bytes(st.session_state["result_image_m1"]),
                    file_name="tryon_result.png",
                    mime="image/png",
                    use_container_width=True,
                )
            elif has_model:
                st.image(
                    st.session_state["model_image"],
                    caption="Generated model — note pixel coordinates for segmentation",
                    use_container_width=True,
                )
                st.info("Model ready. Enter segmentation coordinates and upload a garment, then click **Apply Garment**.")

    # ── Logic ─────────────────────────────────────────────────────────────
    if generate_btn:
        if not prompt.strip():
            st.error("Please enter a clothing description.")
        else:
            with st.spinner("Generating fashion model with RealVisXL…"):
                gen_pipe = load_generation_pipeline()
                img = generate_human_model(gen_pipe, prompt)
                st.session_state["model_image"] = img
                st.session_state.pop("result_image_m1", None)
                st.session_state["_pipeline_step"] = 2
            st.rerun()

    if tryon_btn:
        model_image = st.session_state.get("model_image")
        errors = []
        if model_image is None:        errors.append("Generate a model first.")
        if garment_file is None:       errors.append("Upload a garment image.")
        if not points_input.strip():   errors.append("Enter segmentation coordinates.")
        if errors:
            for e in errors: st.error(e)
        else:
            try:
                points = _parse_points(points_input)
            except ValueError as e:
                st.error(str(e))
                st.stop()

            garment_image = Image.open(garment_file).convert("RGB")

            with st.spinner("Running SAM segmentation…"):
                predictor = load_sam_predictor()
                mask = run_sam_headless(predictor, model_image, points)
                st.session_state["_pipeline_step"] = 3

            with st.spinner("Running IDM-VTON virtual try-on (30 steps)…"):
                result = run_tryon(
                    model_image, mask, garment_image,
                    cloth_type=prompt,
                    denoise_steps=denoise_steps,
                    seed=seed,
                )
                st.session_state["result_image_m1"] = result
                st.session_state["_pipeline_step"] = 5
            st.success("Done! Your virtual try-on result is ready.")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
#  MODE 2 — TRY-ON ONLY
# ══════════════════════════════════════════════════════════════════════════
elif mode == "Try-On Only":

    col_inputs, col_output = st.columns([1.05, 0.95], gap="large")

    with col_inputs:

        # Step 1 — person photo
        st.markdown(
            """
            <div class="section-card">
                <div class="card-header">
                    <div class="step-badge badge-blue">1</div>
                    <div>
                        <div class="card-title">Upload person photo</div>
                        <div class="card-hint">Clean, well-lit portrait at 768 × 1024 works best</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        person_file = st.file_uploader(
            "Person photo", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        # Step 2 — garment
        st.markdown(
            """
            <div class="section-card" style="margin-top:0.25rem;">
                <div class="card-header">
                    <div class="step-badge badge-purple">2</div>
                    <div>
                        <div class="card-title">Upload garment image</div>
                        <div class="card-hint">Flat-lay or mannequin photo</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        garment_file2 = st.file_uploader(
            "Garment image", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="garment_tryon_only",
        )

        if person_file or garment_file2:
            p1, p2 = st.columns(2)
            if person_file:
                with p1: st.image(Image.open(person_file), caption="Person", width=140)
            if garment_file2:
                with p2: st.image(Image.open(garment_file2), caption="Garment", width=140)

        # Step 3 — cloth type
        st.markdown(
            """
            <div class="section-card" style="margin-top:0.25rem;">
                <div class="card-header">
                    <div class="step-badge badge-pink">3</div>
                    <div>
                        <div class="card-title">Garment description</div>
                        <div class="card-hint">Used in the try-on inpainting prompt</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cloth_type = st.text_input(
            "Cloth type",
            placeholder="e.g. crop top",
            label_visibility="collapsed",
        )

        # Step 4 — coordinates
        st.markdown(
            """
            <div class="section-card" style="margin-top:0.25rem;">
                <div class="card-header">
                    <div class="step-badge badge-green">4</div>
                    <div>
                        <div class="card-title">Segmentation coordinates</div>
                        <div class="card-hint">Three x,y pixel points on the clothing region</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        points_input2 = st.text_input(
            "x1,y1,x2,y2,x3,y3",
            placeholder="384,300,400,450,360,500",
            label_visibility="collapsed",
            key="pts_tryon_only",
        )

        st.markdown("<div style='height:0.25rem;'></div>", unsafe_allow_html=True)
        tryon_btn2 = st.button("✨  Apply Garment", use_container_width=True)

    with col_output:
        has_result2 = "result_image_m2" in st.session_state

        if not has_result2:
            st.markdown(
                """
                <div class="output-panel">
                    <div class="output-empty">
                        <div class="output-empty-icon">👗</div>
                        <div class="output-empty-title">Try-on result appears here</div>
                        <div class="output-empty-sub">Upload a person photo and garment,<br>then click Apply Garment</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="output-label">Result</div>', unsafe_allow_html=True)
            st.image(
                st.session_state["result_image_m2"],
                caption="Virtual try-on result",
                use_container_width=True,
            )
            st.download_button(
                "⬇  Download Result",
                data=_img_download_bytes(st.session_state["result_image_m2"]),
                file_name="tryon_result.png",
                mime="image/png",
                use_container_width=True,
            )

    if tryon_btn2:
        errors = []
        if person_file is None:      errors.append("Upload a person photo.")
        if garment_file2 is None:    errors.append("Upload a garment image.")
        if not cloth_type.strip():   errors.append("Enter a garment description.")
        if not points_input2.strip(): errors.append("Enter segmentation coordinates.")
        if errors:
            for e in errors: st.error(e)
        else:
            try:
                points = _parse_points(points_input2)
            except ValueError as e:
                st.error(str(e)); st.stop()

            person_image  = Image.open(person_file).convert("RGB")
            garment_image = Image.open(garment_file2).convert("RGB")

            with st.spinner("Running SAM segmentation…"):
                predictor = load_sam_predictor()
                mask = run_sam_headless(predictor, person_image, points)

            with st.spinner("Running IDM-VTON virtual try-on…"):
                result = run_tryon(
                    person_image, mask, garment_image,
                    cloth_type=cloth_type,
                    denoise_steps=denoise_steps,
                    seed=seed,
                )
                st.session_state["result_image_m2"] = result
                st.session_state["_pipeline_step"] = 5
            st.success("Done! Your virtual try-on result is ready.")
            st.rerun()


# ─── Footer ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        margin-top: 3rem;
        padding: 1.5rem 0 0.5rem 0;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
    ">
        <div style="font-size:0.75rem; color:#4a5568;">
            <strong style="color:#8892a4;">Piyu AI Clothing Fashion Design Generator</strong>
            &nbsp;·&nbsp; MIT License
            &nbsp;·&nbsp; IDM-VTON: CC BY-NC-SA 4.0
        </div>
        <div style="font-size:0.75rem; color:#4a5568;">
            <a href="https://github.com/Piyu242005/Piyu-AI-clothing-fashion-design-generator"
               target="_blank"
               style="color:#63b3ed; text-decoration:none; font-weight:500;">
                GitHub ↗
            </a>
            &nbsp;·&nbsp;
            <a href="https://huggingface.co/Piyu242005/piyu-fashion-models"
               target="_blank"
               style="color:#63b3ed; text-decoration:none; font-weight:500;">
                Hugging Face ↗
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
