"""
segment.py
----------
Stage 2 — Interactively segment a clothing region in a reference image using
Segment Anything Model (SAM ViT-H) and save the resulting binary mask.

The SAM weight is resolved through model_manager, which downloads it from
the configured Hugging Face repository on first use and caches it locally.

Usage — local desktop (requires a display)
------------------------------------------
    python segment.py --input "reference_images/crop_top.png"

    A Matplotlib window will open. Click exactly THREE points on the clothing
    region you want to mask. The window closes automatically after the third
    click, SAM runs segmentation, and the mask is saved as:
        reference_images/crop_top_mask.jpg

Usage — headless / Google Colab (no display available)
------------------------------------------------------
    python segment.py \\
        --input "reference_images/crop_top.png" \\
        --points "384,300,400,450,360,500"

    Pass comma-separated x,y coordinate pairs (3 pairs = 6 integers) to skip
    the interactive GUI entirely.
"""

import argparse
import logging as log

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import torch
from segment_anything import SamPredictor, sam_model_registry

from src.model_manager import get_sam_path

log.getLogger().setLevel(log.INFO)

# ---------------------------------------------------------------------------
# Resolve weight path via model_manager (downloads from HF if not cached)
# ---------------------------------------------------------------------------
SAM_CHECKPOINT = get_sam_path()

# ---------------------------------------------------------------------------
# Load SAM ViT-H onto CUDA
# ---------------------------------------------------------------------------
sam = sam_model_registry["vit_h"](checkpoint=SAM_CHECKPOINT)
sam.to(device="cuda")
predictor = SamPredictor(sam)


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------

def show_mask(mask: np.ndarray, ax, mask_name: str, random_color: bool = False) -> None:
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([255, 255, 255, 1])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    cv2.imwrite(mask_name, mask_image)
    ax.imshow(mask_image)


def show_points(coords: np.ndarray, labels: np.ndarray, ax, marker_size: int = 375) -> None:
    pos = coords[labels == 1]
    neg = coords[labels == 0]
    ax.scatter(pos[:, 0], pos[:, 1], color="green", marker="*",
               s=marker_size, edgecolor="white", linewidth=1.25)
    ax.scatter(neg[:, 0], neg[:, 1], color="red", marker="*",
               s=marker_size, edgecolor="white", linewidth=1.25)


# ---------------------------------------------------------------------------
# Core segmentation logic (shared by interactive and headless paths)
# ---------------------------------------------------------------------------

def _run_sam(image_path: str, garment_locations: list[list[int]]) -> None:
    """
    Run two-pass SAM prediction on *image_path* using the three provided
    click coordinates, then save the binary mask.
    """
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image)

    input_point = np.array(garment_locations[:3])   # exactly 3 points
    input_label = np.array([1, 1, 1])               # all positive prompts

    # Pass 1 — multi-mask to select the best logit
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    mask_input = logits[np.argmax(scores), :, :]

    # Pass 2 — refined single-mask using the best logit
    masks, _, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        mask_input=mask_input[None, :, :],
        multimask_output=False,
    )

    mask_path = image_path.rsplit(".", 1)[0] + "_mask.jpg"
    log.info("Saving mask: %s", mask_path)

    plt.figure(figsize=(10, 10))
    plt.imshow(image)
    show_mask(masks, plt.gca(), mask_path, random_color=False)
    show_points(input_point, input_label, plt.gca())
    plt.axis("off")
    plt.savefig(mask_path, bbox_inches="tight", pad_inches=0)  # safe for headless
    plt.show()

    log.info("Done. Mask saved: %s", mask_path)


# ---------------------------------------------------------------------------
# Interactive mode (local desktop — requires a display)
# ---------------------------------------------------------------------------

def parse_cloth_interactive(image_path: str) -> None:
    """Open a Matplotlib GUI and collect three click coordinates from the user."""
    log.info("Parsing (interactive mode)...")
    garment_locations: list[list[int]] = []

    img = mpimg.imread(image_path)
    fig, ax = plt.subplots()
    ax.imshow(img)

    def onclick(event) -> None:
        if event.xdata is None or event.ydata is None:
            return
        x, y = round(event.xdata), round(event.ydata)
        print(f"Point {len(garment_locations) + 1}: ({x}, {y})")
        garment_locations.append([x, y])
        if len(garment_locations) == 3:
            fig.canvas.mpl_disconnect(cid)
            plt.close(fig)

    cid = fig.canvas.mpl_connect("button_press_event", onclick)
    plt.title("Click THREE points on the clothing region")
    plt.show()   # blocking — waits until 3 clicks and window is closed

    _run_sam(image_path, garment_locations)


# ---------------------------------------------------------------------------
# Headless mode (Google Colab / servers — pass coordinates directly)
# ---------------------------------------------------------------------------

def parse_cloth_headless(image_path: str, points_str: str) -> None:
    """
    Parse pre-specified click coordinates and run SAM without opening a GUI.

    Parameters
    ----------
    image_path : str
        Path to the reference image.
    points_str : str
        Six comma-separated integers representing three (x, y) pairs,
        e.g. "384,300,400,450,360,500".
    """
    log.info("Parsing (headless mode)...")
    values = [int(v.strip()) for v in points_str.split(",")]
    if len(values) != 6:
        raise ValueError(
            "--points must contain exactly 6 comma-separated integers (3 x,y pairs). "
            f"Got {len(values)} values: {points_str!r}"
        )
    garment_locations = [[values[i], values[i + 1]] for i in range(0, 6, 2)]
    _run_sam(image_path, garment_locations)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a clothing mask using SAM ViT-H."
    )
    parser.add_argument(
        "--input", type=str, required=True,
        help="Input reference image (output of generate_model.py).",
    )
    parser.add_argument(
        "--points", type=str, default=None,
        help=(
            "Optional: six comma-separated integers for three (x,y) click points, "
            "e.g. '384,300,400,450,360,500'. "
            "When provided, the interactive GUI is skipped (use for headless / Colab runs)."
        ),
    )

    args, _ = parser.parse_known_args()

    if args.points:
        parse_cloth_headless(args.input, args.points)
    else:
        parse_cloth_interactive(args.input)


if __name__ == "__main__":
    main()
