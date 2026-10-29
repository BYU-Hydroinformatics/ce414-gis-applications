"""Week 9 Thursday, Part 1: kriging told as "closer in space, closer in value", with no hand calculation.

All values are made up: 60 weather stations on a smooth afternoon-temperature field over a
300 x 220 km region, each reading off by a little instrument noise (the nugget).

1. The neighbor test, as three same-size layers the deck stacks and reveals on clicks: the station
   map beside empty axes; one close pair and one far pair, drawn on the map and as two dots; then
   every pair of stations (1,770) as a cloud of distance against temperature difference.
2. The semivariogram: the pairs averaged in 20 km distance bins (half the squared difference, as the
   tool computes it), a spherical model fitted, and the nugget, range and sill marked.
3. Four settings, as cross sections and maps: 8 points along a 100 km line plus 22 scattered off it,
   all read from one made-up temperature map, kriged with the fitted model, a big nugget, a short
   range and a long range. Each panel is the surface read along the line, beside the whole kriged map,
   so each setting's effect shows both ways. The estimates are ordinary kriging of the smooth signal
   (the nugget is treated as measurement noise), which is why the big-nugget curve misses the points.

    python tools/week09_kriging_story_figures.py      (any Python with matplotlib, numpy and scipy)

4. The neighbor test again on two other made-up variables at the same stations: one with no spatial
   pattern at all (every reading independent) and one with a regional trend (warm in the west, cool in
   the east), so the cloud's shape can be compared with the smooth field's.
5. Building the semivariogram one 20 km bin at a time: the pairs in each bin drawn on the map and their
   average placed on the graph, as full frames the deck stacks on clicks.
6. The truth map for that slide: the temperature field, the 100 km line and all 30 thermometers.

Writes slides/week-09/images/ie-neighbor-base.png, ie-neighbor-pairs.png, ie-neighbor-cloud.png,
ie-semivariogram-plain.png, ie-semivariogram-dots.png, ie-kriging-settings-2d.png,
ie-kriging-settings-truth.png, ie-neighbor-{random,trend}-{base,cloud}.png and
ie-semivariogram-build-0.png to -4.png.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.optimize import curve_fit

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#c8102e"
rng = np.random.default_rng(2714)

# --- The made-up region and its stations -----------------------------------------------------------
W, H = 300, 220                                            # km, one cell per km
field = gaussian_filter(rng.normal(size=(H + 160, W + 160)), 40)[80:-80, 80:-80]
field = 62 + 8 * (field - field.mean()) / field.std()     # degrees F
NS = 60
pts = []
while len(pts) < NS:                                       # spread the stations out a little
    q = rng.uniform([8, 8], [W - 8, H - 8])
    if all(np.hypot(*(q - r)) >= 9 for r in pts):
        pts.append(q)
P = np.array(pts)
T = field[P[:, 1].astype(int), P[:, 0].astype(int)] + rng.normal(0, 3.0, NS)
i, j = np.triu_indices(NS, 1)
dist = np.hypot(*(P[i] - P[j]).T)
diff = np.abs(T[i] - T[j])
close = np.argmin(np.abs(dist - 15) + 2 * np.abs(diff - 2))
far = np.argmin(np.abs(dist - 240) + 0.05 * np.abs(diff - 12))   # a far pair with a typical difference


def neighbor_axes():
    fig = plt.figure(figsize=(11.0, 4.6), dpi=170)
    m = fig.add_axes([0.01, 0.06, 0.42, 0.88])
    s = fig.add_axes([0.53, 0.14, 0.44, 0.80])
    m.set_xlim(0, W); m.set_ylim(H, 0); m.set_aspect("equal"); m.set_xticks([]); m.set_yticks([])
    s.set_xlim(0, 330); s.set_ylim(0, 30)
    return fig, m, s


def style_scatter(s):
    s.spines[["top", "right"]].set_visible(False)
    s.set_xlabel("Distance between the two stations (km)", color=NAVY)
    s.set_ylabel("Temperature difference (°F)", color=NAVY)
    s.grid(color="#e3e8ef", lw=0.8)


fig, m, s = neighbor_axes()
m.imshow(field, cmap="RdYlBu_r", vmin=44, vmax=80, extent=(0, W, H, 0), alpha=0.45)
m.plot(P[:, 0], P[:, 1], "o", ms=7, color="black", mec="white", mew=1.2)
for sp in m.spines.values():
    sp.set_color(GRAY)
m.plot([20, 120], [H - 12, H - 12], color="black", lw=3)
m.text(70, H - 18, "100 km", ha="center", fontsize=10)
style_scatter(s)
fig.savefig(IMG / "ie-neighbor-base.png", facecolor="white"); plt.close(fig)

fig, m, s = neighbor_axes()
m.axis("off"); s.axis("off")
for k, color, word, off in [(close, BLUE, "close", (24, 70)), (far, ORANGE, "far", (14, 10))]:
    a, b = P[i[k]], P[j[k]]
    m.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=3.2, zorder=5)
    m.plot([a[0], b[0]], [a[1], b[1]], "o", ms=11, color=color, mec="white", mew=1.6, zorder=6)
    s.plot(dist[k], diff[k], "o", ms=14, color=color, mec="white", mew=1.8, zorder=6)
    s.annotate(f"{word}: {dist[k]:.0f} km apart,\n{diff[k]:.0f}°F different", (dist[k], diff[k]),
               xytext=off, textcoords="offset points", fontsize=12, color=color, weight="bold",
               bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=color, lw=1.2),
               arrowprops=dict(arrowstyle="-", color=color, lw=1.2))
fig.savefig(IMG / "ie-neighbor-pairs.png", transparent=True); plt.close(fig)

fig, m, s = neighbor_axes()
m.axis("off"); s.axis("off")
s.plot(dist, diff, "o", ms=2.6, color=GRAY, alpha=0.45, zorder=3)
fig.savefig(IMG / "ie-neighbor-cloud.png", transparent=True); plt.close(fig)

# --- The semivariogram, in plain words ------------------------------------------------------------------
semi = 0.5 * (T[i] - T[j]) ** 2
edges = np.arange(0, 281, 20)
mid = (edges[:-1] + edges[1:]) / 2
gam = np.array([semi[(dist >= a) & (dist < b)].mean() for a, b in zip(edges[:-1], edges[1:])])


def spherical(h, nugget, psill, rng_):
    s_ = np.clip(h / rng_, 0, 1)
    return nugget + psill * (1.5 * s_ - 0.5 * s_ ** 3)


nug = 3.0 ** 2      # the instrument noise put into the readings: two thermometers a step apart differ this much
(psill, rr), _ = curve_fit(lambda h, ps, r: spherical(h, nug, ps, r), mid, gam, p0=[gam.max(), 120], bounds=([0, 10], [500, 400]))
sill = nug + psill


def semivariogram(curve, name):
    """The binned pairs, with or without the fitted model; same axes either way so the deck can stack them."""
    fig, ax = plt.subplots(figsize=(7.4, 4.6), dpi=170)
    if curve:
        hh = np.linspace(0.5, edges[-1], 300)
        ax.plot(hh, spherical(hh, nug, psill, rr), color=ORANGE, lw=3, zorder=3, label="fitted model")
    ax.plot(mid, gam, "o", ms=9, color=BLUE, mec="white", mew=1.4, zorder=4, label="pairs averaged every 20 km")
    if curve:
        ax.axhline(sill, color=GRAY, lw=1.2, ls=(0, (4, 3)))
        ax.axvline(rr, color=GRAY, lw=1.2, ls=(0, (4, 3)))
        ax.plot([0], [nug], "o", ms=10, color=RED, zorder=5, clip_on=False)
        ax.annotate("nugget", (0, nug), xytext=(16, 6), textcoords="offset points", color=RED, fontsize=13, weight="bold")
        ax.text(rr + 4, sill * 0.55, "range", color=NAVY, fontsize=13, weight="bold")
        ax.text(edges[-1] - 4, sill * 1.03, "sill", color=NAVY, fontsize=13, weight="bold", ha="right", va="bottom")
    ax.set_xlim(0, edges[-1]); ax.set_ylim(0, sill * 1.25)
    ax.set_xlabel("Distance between the two stations (km)", color=NAVY)
    ax.set_ylabel("How different (semivariance, °F²)", color=NAVY)
    ax.spines[["top", "right"]].set_visible(False); ax.grid(color="#e3e8ef", lw=0.8)
    ax.legend(frameon=True, framealpha=0.95, edgecolor="none", loc="lower right", fontsize=11)
    fig.tight_layout(); fig.savefig(IMG / name, facecolor="white"); plt.close(fig)


semivariogram(True, "ie-semivariogram-plain.png")
semivariogram(False, "ie-semivariogram-dots.png")
print(f"stations: nugget {nug:.1f}, sill {sill:.1f} F^2, range {rr:.0f} km; close pair {dist[close]:.0f} km "
      f"{diff[close]:.1f} F, far pair {dist[far]:.0f} km {diff[far]:.1f} F")

# --- One dimension, four settings ---------------------------------------------------------------------
x = np.array([5, 17, 28, 41, 55, 66, 80, 94], float)
z = np.array([58, 62, 61, 67, 64, 55, 57, 63], float)
xs = np.linspace(0, 100, 501)
SILL1 = z.var() * 1.1


def krige(nugget, rng_):
    psill_ = SILL1 - nugget

    def cov(h):
        s_ = np.clip(h / rng_, 0, 1)
        return psill_ * (1 - (1.5 * s_ - 0.5 * s_ ** 3))
    n = len(x)
    A = np.ones((n + 1, n + 1)); A[n, n] = 0
    A[:n, :n] = cov(np.abs(x[:, None] - x[None, :])) + nugget * np.eye(n)
    out = []
    for x0 in xs:
        b = np.append(cov(np.abs(x - x0)), 1.0)
        w = np.linalg.solve(A, b)[:n]
        out.append(w @ z)
    return np.array(out)


# The "truth" for the slide's maps: a temperature field whose middle row (y = 23 km) is the fitted-model
# curve through the 8 points, so the 8 points read as measurements along one 100 km line across a map.
prof = krige(0.0, 20)
gy = np.arange(0, 46)
wobble = gaussian_filter(np.random.default_rng(31).normal(size=(46 + 40, 501 + 40)), (8, 40))[20:-20, 20:-20]
wobble = 6 * wobble / wobble.std()
wt = np.exp(-((gy[:, None] - 23) / 9.0) ** 2)
heat = wt * prof[None, :] + (1 - wt) * (z.mean() + wobble + 0.4 * (prof[None, :] - z.mean()))

# 22 more thermometers scattered off the line (none within 4 km of it), read from the same field.
rngx = np.random.default_rng(57)
extra = []
while len(extra) < 22:
    q = rngx.uniform([3, 3], [97, 43])
    if abs(q[1] - 23) >= 4 and all(np.hypot(*(q - e)) >= 8 for e in extra):
        extra.append(q)
extra = np.array(extra)
PX = np.r_[np.c_[x, np.full_like(x, 23.0)], extra]
PZ = np.r_[z, heat[extra[:, 1].astype(int), np.round(extra[:, 0] / 0.2).astype(int)]]
SILL2 = PZ.var() * 1.1


def krige2(targets, nugget_frac, rng_):
    """Ordinary kriging of the smooth signal at many targets at once (the same recipe as krige())."""
    nugget = nugget_frac * SILL2
    psill_ = SILL2 - nugget

    def cov(h):
        s_ = np.clip(h / rng_, 0, 1)
        return psill_ * (1 - (1.5 * s_ - 0.5 * s_ ** 3))
    n = len(PZ)
    A = np.ones((n + 1, n + 1)); A[n, n] = 0
    A[:n, :n] = cov(np.hypot(*(PX[:, None] - PX[None]).transpose(2, 0, 1))) + nugget * np.eye(n)
    B = np.vstack([cov(np.hypot(*(PX[:, None] - targets[None]).transpose(2, 0, 1))), np.ones(len(targets))])
    W = np.linalg.solve(A, B)[:n]
    return W.T @ PZ


GX, GY = np.meshgrid(np.arange(0.5, 100, 1.0), np.arange(0.5, 46, 1.0))
grid = np.c_[GX.ravel(), GY.ravel()]
line = np.c_[xs, np.full_like(xs, 23.0)]
PANELS = [("Fitted model", "neighbors help out to the range (20 km)", 0.0, 20),
          ("Big nugget", "smooths toward the average, misses the points", 0.8, 20),
          ("Short range", "too far apart to help: back to the average", 0.0, 5),
          ("Long range", "reaches far: no return to the average", 0.0, 400)]
fig = plt.figure(figsize=(11.6, 5.9), dpi=170)
gs = fig.add_gridspec(2, 4, width_ratios=[1.55, 1, 1.55, 1], wspace=0.08, hspace=0.42,
                      left=0.055, right=0.99, top=0.93, bottom=0.11)
for k, (title, note, nfrac, rng_) in enumerate(PANELS):
    r, c = divmod(k, 2)
    ax = fig.add_subplot(gs[r, 2 * c])
    mp = fig.add_subplot(gs[r, 2 * c + 1])
    ax.axhline(PZ.mean(), color=GRAY, lw=1, ls=(0, (4, 3)))
    ax.plot(xs, krige2(line, nfrac, rng_), color=ORANGE, lw=2.6, zorder=3)
    ax.plot(x, z, "o", ms=8, color=BLUE, mec="white", mew=1.3, zorder=4)
    ax.set_title(title, loc="left", fontsize=14, color=NAVY, weight="bold")
    ax.text(0.99, 0.04, note, transform=ax.transAxes, ha="right", va="bottom", fontsize=9.5, color=GRAY)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, 100); ax.set_ylim(50, 71)
    if r == 1:
        ax.set_xlabel("Distance along the line (km)", color=NAVY)
    else:
        ax.set_xticklabels([])
    if c == 0:
        ax.set_ylabel("°F", color=NAVY)
    else:
        ax.set_yticklabels([])
    if k == 0:
        ax.text(1, PZ.mean() + 0.4, "average", ha="left", va="bottom", fontsize=9, color=GRAY)
    surf = krige2(grid, nfrac, rng_).reshape(GX.shape)
    mp.imshow(surf, cmap="RdYlBu_r", vmin=50, vmax=71, extent=(0, 100, 46, 0), aspect="equal")
    mp.plot([0, 100], [23, 23], color="black", lw=1.2)
    mp.plot(x, np.full_like(x, 23), "o", ms=4.5, color=BLUE, mec="white", mew=0.8)
    mp.plot(extra[:, 0], extra[:, 1], "o", ms=3, color="black", mec="white", mew=0.5)
    mp.set_xlim(0, 100); mp.set_ylim(46, 0); mp.set_xticks([]); mp.set_yticks([])
    mp.set_title("the kriged map", fontsize=10, color=GRAY, loc="left")
    for sp in mp.spines.values():
        sp.set_color(GRAY)
fig.savefig(IMG / "ie-kriging-settings-2d.png", facecolor="white"); plt.close(fig)

# The small "truth" map for the top of the slide, with all 30 thermometers.
fig, ax = plt.subplots(figsize=(3.6, 1.9), dpi=200)
ax.imshow(heat, cmap="RdYlBu_r", vmin=50, vmax=71, extent=(0, 100, 46, 0), aspect="auto", alpha=0.8)
ax.plot([0, 100], [23, 23], color="black", lw=1.6)
ax.plot(extra[:, 0], extra[:, 1], "o", ms=4, color="black", mec="white", mew=0.8)
ax.plot(x, np.full_like(x, 23), "o", ms=6.5, color=BLUE, mec="white", mew=1.2)
ax.text(50, 19, "100 km line", ha="center", va="bottom", fontsize=10, color="black", weight="bold")
ax.set_xlim(0, 100); ax.set_ylim(46, 0); ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_color(GRAY)
fig.subplots_adjust(0.02, 0.03, 0.98, 0.97)
fig.savefig(IMG / "ie-kriging-settings-truth.png", facecolor="white"); plt.close(fig)

# --- The neighbor test on two other variables at the same stations -----------------------------------------
rng2 = np.random.default_rng(91)
noise = rng2.normal(size=(H, W))                           # no pattern: every km independent
random_field = 62 + 8 * noise
XX1, _ = np.meshgrid(np.arange(W), np.arange(H))
wiggle = gaussian_filter(rng2.normal(size=(H + 120, W + 120)), 25)[60:-60, 60:-60]
trend_field = 62 + 0.09 * (150 - XX1) + 1.5 * wiggle / wiggle.std()   # warm west, cool east: no sill
for key, fld, sm in [("random", random_field, gaussian_filter(noise, 0.7) * 8 / gaussian_filter(noise, 0.7).std() + 62),
                     ("trend", trend_field, trend_field)]:
    Tk = fld[P[:, 1].astype(int), P[:, 0].astype(int)] + rng2.normal(0, 1.0, NS)
    dk = np.abs(Tk[i] - Tk[j])
    fig, m, s = neighbor_axes()
    m.imshow(sm, cmap="RdYlBu_r", vmin=44, vmax=80, extent=(0, W, H, 0), alpha=0.45)
    m.plot(P[:, 0], P[:, 1], "o", ms=7, color="black", mec="white", mew=1.2)
    for sp in m.spines.values():
        sp.set_color(GRAY)
    m.plot([20, 120], [H - 12, H - 12], color="black", lw=3)
    m.text(70, H - 18, "100 km", ha="center", fontsize=10)
    s.set_ylim(0, 40)
    style_scatter(s)
    fig.savefig(IMG / f"ie-neighbor-{key}-base.png", facecolor="white"); plt.close(fig)
    fig, m, s = neighbor_axes()
    s.set_ylim(0, 40)
    m.axis("off"); s.axis("off")
    s.plot(dist, dk, "o", ms=2.6, color=GRAY, alpha=0.45, zorder=3)
    fig.savefig(IMG / f"ie-neighbor-{key}-cloud.png", transparent=True); plt.close(fig)
    print(f"{key}: mean difference under 30 km {dk[dist < 30].mean():.1f} F, over 150 km {dk[dist > 150].mean():.1f} F")

# --- Building the semivariogram, one 20 km bin at a time -------------------------------------------------------
YMAX = sill * 1.25


def build_frame(n_bins, show_bin, name):
    fig = plt.figure(figsize=(11.0, 4.6), dpi=170)
    m = fig.add_axes([0.01, 0.06, 0.42, 0.88])
    s = fig.add_axes([0.53, 0.14, 0.44, 0.80])
    m.set_xlim(0, W); m.set_ylim(H, 0); m.set_aspect("equal"); m.set_xticks([]); m.set_yticks([])
    m.imshow(field, cmap="RdYlBu_r", vmin=44, vmax=80, extent=(0, W, H, 0), alpha=0.3)
    for sp in m.spines.values():
        sp.set_color(GRAY)
    if show_bin is not None:
        a, b = edges[show_bin], edges[show_bin + 1]
        sel = (dist >= a) & (dist < b)
        for k in np.flatnonzero(sel):
            m.plot([P[i[k], 0], P[j[k], 0]], [P[i[k], 1], P[j[k], 1]], color=BLUE, lw=1.3, alpha=0.55, zorder=4)
        s.axvspan(a, b, color=BLUE, alpha=0.12, lw=0)
        s.annotate(f"{a:.0f}–{b:.0f} km: {sel.sum()} pairs\naverage ½(difference)² = {gam[show_bin]:.0f} °F²",
                   (mid[show_bin], gam[show_bin]), xytext=(60, 105 if show_bin < 2 else -10),
                   textcoords="offset points", fontsize=12, color=BLUE, weight="bold", va="top",
                   bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=BLUE, lw=1.2),
                   arrowprops=dict(arrowstyle="-", color=BLUE, lw=1.2))
    m.plot(P[:, 0], P[:, 1], "o", ms=6, color="black", mec="white", mew=1.1, zorder=5)
    m.plot([20, 120], [H - 12, H - 12], color="black", lw=3)
    m.text(70, H - 18, "100 km", ha="center", fontsize=10)
    s.plot(mid[:n_bins], gam[:n_bins], "o", ms=9, color=BLUE, mec="white", mew=1.4, zorder=4)
    s.set_xlim(0, edges[-1]); s.set_ylim(0, YMAX)
    s.set_xticks(edges[::2])
    s.set_xlabel("Distance between the two stations (km)", color=NAVY)
    s.set_ylabel("How different (semivariance, °F²)", color=NAVY)
    s.spines[["top", "right"]].set_visible(False); s.grid(color="#e3e8ef", lw=0.8)
    fig.savefig(IMG / name, facecolor="white"); plt.close(fig)


build_frame(0, None, "ie-semivariogram-build-0.png")
for k in range(3):
    build_frame(k + 1, k, f"ie-semivariogram-build-{k + 1}.png")
build_frame(len(mid), None, "ie-semivariogram-build-4.png")
