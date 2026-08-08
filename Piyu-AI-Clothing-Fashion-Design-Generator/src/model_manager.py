"""
src/model_manager.py
--------------------
Downloads and caches all 9 model weight files from the project's Hugging Face
model repository.

Hugging Face repository
-----------------------
    Piyu2420/AI-Fashion-Design-Generator-IBM-INTERSHIP-2026

Repository structure expected on Hugging Face
---------------------------------------------
    realvisxl/realvisxl.safetensors
    sam/sam_vit_h_4b8939.pth
    idm_vton/densepose/model_final_162be9.pkl
    idm_vton/humanparsing/parsing_atr.onnx
    idm_vton/humanparsing/parsing_lip.onnx
    idm_vton/openpose/body_pose_model.pth
    idm_vton/image_encoder/config.json
    idm_vton/image_encoder/model.safetensors
    idm_vton/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin

Local cache layout (under project root)
----------------------------------------
    weights/realvisxl.safetensors
    weights/sam_vit_h_4b8939.pth
    idm_vton/ckpt/densepose/model_final_162be9.pkl
    idm_vton/ckpt/humanparsing/parsing_atr.onnx
    idm_vton/ckpt/humanparsing/parsing_lip.onnx
    idm_vton/ckpt/openpose/ckpts/body_pose_model.pth
    idm_vton/ckpt/image_encoder/config.json
    idm_vton/ckpt/image_encoder/model.safetensors
    idm_vton/ckpt/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin

Environment variables
---------------------
    HF_TOKEN     Hugging Face access token (required for private repositories).
                 In Streamlit Cloud set this in st.secrets — never hard-code it.
    HF_REPO_ID   Override the default repository ID.
    MODEL_DIR    Override the local cache root (default: project root).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import hf_hub_download

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ID: str = os.getenv(
    "HF_REPO_ID",
    "Piyu2420/AI-Fashion-Design-Generator-IBM-INTERSHIP-2026",
)
HF_TOKEN: str | None = os.getenv("HF_TOKEN")  # None → public repo

# Project root = two levels up from this file (src/model_manager.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR: Path = Path(os.getenv("MODEL_DIR", str(_PROJECT_ROOT)))


# ---------------------------------------------------------------------------
# HF filename → local relative path mapping (9 files)
# ---------------------------------------------------------------------------

_MODELS: dict[str, tuple[str, str]] = {
    # key: (hf_filename, local_relative_path)
    "realvisxl": (
        "realvisxl/realvisxl.safetensors",
        "weights/realvisxl.safetensors",
    ),
    "sam": (
        "sam/sam_vit_h_4b8939.pth",
        "weights/sam_vit_h_4b8939.pth",
    ),
    "densepose": (
        "idm_vton/densepose/model_final_162be9.pkl",
        "idm_vton/ckpt/densepose/model_final_162be9.pkl",
    ),
    "humanparsing_atr": (
        "idm_vton/humanparsing/parsing_atr.onnx",
        "idm_vton/ckpt/humanparsing/parsing_atr.onnx",
    ),
    "humanparsing_lip": (
        "idm_vton/humanparsing/parsing_lip.onnx",
        "idm_vton/ckpt/humanparsing/parsing_lip.onnx",
    ),
    "openpose": (
        "idm_vton/openpose/body_pose_model.pth",
        "idm_vton/ckpt/openpose/ckpts/body_pose_model.pth",
    ),
    "image_encoder_config": (
        "idm_vton/image_encoder/config.json",
        "idm_vton/ckpt/image_encoder/config.json",
    ),
    "image_encoder": (
        "idm_vton/image_encoder/model.safetensors",
        "idm_vton/ckpt/image_encoder/model.safetensors",
    ),
    "ip_adapter": (
        "idm_vton/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin",
        "idm_vton/ckpt/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin",
    ),
}


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

@dataclass
class ModelPaths:
    """Local filesystem paths to every downloaded weight file."""
    realvisxl: str
    sam: str
    densepose: str
    humanparsing_atr: str
    humanparsing_lip: str
    openpose: str
    image_encoder_config: str
    image_encoder: str
    ip_adapter: str


# ---------------------------------------------------------------------------
# Core download helper
# ---------------------------------------------------------------------------

def _download(hf_filename: str, local_relative: str) -> str:
    """
    Return the local path for *hf_filename*, downloading from HF if needed.

    If the file already exists at the expected local path and is non-empty,
    the download is skipped entirely (no network request made).
    """
    local_path = MODEL_DIR / local_relative
    local_path.parent.mkdir(parents=True, exist_ok=True)

    if local_path.exists() and local_path.stat().st_size > 0:
        log.info("✅ Already cached: %s", local_path)
        return str(local_path)

    log.info("⬇️  Downloading: %s → %s", hf_filename, local_path)
    hf_hub_download(
        repo_id=REPO_ID,
        filename=hf_filename,
        repo_type="model",
        local_dir=str(MODEL_DIR),
        token=HF_TOKEN,
    )
    # hf_hub_download places the file at local_dir/filename; rename to our
    # preferred flat layout if it differs.
    hf_placed = MODEL_DIR / hf_filename
    if hf_placed.exists() and hf_placed != local_path:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        hf_placed.rename(local_path)

    log.info("✅ Ready: %s", local_path)
    return str(local_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def download_all_models() -> ModelPaths:
    """
    Download (or verify cache of) all 9 model weight files.

    Safe to call multiple times — files already on disk are not re-downloaded.
    Returns a ModelPaths dataclass with the resolved local path for each file.
    """
    log.info("=== Model Manager: resolving 9 weights from %s ===", REPO_ID)

    paths: dict[str, str] = {}
    for key, (hf_file, local_file) in _MODELS.items():
        paths[key] = _download(hf_file, local_file)

    log.info("=== ✅ All 9 model weights ready ===")

    return ModelPaths(
        realvisxl=         paths["realvisxl"],
        sam=               paths["sam"],
        densepose=         paths["densepose"],
        humanparsing_atr=  paths["humanparsing_atr"],
        humanparsing_lip=  paths["humanparsing_lip"],
        openpose=          paths["openpose"],
        image_encoder_config=paths["image_encoder_config"],
        image_encoder=     paths["image_encoder"],
        ip_adapter=        paths["ip_adapter"],
    )


# ---------------------------------------------------------------------------
# Convenience: single-model getters (used by individual pipeline scripts)
# ---------------------------------------------------------------------------

def get_realvisxl_path() -> str:
    """Return local path for RealVisXL, downloading if needed."""
    hf, local = _MODELS["realvisxl"]
    return _download(hf, local)


def get_sam_path() -> str:
    """Return local path for SAM ViT-H, downloading if needed."""
    hf, local = _MODELS["sam"]
    return _download(hf, local)


def get_densepose_paths() -> dict[str, str]:
    """Return local paths for DensePose, human-parsing, OpenPose weights."""
    keys = ["densepose", "humanparsing_atr", "humanparsing_lip", "openpose"]
    return {k: _download(*_MODELS[k]) for k in keys}


def get_idm_vton_extra_paths() -> dict[str, str]:
    """Return local paths for image_encoder and ip_adapter weights."""
    keys = ["image_encoder_config", "image_encoder", "ip_adapter"]
    return {k: _download(*_MODELS[k]) for k in keys}


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    result = download_all_models()
    print("\nResolved paths:")
    for field, value in result.__dict__.items():
        print(f"  {field:<22} {value}")
