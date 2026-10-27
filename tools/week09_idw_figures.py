"""Week 9 IDW figures for "Inverse Distance Weighted (IDW): The Method".

1. The IDW equation, and a transparent overlay of the same size that circles the exponent n in both
   places. The deck stacks the overlay on the equation and reveals it on a click. The circles are
   placed from matplotlib's own glyph positions, so they land on the n's whatever the font.
2. A worked example redrawn from the Bolstad textbook figure: three known points (50, 30, 52) at
   distances 4, 2 and 6 from the point being estimated, with the exponent-one arithmetic. The
   textbook figure gives the answer as 34; the arithmetic it shows comes to 39.5, which is what this
   figure prints. With exponent two the answer is 35.5, nearer the closest point's 30.

    python tools/week09_idw_figures.py      (any Python with matplotlib)

Writes slides/week-09/images/ip-idw-equation.png, ip-idw-equation-n.png and ip-idw-worked-example.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Ellipse, PathPatch
from matplotlib.textpath import TextPath, TextToPath

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12,
                     "mathtext.fontset": "dejavusans"})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#c8102e"

# --- 1. The equation and the circled exponent ---------------------------------------------------------
EQ = r"$Z_j = \dfrac{\sum_i \dfrac{Z_i}{d_{ij}^{\,n}}}{\sum_i \dfrac{1}{d_{ij}^{\,n}}}$"
SIZE = 40
fp = FontProperties(size=SIZE)
path = TextPath((0, 0), EQ, prop=fp)
glyphs = TextToPath().get_glyphs_mathtext(fp, EQ)[0]
ns = [(x * SIZE / 100, y * SIZE / 100, s) for gid, x, y, s in glyphs   # positions come at size 100
      if gid.endswith("-6e")]                                           # 0x6e is "n"
ext = path.get_extents()
pad = 10


def eq_axes():
    w, h = ext.width + 2 * pad, ext.height + 2 * pad
    fig = plt.figure(figsize=(w / 72, h / 72), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(ext.x0 - pad, ext.x1 + pad); ax.set_ylim(ext.y0 - pad, ext.y1 + pad)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


fig, ax = eq_axes()
ax.add_patch(PathPatch(path, fc=NAVY, ec="none"))
fig.savefig(IMG / "ip-idw-equation.png", facecolor="white"); plt.close(fig)

fig, ax = eq_axes()
for x, y, s in ns:
    gw = 0.62 * SIZE * s                                                  # width of an oblique "n"
    ax.add_patch(Ellipse((x + 0.5 * gw, y + 0.27 * SIZE * s), 1.9 * gw, 1.25 * SIZE * s,
                         fill=False, ec=ORANGE, lw=2.2))
fig.savefig(IMG / "ip-idw-equation-n.png", transparent=True); plt.close(fig)

# --- 2. The worked example ---------------------------------------------------------------------------
P = {"a": ((0.6, 7.6), 50, 4), "b": ((8.6, 7.9), 30, 2), "c": ((0.9, 1.2), 52, 6)}
X = (5.2, 5.6)
fig = plt.figure(figsize=(4.6, 4.3), dpi=200)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.set_xlim(-0.3, 10.2); ax.set_ylim(-0.4, 8.9); ax.set_aspect("equal"); ax.axis("off")
for (xy, z, d) in P.values():
    ax.annotate("", xy=X, xytext=xy, arrowprops=dict(arrowstyle="<->", color=GRAY, lw=1.4, shrinkA=7, shrinkB=9))
    ax.plot(*xy, "o", ms=11, color=BLUE, mec="white", mew=1.6, zorder=5)
    ax.text(xy[0], xy[1] + 0.45, f"{z}", ha="center", va="bottom", fontsize=15, color=NAVY, weight="bold")
    mx, my = (xy[0] + X[0]) / 2, (xy[1] + X[1]) / 2
    ax.text(mx, my, f"d = {d}", ha="center", va="center", fontsize=12, color=GRAY,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
ax.plot(*X, "o", ms=13, color=ORANGE, mec="white", mew=2, zorder=6)
ax.text(X[0] + 0.25, X[1] - 0.55, "?", fontsize=18, color=ORANGE, weight="bold", va="top")
ax.text(7.3, 2.5, r"$Z = \dfrac{\dfrac{50}{4} + \dfrac{30}{2} + \dfrac{52}{6}}{\dfrac{1}{4} + \dfrac{1}{2} + \dfrac{1}{6}}$",
        ha="center", va="center", fontsize=15, color=NAVY)
ax.text(7.3, 0.35, r"$\approx 39.5$", ha="center", va="center", fontsize=16, color=ORANGE, weight="bold")
fig.savefig(IMG / "ip-idw-worked-example.png", facecolor="white"); plt.close(fig)
