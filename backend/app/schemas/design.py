"""
backend/app/schemas/design.py
===============================
Pydantic request / response models for the /api/design endpoint.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator


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

    @field_validator("prompt")
    @classmethod
    def strip_and_check(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 5:
            raise ValueError("Prompt is too short. Please describe the design in more detail.")
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


# ---------------------------------------------------------------------------
# Error response
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
