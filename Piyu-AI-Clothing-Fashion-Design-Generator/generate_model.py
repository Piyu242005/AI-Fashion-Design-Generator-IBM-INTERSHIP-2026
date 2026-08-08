"""
generate_model.py
-----------------
Stage 1 — Generate a photorealistic human fashion model from a text prompt.

Uses RealVisXL V4.0 Lightning (SDXL-based) via the Diffusers library.
Replaces the old auto1111sdk backend which is incompatible with Python 3.12+
and requires the 'clip' package that is not reliably installable in Colab.

The model weight is resolved through src/model_manager, which downloads it
from the configured Hugging Face repository on first use and caches locally.

Usage
-----
    python generate_model.py \\
        --prompt "a crop top and mini skirt" \\
        --output_path "reference_images/crop_top.png"
"""

from __future__ import annotations

import argparse
import gc
import logging
import os
import random
import sys
from pathlib import Path

import torch

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


# ── Ensure src/ is importable when run as a subprocess from Colab ─────────
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from src.model_manager import get_realvisxl_path  # noqa: E402


# ── Lazy pipeline loader (avoids importing torch at module level in Colab) ─
def _load_pipeline(model_path: str):
    """
    Load RealVisXL via Diffusers from_single_file().

    Works with Python 3.10–3.12+.  No auto1111sdk, no CLIP dependency.
    """
    from diffusers import DPMSolverSinglestepScheduler, StableDiffusionXLPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device == "cuda" else torch.float32

    log.info("Device: %s  |  dtype: %s", device, dtype)
    log.info("Loading RealVisXL from: %s", model_path)

    pipe = StableDiffusionXLPipeline.from_single_file(
        model_path,
        # Use the official SDXL base config so tokenizers / text-encoders
        # are resolved correctly without needing a local config.json.
        config="stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=dtype,
        use_safetensors=True,
        safety_checker=None,
        # Suppress the unnecessary "config ignored" warnings from diffusers
        ignore_mismatched_sizes=True,
    )

    # Swap to the fast DPM++ SDE (Karras) scheduler used by RealVisXL Lightning
    try:
        pipe.scheduler = DPMSolverSinglestepScheduler.from_config(
            pipe.scheduler.config,
            use_karras_sigmas=True,
        )
        log.info("Scheduler: DPMSolverSinglestep (Karras)")
    except Exception as exc:
        log.warning("Could not set Karras scheduler: %s — keeping default.", exc)

    # Memory optimisations (safe on both GPU and CPU)
    pipe.enable_vae_slicing()
    pipe.enable_vae_tiling()

    if device == "cuda":
        # Sequential CPU offload keeps VRAM usage low enough for Colab T4 (15 GB)
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)

    return pipe, device


# ── Generation ────────────────────────────────────────────────────────────

def generate(
    clothing_type: str,
    output_path: str,
    steps: int = 4,
    width: int = 768,
    height: int = 1024,
    guidance_scale: float = 0.0,
    seed: int | None = None,
) -> None:
    """
    Generate a 768×1024 portrait of a woman wearing the described clothing.

    Parameters
    ----------
    clothing_type   : str   — clothing description used in the prompt
    output_path     : str   — where to save the output PNG
    steps           : int   — inference steps (4 recommended for Lightning)
    width / height  : int   — output resolution
    guidance_scale  : float — 0.0 for Lightning distilled models
    seed            : int | None — reproducibility seed; random if None
    """
    model_path = get_realvisxl_path()
    pipe, device = _load_pipeline(model_path)

    prompt = (
        f"centered, portrait photo of a woman, wearing {clothing_type}, "
        "natural skin, photorealistic, high detail clothing, realistic fabric, "
        "studio fashion photography, neutral background, sharp focus"
    )
    negative_prompt = (
        "low quality, blurry, deformed, bad anatomy, bad hands, "
        "extra fingers, fused fingers, distorted face, duplicate, "
        "cropped head, text, watermark, cartoon, illustration, "
        "painting, drawing, anime, nsfw"
    )

    if seed is None:
        seed = random.randint(0, 2 ** 32 - 1)

    generator = torch.Generator(device="cpu").manual_seed(seed)

    log.info("Seed: %d", seed)
    log.info("Prompt: %s", prompt)
    log.info("Generating %dx%d in %d steps…", width, height, steps)

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        generator=generator,
    )

    image = result.images[0]

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    log.info("Saved: %s", out)

    # Release GPU memory for the next pipeline stage (SAM / IDM-VTON)
    del pipe, result
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        log.info("GPU cache cleared.")


# ── Entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a realistic human fashion model from a text prompt."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help='Clothing description, e.g. "a crop top and mini skirt"',
    )
    parser.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="Output image path, e.g. reference_images/crop_top.png",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=4,
        help="Number of inference steps (default: 4 for Lightning)",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=768,
        help="Output image width (default: 768)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1024,
        help="Output image height (default: 1024)",
    )
    parser.add_argument(
        "--guidance_scale",
        type=float,
        default=0.0,
        help="CFG guidance scale — use 0.0 for Lightning distilled models",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (random if not set)",
    )

    args, _ = parser.parse_known_args()

    generate(
        clothing_type=args.prompt,
        output_path=args.output_path,
        steps=args.steps,
        width=args.width,
        height=args.height,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
