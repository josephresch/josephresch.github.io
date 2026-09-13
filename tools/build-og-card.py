#!/usr/bin/env python3
"""Rebuild assets/og-card.png, the 1200x630 image link previews use.

Run from the repository root after changing the headshot or the tagline:

    python3 tools/build-og-card.py

Requires Pillow (pip3 install Pillow). Uses Helvetica Neue, which ships with
macOS and stands in for the site's Inter at this size.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
HEADSHOT = ROOT / "assets" / "headshot.jpg"
OUT = ROOT / "assets" / "og-card.png"

W, H = 1200, 630
BG, INK, TEXT, MUTED = (255, 255, 255), (10, 10, 10), (53, 58, 66), (107, 114, 128)
LINE, STRONG, ACCENT = (230, 232, 236), (214, 218, 224), (37, 99, 235)

FONT_FILE = "/System/Library/Fonts/HelveticaNeue.ttc"
REGULAR, BOLD, MEDIUM = 0, 1, 10

NAME = "Joseph Resch"
ROLE = "Applied Statistician & Data Scientist"
LEAD = ["Bayesian modeling · Causal inference",
        "Experimentation · Machine learning"]
SUB = "Statistics Ph.D., UCLA"


def font(size, index):
    return ImageFont.truetype(FONT_FILE, size, index=index)


def tracked(draw, xy, text, fnt, fill, track):
    """Draw text with manual letter-spacing, which Pillow has no setting for."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + track


def circular_portrait(diameter, supersample=4):
    """Crop the headshot the way the site's CSS does, then mask it to a circle."""
    src = Image.open(HEADSHOT).convert("RGB")
    w, h = src.size
    side = min(w, h)
    # Matches `object-fit: cover; object-position: center 20%` in main.scss.
    box = ((w - side) // 2, int((h - side) * 0.20))
    square = src.crop((box[0], box[1], box[0] + side, box[1] + side))

    big = diameter * supersample
    ring = Image.new("RGB", (big, big), BG)
    ring.paste(square.resize((big, big), Image.LANCZOS), (0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, big - 1, big - 1), outline=STRONG, width=supersample)

    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big - 1, big - 1), fill=255)

    return (ring.resize((diameter, diameter), Image.LANCZOS),
            mask.resize((diameter, diameter), Image.LANCZOS))


def main():
    card = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(card)

    diameter = 300
    portrait, mask = circular_portrait(diameter)
    px, py = 124, (H - diameter) // 2 - 4
    card.paste(portrait, (px, py), mask)

    x = px + diameter + 78
    y = py + 2

    # Name first, role beneath it.
    draw.text((x, y), NAME, font=font(84, BOLD), fill=INK)
    y += 104
    draw.text((x, y), ROLE, font=font(30, MEDIUM), fill=ACCENT)
    y += 56
    draw.line([(x, y), (x + 540, y)], fill=LINE, width=2)
    y += 30
    for line in LEAD:
        draw.text((x, y), line, font=font(29, MEDIUM), fill=TEXT)
        y += 40
    y += 8
    draw.text((x, y), SUB, font=font(26, REGULAR), fill=MUTED)

    draw.rectangle([(0, H - 10), (W, H)], fill=ACCENT)

    card.save(OUT, optimize=True)
    print(f"{OUT.relative_to(ROOT)}  {card.width}x{card.height}")


if __name__ == "__main__":
    main()
