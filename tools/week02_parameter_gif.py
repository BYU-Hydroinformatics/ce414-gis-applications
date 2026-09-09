"""Assemble slides/week-02/images/mbb-distance-parameter.gif, a slow-looping stepped animation of
"right-click Buffer > Create Variable > From Parameter > Distance, then right-click the new element >
Parameter" from seven screen grabs of ArcGIS Pro 3.7.1 (175 % scaling, ModelBuilder at 90 % zoom,
region 440,270-1425,745 in the 1456x819 desktop-control frame). The grabs live in the session
scratchpad (gif/f1-idle.png ... f7-pmarker.png); this script draws a cursor arrow at the click or
hover point of each frame, repairs three blemishes, blanks the scrollbars, and writes the GIF with
per-frame durations.

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools\\week02_parameter_gif.py SCRATCH_GIF_DIR
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

SRC = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "slides", "week-02", "images", "mbb-distance-parameter.gif")
F = 1920 / 1456          # desktop-control frame -> native pixels
X0, Y0 = 440, 270        # region origin in frame coordinates
WIDTH = 1000             # output width


def native(fx, fy):
    return int((fx - X0) * F), int((fy - Y0) * F)


def cursor(im, fx, fy):
    """A standard arrow cursor with its tip at the frame coordinate (fx, fy)."""
    x, y = native(fx, fy)
    d = ImageDraw.Draw(im)
    pts = [(x, y), (x, y + 30), (x + 8, y + 23), (x + 13, y + 35), (x + 19, y + 32), (x + 14, y + 21), (x + 24, y + 21)]
    d.polygon(pts, fill="#ffffff", outline="#000000")
    d.line(pts + [pts[0]], fill="#000000", width=2)
    return im


# (file, cursor frame coords or None, duration ms)
FRAMES = [
    ("f1-idle.png", None, 1600),
    ("f2-menu.png", (650, 368), 1600),
    ("f3-createvar.png", (730, 438), 1600),
    ("f4-distance.png", (1280, 447), 1900),
    ("f5-element.png", (715, 310), 1600),
    ("f6-parameter-menu.png", (790, 404), 1900),
    ("f7-pmarker.png", None, 2600),
]

ims = {}
for name, _, _ in FRAMES:
    ims[name] = Image.open(os.path.join(SRC, name)).convert("RGB")
w, h = ims["f1-idle.png"].size
f2, f5, f6, f7 = (ims[n] for n in ("f2-menu.png", "f5-element.png", "f6-parameter-menu.png", "f7-pmarker.png"))

# patch 1: a Windows notification toast landed in the bottom-right of frame 6. Outside the menu that
# corner is empty canvas in frame 7 (same layout), so copy it across. Inside the menu the toast hid
# the right ends of the Cut, Copy and Select All rows; frame 2's Buffer menu ends with the same three
# rows, so align the two menus by template-matching an intact row of frame 6 (the Rename row's
# shortcut) against frame 2 and copy the hidden rectangle from there.
f6.paste(f7.crop((770, 415, w, h)), (770, 415))
f6.paste(f7.crop((660, 512, 800, h)), (660, 512))
a6 = np.asarray(f6.convert("L")).astype(int); a2 = np.asarray(f2.convert("L")).astype(int)
tx0, ty0, tx1, ty1 = 640, 262, 730, 296
tpl = a6[ty0:ty1, tx0:tx1]
best = None
for dy in range(80, 125):
    for dx in range(80, 120):
        sx, sy = tx0 - dx, ty0 + dy          # where the template should sit in frame 2
        e = float(np.abs(a2[sy:sy + tpl.shape[0], sx:sx + tpl.shape[1]] - tpl).mean())
        if best is None or e < best[0]:
            best = (e, dx, dy)
e, dx, dy = best
print("frame 6 menu alignment: frame 2 = frame 6 shifted by dx", -dx, "dy", dy, "err", round(e, 2))
def darkest(arr):
    return int(np.asarray(arr).argmin())
right = 750 + darkest(a6[400, 750:775])          # x of frame 6's own right border line
bottom = 490 + darkest(a6[490:530, 600])         # y of its bottom border line
print("frame 6 menu borders: right", right, "bottom", bottom)
# the hidden rectangle inside the menu, from frame 2, stopping short of the border lines
f6.paste(f2.crop((650 - dx, 405 + dy, right - 4 - dx, bottom - 4 + dy)), (650, 405))
# the border lines themselves, replicated from frame 6's own intact pixels
col = f6.crop((right - 4, 395, right + 4, 400))
for y in range(405, bottom + 4, 5):
    f6.paste(col, (right - 4, y))
strip = f6.crop((560, bottom - 4, 640, bottom + 4))
for x in range(650, right, 80):
    f6.paste(strip.crop((0, 0, min(80, right - x), 8)), (x, bottom - 4))
# plain canvas right of and below the menu, where the toast was
f6.paste(Image.new("RGB", (w - right - 4, 160), "#ffffff"), (right + 4, 405))
f6.paste(Image.new("RGB", (200, 60), "#ffffff"), (650, bottom + 4))

# patch 2: Buffer was re-run between frames 5 and 7, so frame 7 carries a green check the earlier
# frames do not; copy Buffer's top-right corner from frame 5
f7.paste(f5.crop((440, 60, 500, 120)), (440, 60))

# patch 3: blank the "Show Toolbar" overlay in the top-right corner of every frame, the vertical
# scrollbar, and the bottom scrollbar with the Mode bar, except where a menu lies over them
MENU_KEEP = {"f2-menu.png": [(270, 548, 660, h)], "f3-createvar.png": [(270, 548, 643, h)],
             "f4-distance.png": [(270, 548, 643, h), (1240, 190, w, 385)]}
white = Image.new("RGB", (w, h), "#ffffff")
for name, im in ims.items():
    boxes = MENU_KEEP.get(name, [])
    keep = [im.crop(box) for box in boxes]
    im.paste(white.crop((1060, 0, w, 62)), (1060, 0))
    im.paste(white.crop((1244, 0, w, h)), (1244, 0))
    im.paste(white.crop((0, 548, w, h)), (0, 548))
    for box, piece in zip(boxes, keep):
        im.paste(piece, (box[0], box[1]))

frames, durations = [], []
for name, cur, dur in FRAMES:
    im = ims[name].copy().crop((0, 0, w, 622))
    if cur:
        cursor(im, *cur)
    im = im.resize((WIDTH, int(im.height * WIDTH / im.width)), Image.LANCZOS)
    frames.append(im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    durations.append(dur)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
print(OUT, os.path.getsize(OUT) // 1024, "KB", len(frames), "frames", frames[0].size)
