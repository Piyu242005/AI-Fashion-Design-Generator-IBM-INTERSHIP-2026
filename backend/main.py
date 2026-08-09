"""
AI Fashion Studio — FastAPI Backend
====================================
Responsibilities
  1. /api/generate-image  →  Calls Hugging Face Inference API (FLUX model)
                              Keeps HUGGINGFACE_API_TOKEN server-side (safe).
  2. CORS middleware       →  Allows the React dev server (localhost:5173) to call us.

Run:
  cd backend
  uvicorn main:app --reload --port 8000
"""

import os
import io
import base64
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from the project root (one level up from /backend)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = FastAPI(title="AI Fashion Studio API", version="1.0.0")

# ─── CORS ───────────────────────────────────────────────────────────────────
# Allow the Vite dev server and any localhost port to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite default
        "http://localhost:3000",   # CRA / alternate
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CONFIG ─────────────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
HF_MODEL = os.getenv("HUGGINGFACE_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
HF_URL   = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# Timeout: FLUX.1-schnell cold-starts can take ~30 s on free tier
HF_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


# ─── SCHEMAS ────────────────────────────────────────────────────────────────
class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str = "blurry, low quality, text, watermark, ugly, distorted"
    width: int = 768
    height: int = 768
    num_inference_steps: int = 4   # FLUX.1-schnell is optimised for 1-4 steps


class ImageResponse(BaseModel):
    image_base64: str              # data:image/png;base64,…
    model_used: str
    provider: str = "huggingface"


# ─── ROUTES ─────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "service": "AI Fashion Studio API"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "hf_token_set": bool(HF_TOKEN),
        "model": HF_MODEL,
    }


@app.post("/api/generate-image", response_model=ImageResponse)
async def generate_image(req: ImageRequest):
    """
    Generate a fashion image via Hugging Face Inference API.

    Falls back to a curated Unsplash fashion image URL (as a JSON string) 
    when the HF token is not set — so the React app always gets something back.
    """
    if not HF_TOKEN:
        # Mock mode: return a placeholder so the frontend still works
        raise HTTPException(
            status_code=503,
            detail={
                "mock": True,
                "fallback_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80",
                "message": "HUGGINGFACE_API_TOKEN not set. Using fallback image.",
            },
        )

    payload = {
        "inputs": req.prompt,
        "parameters": {
            "negative_prompt": req.negative_prompt,
            "width": req.width,
            "height": req.height,
            "num_inference_steps": req.num_inference_steps,
        },
    }

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true",   # Wait instead of returning 503 on cold-start
    }

    async with httpx.AsyncClient(timeout=HF_TIMEOUT) as client:
        try:
            resp = await client.post(HF_URL, json=payload, headers=headers)
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="HuggingFace model timed out. Try again — cold starts can take ~30 s.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Network error calling HuggingFace: {e}")

    if resp.status_code == 503:
        raise HTTPException(
            status_code=503,
            detail="Model is loading on HuggingFace servers. Wait ~20 s and retry.",
        )

    if resp.status_code == 402:
        raise HTTPException(
            status_code=402,
            detail="HuggingFace free credits ($0.10) exhausted. Add billing or switch to mock mode.",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"HuggingFace API error: {resp.text[:400]}",
        )

    # HF returns raw image bytes for image models
    image_bytes = resp.content
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return ImageResponse(
        image_base64=f"data:image/png;base64,{b64}",
        model_used=HF_MODEL,
    )
