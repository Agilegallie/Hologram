#!/usr/bin/env python3
"""
Hologram Pyramid Cross Generator

- Creates a square canvas with a 4-view cross layout.
- Leaves a blank square in the middle for the pyramid opening.
- Rotates views to face outward (0°, 270°, 180°, 90°).
- Optional blue hologram tint + scan lines.

Dependencies: Pillow

Usage:
    python hologram_cross.py input.jpg --out cross.png --holo cross_blue.png         --canvas 1170 --blank 400 --size 300 --inset 50
"""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

# ---- Core helpers -----------------------------------------------------------

def load_rgba(path: Path) -> Image.Image:
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    return img

def make_canvas(size: int, bg: int = 0) -> Image.Image:
    return Image.new("RGBA", (size, size), (bg, bg, bg, 255))

def place_four_outwards(canvas: Image.Image, subject: Image.Image, blank: int, inset: int) -> None:
    """Place four rotated copies around a centered blank square.

    Orientations (outward):
      - North  : 0°
      - East   : 270°
      - South  : 180°
      - West   : 90°
    """
    W, H = canvas.size
    cx, cy = W // 2, H // 2
    hb = blank // 2

    placements = [
        ((cx - subject.width // 2,           cy - hb - subject.height + inset),   0),   # North
        ((cx + hb - inset,                   cy - subject.height // 2),           270), # East (faces right)
        ((cx - subject.width // 2,           cy + hb - inset),                    180), # South
        ((cx - hb - subject.width + inset,   cy - subject.height // 2),           90),  # West (faces left)
    ]

    for (x, y), angle in placements:
        rotated = subject.rotate(angle, expand=True)
        canvas.paste(rotated, (x, y), rotated)

def to_blue_hologram(img: Image.Image, scan_step: int = 4, scan_strength: float = 0.5) -> Image.Image:
    """Convert RGBA image to a blue hologram look with scan lines.
    Pure-Pillow approach (no NumPy required).
    """
    gray = ImageOps.grayscale(img)
    blue = ImageOps.colorize(gray, black="#001018", white="#58c6ff")

    if img.mode == "RGBA":
        blue.putalpha(img.split()[-1])

    draw = ImageDraw.Draw(blue, mode="RGBA")
    W, H = blue.size
    alpha = int(255 * scan_strength)
    for y in range(0, H, scan_step):
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    return blue

# ---- CLI -------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Generate a 4-view hologram cross image.")
    p.add_argument("input", type=Path, help="Input image (PNG/JPG/etc.)")
    p.add_argument("--out", type=Path, default=Path("cross.png"), help="Output cross image path")
    p.add_argument("--holo", type=Path, default=None, help="Optional blue hologram output path")
    p.add_argument("--canvas", type=int, default=1170, help="Square canvas size in px (default 1170)")
    p.add_argument("--blank", type=int, default=400, help="Central blank square size in px (default 400)")
    p.add_argument("--size", type=int, default=300, help="Max width/height of subject in px (default 300)")
    p.add_argument("--inset", type=int, default=50, help="Move subjects towards center by px (default 50)")
    p.add_argument("--bg", type=int, default=0, help="Background gray level 0-255 (default 0 = black)")

    args = p.parse_args()

    subj = load_rgba(args.input)
    subj = ImageOps.contain(subj, (args.size, args.size))

    canvas = make_canvas(args.canvas, args.bg)
    place_four_outwards(canvas, subj, blank=args.blank, inset=args.inset)

    W, H = canvas.size
    cx, cy = W // 2, H // 2
    hb = args.blank // 2
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([cx - hb, cy - hb, cx + hb, cy + hb], fill=(args.bg, args.bg, args.bg, 255))

    canvas.save(args.out)
    print(f"Saved cross layout -> {args.out}")

    if args.holo:
        holo = to_blue_hologram(canvas)
        holo.save(args.holo)
        print(f"Saved blue hologram -> {args.holo}")

if __name__ == "__main__":
    main()
