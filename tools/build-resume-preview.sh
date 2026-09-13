#!/usr/bin/env bash
# Rebuild the resume page image shown on /resume/ from the resume PDF.
#
# Run this after replacing assets/Joseph_Resch_Resume.pdf, or the page will
# still show the old resume:
#
#     ./tools/build-resume-preview.sh
#
# Requires poppler (brew install poppler) and Pillow (pip3 install Pillow).

set -euo pipefail

cd "$(dirname "$0")/.."

PDF="assets/Joseph_Resch_Resume.pdf"
OUT_BASE="assets/resume-preview"
DPI=200

command -v pdftoppm >/dev/null || { echo "pdftoppm not found. brew install poppler"; exit 1; }
python3 -c "import PIL" 2>/dev/null || { echo "Pillow not found. pip3 install Pillow"; exit 1; }
[ -f "$PDF" ] || { echo "Missing $PDF"; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Page 1 only: the site shows a single sheet.
pdftoppm -png -r "$DPI" -aa yes -aaVector yes -f 1 -l 1 "$PDF" "$TMP/page"

python3 - "$TMP" "$OUT_BASE" <<'PY'
import glob, sys
from PIL import Image

tmp, out_base = sys.argv[1], sys.argv[2]
src = sorted(glob.glob(f"{tmp}/page*.png"))[0]

# The sheet is black text on white, so greyscale costs nothing and compresses
# far better than RGB. Lossless WebP beats PNG by ~45% on this kind of image;
# the PNG is only the fallback for browsers without WebP.
im = Image.open(src).convert("L")
im.save(f"{out_base}.webp", lossless=True, quality=100, method=6)
im.save(f"{out_base}.png", optimize=True)
print(f"{out_base}.webp / .png  {im.width}x{im.height}")
PY
