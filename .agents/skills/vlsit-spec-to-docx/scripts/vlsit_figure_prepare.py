#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# File     : vlsit_figure_prepare.py
# Function : copy a figure and crop it to the drawing area when the image also carries tables
# Author   : VLSI Technology
# GitHub   : https://github.com/nguyenquanicd/VLSIT_ASIC_SOC_AI_SKILLS
# ---------------------------------------------------------------------------
"""Prepare a figure for insertion.

A draw.io export often puts the block diagram, the block-description table, the
interface table and the legend on one canvas. The template already carries its own
tables, so only the drawing is inserted (rule R-012). The crop keeps the region
above the first wide blank band that separates the drawing from the tables.

Exit codes:
    0  image written
    3  Pillow missing, file copied but not cropped
    4  no crop band found, file copied unchanged

Usage:
    vlsit_figure_prepare.py <image> --out <folder> [--mode auto|none] [--suffix _diagram]
"""

import argparse
import os
import shutil
import sys

try:
    from PIL import Image
except ImportError:
    Image = None


def find_split(image):
    """Return the y coordinate of the first wide blank band below the drawing, or None."""
    gray = image.convert("L")
    width, height = gray.size
    step = max(1, width // 400)
    pixels = gray.load()

    def row_ink(y):
        dark = 0
        total = 0
        for x in range(0, width, step):
            total += 1
            if pixels[x, y] < 245:
                dark += 1
        return dark / float(total)

    start = int(height * 0.25)
    band_min = max(12, int(height * 0.02))
    band_start = None
    for y in range(start, height):
        if row_ink(y) < 0.004:
            if band_start is None:
                band_start = y
        else:
            if band_start is not None and y - band_start >= band_min:
                return band_start
            band_start = None
    return None


def main():
    parser = argparse.ArgumentParser(description="Prepare a figure for the DOCX template.")
    parser.add_argument("image", help="the source image (png, jpg, svg, ...)")
    parser.add_argument("--out", required=True, help="output folder")
    parser.add_argument("--mode", choices=("auto", "none"), default="auto")
    parser.add_argument("--suffix", default="_diagram", help="suffix added to the file name")
    parser.add_argument("--force", action="store_true", help="overwrite an existing output image")
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print("ERROR image not found: %s" % args.image)
        return 2
    os.makedirs(args.out, exist_ok=True)
    stem, extension = os.path.splitext(os.path.basename(args.image))
    target = os.path.join(args.out, stem + args.suffix + ".png")
    if os.path.exists(target) and not args.force:
        print("ERROR output exists, pass --force to overwrite: %s" % target)
        return 2

    if Image is None:
        shutil.copyfile(args.image, target)
        print("NO-CROP Pillow is not installed; the image was copied unchanged to %s" % target)
        print("Ask the user to approve Pillow, or export a diagram-only image from the source tool.")
        return 3

    try:
        image = Image.open(args.image)
        image.load()
    except OSError as exc:
        print("ERROR cannot open the image (%s); convert it to PNG or JPG first: %s" % (exc, args.image))
        return 2

    if args.mode == "none" or extension.lower() == ".svg":
        image.convert("RGB").save(target, "PNG")
        print("COPY  %s (%dx%d) -> %s" % (args.image, image.width, image.height, target))
        return 0

    split = find_split(image)
    if split is None:
        image.convert("RGB").save(target, "PNG")
        print("NO-BAND no separating band found; the whole image was saved to %s" % target)
        print("Show it to the user and ask for a diagram-only export if it still carries tables.")
        return 4

    cropped = image.crop((0, 0, image.width, split))
    cropped.convert("RGB").save(target, "PNG")
    print("CROP  box=(0,0,%d,%d) of %dx%d -> %s" % (cropped.width, cropped.height,
                                                    image.width, image.height, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
