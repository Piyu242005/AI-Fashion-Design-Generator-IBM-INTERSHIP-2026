"""
model_manager.py
----------------
Downloads and caches all model weight files from a Hugging Face model repository.

Usage
-----
    from model_manager import ModelPaths, download_all_models

    paths = download_all_models()
    print(paths.realvisxl)      # local path to RealVisXL .safetensors
    print(paths.sam)            # local path to SAM ViT-H .pth
    print(paths.densepose)      # local path to DensePose .pkl
    print(paths.humanparsing_atr)
    print(paths.humanparsing_lip)
    print(paths.openpose)

Environment variables
---------------------
    HF_REPO_ID   Override the default Hugging Face repo (default: Piyu242005/piyu-fashion-models)
    HF_TOKEN     Hugging Face access token for gated / private repositories
    MODEL_DIR    Local directory to cache downloaded weights (default: models/)

Notes
-----
    * hf_hub_download() caches files under MODEL_DIR and skips re-downloading
      if the file is already present and up-to-date.
    * Large files (~10 GB total) are downloaded once and reused across runs.
    * Never commit HF_TOKEN to source control — store it as an environment variable
      or a .env file that is excluded via .gitignore.
"""

from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from pathlib import Path

from huggingface_hub import hf_hub_download

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

# ---------------------------------------------------------------------------
# Configuration — override with environment variables
# ---------------------------------------------------------------------------

REPO_ID: str = os.getenv("HF_REPO_ID", "Piyu242005/piyu-fashion-models")
HF_TOKEN: str | None = os.getenv("HF_TOKEN")          # None → public repo
MODEL_DIR: str = os.getenv("MODEL_DIR", "models")


# ---------------------------------------------------------------------------
# File paths inside the Hugging Face repository
# ---------------------------------------------------------------------------

_HF_FILES = {
    "realvisxl":         "realvisxl/realvisxl.safetensors",
    "sam":               "sam/sam_vit_h_4b8939.pth",
    "densepose":         "idm_vton/densepose/model_final_162be9.pkl",
    "humanparsing_atr":  "idm_vton/humanparsing/parsing_atr.onnx",
    "humanparsing_lip":  "idm_vton/humanparsing/parsing_lip.onnx",
    "openpose":          "idm_vton/openpose/body_pose_model.pth",
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


# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def _download(filename: str) -> str:
    """
    Download a single file from the Hugging Face Hub and return its local path.

    hf_hub_download() caches the file under MODEL_DIR and skips the network
    request if an up-to-date copy already exists.
    """
    log.info("Ensuring weight is available: %s", filename)
    local_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=filename,
        local_dir=MODEL_DIR,
        token=HF_TOKEN,
    )
    log.info("  → %s", local_path)
    return local_path


def download_all_models() -> ModelPaths:
    """
    Download (or verify cache of) all model weight files and return a
    ModelPaths dataclass with the local path for each weight.

    This function is safe to call multiple times — files are only downloaded
    if they are not already cached locally.
    """
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

    log.info("=== Model Manager: resolving weights from %s ===", REPO_ID)

    paths = ModelPaths(
        realvisxl=        _download(_HF_FILES["realvisxl"]),
        sam=              _download(_HF_FILES["sam"]),
        densepose=        _download(_HF_FILES["densepose"]),
        humanparsing_atr= _download(_HF_FILES["humanparsing_atr"]),
        humanparsing_lip= _download(_HF_FILES["humanparsing_lip"]),
        openpose=         _download(_HF_FILES["openpose"]),
    )

    log.info("=== All weights resolved ===")
    return paths


# ---------------------------------------------------------------------------
# Convenience: download only what you need
# ---------------------------------------------------------------------------

def get_realvisxl_path() -> str:
    """Return the local path for the RealVisXL weight, downloading if needed."""
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
    return _download(_HF_FILES["realvisxl"])


def get_sam_path() -> str:
    """Return the local path for the SAM ViT-H weight, downloading if needed."""
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
    return _download(_HF_FILES["sam"])


def get_densepose_paths() -> dict[str, str]:
    """Return local paths for all DensePose / human-parsing / OpenPose weights."""
    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
    return {
        "densepose":        _download(_HF_FILES["densepose"]),
        "humanparsing_atr": _download(_HF_FILES["humanparsing_atr"]),
        "humanparsing_lip": _download(_HF_FILES["humanparsing_lip"]),
        "openpose":         _download(_HF_FILES["openpose"]),
    }


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    paths = download_all_models()
    print("\nResolved paths:")
    for field, value in paths.__dict__.items():
        print(f"  {field:<20} {value}")
