"""
backend/app/schemas/design.py
===============================
Pydantic request / response models for the /api/design endpoint.

Model ID convention (used by frontend & backend routing):
  @cf/...       → Cloudflare Workers AI
  hf/...        → HuggingFace Inference API
  google/...    → Google Imagen (Gemini key)
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Allowed model IDs — prefix determines which provider is called
# ---------------------------------------------------------------------------
ALLOWED_MODELS = {
    # ── Cloudflare Workers AI ────────────────────────────────────────────────
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    "@cf/lykon/dreamshaper-8-lcm",
    "@cf/bytedance/stable-diffusion-xl-lightning",
    # ── HuggingFace Inference API ────────────────────────────────────────────
    "hf/black-forest-labs/FLUX.1-schnell",
    "hf/stabilityai/stable-diffusion-xl-base-1.0",
    "hf/runwayml/stable-diffusion-v1-5",
    # ── Google Imagen ────────────────────────────────────────────────────────
    "google/imagen-3.0-generate-002",
}
DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------
class DesignRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Fashion design prompt in plain language.",
        examples=["Modern Indian half-saree in pastel pink and gold"],
    )
    model: Optional[str] = Field(
        default=None,
        description=(
            "Model ID. Prefix selects provider: @cf/ = Cloudflare, "
            "hf/ = HuggingFace, google/ = Google Imagen. "
            f"Defaults to {DEFAULT_MODEL}."
        ),
        examples=list(ALLOWED_MODELS),
    )

    @field_validator("prompt")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Prompt is too short.")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in ALLOWED_MODELS:
            raise ValueError(
                f"Unknown model '{v}'. "
                f"Allowed values: {', '.join(sorted(ALLOWED_MODELS))}"
            )
        return v


# ---------------------------------------------------------------------------
# Success response
# ---------------------------------------------------------------------------
class DesignResponse(BaseModel):
    success: bool = True
    image: str = Field(..., description="Base64-encoded image as a data URI.")
    provider: str = Field(default="cloudflare", description="Which AI provider generated the image.")


# ---------------------------------------------------------------------------
# Error detail  (nested inside ErrorResponse)
# ---------------------------------------------------------------------------
class ErrorDetail(BaseModel):
    code: str
    message: str
    fallback_url: Optional[str] = None   # populated when falling back to placeholder


# ---------------------------------------------------------------------------
# Error response
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
