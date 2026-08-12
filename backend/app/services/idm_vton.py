"""
backend/app/services/idm_vton.py
=================================
Calls the Hugging Face IDM-VTON Gradio Space for real AI virtual try-on.

Space  : yisol/IDM-VTON  (https://huggingface.co/spaces/yisol/IDM-VTON)
Model  : IDM-VTON — high-fidelity diffusion-based garment try-on
License: CC BY-NC-SA 4.0  (non-commercial use only)

Environment variables required (set in .env):
    HF_TOKEN      — Hugging Face read token (https://huggingface.co/settings/tokens)
    HF_SPACE_ID   — defaults to "yisol/IDM-VTON"

Security:
    - HF_TOKEN is loaded from env only, never logged or forwarded to the client.
    - Raw Gradio/HF errors are sanitised before reaching the API layer.
"""

from __future__ import annotations

import base64
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

HF_TOKEN  = os.getenv("HF_TOKEN", "").strip()
SPACE_ID  = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
SAFE_MSG  = "Virtual try-on failed. Please try again."


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

@dataclass
class TryOnResult:
    success: bool
    image_base64: Optional[str] = None   # "data:image/jpeg;base64,…"
    error_code:   Optional[str] = None
    error_message: Optional[str] = None


def hf_configured() -> bool:
    """Return True when a HF token is present."""
    return bool(os.getenv("HF_TOKEN", "").strip())


async def run_tryon(person_bytes: bytes, garment_bytes: bytes,
                    person_ext: str = "jpg", garment_ext: str = "jpg") -> TryOnResult:
    """
    Send person + garment images to IDM-VTON and return the result image.

    Both inputs are raw bytes (JPEG/PNG).  We write them to temp files because
    gradio_client.handle_file() expects a file path or URL.

    IDM-VTON /tryon endpoint signature (from client.view_api()):
        fn_index=0  /  api_name="/tryon"
        Inputs:
            dict  — {"background": <file>, "layers": [], "composite": null}  (person image, ImageEditor)
            dict  — {"image": <file>, "description": str}                    (garment, image + text)
            str   — garment description (passed inside garment dict above)
            bool  — is_checked          (auto-masking, True recommended)
            bool  — is_checked_crop     (auto-crop,    False recommended)
            int   — denoise_steps       (30 default)
            int   — seed                (42 default)
        Output:
            filepath — result image path
            filepath — masked person image path
    """
    try:
        from gradio_client import Client, handle_file  # imported lazily to avoid startup cost
    except ImportError:
        logger.error("gradio_client not installed. Run: pip install gradio_client")
        return TryOnResult(success=False, error_code="DEPENDENCY_MISSING",
                           error_message=SAFE_MSG)

    if not HF_TOKEN:
        logger.warning("HF_TOKEN not set — IDM-VTON requests will be rate-limited.")

    # ── Write temp files ────────────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as tmpdir:
        person_path  = Path(tmpdir) / f"person.{person_ext}"
        garment_path = Path(tmpdir) / f"garment.{garment_ext}"
        person_path.write_bytes(person_bytes)
        garment_path.write_bytes(garment_bytes)

        try:
            client = Client(
                SPACE_ID,
                hf_token=HF_TOKEN or None,  # None = unauthenticated (lower quota)
            )
        except Exception as exc:
            logger.error("Failed to connect to HF Space %s: %s", SPACE_ID, type(exc).__name__)
            return TryOnResult(success=False, error_code="SPACE_UNAVAILABLE",
                               error_message=SAFE_MSG)

        try:
            # Submit asynchronously so we can respect the ZeroGPU queue
            job = client.submit(
                # Input 0 — person image as ImageEditor dict
                {"background": handle_file(str(person_path)), "layers": [], "composite": None},
                # Input 1 — garment image dict
                {"image": handle_file(str(garment_path)), "description": ""},
                # Input 2 — garment description (empty = auto)
                "",
                # Input 3 — is_checked: use auto-masking
                True,
                # Input 4 — is_checked_crop: no auto-crop
                False,
                # Input 5 — denoise_steps
                30,
                # Input 6 — seed
                42,
                api_name="/tryon",
            )

            # Block until the ZeroGPU job completes (may queue for up to ~60 s)
            outputs = job.result()   # raises on failure

        except Exception as exc:
            err = str(exc)
            logger.error("IDM-VTON job failed: %s", type(exc).__name__)

            if "quota" in err.lower() or "exceeded" in err.lower():
                return TryOnResult(success=False, error_code="QUOTA_EXCEEDED",
                                   error_message="ZeroGPU daily quota reached. Try again tomorrow.")
            if "loading" in err.lower() or "503" in err:
                return TryOnResult(success=False, error_code="SPACE_LOADING",
                                   error_message="IDM-VTON space is loading. Wait 30 s and retry.")
            return TryOnResult(success=False, error_code="TRYON_FAILED",
                               error_message=SAFE_MSG)

        # ── Extract result image ────────────────────────────────────────────
        # outputs[0] is the result image filepath returned by Gradio
        try:
            result_path = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
            result_bytes = Path(result_path).read_bytes()
            b64 = base64.b64encode(result_bytes).decode("utf-8")
            # Detect JPEG vs PNG from magic bytes
            mime = "image/jpeg" if result_bytes[:2] == b"\xff\xd8" else "image/png"
            return TryOnResult(success=True, image_base64=f"data:{mime};base64,{b64}")

        except Exception as exc:
            logger.error("Could not read IDM-VTON result file: %s", exc)
            return TryOnResult(success=False, error_code="PARSE_ERROR",
                               error_message=SAFE_MSG)
