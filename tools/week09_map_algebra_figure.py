"""Week 9 Thursday figure: the error raster as map algebra, truth minus surface, cell by cell.

Three small rasters drawn as tilted layers hovering one above the next: a true DEM, an interpolated
surface, and their difference on a diverging scale. One cell is picked out in all three with its value
(2,450 - 2,410 = +40 m, the deck's "+40" question), and a dashed line through the layers says the
subtraction happens cell by cell, as in the Week 3 raster-analysis map algebra. The values are made up.

    python tools/week09_map_algebra_figure.py      (any Python with matplotlib, numpy and scipy)

Writes slides/week-09/images/ie-map-algebra-error.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from scipy.ndimage import uniform_filter

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, GRAY, RED = "#002e5d", "#5b6770", "#c8102e"

N = 6
rr, cc = np.mgrid[0:N, 0:N]
PICK = (2, 3)
bump = np.exp(-((rr - PICK[0]) ** 2 + (cc - PICK[1]) ** 2) / 2.0)
k = (bump - uniform_filter(bump, 3, mode="nearest"))[PICK]
truth = 40 * cc + 25 * rr + (40 / k) * bump        # the surface smooths the bump's top off by exactly 40 m
surface = uniform_filter(truth, 3, mode="nearest")
shift = 2450 - truth[PICK]                          # so the picked cell reads 2,450 and 2,410
truth, surface = truth + shift, surface + shift
err = truth - surface

DX, DY, SK = 1.0, 0.36, 0.55                       # cell width, cell depth, skew per row


def corners(r, c, y0):
    x0 = c * DX + r * SK
    yb = y0 - r * DY
    return [(x0, yb), (x0 + DX, yb), (x0 + DX + SK, yb - DY), (x0 + SK, yb - DY)]


def layer(ax, vals, cmap, vmin, vmax, y0, name, value):
    cm = plt.get_cmap(cmap)
    for r in range(N):
        for c in range(N):
            ax.add_patch(Polygon(corners(r, c, y0), closed=True, fc=cm((vals[r, c] - vmin) / (vmax - vmin)),
                                 ec="white", lw=0.8))
    ax.add_patch(Polygon(corners(*PICK, y0), closed=True, fill=False, ec="black", lw=2.4, zorder=5))
    ax.text(-0.25, y0 - N * DY / 2, name, ha="right", va="center", fontsize=15, color=NAVY, weight="bold")
    px, py = np.mean(corners(*PICK, y0), axis=0)
    ax.annotate(value, (px + 0.3, py), xytext=(N * DX + N * SK + 0.5, y0 - N * DY / 2), fontsize=15,
                weight="bold", color="black", va="center",
                arrowprops=dict(arrowstyle="-", color="black", lw=1.2))
    return px, py


fig, ax = plt.subplots(figsize=(6.4, 5.0), dpi=200)
Y = [0.0, -3.0, -6.4]
tops = []
tops.append(layer(ax, truth, "terrain", 1950, 2700, Y[0], "True_DEM", "2,450 m"))
tops.append(layer(ax, surface, "terrain", 1950, 2700, Y[1], "Surface", "2,410 m"))
tops.append(layer(ax, err, "RdBu", -50, 50, Y[2], "Error", "+40 m"))
ax.plot([tops[0][0], tops[2][0]], [tops[0][1], tops[2][1]], color=GRAY, lw=1.3, ls=(0, (3, 3)), zorder=1)
mid_x = N * DX / 2 + N * SK / 2
ax.text(-1.7, (Y[0] - N * DY + Y[1]) / 2, "−", fontsize=40, ha="center", va="center", color=RED, weight="bold")
ax.text(-1.7, (Y[1] - N * DY + Y[2]) / 2, "=", fontsize=40, ha="center", va="center", color=RED, weight="bold")
ax.set_xlim(-3.1, N * DX + N * SK + 2.4)
ax.set_ylim(Y[2] - N * DY - 0.3, Y[0] + 0.3)
ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig(IMG / "ie-map-algebra-error.png", facecolor="white", bbox_inches="tight", pad_inches=0.05)
plt.close(fig)
