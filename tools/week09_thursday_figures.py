"""Week 9 Thursday figures that replace the scanned Bolstad textbook figures in the kriging part.

1. Lag distance: four sample points and the six pairs between them, each pair labeled with its
   distance h (computed from the coordinates, so the numbers agree with the drawing).
2. Spatial autocorrelation: a smooth (autocorrelated) 12 x 12 layer and a random one, each beside a
   scatter of every cell against its neighbor one cell over (h = one cell). Made-up values.
3. The semivariance equation, written with 1/(2n) out front so nobody reads it as n/2.
4. A variogram: semivariance calculated from 400 points on a made-up smooth surface, in narrow lag
   bins (the jagged line), and a spherical model fitted to it (the smooth line).

    python tools/week09_thursday_figures.py      (any Python with matplotlib, numpy and scipy)

Writes slides/week-09/images/ie-lag-pairs.png, ie-autocorr-pairs.png, ie-semivariance-formula.png
and ie-variogram-bins.png.
"""

import itertools
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12,
                     "mathtext.fontset": "dejavusans"})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#c8102e"
rng = np.random.default_rng(914)

# --- 1. Lag distance -----------------------------------------------------------------------------------
P = np.array([[0.8, 6.2], [8.6, 8.4], [5.2, 5.4], [7.8, 0.8]])
fig = plt.figure(figsize=(4.6, 4.6), dpi=200)
ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
ax.set_xlim(-0.6, 10); ax.set_ylim(-0.4, 9.6); ax.set_aspect("equal"); ax.axis("off")
for i, j in itertools.combinations(range(4), 2):
    (x1, y1), (x2, y2) = P[i], P[j]
    ax.plot([x1, x2], [y1, y2], color=GRAY, lw=1.4, ls=(0, (5, 3)), zorder=2)
    h = np.hypot(x2 - x1, y2 - y1)
    ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"{h:.1f}", ha="center", va="center", fontsize=13, color=RED,
            weight="bold", bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"), zorder=4)
ax.plot(P[:, 0], P[:, 1], "o", ms=12, color=BLUE, mec="white", mew=1.8, zorder=5)
for k, (x, y) in enumerate(P, 1):
    dx, dy = {1: (-0.2, 0.55), 2: (0.0, 0.55), 3: (-0.1, 0.6), 4: (0.0, -0.75)}[k]
    ax.text(x + dx, y + dy, f"$Z_{k}$", ha="center", va="center", fontsize=16, color=NAVY)
fig.savefig(IMG / "ie-lag-pairs.png", facecolor="white"); plt.close(fig)

# --- 2. Spatial autocorrelation --------------------------------------------------------------------------
N = 12
smooth = gaussian_filter(rng.normal(size=(N + 8, N + 8)), 2.2)[4:-4, 4:-4]
noisy = rng.normal(size=(N, N))
fig, axs = plt.subplots(2, 2, figsize=(6.4, 6.2), dpi=200, gridspec_kw=dict(width_ratios=[1, 1.15]))
for row, (grid, name) in enumerate([(smooth, "Autocorrelated"), (noisy, "Random")]):
    g = (grid - grid.min()) / (grid.max() - grid.min()) * 100
    a, b = axs[row]
    a.imshow(g, cmap="Greys", vmin=-10, vmax=110)
    a.set_xticks(np.arange(-0.5, N, 1), minor=True); a.set_yticks(np.arange(-0.5, N, 1), minor=True)
    a.grid(which="minor", color="white", lw=0.6); a.tick_params(which="both", length=0)
    a.set_xticks([]); a.set_yticks([])
    a.set_title(name, loc="left", fontsize=14, color=NAVY, weight="bold")
    b.plot(g[:, :-1].ravel(), g[:, 1:].ravel(), "o", ms=3.5, color=BLUE, alpha=0.75)
    b.set_xlim(0, 100); b.set_ylim(0, 100); b.set_aspect("equal")
    b.set_xticks([0, 50, 100]); b.set_yticks([0, 50, 100])
    b.spines[["top", "right"]].set_visible(False)
    b.set_xlabel("value at a cell", color=NAVY); b.set_ylabel("value one cell over", color=NAVY)
fig.tight_layout(h_pad=1.5, w_pad=1.5)
fig.savefig(IMG / "ie-autocorr-pairs.png", facecolor="white"); plt.close(fig)

# --- 3. The semivariance equation -----------------------------------------------------------------------
fig = plt.figure(figsize=(4.4, 1.3), dpi=250)
fig.text(0.5, 0.5, r"$\gamma(h) = \dfrac{1}{2n}\sum_{i=1}^{n}\left(Z_i - Z_j\right)^2$",
         ha="center", va="center", fontsize=24, color=NAVY)
fig.savefig(IMG / "ie-semivariance-formula.png", facecolor="white"); plt.close(fig)

# --- 4. A variogram from points on a made-up surface ----------------------------------------------------
L = 400                                                   # 400 x 400 cells of 50 m: a 20 km square
field = gaussian_filter(rng.normal(size=(L, L)), 14) * 1000
idx = rng.integers(0, L, size=(400, 2))
xy, z = idx * 50.0, field[idx[:, 0], idx[:, 1]]
i, j = np.triu_indices(len(z), 1)
h = np.hypot(*(xy[i] - xy[j]).T); sv = 0.5 * (z[i] - z[j]) ** 2
edges = np.arange(0, 8001, 200)
mid = (edges[:-1] + edges[1:]) / 2
gam = np.array([sv[(h >= a) & (h < b)].mean() for a, b in zip(edges[:-1], edges[1:])])


def spherical(hh, sill, rng_):
    s = np.clip(hh / rng_, 0, 1)
    return sill * (1.5 * s - 0.5 * s ** 3)


(sill, rr), _ = curve_fit(spherical, mid, gam, p0=[gam.max(), 2500])
fig, ax = plt.subplots(figsize=(5.4, 4.4), dpi=200)
ax.plot(mid, gam, color=GRAY, lw=1.3, label="calculated semivariance")
hh = np.linspace(0, edges[-1], 300)
ax.plot(hh, spherical(hh, sill, rr), color=ORANGE, lw=2.8, label="fitted model")
ax.set_xlim(0, edges[-1]); ax.set_ylim(0, None)
ax.set_xlabel("Lag distance h (m)", color=NAVY); ax.set_ylabel("Semivariance", color=NAVY)
ax.set_yticks([]); ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="lower right", fontsize=11)
fig.tight_layout(); fig.savefig(IMG / "ie-variogram-bins.png", facecolor="white"); plt.close(fig)
print(f"variogram fit: sill {sill:.0f}, range {rr:.0f} m")
