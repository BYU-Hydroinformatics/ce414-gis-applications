# Render the per-step ModelBuilder snippets for the Lab 2 page from ModelBuilder's own SVG exports,
# one export per step, so no snippet shows a tool that does not exist yet at that step.
#
#   "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\lab02\render_model_snippets.py
#
# Inputs: tools/lab02/model-svg/*.svg, exported from ModelBuilder (Export > Export To Graphic, SVG,
# nothing selected) after Step 1, Step 2, Step 3 and after Step 5. Each is rendered at 3x with
# headless Chrome (do NOT pass --disable-gpu, it renders blank here), cropped to the part of the
# model the step is about, trimmed to content, and written to docs/assignments/lab-02/images.
# NDVI-final.svg is also copied there as lab02-model-overview.svg (Figure C).
import os, re, shutil, subprocess, tempfile
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SVGS = os.path.join(HERE, "model-svg")
IMAGES = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "assignments", "lab-02", "images"))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCALE = 3

# (svg, crop box in rendered px or None for the whole thing, output name)
# Columns of the model are 100.5 SVG pt apart; 1 pt = 4 px at 3x.
SNIPPETS = [
    ("step1-float.svg",      None,                 "lab02-float-tool-modelbuilder.png"),        # Step 1
    ("step2-ndvi.svg",       (820, 0, None, None), "lab02-minus-plus-divide-modelbuilder.png"), # Step 2: from NIR_Float on
    ("step3-reclassify.svg", (2440, 0, None, None), "lab02-reclassify-modelbuilder.png"),       # Step 3: NDVI on
    ("NDVI-final.svg",       (2440, 0, None, None), "lab02-example-model-threshold.png"),       # Step 5, Figure 16
]


def render(svg_path):
    text = open(svg_path, encoding="utf-8").read()
    w = float(re.search(r'width="([\d.]+)pt"', text).group(1))
    h = float(re.search(r'height="([\d.]+)pt"', text).group(1))
    W, H = int(w * 4 / 3) + 2, int(h * 4 / 3) + 2  # pt -> CSS px, a hair larger so nothing clips
    out = os.path.join(tempfile.gettempdir(), os.path.basename(svg_path) + ".png")
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", f"--force-device-scale-factor={SCALE}",
                    f"--window-size={W},{H}", f"--screenshot={out}", "file:///" + svg_path.replace("\\", "/")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(out).convert("RGB")


def trim(im, margin=12):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).getbbox()
    if not bb:
        return im
    return im.crop((max(bb[0] - margin, 0), max(bb[1] - margin, 0),
                    min(bb[2] + margin, im.size[0]), min(bb[3] + margin, im.size[1])))


def main():
    for svg, box, name in SNIPPETS:
        im = render(os.path.join(SVGS, svg))
        if box:
            x0, y0, x1, y1 = box
            im = im.crop((x0, y0, x1 or im.size[0], y1 or im.size[1]))
        im = trim(im)
        im.save(os.path.join(IMAGES, name))
        print(name, im.size)
    shutil.copy(os.path.join(SVGS, "NDVI-final.svg"), os.path.join(IMAGES, "lab02-model-overview.svg"))
    print("lab02-model-overview.svg copied")


if __name__ == "__main__":
    main()
