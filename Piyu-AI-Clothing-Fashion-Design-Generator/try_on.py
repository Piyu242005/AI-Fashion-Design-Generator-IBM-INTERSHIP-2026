"""
try_on.py
---------
Stage 3 — Apply a target garment to a human model image using IDM-VTON.

The IDM-VTON pipeline weights are loaded from Hugging Face (yisol/idm_vton).
Supporting checkpoint paths (DensePose, human parsing, OpenPose) are resolved
through model_manager, which downloads them from the project's Hugging Face
repository on first use and caches them locally.

IMPORTANT — license notice
--------------------------
IDM-VTON code and checkpoints are released under CC BY-NC-SA 4.0.
Non-commercial use only. Attribute the original authors:
    Choi et al., "Improving Diffusion Models for Authentic Virtual Try-on in
    the Wild", ECCV 2024. https://github.com/yisol/IDM-VTON

Usage
-----
    # Run from inside the idm_vton/ directory:
    cd idm_vton
    python try_on.py \\
        --reference_image "../reference_images/crop_top.png" \\
        --mask            "../reference_images/crop_top_mask.jpg" \\
        --garment         "../samples/garment.png" \\
        --cloth_type      "crop top" \\
        --output_path     "../results/result_crop_top.png"
"""

import sys
import os
import argparse
import logging as log
from typing import List

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from torchvision.transforms.functional import to_pil_image
from transformers import (
    AutoTokenizer,
    CLIPImageProcessor,
    CLIPVisionModelWithProjection,
    CLIPTextModel,
    CLIPTextModelWithProjection,
)
from diffusers import DDPMScheduler, AutoencoderKL

# IDM-VTON internal modules — must be run from inside idm_vton/
sys.path.append("./")
from src.tryon_pipeline import StableDiffusionXLInpaintPipeline as TryonPipeline
from src.unet_hacked_garmnet import UNet2DConditionModel as UNet2DConditionModel_ref
from src.unet_hacked_tryon import UNet2DConditionModel
from utils_mask import get_mask_location
import apply_net
from preprocess.humanparsing.run_parsing import Parsing
from preprocess.openpose.run_openpose import OpenPose
from detectron2.data.detection_utils import (
    convert_PIL_to_numpy,
    _apply_exif_orientation,
)

from model_manager import get_densepose_paths

log.getLogger().setLevel(log.INFO)

# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------
device = "cuda:0" if torch.cuda.is_available() else "cpu"
log.info("Using device: %s", device)

# ---------------------------------------------------------------------------
# Resolve supporting checkpoint paths via model_manager
# ---------------------------------------------------------------------------
_ckpt = get_densepose_paths()
DENSEPOSE_PKL  = _ckpt["densepose"]
PARSING_ATR    = _ckpt["humanparsing_atr"]
PARSING_LIP    = _ckpt["humanparsing_lip"]
OPENPOSE_PTH   = _ckpt["openpose"]

# ---------------------------------------------------------------------------
# IDM-VTON pipeline (loaded from Hugging Face)
# ---------------------------------------------------------------------------
_BASE = "yisol/idm_vton"

log.info("Loading IDM-VTON pipeline from %s ...", _BASE)

unet = UNet2DConditionModel.from_pretrained(
    _BASE, subfolder="unet", torch_dtype=torch.float16
)
unet.requires_grad_(False)

tokenizer_one = AutoTokenizer.from_pretrained(
    _BASE, subfolder="tokenizer", revision=None, use_fast=False
)
tokenizer_two = AutoTokenizer.from_pretrained(
    _BASE, subfolder="tokenizer_2", revision=None, use_fast=False
)
noise_scheduler = DDPMScheduler.from_pretrained(_BASE, subfolder="scheduler")

text_encoder_one = CLIPTextModel.from_pretrained(
    _BASE, subfolder="text_encoder", torch_dtype=torch.float16
)
text_encoder_two = CLIPTextModelWithProjection.from_pretrained(
    _BASE, subfolder="text_encoder_2", torch_dtype=torch.float16
)
image_encoder = CLIPVisionModelWithProjection.from_pretrained(
    _BASE, subfolder="image_encoder", torch_dtype=torch.float16
)
vae = AutoencoderKL.from_pretrained(
    _BASE, subfolder="vae", torch_dtype=torch.float16
)
UNet_Encoder = UNet2DConditionModel_ref.from_pretrained(
    _BASE, subfolder="unet_encoder", torch_dtype=torch.float16
)

parsing_model = Parsing(0)

for m in (UNet_Encoder, image_encoder, vae, unet, text_encoder_one, text_encoder_two):
    m.requires_grad_(False)

tensor_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),
])

pipe = TryonPipeline.from_pretrained(
    _BASE,
    unet=unet,
    vae=vae,
    feature_extractor=CLIPImageProcessor(),
    text_encoder=text_encoder_one,
    text_encoder_2=text_encoder_two,
    tokenizer=tokenizer_one,
    tokenizer_2=tokenizer_two,
    scheduler=noise_scheduler,
    image_encoder=image_encoder,
    torch_dtype=torch.float16,
)
pipe.unet_encoder = UNet_Encoder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pil_to_binary_mask(pil_image: Image.Image, threshold: int = 0) -> Image.Image:
    np_image = np.array(pil_image)
    grayscale = Image.fromarray(np_image).convert("L")
    binary = np.array(grayscale) > threshold
    mask = (binary.astype(np.uint8) * 255)
    return Image.fromarray(mask)


# ---------------------------------------------------------------------------
# Core try-on function
# ---------------------------------------------------------------------------

def start_tryon(
    human_img_orig: Image.Image,
    mask_image: Image.Image,
    garm_img: Image.Image,
    garment_des: str,
    is_checked: bool,
    is_checked_crop: bool,
    denoise_steps: int,
    seed: int,
) -> tuple[Image.Image, Image.Image]:
    """
    Parameters
    ----------
    human_img_orig  : PIL Image — reference human model (from Stage 1)
    mask_image      : PIL Image — binary clothing mask (from Stage 2)
    garm_img        : PIL Image — target garment to apply
    garment_des     : str       — text description of the garment (used in prompt)
    is_checked      : bool      — if True, use automatic mask from human parsing
                                  (currently disabled; pass False to use provided mask)
    is_checked_crop : bool      — if True, auto-crop image to 3:4 aspect ratio first
    denoise_steps   : int       — number of DDPM denoising steps (30 recommended)
    seed            : int       — random seed for reproducibility

    Returns
    -------
    result_image : PIL Image — virtual try-on output at 768×1024
    mask_gray    : PIL Image — greyscale masked region for reference
    """
    pipe.to(device)
    pipe.unet_encoder.to(device)

    garm_img = garm_img.convert("RGB").resize((768, 1024))

    if is_checked_crop:
        w, h = human_img_orig.size
        target_w = int(min(w, h * (3 / 4)))
        target_h = int(min(h, w * (4 / 3)))
        left   = (w - target_w) / 2
        top    = (h - target_h) / 2
        right  = (w + target_w) / 2
        bottom = (h + target_h) / 2
        cropped = human_img_orig.crop((left, top, right, bottom))
        crop_size = cropped.size
        human_img = cropped.resize((768, 1024))
    else:
        human_img = human_img_orig.resize((768, 1024))

    if is_checked:
        # Automatic mask via human parsing (currently disabled)
        mask = mask_image.resize((768, 1024))
    else:
        mask = mask_image.resize((768, 1024))

    mask_gray = (1 - transforms.ToTensor()(mask)) * tensor_transform(human_img)
    mask_gray = to_pil_image((mask_gray + 1.0) / 2.0)

    # DensePose body estimation
    human_img_arg = _apply_exif_orientation(human_img.resize((768, 1024)))
    human_img_arg = convert_PIL_to_numpy(human_img_arg, format="BGR")

    densepose_args = apply_net.create_argument_parser().parse_args((
        "show",
        "configs/densepose_rcnn_R_50_FPN_s1x.yaml",
        DENSEPOSE_PKL,
        "dp_segm", "-v",
        "--opts", "MODEL.DEVICE", "cuda",
    ))
    pose_img = densepose_args.func(densepose_args, human_img_arg)
    pose_img = pose_img[:, :, ::-1]
    pose_img = Image.fromarray(pose_img).resize((768, 1024))

    with torch.no_grad():
        with torch.cuda.amp.autocast():
            prompt = "model is wearing " + garment_des
            negative_prompt = "monochrome, lowres, bad anatomy, worst quality, low quality"

            with torch.inference_mode():
                (
                    prompt_embeds,
                    negative_prompt_embeds,
                    pooled_prompt_embeds,
                    negative_pooled_prompt_embeds,
                ) = pipe.encode_prompt(
                    prompt,
                    num_images_per_prompt=1,
                    do_classifier_free_guidance=True,
                    negative_prompt=negative_prompt,
                )

                prompt_c = "a photo of " + garment_des
                negative_prompt_c = "monochrome, lowres, bad anatomy, worst quality, low quality"
                if not isinstance(prompt_c, List):
                    prompt_c = [prompt_c]
                if not isinstance(negative_prompt_c, List):
                    negative_prompt_c = [negative_prompt_c]

                with torch.inference_mode():
                    (prompt_embeds_c, _, _, _) = pipe.encode_prompt(
                        prompt_c,
                        num_images_per_prompt=1,
                        do_classifier_free_guidance=False,
                        negative_prompt=negative_prompt_c,
                    )

                pose_tensor = tensor_transform(pose_img).unsqueeze(0).to(device, torch.float16)
                garm_tensor = tensor_transform(garm_img).unsqueeze(0).to(device, torch.float16)
                generator = torch.Generator(device).manual_seed(seed) if seed is not None else None

                images = pipe(
                    prompt_embeds=prompt_embeds.to(device, torch.float16),
                    negative_prompt_embeds=negative_prompt_embeds.to(device, torch.float16),
                    pooled_prompt_embeds=pooled_prompt_embeds.to(device, torch.float16),
                    negative_pooled_prompt_embeds=negative_pooled_prompt_embeds.to(device, torch.float16),
                    num_inference_steps=denoise_steps,
                    generator=generator,
                    strength=1.0,
                    pose_img=pose_tensor,
                    text_embeds_cloth=prompt_embeds_c.to(device, torch.float16),
                    cloth=garm_tensor,
                    mask_image=mask,
                    image=human_img,
                    height=1024,
                    width=768,
                    ip_adapter_image=garm_img.resize((768, 1024)),
                    guidance_scale=2.0,
                )[0]

    if is_checked_crop:
        out = images[0].resize(crop_size)
        human_img_orig.paste(out, (int(left), int(top)))
        return human_img_orig, mask_gray

    return images[0], mask_gray


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Realistic virtual try-on using IDM-VTON.")
    parser.add_argument("--reference_image", type=str, required=True,
                        help="Path to the reference human model image (Stage 1 output).")
    parser.add_argument("--mask",            type=str, required=True,
                        help="Path to the binary clothing mask (Stage 2 output).")
    parser.add_argument("--garment",         type=str, required=True,
                        help="Path to the target garment image.")
    parser.add_argument("--cloth_type",      type=str, required=True,
                        help="Short text description of the garment (used in the prompt).")
    parser.add_argument("--output_path",     type=str, required=True,
                        help="Output path for the final try-on image.")
    parser.add_argument("--denoise_steps",   type=int, default=30,
                        help="Number of DDPM denoising steps (default: 30).")
    parser.add_argument("--seed",            type=int, default=42,
                        help="Random seed for reproducibility (default: 42).")

    args, _ = parser.parse_known_args()

    reference_image = Image.open(args.reference_image)
    mask_image      = Image.open(args.mask)
    garment_image   = Image.open(args.garment)

    result, _ = start_tryon(
        reference_image,
        mask_image,
        garment_image,
        args.cloth_type,
        is_checked=False,
        is_checked_crop=False,
        denoise_steps=args.denoise_steps,
        seed=args.seed,
    )
    result.save(args.output_path)
    log.info("Result saved: %s", args.output_path)


if __name__ == "__main__":
    main()
