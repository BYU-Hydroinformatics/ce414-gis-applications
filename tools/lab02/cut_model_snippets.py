# Cut the per-step ModelBuilder snippets for the Lab 2 page from the model's SVG export,
# so the snippets, Figure C and the tool dialogs all come from the same run.
#
#   "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\lab02\cut_model_snippets.py
#
# Source: docs/assignments/lab-02/images/lab02-model-overview.svg, exported from ModelBuilder
# (Export > Export To Graphic, SVG, nothing selected). It is rendered at 3x with headless Chrome
# (1 SVG unit = 4 px; do NOT pass --disable-gpu, it renders blank here) and cropped by the
# resolved label positions. Steps 1-3 happen before Step 4 marks anything as a parameter, so
# those three snippets are cut from a copy of the SVG with the P markers removed.
import os, re, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "assignments", "lab-02", "images"))
SRC = os.path.join(IMAGES, "lab02-model-overview.svg")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCALE = 3                      # device scale factor; the SVG is 909.84 pt = 1213 px wide at 1x
WINDOW = (1214, 154)           # a hair larger than the SVG so nothing is clipped

# Crops in rendered pixels (3642 x 462). Columns are 100.5 SVG units (402 px) apart.
# (box, keep P markers, regions to blank out because they do not exist yet at that step)
CROPS = {
    # Step 1: the two inputs, the two Float tools and their outputs
    "lab02-float-tool-modelbuilder.png":        ((0, 0, 1215, 462), False, ()),
    # Step 2: Float outputs through Minus / Plus / Divide to NDVI; the Threshold variable
    # (bottom right, added in Step 5) is masked out
    "lab02-minus-plus-divide-modelbuilder.png": ((820, 0, 2800, 462), False, ((2400, 235, 2800, 462),)),
    # Step 3: NDVI into Reclassify, top row only (Threshold does not exist yet)
    "lab02-reclassify-modelbuilder.png":        ((2420, 0, 3642, 240), False, ()),
    # Step 5, Figure 16: both classification branches with the P markers
    "lab02-example-model-threshold.png":        ((2420, 0, 3642, 462), True, ()),
}


def strip_parameter_markers(svg_text):
    """Remove the P badges: each is a filled circle path, a <text>P</text>, and a stroked circle."""
    lines = svg_text.split("\n")
    drop = set()
    for i, line in enumerate(lines):
        if ">P</text>" in line:
            for j in (i - 1, i, i + 1):
                assert j == i or "<path d=\"M" in lines[j], "unexpected markup around a P marker"
                drop.add(j)
    assert len(drop) == 15, f"expected 5 markers x 3 elements, found {len(drop)} lines"
    return "\n".join(l for i, l in enumerate(lines) if i not in drop)


def render(svg_path, png_path):
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars",
                    f"--force-device-scale-factor={SCALE}",
                    f"--window-size={WINDOW[0]},{WINDOW[1]}",
                    f"--screenshot={png_path}", "file:///" + svg_path.replace("\\", "/")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png_path)
    assert im.size[0] >= 3600, f"render came out {im.size}; is Chrome at {CHROME}?"
    return im


def main():
    svg = open(SRC, encoding="utf-8").read()
    with tempfile.TemporaryDirectory() as tmp:
        with_p = render(SRC, os.path.join(tmp, "with_p.png"))
        nop_svg = os.path.join(tmp, "no_p.svg")
        open(nop_svg, "w", encoding="utf-8").write(strip_parameter_markers(svg))
        no_p = render(nop_svg, os.path.join(tmp, "no_p.png"))
        for name, (box, keep_p, masks) in CROPS.items():
            src = (with_p if keep_p else no_p).copy()
            for m in masks:
                src.paste((255, 255, 255), m)
            out = os.path.join(IMAGES, name)
            src.crop(box).save(out, optimize=True)
            print(f"{name}: {box} {'with' if keep_p else 'without'} P markers, {len(masks)} mask(s)")


if __name__ == "__main__":
    main()
