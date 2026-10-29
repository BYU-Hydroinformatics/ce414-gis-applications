"""Week 9 ArcGIS Pro dialogs with red callouts: an arrow to each key field and a few words on what it
needs and why it matters.

The captures themselves are untouched ArcGIS Pro 3.7.1 screenshots from the Lab 8 model (see the
speaker notes on "Thiessen Polygons in ArcGIS Pro" and "IDW in ArcGIS Pro"). This script only sets
each one beside a column of notes and draws the arrows; the y values below are the pixel rows of the
fields in those captures.

    python tools/week09_dialog_callouts.py      (any Python with matplotlib)

Writes slides/week-09/images/ip-pro-thiessen-callouts.png, ip-pro-polygon-to-raster-callouts.png,
ie-idw-callouts.png, and for Thursday ie-kriging-callouts.png, ie-rc-error-callouts.png,
ie-rc-square-callouts.png and ie-zonal-callouts.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
RED = "#c8102e"
NOTE_W = 440            # width of the notes column, in screenshot pixels
# Wide dialogs shrink more on the slide, so their notes are set larger.
FONT = {"ie-rc-error.png": 26, "ie-rc-square.png": 24, "ie-zonal-table.png": 23, "ie-calc-field.png": 22}

# capture, output, side the notes go on, [(row of the field, x the arrow points at, note, optional nudge
# of the note up or down so neighboring notes do not collide)]
DIALOGS = [
    ("ip-pro-thiessen.png", "ip-pro-thiessen-callouts.png", "left", [
        (168, 40, "The sample points,\nwith their values"),
        (332, 40, "All fields: keeps\neach sample's value\n(default drops it)"),
    ]),
    ("ip-pro-polygon-to-raster.png", "ip-pro-polygon-to-raster-callouts.png", "right", [
        (251, 650, "The measured value,\nnot OBJECTID\n(polygon numbers)"),
        (579, 650, "30 m: the same\ncells as the\ntrue DEM"),
    ]),
    ("ie-idw.png", "ie-idw-callouts.png", "left", [
        (251, 40, "The value to interpolate\n(elevation), not an ID"),
        (414, 40, "30 m: same cells as the DEM", -14),
        (467, 35, "Exponent n: bigger = nearer\npoints count more", 20),
        (568, 150, "How many neighbors\neach estimate uses (12)"),
    ]),
    # Thursday
    ("ie-kriging.png", "ie-kriging-callouts.png", "left", [
        (460, 108, "The model's shape:\nspherical, Gaussian, ...", -30),
        (502, 248, "Distance-bin width"),
        (586, 205, "Range, sill, nugget:\nleave empty to fit them", 18),
        (711, 40, "30 m: same cells as the DEM"),
    ]),
    ("ie-rc-error.png", "ie-rc-error-callouts.png", "left", [
        (423, 40, "Truth minus\nsurface: this order\nsets the sign"),
        (621, 40, "One error raster\nper method"),
    ]),
    ("ie-rc-square.png", "ie-rc-square-callouts.png", "left", [
        (423, 40, "Square each error\nso highs and lows\nboth count"),
    ]),
    ("ie-zonal-table.png", "ie-zonal-callouts.png", "left", [
        (168, 40, "One zone: the\nwhole study area"),
        (332, 40, "The squared\nerror raster"),
        (540, 40, "Mean, not the\ndefault All"),
    ]),
    # Step 4 of the RMSE recipe; the capture is Lab 8 Step 7's Calculate Field (lab08-calculate-field.png)
    ("ie-calc-field.png", "ie-calc-field-callouts.png", "left", [
        (168, 40, "The table Zonal\nStatistics wrote"),
        (250, 40, "A new field, RMSE"),
        (917, 40, "Square root of the\nmean: back in meters"),
    ]),
]

for src, out, side, notes in DIALOGS:
    im = mpimg.imread(IMG / src)
    h, w = im.shape[:2]
    W = NOTE_W + w
    x0 = NOTE_W if side == "left" else 0                                  # left edge of the capture
    fig = plt.figure(figsize=(W / 100, h / 100), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(h, 0); ax.axis("off")
    ax.imshow(im, extent=(x0, x0 + w, h, 0))
    for y, x, text, *nudge in notes:
        tx = NOTE_W - 25 if side == "left" else w + 25
        ax.annotate(text, xy=(x0 + x, y), xytext=(tx, y + (nudge[0] if nudge else 0)), ha="right" if side == "left" else "left", va="center",
                    fontsize=FONT.get(src, 19), color=RED, weight="bold", linespacing=1.1,
                    arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=RED, lw=2.4,
                                    shrinkA=4, shrinkB=0))
    fig.savefig(IMG / out, facecolor="white"); plt.close(fig)
