"""Week 11 Part B ArcGIS Pro dialogs with red callouts: an arrow to each key field and a few words on
what it does. Same pattern as tools/week09_dialog_callouts.py.

The captures are untouched ArcGIS Pro 3.7.1 screenshots from the Lab 10 model (Lab 10's Figures 7a and
7b). This script sets each one beside a column of notes and draws the arrows; the y values below are
the pixel rows of the fields in those captures.

    python tools/week11_dialog_callouts.py      (any Python with matplotlib)

Writes slides/week-11/images/lcpb-distance-accumulation-callouts.png and
lcpb-optimal-path-callouts.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-11" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
RED = "#c8102e"
NOTE_W = 470            # width of the notes column, in screenshot pixels
FONT = 21

# capture, output, [(row of the field, x the arrow points at, note, optional nudge of the note up or down)]
# A note with empty text draws only an arrow, from wherever its nudge puts the start.
DIALOGS = [
    ("lcpb-distance-accumulation.png", "lcpb-distance-accumulation-callouts.png", [
        (167, 40, "Start point:\nthe Spanish Fork substation"),
        (250, 40, "Cheapest total cost from\nthe source to every cell"),
        (333, 40, "Cells the route may never\nenter: the lakes"),
        (414, 40, "Leave empty: it measures\nground distance, not cost"),
        (496, 40, "Your cost surface: the price\nof crossing each cell"),
        (578, 40, "Which way is home from\neach cell, as an angle"),
    ]),
    ("lcpb-optimal-path.png", "lcpb-optimal-path-callouts.png", [
        (167, 40, "End point:\nthe Bluffdale substation"),
        (333, 40, "Both rasters from\nDistance Accumulation", 40),
        (414, 40, "", -41),
        (496, 40, "The route: a line\nyou can map and measure"),
    ]),
]

for src, out, notes in DIALOGS:
    im = mpimg.imread(IMG / src)
    h, w = im.shape[:2]
    W = NOTE_W + w
    x0 = NOTE_W                                                           # notes on the left
    fig = plt.figure(figsize=(W / 100, h / 100), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(h, 0); ax.axis("off")
    ax.imshow(im, extent=(x0, x0 + w, h, 0))
    for y, x, text, *nudge in notes:
        ax.annotate(text, xy=(x0 + x, y), xytext=(NOTE_W - 25, y + (nudge[0] if nudge else 0)),
                    ha="right", va="center", fontsize=FONT, color=RED, weight="bold", linespacing=1.1,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=RED, lw=2.4,
                                    shrinkA=4, shrinkB=0))
    fig.savefig(IMG / out, facecolor="white"); plt.close(fig)
