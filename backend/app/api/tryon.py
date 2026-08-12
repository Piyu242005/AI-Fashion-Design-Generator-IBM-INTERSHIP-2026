"""
backend/app/api/tryon.py
========================
POST /api/try-on  — AI Virtual Try-On via IDM-VTON (Hugging Face Space)

Accepts two image uploads (multipart/form-data):
    person   — full-body photo of the user
    garment  — clothing item image

Returns JSON:
    { "success": true,  "image": "data:image/jpeg;base64,…" }
    { "success": false, "error": { "code": "…", "message": "…" } }
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.idm_vton import hf_configured, run_tryon

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Allowed MIME types
_ALLOWED = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
# Max file size: 10 MB per image
_MAX_BYTES = 10 * 1024 * 1024


def _ext(filename: str | None, content_type: str) -> str:
    """Derive a safe file extension from filename or content-type."""
    if filename:
        suffix = Path(filename).suffix.lstrip(".").lower()
        if suffix in ("jpg", "jpeg", "png", "webp"):
            return "jpg" if suffix == "jpeg" else suffix
    return "jpg" if "jpeg" in content_type else "png"


@router.post(
    "/api/try-on",
    summary="AI Virtual Try-On via IDM-VTON",
    response_description="Try-on result image as base64 data URI",
)
@limiter.limit("4/minute")
async def virtual_tryon(
    request: Request,
    person:  UploadFile = File(..., description="Full-body person photo"),
    garment: UploadFile = File(..., description="Garment / clothing item image"),
) -> JSONResponse:

    # ── Validate content types ───────────────────────────────────────────────
    for upload, label in ((person, "person"), (garment, "garment")):
        ct = (upload.content_type or "").lower()
        if ct not in _ALLOWED:
            raise HTTPException(
                status_code=415,
                detail=f"'{label}' must be a JPEG, PNG or WebP image (got '{ct}').",
            )

    # ── Read bytes with size cap ─────────────────────────────────────────────
    person_bytes  = await person.read()
    garment_bytes = await garment.read()

    if len(person_bytes) > _MAX_BYTES or len(garment_bytes) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="Each image must be under 10 MB.")

    if not person_bytes or not garment_bytes:
        raise HTTPException(status_code=400, detail="One or both uploaded files are empty.")

    person_ext  = _ext(person.filename,  person.content_type  or "")
    garment_ext = _ext(garment.filename, garment.content_type or "")

    logger.info(
        "POST /api/try-on  person=%d B  garment=%d B  hf_configured=%s",
        len(person_bytes), len(garment_bytes), hf_configured(),
    )

    # ── Call IDM-VTON ────────────────────────────────────────────────────────
    result = await run_tryon(person_bytes, garment_bytes, person_ext, garment_ext)

    if result.success and result.image_base64:
        return JSONResponse(status_code=200, content={
            "success": True,
            "image":   result.image_base64,
            "provider": "idm-vton",
        })

    # Map error codes to HTTP status codes
    status = {
        "QUOTA_EXCEEDED":   429,
        "SPACE_LOADING":    503,
        "SPACE_UNAVAILABLE": 503,
        "DEPENDENCY_MISSING": 500,
    }.get(result.error_code or "", 500)

    return JSONResponse(status_code=status, content={
        "success": False,
        "error": {
            "code":    result.error_code    or "TRYON_FAILED",
            "message": result.error_message or "Virtual try-on failed. Please try again.",
        },
    })
