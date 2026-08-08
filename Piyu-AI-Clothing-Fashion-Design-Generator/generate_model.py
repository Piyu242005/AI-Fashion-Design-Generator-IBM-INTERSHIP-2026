"""
generate_model.py
-----------------
Stage 1 — Generate a photorealistic human fashion model from a text prompt.

Uses RealVisXL V4.0 Lightning (SDXL-based) via auto1111sdk.
The model weight is resolved through model_manager, which downloads it from
the configured Hugging Face repository on first use and caches it locally.

Usage
-----
    python generate_model.py \\
        --prompt "a crop top and mini skirt" \\
        --output_path "reference_images/crop_top.png"
"""

import random
import argparse
import logging as log

import torch
from auto1111sdk import StableDiffusionPipeline

from model_manager import get_realvisxl_path

log.getLogger().setLevel(log.INFO)

# ---------------------------------------------------------------------------
# Resolve weight path via model_manager (downloads from HF if not cached)
# ---------------------------------------------------------------------------
MODEL_PATH = get_realvisxl_path()


# ---------------------------------------------------------------------------
# Pipeline setup
# ---------------------------------------------------------------------------

def set_seed() -> int:
    return random.randint(42, 4294967295)


def create_pipeline(model_path: str) -> StableDiffusionPipeline:
    return StableDiffusionPipeline(model_path, default_command_args='--device-id 0')


pipe = create_pipeline(MODEL_PATH)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def generate(clothing_type: str, output_name: str) -> None:
    """
    Generate a 768×1024 portrait of a woman wearing the described clothing.

    Parameters
    ----------
    clothing_type : str
        Clothing description, e.g. "a crop top and mini skirt".
    output_name : str
        Output image path, e.g. "reference_images/crop_top.png".
    """
    log.info("Generating...")

    prompt = (
        "centered, portrait photo of a woman, wearing {}, natural skin, dark shot"
    ).format(clothing_type)

    negative_prompt = (
        "(octane render, render, drawing, anime, bad photo, bad photography:1.3), "
        "(worst quality, low quality, blurry:1.2), (bad teeth, deformed teeth, deformed lips), "
        "(bad anatomy, bad proportions:1.1), (deformed iris, deformed pupils), (deformed eyes, bad eyes), "
        "(deformed face, ugly face, bad face), (deformed hands, bad hands, fused fingers), "
        "morbid, mutilated, mutation, disfigured"
    )

    log.info("Prompt: %s", prompt)

    image = pipe.generate_txt2img(
        prompt=prompt,
        negative_prompt=negative_prompt,
        height=1024,
        width=768,
        cfg_scale=2,
        steps=5,
        sampler_name="DPM++ SDE",
    )

    image[0].save(output_name)
    log.info("Image saved: %s", output_name)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a realistic human fashion model from a text prompt."
    )
    parser.add_argument("--prompt",      type=str, required=True,
                        help='Clothing description, e.g. "a crop top and mini skirt"')
    parser.add_argument("--output_path", type=str, required=True,
                        help="Output image path, e.g. reference_images/crop_top.png")

    args, _ = parser.parse_known_args()
    generate(args.prompt, args.output_path)


if __name__ == "__main__":
    main()
