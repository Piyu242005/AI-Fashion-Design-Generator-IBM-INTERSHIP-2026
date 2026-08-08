"""
app.py
------
Streamlit web interface for the Piyu AI Clothing Fashion Design Generator.

Architecture
------------
    GitHub (code)
        ↓
    Streamlit (this file — UI layer)
        ↓
    GPU Server (PyTorch inference — same process on a GPU machine)
        ↓
    Hugging Face (model storage — downloaded once via model_manager)

Two modes
---------
    Mode 1 — Generate & Try-On
        User provides a text prompt → RealVisXL generates a human model →
        SAM segments the clothing region (headless: user provides coordinates) →
        IDM-VTON applies the uploaded garment.

    Mode 2 — Try-On Only
        User uploads an existing person photo and a garment image →
        SAM segments the clothing region →
        IDM-VTON applies the garment.

Running
-------
    streamlit run app.py

Environment variables
---------------------
    HF_TOKEN     Hugging Face token (required for private repos)
    HF_REPO_ID   Override model repo (default: Piyu242005/piyu-fashion-models)
    MODEL_DIR    Local cache directory (default: models/)
"""

from __future__ import annotations

import io
import os
import tempfile
import logging

import numpy as np
import torch
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Piyu AI Fashion Design Generator",
    page_icon="🪡",
    layout="wide",
    initial_sidebar_state="expanded",
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cached model loading — runs once per server process, not per user click
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading AI models… this may take a few minutes on first run.")
def load_generation_pipeline():
    """Load and cache the RealVisXL generation pipeline."""
    from model_manager import get_realvisxl_path
    from auto1111sdk import StableDiffusionPipeline

    model_path = get_realvisxl_path()
    pipe = StableDiffusionPipeline(model_path, default_command_args="--device-id 0")
    return pipe


@st.cache_resource(show_spinner="Loading SAM ViT-H…")
def load_sam_predictor():
    """Load and cache SAM ViT-H on CUDA."""
    from model_manager import get_sam_path
    from segment_anything import SamPredictor, sam_model_registry

    checkpoint = get_sam_path()
    sam = sam_model_registry["vit_h"](checkpoint=checkpoint)
    sam.to(device="cuda")
    return SamPredictor(sam)


@st.cache_resource(show_spinner="Loading IDM-VTON pipeline…")
def load_tryon_pipeline():
    """
    Load and cache the full IDM-VTON pipeline.

    Note: try_on.py must be invoked from inside the idm_vton/ directory
    because it relies on relative imports (src/, utils_mask, apply_net, etc.).
    In the Streamlit context we call start_tryon() directly after ensuring
    sys.path includes the idm_vton directory.
    """
    import sys
    sys.path.insert(0, "idm_vton")

    from try_on import pipe as tryon_pipe
    return tryon_pipe


# ---------------------------------------------------------------------------
# Helper: run SAM segmentation in headless mode (no GUI)
# ---------------------------------------------------------------------------

def run_sam_headless(
    predictor,
    image: Image.Image,
    points: list[tuple[int, int]],
) -> Image.Image:
    """
    Run SAM segmentation on *image* using three (x, y) point prompts.

    Returns a binary PIL mask image (white = clothing region).
    """
    import cv2 as _cv2

    img_array = np.array(image.convert("RGB"))
    img_bgr = _cv2.cvtColor(img_array, _cv2.COLOR_RGB2BGR)
    img_rgb = _cv2.cvtColor(img_bgr, _cv2.COLOR_BGR2RGB)

    predictor.set_image(img_rgb)

    input_point = np.array(points[:3])
    input_label = np.array([1, 1, 1])

    # Pass 1 — multi-mask
    _, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    mask_input = logits[np.argmax(scores), :, :]

    # Pass 2 — refined single-mask
    masks, _, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        mask_input=mask_input[None, :, :],
        multimask_output=False,
    )

    mask_array = (masks[0].astype(np.uint8) * 255)
    return Image.fromarray(mask_array)


# ---------------------------------------------------------------------------
# Helper: generate human model image
# ---------------------------------------------------------------------------

def generate_human_model(pipe, clothing_description: str) -> Image.Image:
    import random
    prompt = (
        f"centered, portrait photo of a woman, wearing {clothing_description}, "
        "natural skin, dark shot"
    )
    negative_prompt = (
        "(octane render, render, drawing, anime, bad photo, bad photography:1.3), "
        "(worst quality, low quality, blurry:1.2), (bad teeth, deformed teeth, deformed lips), "
        "(bad anatomy, bad proportions:1.1), (deformed iris, deformed pupils), "
        "(deformed eyes, bad eyes), (deformed face, ugly face, bad face), "
        "(deformed hands, bad hands, fused fingers), morbid, mutilated, mutation, disfigured"
    )
    images = pipe.generate_txt2img(
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=1024,
        width=768,
        cfg_scale=2,
        steps=5,
        sampler_name="DPM++ SDE",
    )
    return images[0]


# ---------------------------------------------------------------------------
# Helper: run virtual try-on
# ---------------------------------------------------------------------------

def run_tryon(
    human_image: Image.Image,
    mask_image: Image.Image,
    garment_image: Image.Image,
    cloth_type: str,
    denoise_steps: int = 30,
    seed: int = 42,
) -> Image.Image:
    """Call start_tryon() from try_on.py with sensible defaults."""
    import sys
    sys.path.insert(0, "idm_vton")
    from try_on import start_tryon

    result, _ = start_tryon(
        human_img_orig=human_image,
        mask_image=mask_image,
        garm_img=garment_image,
        garment_des=cloth_type,
        is_checked=False,
        is_checked_crop=False,
        denoise_steps=denoise_steps,
        seed=seed,
    )
    return result


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🪡 Piyu AI Fashion")
    st.caption("AI Clothing Fashion Design Generator")
    st.divider()

    mode = st.radio(
        "Pipeline mode",
        options=["Generate & Try-On", "Try-On Only"],
        help=(
            "**Generate & Try-On**: Create a fashion model from a text prompt, "
            "then apply a garment.\n\n"
            "**Try-On Only**: Upload an existing person photo and apply a garment directly."
        ),
    )

    st.divider()
    st.subheader("Try-On settings")
    denoise_steps = st.slider("Denoising steps", min_value=10, max_value=50, value=30, step=5)
    seed = st.number_input("Seed", min_value=0, max_value=999999, value=42)

    st.divider()
    st.caption(
        "**License notice:** IDM-VTON is CC BY-NC-SA 4.0 — non-commercial use only. "
        "RealVisXL is subject to CivitAI / Stability AI community terms."
    )


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------

st.title("AI Clothing Fashion Design Generator")
st.caption(
    "Generate photorealistic fashion models and apply garments using "
    "RealVisXL · Segment Anything · IDM-VTON"
)
st.divider()

# ── Mode 1: Generate & Try-On ──────────────────────────────────────────────
if mode == "Generate & Try-On":

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("1. Describe the clothing")
        prompt = st.text_area(
            "Clothing description",
            placeholder="a crop top and mini skirt",
            height=80,
            label_visibility="collapsed",
        )

        st.subheader("2. Upload a garment image")
        garment_file = st.file_uploader(
            "Garment image", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        st.subheader("3. Segmentation point coordinates")
        st.caption(
            "After generating the model (Step 4), note three (x, y) pixel coordinates "
            "on the clothing region you want to replace, then enter them below. "
            "This replaces the interactive desktop GUI for server/Colab compatibility."
        )
        points_input = st.text_input(
            "x1,y1,x2,y2,x3,y3",
            placeholder="384,300,400,450,360,500",
        )

        generate_btn = st.button("Generate Model", use_container_width=True)
        tryon_btn    = st.button("Apply Garment",  use_container_width=True)

    with col_right:
        st.subheader("Output")
        output_placeholder = st.empty()

    # --- Step A: Generate human model ---
    if generate_btn:
        if not prompt.strip():
            st.error("Please enter a clothing description.")
        else:
            with st.spinner("Generating human fashion model…"):
                gen_pipe = load_generation_pipeline()
                model_image = generate_human_model(gen_pipe, prompt)
                st.session_state["model_image"] = model_image

            output_placeholder.image(
                model_image,
                caption="Generated model — note clothing pixel coordinates for segmentation",
                use_container_width=True,
            )
            st.success("Model generated. Note three (x, y) coordinates on the clothing, then click Apply Garment.")

    elif "model_image" in st.session_state:
        output_placeholder.image(
            st.session_state["model_image"],
            caption="Generated model",
            use_container_width=True,
        )

    # --- Step B: Segment + Try-On ---
    if tryon_btn:
        model_image = st.session_state.get("model_image")
        if model_image is None:
            st.error("Generate a model first.")
        elif garment_file is None:
            st.error("Upload a garment image.")
        elif not points_input.strip():
            st.error("Enter three clothing pixel coordinates (x1,y1,x2,y2,x3,y3).")
        else:
            try:
                vals = [int(v.strip()) for v in points_input.split(",")]
                if len(vals) != 6:
                    raise ValueError("Need exactly 6 integers.")
                points = [(vals[i], vals[i + 1]) for i in range(0, 6, 2)]
            except ValueError as e:
                st.error(f"Invalid coordinates: {e}")
                st.stop()

            garment_image = Image.open(garment_file).convert("RGB")

            with st.spinner("Running SAM segmentation…"):
                predictor = load_sam_predictor()
                mask = run_sam_headless(predictor, model_image, points)

            with st.spinner("Running IDM-VTON virtual try-on…"):
                result = run_tryon(
                    model_image, mask, garment_image,
                    cloth_type=prompt,
                    denoise_steps=denoise_steps,
                    seed=seed,
                )

            output_placeholder.image(result, caption="Virtual try-on result", use_container_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button(
                "Download result",
                data=buf.getvalue(),
                file_name="tryon_result.png",
                mime="image/png",
                use_container_width=True,
            )


# ── Mode 2: Try-On Only ────────────────────────────────────────────────────
elif mode == "Try-On Only":

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("1. Upload person photo")
        person_file = st.file_uploader(
            "Person photo", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        st.subheader("2. Upload garment image")
        garment_file = st.file_uploader(
            "Garment image", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="garment_tryon_only",
        )

        st.subheader("3. Cloth type / description")
        cloth_type = st.text_input(
            "Cloth type",
            placeholder="crop top",
            label_visibility="collapsed",
        )

        st.subheader("4. Segmentation point coordinates")
        st.caption(
            "View the uploaded person photo and enter three (x, y) pixel coordinates "
            "on the clothing region to replace."
        )
        points_input = st.text_input(
            "x1,y1,x2,y2,x3,y3",
            placeholder="384,300,400,450,360,500",
            key="pts_tryon_only",
        )

        tryon_btn2 = st.button("Apply Garment", use_container_width=True)

    with col_right:
        st.subheader("Preview & Output")

        if person_file:
            person_image = Image.open(person_file).convert("RGB")
            st.image(person_image, caption="Uploaded person photo", use_container_width=True)

        output_placeholder2 = st.empty()

    if tryon_btn2:
        if person_file is None:
            st.error("Upload a person photo.")
        elif garment_file is None:
            st.error("Upload a garment image.")
        elif not cloth_type.strip():
            st.error("Enter a cloth type description.")
        elif not points_input.strip():
            st.error("Enter three clothing pixel coordinates.")
        else:
            try:
                vals = [int(v.strip()) for v in points_input.split(",")]
                if len(vals) != 6:
                    raise ValueError("Need exactly 6 integers.")
                points = [(vals[i], vals[i + 1]) for i in range(0, 6, 2)]
            except ValueError as e:
                st.error(f"Invalid coordinates: {e}")
                st.stop()

            person_image  = Image.open(person_file).convert("RGB")
            garment_image = Image.open(garment_file).convert("RGB")

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

            output_placeholder2.image(result, caption="Virtual try-on result", use_container_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button(
                "Download result",
                data=buf.getvalue(),
                file_name="tryon_result.png",
                mime="image/png",
                use_container_width=True,
            )


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Piyu AI Clothing Fashion Design Generator · "
    "[GitHub](https://github.com/Piyu242005/Piyu-AI-clothing-fashion-design-generator) · "
    "MIT License · "
    "IDM-VTON: CC BY-NC-SA 4.0 (non-commercial)"
)
