"""Week 9 Thursday primer slide: the two figures of the kriging-weights worked example, as images.

The same made-up example as docs/explainers/kriging-weights/index.html: an unknown point Z0 and four
measured temperatures (Z1 10 km east, Z2 25 km north, Z3 and Z4 8 km apart, 30.3 km west), and a
spherical semivariogram with nugget 2, sill 20 (degrees F squared) and range 50 km.

1. The map: blue dashed lines from Z0 to each sample (the distances D1-D4) and gray lines between
   every pair of samples (D12 ... D34): the two kinds of distance kriging reads the curve at.
2. The semivariogram with the four target readings V1-V4 (blue) and the six pair readings Vij (gray).

Also solves the system and prints the weights, so the slide and the page can be checked against it.

    python tools/week09_kriging_weights_figures.py      (any Python with matplotlib and numpy)

Writes slides/week-09/images/ie-kw-map.png and ie-kw-vario.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, BLUE, ORANGE, GRAY, INK = "#002e5d", "#0062b8", "#c9620f", "#7c8794", "#1c2633"

C0, C, A = 2.0, 18.0, 50.0


def gamma(h):
    h = np.asarray(h, float)
    s = np.clip(h / A, 0, 1)
    return np.where(h > 0, C0 + C * (1.5 * s - 0.5 * s ** 3), 0.0)


P = np.array([[10, 0], [0, 25], [-30, 4], [-30, -4]], float)
Z = np.array([61, 58, 66, 65], float)
D = np.hypot(*P.T)
V = gamma(D)
Dij = np.hypot(*(P[:, None] - P[None]).transpose(2, 0, 1))
Mx = np.ones((5, 5)); Mx[:4, :4] = gamma(Dij); Mx[4, 4] = 0
sol = np.linalg.solve(Mx, np.append(V, 1))
lam, m = sol[:4], sol[4]
print("weights", lam.round(3), "m", round(m, 3), "Z0", round(lam @ Z, 2), "variance", round(lam @ V + m, 2))

# --- the map --------------------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.6, 3.3), dpi=200)
for i in range(4):
    for j in range(i + 1, 4):
        ax.plot(*P[[i, j]].T, color=GRAY, lw=1.1, alpha=0.6, zorder=1)
for k, (dx, dy, ha) in enumerate([(0, 1.6, "center"), (1.2, 0, "left"), (0, 2.0, "center"), (0, -3.6, "center")]):
    ax.plot([0, P[k, 0]], [0, P[k, 1]], color=BLUE, lw=2.2, ls=(0, (5, 3)), zorder=2)
    mx, my = P[k] / 2
    ax.text(mx + dx, my + dy, f"D$_{k + 1}$", color=BLUE, fontsize=12, weight="bold", ha=ha, va="center")
ax.text(-33.5, 0, "D$_{34}$", color=GRAY, fontsize=11, ha="right", va="center", weight="bold")
ax.text(5.8, 14.5, "D$_{12}$", color=GRAY, fontsize=11, ha="left", va="center", weight="bold")
names = ["Z$_1$ 61°", "Z$_2$ 58°", "Z$_3$ 66°", "Z$_4$ 65°"]
offs = [(1.8, -0.2, "left"), (1.8, 0, "left"), (-1.8, 1.6, "right"), (-1.8, -1.6, "right")]
for k in range(4):
    ax.plot(*P[k], "o", ms=9, color=INK, mec="white", mew=1.6, zorder=4)
    ax.text(P[k, 0] + offs[k][0], P[k, 1] + offs[k][1], names[k], fontsize=12, weight="bold", color=INK,
            ha=offs[k][2], va="center")
ax.plot(0, 0, "o", ms=11, mfc="white", mec=ORANGE, mew=2.6, zorder=5)
ax.text(1.2, -3.2, "Z$_0$ ?", color=ORANGE, fontsize=12, weight="bold")
ax.plot([-38, -28], [-9.5, -9.5], color=INK, lw=2.5)
ax.text(-33, -8.2, "10 km", ha="center", fontsize=9, color=GRAY)
ax.set_xlim(-42, 22); ax.set_ylim(-11, 28); ax.set_aspect("equal"); ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig(IMG / "ie-kw-map.png", facecolor="white"); plt.close(fig)

# --- the semivariogram readings ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5.6, 3.1), dpi=200)
hh = np.linspace(0.01, 60, 400)
ax.plot(np.r_[0, hh], np.r_[0, gamma(hh)], color=INK, lw=2.2, zorder=2)
iu = np.triu_indices(4, 1)
for h in np.unique(Dij[iu].round(2)):
    ax.plot([h, h], [0, gamma(h)], color=GRAY, lw=1, ls=(0, (2, 2)))
    ax.plot(h, gamma(h), "o", ms=6, color=GRAY, zorder=3)
ax.text(7.0, gamma(8) - 3.4, "V$_{34}$", color=GRAY, fontsize=10, weight="bold", ha="right")
ax.text(40.5, 21.0, "V$_{ij}$ (pairs)", color=GRAY, fontsize=10, weight="bold", ha="center")
for h, t in [(10, "V$_1$"), (25, "V$_2$"), (D[2], "V$_3$ = V$_4$")]:
    ax.plot([h, h], [0, gamma(h)], color=BLUE, lw=1.4, ls=(0, (4, 3)))
    ax.plot([0, h], [gamma(h), gamma(h)], color=BLUE, lw=1.4, ls=(0, (4, 3)))
    ax.plot(h, gamma(h), "o", ms=8, color=BLUE, mec="white", mew=1.4, zorder=4)
    ax.text(h - 1, gamma(h) + 0.9, t, color=BLUE, fontsize=11, weight="bold", ha="right")
ax.set_xlim(0, 60); ax.set_ylim(0, 23)
ax.set_xlabel("Distance (km)", color=NAVY)
ax.set_ylabel("Semivariance (°F²)", color=NAVY)
ax.spines[["top", "right"]].set_visible(False); ax.grid(color="#e8ecf1", lw=0.8)
fig.tight_layout()
fig.savefig(IMG / "ie-kw-vario.png", facecolor="white"); plt.close(fig)
