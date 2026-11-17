"""Week 14 Lab 12 studio deck: the Package Project pane with red callouts.

The capture is an untouched ArcGIS Pro 3.7.1 screen grab at 175 % (November 16, 2026, on the Lab 11
GUI project; Item Details collapsed so no user path shows), set as Lab 12 Step 7 says: Save package
to file, Share outside of organization checked, Include Toolboxes and Include History Items left
checked. Nothing was packaged. This script sets it beside a column of notes and draws the arrows,
in the style of tools/week12_dialog_callouts.py.

    python tools/week14_studio_figures.py      (any Python with matplotlib)

Writes slides/week-14/images/studio-package-project-callouts.png.
"""
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-14" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"]})
RED = "#c8102e"
NOTE_W = 560
FONT = 22
NOTES = [  # (row in the capture, x the arrow points at, note, nudge)
    (231, 44, "Default: uploads to ArcGIS Online", 0),
    (272, 44, "Choose this: a .ppkx file", 0),
    (327, 18, "Name: browse to your Lab12 folder\n(the default is Documents)", 0),
    (422, 44, "Check: copies web layers in", 0),
    (486, 44, "Keep both: your toolbox and the\nmodel's run, with its input data", 0),
]
# The last note sits inside the pane's empty space, so its arrow does not cross "Finish Packaging".
INSIDE = (738, 252, "Then click Package", 330, 640)

im = mpimg.imread(IMG / "studio-package-project.png")
h, w = im.shape[:2]
W = NOTE_W + w
fig = plt.figure(figsize=(W / 100, h / 100), dpi=200)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(h, 0); ax.axis("off")
ax.imshow(im, extent=(NOTE_W, NOTE_W + w, h, 0))
for y, x, text, nudge in NOTES:
    ax.annotate(text, xy=(NOTE_W + x, y), xytext=(NOTE_W - 25, y + nudge), ha="right", va="center",
                fontsize=FONT, color=RED, weight="bold", linespacing=1.1,
                arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=RED, lw=2.4,
                                shrinkA=4, shrinkB=0))
y, x, text, tx, ty = INSIDE
ax.annotate(text, xy=(NOTE_W + x, y), xytext=(NOTE_W + tx, ty), ha="center", va="center",
            fontsize=FONT, color=RED, weight="bold",
            arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.6", color=RED, lw=2.4,
                            shrinkA=4, shrinkB=0))
fig.savefig(IMG / "studio-package-project-callouts.png", facecolor="white"); plt.close(fig)
print("wrote studio-package-project-callouts.png")


# ---------------------------------------------------------------- recording and posting, as two step rows
def steps(out, title, items, color):
    from matplotlib.patches import FancyBboxPatch
    n = len(items)
    fig, ax = plt.subplots(figsize=(4.6, 1.15 * n + 0.6), dpi=200)
    ax.set_xlim(0, 4.6); ax.set_ylim(0, 1.15 * n + 0.6); ax.axis("off")
    ax.text(0.05, 1.15 * n + 0.35, title, fontsize=15, weight="bold", color="#002e5d", va="center")
    for i, (head, body) in enumerate(items):
        y = 1.15 * (n - 1 - i) + 0.1
        ax.add_patch(FancyBboxPatch((0.05, y), 4.5, 0.95, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc="#eef3f9", ec=color, lw=2.2))
        ax.add_patch(plt.Circle((0.42, y + 0.475), 0.27, fc=color, ec="none"))
        ax.text(0.42, y + 0.475, str(i + 1), ha="center", va="center", color="white", fontsize=14, weight="bold")
        ax.text(0.85, y + 0.62, head, fontsize=12.5, weight="bold", color="#002e5d", va="center")
        ax.text(0.85, y + 0.3, body, fontsize=10.5, color="#22262e", va="center")
    fig.savefig(IMG / out, facecolor="white", bbox_inches="tight", pad_inches=0.05); plt.close(fig)
    print("wrote", out)


steps("studio-record-steps.png", "Record: Snipping Tool", [
    ("Open Snipping Tool", "Start menu; choose the video camera"),
    ("New, then drag a box", "around the ArcGIS Pro window"),
    ("Microphone on, then Start", "talk as you click; stop when done"),
    ("Save the recording", "one clip per piece: data, model, map"),
], "#0062b8")
steps("studio-youtube-steps.png", "Post: YouTube, unlisted", [
    ("Sign in at youtube.com", "any Google account"),
    ("Create, then Upload video", "title: CE 414 Lab 12 and your project"),
    ("Visibility: Unlisted", "anyone with the link; not in search"),
    ("Copy the link", "open it in a private window to test"),
], "#e8792b")
