"""Week 9 Thiessen construction figure: building Thiessen polygons by hand, in four panels.

Redraws the scanned gray textbook-style figure on a white background with the same five points:
Start (the samples), 1) connect each point to its nearest neighbors (the Delaunay triangles),
2) mark the perpendicular bisector of each line, 3) join the bisectors into polygons. The panel
titles match the numbered steps on the "Thiessen Polygons: The Method" slide.

    python tools/week09_thiessen_construction.py      (any Python with matplotlib, numpy and scipy)

Writes slides/week-09/images/ip-thiessen-construction.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay, Voronoi

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#c8102e"

P = np.array([[1.6, 7.6], [5.0, 6.6], [8.4, 8.2], [2.4, 1.6], [6.8, 3.0]])
W, H = 10.0, 10.0
tri = Delaunay(P)
edges = sorted({tuple(sorted((s[i], s[(i + 1) % 3]))) for s in tri.simplices for i in range(3)})

# Mirror the points across the four sides of the box so every Voronoi cell of a real point is
# closed, and its edges stop at the box rather than running off to infinity.
mirrors = np.vstack([P, P * [-1, 1], P * [-1, 1] + [2 * W, 0], P * [1, -1], P * [1, -1] + [0, 2 * H]])
vor = Voronoi(mirrors)
n = len(P)
ridges = [(vor.vertices[a], vor.vertices[b]) for (i, j), (a, b) in zip(vor.ridge_points, vor.ridge_vertices)
          if i < n and j < n]
corners = {tuple(np.round(v, 6)) for seg in ridges for v in seg
           if 0.01 < v[0] < W - 0.01 and 0.01 < v[1] < H - 0.01}


def panel(ax, title):
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(NAVY); sp.set_linewidth(1.6)
    ax.set_title(title, loc="left", fontsize=15, color=NAVY, fontweight="bold")


def points(ax, labels=False):
    ax.plot(P[:, 0], P[:, 1], "o", ms=13, color=RED, mec="white", mew=2, zorder=6)
    if labels:
        for k, (x, y) in enumerate(P, 1):
            ax.text(x + 0.35, y + 0.3, str(k), fontsize=13, color=NAVY, zorder=7)


def triangles(ax, color=GRAY, alpha=1.0):
    for i, j in edges:
        ax.plot(*zip(P[i], P[j]), color=color, lw=1.5, ls=(0, (4, 3)), alpha=alpha, zorder=2)


fig, axs = plt.subplots(2, 2, figsize=(8.4, 8.0), dpi=170)
(a0, a1), (a2, a3) = axs

panel(a0, "Start"); points(a0, labels=True)

panel(a1, "1) Connect neighbors"); triangles(a1); points(a1)

panel(a2, "2) Bisect each line"); triangles(a2)
for i, j in edges:
    m = (P[i] + P[j]) / 2
    d = P[j] - P[i]; u = np.array([-d[1], d[0]]) / np.hypot(*d)
    a2.plot(*zip(m - 0.6 * u, m + 0.6 * u), color=BLUE, lw=2.6, zorder=4)
points(a2)

panel(a3, "3) Join the bisectors"); triangles(a3, alpha=0.35)
for p, q in ridges:
    a3.plot(*zip(p, q), color=BLUE, lw=2.8, zorder=4, solid_capstyle="round")
for v in corners:
    a3.plot(*v, "o", ms=7, color=NAVY, zorder=5)
points(a3)

fig.tight_layout(h_pad=1.6, w_pad=1.6)
fig.savefig(IMG / "ip-thiessen-construction.png", facecolor="white")
plt.close(fig)
