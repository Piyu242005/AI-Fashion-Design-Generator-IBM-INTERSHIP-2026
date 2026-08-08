"""
model_manager.py
----------------
Downloads and caches all 9 model weight files from the project's Hugging Face
model repository.

Hugging Face repository
-----------------------
    Piyu2420/AI-Fashion-Design-Generator-IBM-INTERNSHIP-2026

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

from pathlib import Path
import os

from huggingface_hub import hf_hub_download


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

REPO_ID = os.getenv(
    "HF_REPO_ID",
    "Piyu2420/AI-Fashion-Design-Generator-IBM-INTERNSHIP-2026",
)

# Set this ONLY if the HF repository is private.
# For Streamlit, use st.secrets instead of hard-coding the token.
HF_TOKEN = os.getenv("HF_TOKEN", None)


# ============================================================
# HF filename → local absolute path mapping (9 files)
# ============================================================

_HF_FILES = {
    "realvisxl":           "realvisxl/realvisxl.safetensors",
    "sam":                 "sam/sam_vit_h_4b8939.pth",
    "densepose":           "idm_vton/densepose/model_final_162be9.pkl",
    "parsing_atr":         "idm_vton/humanparsing/parsing_atr.onnx",
    "parsing_lip":         "idm_vton/humanparsing/parsing_lip.onnx",
    "openpose":            "idm_vton/openpose/body_pose_model.pth",
    "image_encoder_config":"idm_vton/image_encoder/config.json",
    "image_encoder":       "idm_vton/image_encoder/model.safetensors",
    "ip_adapter":          "idm_vton/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin",
}

_LOCAL_FILES = {
    "realvisxl":            PROJECT_ROOT / "weights/realvisxl.safetensors",
    "sam":                  PROJECT_ROOT / "weights/sam_vit_h_4b8939.pth",
    "densepose":            PROJECT_ROOT / "idm_vton/ckpt/densepose/model_final_162be9.pkl",
    "parsing_atr":          PROJECT_ROOT / "idm_vton/ckpt/humanparsing/parsing_atr.onnx",
    "parsing_lip":          PROJECT_ROOT / "idm_vton/ckpt/humanparsing/parsing_lip.onnx",
    "openpose":             PROJECT_ROOT / "idm_vton/ckpt/openpose/ckpts/body_pose_model.pth",
    "image_encoder_config": PROJECT_ROOT / "idm_vton/ckpt/image_encoder/config.json",
    "image_encoder":        PROJECT_ROOT / "idm_vton/ckpt/image_encoder/model.safetensors",
    "ip_adapter":           PROJECT_ROOT / "idm_vton/ckpt/ip_adapter/ip-adapter-plus_sdxl_vit-h.bin",
}


# ============================================================
# DOWNLOAD ONE FILE
# ============================================================

def _download(model_name: str) -> str:

    hf_file    = _HF_FILES[model_name]
    local_path = _LOCAL_FILES[model_name]

    local_path.parent.mkdir(parents=True, exist_ok=True)

    # Already on disk — skip download
    if local_path.exists() and local_path.stat().st_size > 0:
        size_mb = local_path.stat().st_size / (1024 ** 2)
        print(f"✅ {model_name:<25} already available ({size_mb:.2f} MB)")
        return str(local_path)

    # Download from Hugging Face
    print(f"⬇️  Downloading {model_name}")
    print(f"    repo : {REPO_ID}")
    print(f"    file : {hf_file}")

    try:
        hf_hub_download(
            repo_id=REPO_ID,
            filename=hf_file,
            repo_type="model",
            token=HF_TOKEN,
            local_dir=str(PROJECT_ROOT),
        )

        # hf_hub_download writes to PROJECT_ROOT/hf_file; move to our layout
        hf_placed = PROJECT_ROOT / hf_file
        if hf_placed.exists() and hf_placed.resolve() != local_path.resolve():
            local_path.parent.mkdir(parents=True, exist_ok=True)
            hf_placed.rename(local_path)

        if not local_path.exists() or local_path.stat().st_size == 0:
            raise RuntimeError(f"File missing or empty after download: {local_path}")

        size_mb = local_path.stat().st_size / (1024 ** 2)
        print(f"✅ {model_name:<25} downloaded ({size_mb:.2f} MB)")
        return str(local_path)

    except Exception as exc:
        raise RuntimeError(
            f"\n❌ Failed to download '{model_name}'\n"
            f"   repo : {REPO_ID}\n"
            f"   file : {hf_file}\n\n"
            f"Original error:\n{exc}\n"
        ) from exc


# ============================================================
# PUBLIC API
# ============================================================

def download_all_models() -> dict:
    """Download (or verify) all 9 model weights. Returns a dict of local paths."""
    print("=" * 70)
    print("HUGGING FACE MODEL MANAGER")
    print(f"Repository: {REPO_ID}")
    print("=" * 70)

    paths = {name: _download(name) for name in _HF_FILES}

    print()
    print("=" * 70)
    print("🎉 ALL 9 MODELS READY")
    print("=" * 70)
    return paths


def verify_models() -> bool:
    """Check all 9 local paths exist and are non-empty. No network calls."""
    print("=" * 70)
    print("LOCAL MODEL VERIFICATION")
    print("=" * 70)

    passed = 0
    failed = 0

    for name, path in _LOCAL_FILES.items():
        if path.exists() and path.stat().st_size > 0:
            size_mb = path.stat().st_size / (1024 ** 2)
            print(f"✅ {name:<25} {size_mb:>10.2f} MB")
            passed += 1
        else:
            print(f"❌ {name:<25} MISSING — {path}")
            failed += 1

    print()
    print(f"PASSED: {passed}/{len(_LOCAL_FILES)}")
    print(f"FAILED: {failed}/{len(_LOCAL_FILES)}")
    return failed == 0


# Convenience getters — keep same API as before
def get_realvisxl_path() -> str:
    return _download("realvisxl")

def get_sam_path() -> str:
    return _download("sam")

def get_densepose_paths() -> dict:
    return {k: _download(k) for k in ("densepose", "parsing_atr", "parsing_lip", "openpose")}

def get_idm_vton_extra_paths() -> dict:
    return {k: _download(k) for k in ("image_encoder_config", "image_encoder", "ip_adapter")}


# ============================================================
# MAIN — run directly to verify or download
# ============================================================

if __name__ == "__main__":

    if verify_models():
        print("\n🎉 All 9 models already exist locally.")
        print("No Hugging Face download is required.")
    else:
        print("\n⬇️  Some models are missing. Downloading from Hugging Face...\n")
        download_all_models()
