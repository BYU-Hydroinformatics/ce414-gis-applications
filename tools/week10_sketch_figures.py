"""Figures for the Week 10 decks that need no GIS data (plain Python with numpy, scipy, matplotlib).

- vo-tiny-grid.png, vo-tiny-grid-diff.png: the made-up nine-cell pad of Tuesday's "Your Turn" and
  "Check Your Work" slides (ground heights, then ground minus 102 m colored as cut or fill).
- vo-spline-idw.png: a SCHEMATIC transect (made-up points, not Lab 9 data) showing why IDW stays
  inside the range of its points while a spline, which bends smoothly through them, can overshoot
  where it has no points. A reminder of Week 9; no Lab 9 result is computed here.

    python tools/week10_sketch_figures.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
from scipy.interpolate import CubicSpline

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "slides", "week-10", "images")
plt.rcParams.update({"font.size": 14, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(os.path.join(OUT, name), dpi=150); plt.close(fig)


# ------------------------------------------------------------------ the nine-cell pad
G = np.array([[102, 103, 105], [101, 102, 104], [100, 101, 103]], dtype=float)


def grid(vals, name, title, cmap, norm, fmt):
    fig, ax = plt.subplots(figsize=(5, 5.4))
    ax.imshow(vals, cmap=cmap, norm=norm)
    for (r, c), v in np.ndenumerate(vals):
        ax.text(c, r, fmt(v), ha="center", va="center", fontsize=24, fontweight="bold")
    ax.set_xticks(np.arange(-0.5, 3), minor=True); ax.set_yticks(np.arange(-0.5, 3), minor=True)
    ax.grid(which="minor", color="white", lw=3)
    ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, fontsize=15)
    save(fig, name)


grid(G, "vo-tiny-grid.png", "Existing ground (m), 10 m cells", "Greys", plt.Normalize(97, 108), lambda v: f"{v:.0f}")
D = G - 102
grid(D, "vo-tiny-grid-diff.png", "Ground − 102 m: red cut, blue fill", "RdBu_r", TwoSlopeNorm(0, -4, 4),
     lambda v: f"{v:+.0f}" if v else "0")

# ------------------------------------------------------------------ spline vs IDW, schematic
x = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.4, 5.6, 6.0, 6.5, 7.0, 7.5, 8.0])   # no points from 2.4 to 5.6
z = np.array([24.0, 24.4, 25.0, 25.9, 27.2, 29.0, 22.5, 20.3, 18.8, 17.8, 17.0, 16.4])  # rising toward the gap
xs = np.linspace(0, 8, 400)
w = 1.0 / np.maximum(np.abs(xs[:, None] - x[None, :]), 1e-9) ** 2
idw = (w * z).sum(1) / w.sum(1)
spl = CubicSpline(x, z, bc_type="natural")(xs)
fig, ax = plt.subplots(figsize=(10, 5))
ax.axvspan(2.4, 5.6, color="#edf2f7")
ax.text(4.0, 13.2, "no points here", ha="center", color="#4a5568")
ax.plot(xs, spl, color="#c05621", lw=3, label="spline: bends smoothly through every point")
ax.plot(xs, idw, color="#2b6cb0", lw=3, label="IDW: a weighted average of nearby points")
ax.scatter(x, z, color="#2d3748", zorder=5, s=40, label="sample points")
ax.axhline(z.max(), color="#a0aec0", ls=":", lw=1.2)
ax.text(8.0, z.max() + 0.4, "highest point", ha="right", color="#718096", fontsize=12)
ax.set_xlabel("distance along a transect (km)"); ax.set_ylabel("elevation (m above a datum)")
ax.set_title("Schematic: the same points, two interpolators")
ax.set_ylim(12, max(spl.max(), z.max()) + 3)
ax.legend(frameon=False, loc="lower left", fontsize=12)
save(fig, "vo-spline-idw.png")
print("spline max", round(float(spl.max()), 1), "point max", z.max(), "idw max", round(float(idw.max()), 1))
