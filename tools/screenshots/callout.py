"""Draw red callout boxes (and an optional label) on a capture.

    callout.py IN OUT x0 y0 x1 y1 [x0 y0 x1 y1 ...] [--label "text"] [--at above|below|right]

Coordinates are in the image's own pixels (open the PNG to read them; captures at 175 % are
1.75x the 100 % size). Several boxes may be given; the label, if any, goes next to the first.
The style matches across the ArcGIS Tips figures: a 4 px #D62728 rounded rectangle and a label
in white-on-red, so use one or two callouts per image at most.
"""
import argparse

from PIL import Image, ImageDraw, ImageFont

RED = (214, 39, 40)
STROKE = 4
PAD = 6


def font(size):
    for name in ("segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("coords", nargs="+", type=int)
    ap.add_argument("--label")
    ap.add_argument("--at", default="below", choices=["above", "below", "right"])
    ap.add_argument("--size", type=int, default=26)
    a = ap.parse_args()
    if len(a.coords) % 4:
        ap.error("coordinates come in groups of four")

    im = Image.open(a.inp).convert("RGB")
    boxes = [a.coords[i:i + 4] for i in range(0, len(a.coords), 4)]
    label_h = 0
    if a.label:
        f = font(a.size)
        tw, th = ImageDraw.Draw(im).textbbox((0, 0), a.label, font=f)[2:]
        label_h = th + 2 * PAD + 8
    # Grow the canvas if a label would fall off the top or bottom edge.
    top_pad = bottom_pad = 0
    if a.label:
        x0, y0, x1, y1 = boxes[0]
        if a.at == "above" and y0 - PAD - label_h < 0:
            top_pad = label_h
        if a.at == "below" and y1 + PAD + label_h > im.height:
            bottom_pad = label_h
    if top_pad or bottom_pad:
        big = Image.new("RGB", (im.width, im.height + top_pad + bottom_pad), (255, 255, 255))
        big.paste(im, (0, top_pad))
        im = big
        boxes = [[x0, y0 + top_pad, x1, y1 + top_pad] for x0, y0, x1, y1 in boxes]

    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:
        d.rounded_rectangle([x0 - PAD, y0 - PAD, x1 + PAD, y1 + PAD], radius=8, outline=RED,
                            width=STROKE)
    if a.label:
        x0, y0, x1, y1 = boxes[0]
        if a.at == "above":
            lx, ly = x0 - PAD, y0 - PAD - label_h + 4
        elif a.at == "below":
            lx, ly = x0 - PAD, y1 + PAD + 4
        else:
            lx, ly = x1 + PAD + 8, (y0 + y1) // 2 - label_h // 2
        lx = max(0, min(lx, im.width - tw - 2 * PAD))
        d.rounded_rectangle([lx, ly, lx + tw + 2 * PAD, ly + th + 2 * PAD], radius=6, fill=RED)
        d.text((lx + PAD, ly + PAD - 2), a.label, font=f, fill=(255, 255, 255))
    im.save(a.out)
    print(a.out, im.size)


if __name__ == "__main__":
    main()
