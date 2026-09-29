"""Crop the TNM Downloader captures (from week05_dem_sources.py tnm) to the part each step is about,
so the three-step slide is readable when projected.

The full captures are not committed; regenerate them first with
  python tools/week05_dem_sources.py tnm
then run from the repo root: python tools/week05_tnm_crops.py
"""
from pathlib import Path

from PIL import Image

IMG = Path("slides/week-05/images")

# (source, output, box as left, top, right, bottom in the 1600 x 1000 capture)
CROPS = [
    ("ed-tnm-step2.png", "ed-tnm-step2-crop.png", (0, 560, 660, 960)),   # Elevation Products + 1/3 arc-second, Current
    ("ed-tnm-step3.png", "ed-tnm-step3-crop.png", (0, 180, 1600, 640)),  # area-of-interest buttons + map zoomed to Provo
    ("ed-tnm-step4.png", "ed-tnm-step4-crop.png", (0, 128, 1400, 700)),  # Products list + tile footprint
]

for src, out, box in CROPS:
    Image.open(IMG / src).crop(box).save(IMG / out, optimize=True)
    print(out, box)
