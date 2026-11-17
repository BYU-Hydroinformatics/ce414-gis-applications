"""Week 12 ArcGIS Pro dialogs with red callouts: an arrow to each key field and a few words on what
it does. Same pattern as tools/week11_dialog_callouts.py.

The captures are untouched ArcGIS Pro 3.7.1 screenshots from the Lab 11 GUI build (Lab 11's Figures
2, 3, 4, 5b and 5c). This script sets each one beside a column of notes and draws the arrows; the y
values below are the pixel rows of the fields in those captures.

    python tools/week12_dialog_callouts.py      (any Python with matplotlib)

Writes slides/week-12/images/nab-dlg-*-callouts.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-12" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
RED = "#c8102e"
FONT = 21

# capture, output, width of the notes column,
# [(row of the field, x the arrow points at, note, optional nudge of the note up or down)]
DIALOGS = [
    ("nab-dlg-make-service-area.png", "nab-dlg-make-service-area-callouts.png", 470, [
        (167, 40, "The network: edges,\njunctions, minutes"),
        (331, 40, "Empty: no travel modes,\nso TravelMinutes runs"),
        (414, 40, "Away: the way an\nengine drives"),
        (503, 96, "The cutoff, in minutes:\none value per row"),
        (891, 40, "Dissolve: a block near two\nstations counts once"),
        (973, 40, "Rings: 0-4, 4-8 when\nthere are two cutoffs"),
    ]),
    ("nab-dlg-add-locations.png", "nab-dlg-add-locations-callouts.png", 430, [
        (167, 40, "The analysis layer\nfrom the first tool"),
        (250, 40, "Which sublayer:\nthe stations are Facilities"),
        (332, 40, "The 42 station points"),
        (681, 40, "Snap each station to a\nstreet within 5 km"),
    ]),
    ("nab-dlg-select-data.png", "nab-dlg-select-data-callouts.png", 400, [
        (167, 40, "The solved analysis\nlayer"),
        (250, 40, "Take out its\nPolygons sublayer"),
    ]),
    ("nab-dlg-select-by-location.png", "nab-dlg-select-by-location-callouts.png", 430, [
        (175, 96, "The blocks: in your model,\nBlocks_Net, a layer of its own"),
        (306, 40, "A block counts by\nits center point"),
        (388, 40, "The four-minute area"),
        (601, 40, "Inverted: keep the\nblocks OUTSIDE"),
    ]),
    ("nab-dlg-summary-statistics.png", "nab-dlg-summary-statistics-callouts.png", 430, [
        (167, 40, "The blocks outside"),
        (370, 96, "Sum of PP_TOTAL:\nthe people", -40),
        (416, 96, "Count: how many\nblocks", 40),
    ]),
]

for src, out, note_w, notes in DIALOGS:
    im = mpimg.imread(IMG / src)
    h, w = im.shape[:2]
    W = note_w + w
    x0 = note_w                                                           # notes on the left
    fig = plt.figure(figsize=(W / 100, h / 100), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(h, 0); ax.axis("off")
    ax.imshow(im, extent=(x0, x0 + w, h, 0))
    for y, x, text, *nudge in notes:
        ax.annotate(text, xy=(x0 + x, y), xytext=(note_w - 25, y + (nudge[0] if nudge else 0)),
                    ha="right", va="center", fontsize=FONT, color=RED, weight="bold", linespacing=1.1,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=RED, lw=2.4,
                                    shrinkA=4, shrinkB=0))
    fig.savefig(IMG / out, facecolor="white"); plt.close(fig)
    print(out)
