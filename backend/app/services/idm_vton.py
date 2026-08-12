"""
backend/app/services/idm_vton.py
=================================
Calls the Hugging Face IDM-VTON Gradio Space for real AI virtual try-on.

Space  : yisol/IDM-VTON  (https://huggingface.co/spaces/yisol/IDM-VTON)
License: CC BY-NC-SA 4.0  (non-commercial use only)

Official API signature (from "Use via API" page):
    client.predict(
        dict         = {"background": file(...), "layers": [], "composite": None},
        garm_img     = file(...),
        garment_des  = "Description of garment",
        is_checked   = True,
        is_checked_crop = False,
        denoise_steps   = 30,
        seed            = 42,
        api_name        = "/tryon"
    )
    Returns: (result_filepath, masked_person_filepath)

Environment variables (set in .env):
    HF_TOKEN    — Hugging Face READ token  (for higher ZeroGPU quota)
    HF_SPACE_ID — defaults to "yisol/IDM-VTON"

ZeroGPU spaces go to sleep after inactivity. The client will retry the
connection up to CONNECT_RETRIES times with a short back-off to give the
space time to wake up before giving up.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Read once at import time; FastAPI restarts pick up new values.
SPACE_ID = os.getenv("HF_SPACE_ID", "yisol/IDM-VTON")
SAFE_MSG  = "Virtual try-on failed. Please try again."

# How many times to retry connecting to the Space when it is sleeping/loading.
# Each attempt waits CONNECT_RETRY_DELAY seconds before the next try.
CONNECT_RETRIES     = 3
CONNECT_RETRY_DELAY = 10   # seconds between connection retries


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

@dataclass
class TryOnResult:
    success: bool
    image_base64:  Optional[str] = None   # "data:image/jpeg;base64,…"
    error_code:    Optional[str] = None
    error_message: Optional[str] = None


def hf_configured() -> bool:
    """Return True when a HF token is present."""
    return bool(os.getenv("HF_TOKEN", "").strip())


def _is_space_sleeping(exc: Exception) -> bool:
    """Return True when the exception looks like a sleeping/loading Space."""
    msg = str(exc).lower()
    return (
        "loading" in msg
        or "503" in msg
        or "unavailable" in msg
        or "space is sleeping" in msg
        or "waking up" in msg
        or "starting" in msg
        or "connection" in msg
        or "connect" in msg
    )


async def run_tryon(
    person_bytes:  bytes,
    garment_bytes: bytes,
    person_ext:    str = "jpg",
    garment_ext:   str = "jpg",
    garment_desc:  str = "",
) -> TryOnResult:
    """
    Send person + garment images to IDM-VTON and return the result.

    Args:
        person_bytes  : raw image bytes of the person photo
        garment_bytes : raw image bytes of the garment
        person_ext    : file extension for person  (jpg / png / webp)
        garment_ext   : file extension for garment (jpg / png / webp)
        garment_desc  : optional text description of the garment

    Returns:
        TryOnResult with image_base64 set on success.
    """
    # Lazy import — avoids adding startup time when the feature isn't used
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        logger.error("gradio_client not installed. Run: pip install gradio_client")
        return TryOnResult(
            success=False,
            error_code="DEPENDENCY_MISSING",
            error_message=SAFE_MSG,
        )

    hf_token = os.getenv("HF_TOKEN", "").strip() or None
    if not hf_token:
        logger.warning("HF_TOKEN not set — IDM-VTON will use unauthenticated quota (2 min/day).")

    # Write temp files — gradio_client needs filesystem paths, not bytes.
    # All gradio_client calls (Client(), submit(), result()) are blocking I/O;
    # run them in a thread executor so the FastAPI event loop stays responsive.
    loop = asyncio.get_event_loop()

    def _blocking_tryon(tmpdir: str) -> TryOnResult:
        person_path  = Path(tmpdir) / f"person.{person_ext}"
        garment_path = Path(tmpdir) / f"garment.{garment_ext}"
        person_path.write_bytes(person_bytes)
        garment_path.write_bytes(garment_bytes)

        # ── Connect to Space (with retry for sleeping ZeroGPU spaces) ───────
        client = None
        last_connect_exc: Exception | None = None

        for attempt in range(1, CONNECT_RETRIES + 1):
            try:
                logger.info(
                    "Connecting to HF Space %s (attempt %d/%d)…",
                    SPACE_ID, attempt, CONNECT_RETRIES,
                )
                client = Client(SPACE_ID, hf_token=hf_token)
                last_connect_exc = None
                break   # success
            except Exception as exc:
                last_connect_exc = exc
                logger.warning(
                    "HF Space connect attempt %d/%d failed: %s — %s",
                    attempt, CONNECT_RETRIES, type(exc).__name__, str(exc)[:120],
                )
                if attempt < CONNECT_RETRIES:
                    logger.info("Waiting %d s before retry (Space may be waking up)…", CONNECT_RETRY_DELAY)
                    import time as _time; _time.sleep(CONNECT_RETRY_DELAY)

        if client is None:
            exc = last_connect_exc
            logger.error(
                "Cannot connect to HF Space %s after %d attempts: %s",
                SPACE_ID, CONNECT_RETRIES, type(exc).__name__ if exc else "unknown",
            )
            if exc and _is_space_sleeping(exc):
                return TryOnResult(
                    success=False,
                    error_code="SPACE_LOADING",
                    error_message=(
                        "The IDM-VTON space is waking up from sleep. "
                        "Please wait 30–60 seconds and try again."
                    ),
                )
            return TryOnResult(
                success=False,
                error_code="SPACE_UNAVAILABLE",
                error_message="IDM-VTON space is unreachable. Please try again shortly.",
            )

        # ── Submit job (exact param names from the API docs) ─────────────────
        try:
            job = client.submit(
                # param: dict  — ImageEditor with the person photo as background
                dict={
                    "background": handle_file(str(person_path)),
                    "layers":     [],
                    "composite":  None,
                },
                # param: garm_img  — garment image (plain filepath, NOT a dict)
                garm_img=handle_file(str(garment_path)),
                # param: garment_des  — text description of the garment
                garment_des=garment_desc or "",
                # param: is_checked  — use auto-masking (True = recommended)
                is_checked=True,
                # param: is_checked_crop  — auto-crop the person image to body region.
                # Enabling this makes results more robust for varied photo compositions
                # (e.g. portrait crops, non-centered subjects).
                is_checked_crop=True,
                # param: denoise_steps — 40 gives noticeably better garment texture
                # reproduction than 30 with only ~5 s additional latency.
                denoise_steps=40,
                # param: seed
                seed=42,
                api_name="/tryon",
            )

            # Block until ZeroGPU queue completes (~10–60 s)
            outputs = job.result()

        except Exception as exc:
            err_str = str(exc).lower()
            logger.error("IDM-VTON job error: %s — %s", type(exc).__name__, str(exc)[:120])

            if "quota" in err_str or "exceeded" in err_str or "limit" in err_str:
                return TryOnResult(
                    success=False,
                    error_code="QUOTA_EXCEEDED",
                    error_message="ZeroGPU daily quota reached. Try again tomorrow or add a HF Pro subscription.",
                )
            if "loading" in err_str or "503" in err_str or "unavailable" in err_str:
                return TryOnResult(
                    success=False,
                    error_code="SPACE_LOADING",
                    error_message="IDM-VTON space is loading. Wait ~30 s and retry.",
                )
            if "timeout" in err_str:
                return TryOnResult(
                    success=False,
                    error_code="TIMEOUT",
                    error_message="IDM-VTON timed out. The ZeroGPU queue may be busy — please retry.",
                )
            return TryOnResult(
                success=False,
                error_code="TRYON_FAILED",
                error_message=SAFE_MSG,
            )

        # ── Extract result image (outputs[0] = result, outputs[1] = mask) ───
        try:
            result_path  = outputs[0] if isinstance(outputs, (list, tuple)) else outputs
            result_bytes = Path(result_path).read_bytes()
            b64  = base64.b64encode(result_bytes).decode("utf-8")
            mime = "image/jpeg" if result_bytes[:2] == b"\xff\xd8" else "image/png"
            return TryOnResult(success=True, image_base64=f"data:{mime};base64,{b64}")

        except Exception as exc:
            logger.error("Could not read IDM-VTON result file: %s", exc)
            return TryOnResult(
                success=False,
                error_code="PARSE_ERROR",
                error_message=SAFE_MSG,
            )

    with tempfile.TemporaryDirectory() as tmpdir:
        return await loop.run_in_executor(None, _blocking_tryon, tmpdir)
