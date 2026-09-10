#!/usr/bin/env python3
"""Compose the "Make the threshold a parameter" figure on Week 3, Part B.

    python3 tools/week03_threshold_parameter_figure.py MODEL.png DIALOG.png

Two real ArcGIS Pro captures side by side: the tail of the Lab 2 NDVI model, where the Threshold
variable carries its P, and the tool dialog that P produces. It replaces a hand-drawn schematic.

The captures come from a live session — see the Lessons in tools/screenshots/README.md for how they
are taken (175 % display scaling, grabwin.py, Claude window parked). Nothing here is drawn except
the two labels, the arrow between the panels and the frame around each capture.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = (Path(__file__).resolve().parent.parent / "slides" / "week-03" / "images"
       / "ra-threshold-parameter.png")
NAVY = (0, 46, 93)
INK = (75, 85, 99)
FRAME = (154, 166, 182)
DIALOG_SCALE = 0.82
PAD, GAP, LABEL_H, CAP_H = 34, 78, 46, 44


def font(size, bold=False):
    for name in (("segoeuib.ttf", "seguisb.ttf") if bold else ("segoeui.ttf",)):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main(model_path, dialog_path):
    model = Image.open(model_path).convert("RGB")
    dialog = Image.open(dialog_path).convert("RGB")
    dialog = dialog.resize((round(dialog.width * DIALOG_SCALE),
                            round(dialog.height * DIALOG_SCALE)), Image.LANCZOS)

    body_h = max(model.height, dialog.height)
    w = PAD * 2 + model.width + GAP + dialog.width
    h = LABEL_H + body_h + CAP_H
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)

    mx, my = PAD, LABEL_H + (body_h - model.height) // 2
    dx, dy = PAD + model.width + GAP, LABEL_H
    im.paste(model, (mx, my))
    im.paste(dialog, (dx, dy))
    for box in ((mx, my, mx + model.width, my + model.height),
                (dx, dy, dx + dialog.width, dy + dialog.height)):
        d.rectangle([box[0] - 1, box[1] - 1, box[2], box[3]], outline=FRAME, width=2)

    f_lab, f_cap = font(23, bold=True), font(19)
    d.text((mx + model.width // 2, LABEL_H - 16), "In the model",
           font=f_lab, fill=NAVY, anchor="mb")
    d.text((dx + dialog.width // 2, LABEL_H - 16), "On the tool dialog",
           font=f_lab, fill=NAVY, anchor="mb")

    # The arrow between the panels, on the model's centre line.
    ay = my + model.height // 2
    ax0, ax1 = mx + model.width + 16, dx - 16
    d.line([ax0, ay, ax1 - 14, ay], fill=NAVY, width=7)
    d.polygon([(ax1, ay), (ax1 - 18, ay - 12), (ax1 - 18, ay + 12)], fill=NAVY)
    d.text(((ax0 + ax1) // 2, ay - 16), "gives", font=f_cap, fill=NAVY, anchor="mb")

    d.text((w // 2, h - 14),
           "ArcGIS Pro 3.7.1, the Lab 2 NDVI model. The P on Threshold is what puts the "
           "Threshold box on the dialog.", font=f_cap, fill=INK, anchor="mb")

    im.save(OUT)
    print(f"wrote {OUT} {im.size}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else r"C:\Ames\cap-model.png",
         sys.argv[2] if len(sys.argv) > 2 else r"C:\Ames\cap-dialog.png")
