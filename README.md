# Hologram Pyramid Cross Generator

A tiny, well‑documented Python script that turns **any image** into a **4‑view cross layout** for smartphone **holographic pyramid** projectors. It also includes an optional **blue hologram + scan‑lines** effect.

Works great with Grok/Runway/Pika/etc. for animating after the layout is generated.

---

## Features

* Outputs a **1170×1170** square by default (iPhone 14 fit).
* Adds a **400×400 px** black blank square in the center for the pyramid’s opening.
* Places the subject **four times** (North/East/South/West) and rotates them to face **outwards**:

  * North: **0°**
  * East: **270°** (so it faces right/outward)
  * South: **180°**
  * West: **90°** (so it faces left/outward)
* Adjustable subject size and inward offset.
* Optional **blue hologram** tint with **scan lines**.

---

## Quick Start

```bash
# 1) Create a virtual env (optional)
python -m venv .venv && source .venv/bin/activate  # on macOS/Linux
# or: .venv\Scripts\activate  # on Windows

# 2) Install dependency
pip install Pillow

# 3) Run
python hologram_cross.py input.jpg --out cross.png --holo cross_holo.png
```

> Tip: If you want the blue hologram version only, use `--holo` and then display that on your phone.

---

## Usage

```bash
python hologram_cross.py <input_image> [options]
```

**Options**

* `--out PATH` – Save the basic cross layout to this file (PNG/JPG).
* `--holo PATH` – Also save a blue hologram + scan lines version.
* `--canvas 1170` – Square canvas size in pixels (default **1170**).
* `--blank 400` – Size of the central blank square in pixels (default **400**).
* `--size 300` – Max width/height for the subject image (default **300**).
* `--inset 50` – How far to nudge each subject **towards the center** (default **50**).
* `--bg 0` – Background gray level 0–255 (default **0** = black).

---

## Example Commands

```bash
# iPhone 14 defaults with all outputs
python hologram_cross.py me.jpg --out scan_cross.png --holo scan_cross_blue.png

# Bigger center opening, slightly smaller subject
python hologram_cross.py ani.png --blank 500 --size 260 --out ani_cross.png --holo ani_cross_blue.png

# Square canvas for other phones (e.g., 1440x1440)
python hologram_cross.py butterfly.png --canvas 1440 --out butterfly_cross.png
```

---

## Grok/Animator Prompt (drop‑in)

```
Create a 10‑second seamlessly looping animation on a square canvas of 1170×1170 px for a 4‑sided holographic pyramid projector. Use the provided cross layout image as the exact composition guide.

Keep the black background and the 400×400 px blank square in the center. Respect the outward orientation:
- Top (North): 0°
- Right (East): 270°
- Bottom (South): 180°
- Left (West): 90°

Apply a translucent blue hologram look with gentle flicker, scan lines, and subtle distortion. Ensure the loop is seamless.
```

---

## License

MIT License — do whatever you want; attribution appreciated.

---

## File: `hologram_cross.py`

```python
#!/usr/bin/env python3
"""
Hologram Pyramid Cross Generator

- Creates a square canvas with a 4-view cross layout.
- Leaves a blank square in the middle for the pyramid opening.
- Rotates views to face outward (0°, 270°, 180°, 90°).
- Optional blue hologram tint + scan lines.

Dependencies: Pillow

Usage:
    python hologram_cross.py input.jpg --out cross.png --holo cross_blue.png \
        --canvas 1170 --blank 400 --size 300 --inset 50
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
    # Convert to grayscale then colorize with a blue gradient
    gray = ImageOps.grayscale(img)
    # Map black->near black, white->electric blue
    blue = ImageOps.colorize(gray, black="#001018", white="#58c6ff")

    # Re-apply alpha channel from original
    if img.mode == "RGBA":
        blue.putalpha(img.split()[-1])

    # Add horizontal scan lines by drawing semi-transparent stripes
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

    # Load & resize subject
    subj = load_rgba(args.input)
    subj = ImageOps.contain(subj, (args.size, args.size))

    # Build base cross
    canvas = make_canvas(args.canvas, args.bg)
    place_four_outwards(canvas, subj, blank=args.blank, inset=args.inset)

    # Draw the central blank explicitly (kept black)
    # (Not strictly necessary since background is black, but ensures it's clear)
    W, H = canvas.size
    cx, cy = W // 2, H // 2
    hb = args.blank // 2
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([cx - hb, cy - hb, cx + hb, cy + hb], fill=(args.bg, args.bg, args.bg, 255))

    # Save base cross
    canvas.save(args.out)
    print(f"Saved cross layout -> {args.out}")

    # Optional hologram look
    if args.holo:
        holo = to_blue_hologram(canvas)
        holo.save(args.holo)
        print(f"Saved blue hologram -> {args.holo}")

if __name__ == "__main__":
    main()
```

---

## requirements.txt

```
Pillow>=10.0.0
```

---

## Notes

* If your input has a non‑transparent background, it will still work; the script treats it as part of the subject.
* For very large images, run them through `--size` to dial in how big your subject appears.
* You can change `--canvas` to match other phone resolutions (e.g., 1242, 1440). Keep the display black around the cross for best reflections.
