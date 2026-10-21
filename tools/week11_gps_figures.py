r"""Figures for the Week 11 Thursday deck (slides/week-11/gps-triangulation.md).

Replaces three scanned line drawings of unknown origin and a PowerPoint-shape render that labeled an
offset as a coordinate. Everything here is geometry computed on the spot:

  gps-range-uncertainty.png   one measured range is a band, not a line
  gps-dop-intersection.png    two bands cross; the overlap is the position uncertainty
  gps-pdop-high-vs-low.png    the same range error, two satellite geometries, with the horizontal DOP
                              of each computed from the unit vectors (2-D, receiver clock solved for)
  gps-dgps-worked-example.png a base at a known point, its error, and the same correction on the rover
  gps-accuracy-ladder.png     published accuracy of each positioning method, log scale; values and
                              sources are in ACCURACY below and in the slide notes

Run with a Python that has numpy and matplotlib. Writes slides/week-11/images/gps-*.png.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-11", "images")
NAVY, BLUE, RED, GRAY = "#002E5D", "#0062b8", "#c8102e", "#6b7280"
plt.rcParams.update({"font.size": 14, "font.family": "DejaVu Sans"})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    plt.close(fig)


def band(ax, c, r, w, color, label=None):
    t = np.linspace(0, 2 * np.pi, 720)
    for rr, ls in ((r - w, "--"), (r + w, "--")):
        ax.plot(c[0] + rr * np.cos(t), c[1] + rr * np.sin(t), color=color, lw=1.2, ls=ls)
    ax.fill(np.r_[c[0] + (r + w) * np.cos(t), c[0] + (r - w) * np.cos(t[::-1])],
            np.r_[c[1] + (r + w) * np.sin(t), c[1] + (r - w) * np.sin(t[::-1])], color=color, alpha=0.18, lw=0)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=2)
    ax.plot(*c, "s", ms=13, color=color)
    if label: ax.annotate(label, c, (12, 10), textcoords="offset points", color=color, fontweight="bold")


def overlap_mask(ax, sats, rx, w, extent, color=NAVY):
    x = np.linspace(extent[0], extent[1], 900); y = np.linspace(extent[2], extent[3], 900)
    X, Y = np.meshgrid(x, y)
    inside = np.ones_like(X, bool)
    for s in sats:
        r = np.hypot(*(np.array(rx) - s))
        inside &= np.abs(np.hypot(X - s[0], Y - s[1]) - r) <= w
    ax.contourf(X, Y, inside.astype(float), levels=[0.5, 1.5], colors=[color], alpha=0.85)
    ys, xs = np.nonzero(inside)
    return (x[xs].max() - x[xs].min(), y[ys].max() - y[ys].min()) if len(xs) else (0, 0)


def hdop(sats, rx):
    """2-D DOP with a receiver clock term: rows are [unit vector from satellite to receiver, 1]."""
    G = np.array([[*(np.array(rx) - s) / np.hypot(*(np.array(rx) - s)), 1.0] for s in sats])
    Q = np.linalg.inv(G.T @ G)
    return float(np.sqrt(Q[0, 0] + Q[1, 1]))


rx = np.array([0.0, 0.0])
W = 0.6  # half-width of every range band, same units as the axes

# 1. One range is a band
fig, ax = plt.subplots(figsize=(7, 6.4))
s = np.array([-6.0, 7.0]); r = np.hypot(*(rx - s))
band(ax, s, r, W, BLUE, "satellite")
ax.plot(*rx, "*", ms=20, color=RED); ax.annotate("you are somewhere\nin the shaded band", rx, (20, -40),
                                                  textcoords="offset points", color=RED, fontweight="bold")
ax.annotate("", s + (r - W) * np.array([0.7, -0.714]), s + (r + W) * np.array([0.7, -0.714]),
            arrowprops=dict(arrowstyle="<->", color="k", lw=1.5))
ax.text(*(s + (r + W + 0.4) * np.array([0.7, -0.714])), "range\nerror", fontsize=12)
ax.set_xlim(-5, 7); ax.set_ylim(-6, 5); ax.set_aspect("equal"); ax.axis("off")
save(fig, "gps-range-uncertainty.png")

# 2. Two bands cross
fig, ax = plt.subplots(figsize=(7.5, 6.4))
sats = [np.array([-7.0, 6.0]), np.array([7.0, 6.5])]
for sv, col, lab in zip(sats, (BLUE, "#2e7d32"), ("satellite 1", "satellite 2")):
    band(ax, sv, np.hypot(*(rx - sv)), W, col, lab)
overlap_mask(ax, sats, rx, W, (-4, 4, -4, 4))
ax.plot(*rx, "*", ms=18, color=RED)
ax.annotate("position uncertainty:\nwhere the bands overlap", (0.3, -0.6), (40, -60), textcoords="offset points",
            color=NAVY, fontweight="bold", arrowprops=dict(arrowstyle="->", color=NAVY))
ax.set_xlim(-8.5, 8.5); ax.set_ylim(-4.5, 8); ax.set_aspect("equal"); ax.axis("off")
save(fig, "gps-dop-intersection.png")

# 3. Same range error, two geometries
fig, axs = plt.subplots(1, 2, figsize=(13, 6.2))
cases = [("Satellites bunched together", [np.array([-3.6, 9.0]), np.array([0.3, 9.3]), np.array([3.8, 8.8])]),
         ("Satellites spread across the sky", [np.array([-8.5, 4.0]), np.array([0.0, 9.3]), np.array([8.5, 4.2])])]
for ax, (title, sv) in zip(axs, cases):
    for k, s in enumerate(sv):
        band(ax, s, np.hypot(*(rx - s)), W, BLUE)
    dx, dy = overlap_mask(ax, sv, rx, W, (-6, 6, -6, 6))
    ax.plot(*rx, "*", ms=16, color=RED)
    ax.set_title(f"{title}\nhorizontal DOP = {hdop(sv, rx):.1f}", color=NAVY, fontsize=15)
    ax.set_xlim(-6.5, 6.5); ax.set_ylim(-5.5, 10.5); ax.set_aspect("equal"); ax.axis("off")
fig.text(0.5, 0.01, "Same receiver, same range error on every satellite: only the geometry changed. "
         "Dark area = where the receiver could be.", ha="center", fontsize=13, color=GRAY)
save(fig, "gps-pdop-high-vs-low.png")

# 4. DGPS worked example
fig, ax = plt.subplots(figsize=(11, 6.2))
B, R, err = np.array([2.0, 3.0]), np.array([9.0, 5.0]), np.array([5.0, -3.0])
for p, name, col in ((B, "Base station", NAVY), (R, "Rover", "#2e7d32")):
    ax.plot(*p, "o", ms=14, color=col)
    ax.plot(*(p + err), "o", ms=14, mfc="white", mec=col, mew=2.5)
    ax.add_patch(FancyArrowPatch(p + err, p, arrowstyle="-|>", mutation_scale=22, color=RED, lw=2.2))
    ax.annotate(f"{name}: true position", p, (-14, 14), textcoords="offset points", ha="right", color=col,
                fontweight="bold")
    ax.annotate("where GPS says it is", p + err, (12, -22), textcoords="offset points", color=col)
ax.text(*(B + err / 2 + np.array([0.35, 0.35])), "error = (+5, −3)\ncorrection = (−5, +3)", color=RED,
        fontsize=13, fontweight="bold")
ax.text(*(R + err / 2 + np.array([0.35, 0.3])), "apply the same (−5, +3)", color=RED, fontsize=13,
        fontweight="bold")
ax.text(0.2, -1.2, "The base knows where it really is, so it can measure the error the satellites have right "
        "now.\nThe rover, nearby and at the same moment, has almost the same error, so the same "
        "correction fixes it.", fontsize=12.5, color=GRAY, va="top")
ax.set_xlim(-0.5, 16); ax.set_ylim(-3, 7); ax.set_aspect("equal"); ax.axis("off")
save(fig, "gps-dgps-worked-example.png")

# 5. Accuracy ladder: (method, low m, high m, source shown on the slide notes)
ACCURACY = [
    ("Smartphone, open sky", 4.9, 4.9, "gps.gov, GPS Accuracy"),
    ("GPS + WAAS (SBAS)", 0.5, 3.0, "FAA: 'a few meters'; measured 95% about 0.5-2 m"),
    ("PPP, after convergence", 0.01, 0.10, "ESA Navipedia: centimeter to decimeter"),
    ("RTK / network RTK (TURN)", 0.01, 0.05, "ESA Navipedia: a few centimeters near the base"),
    ("OPUS post-processing", 0.01, 0.05, "NGS OPUS: most positions within a few centimeters"),
]
fig, ax = plt.subplots(figsize=(12, 5.2))
for i, (name, lo, hi, _) in enumerate(ACCURACY):
    y = len(ACCURACY) - 1 - i
    if lo == hi:
        ax.plot(lo, y, "D", ms=13, color=NAVY)
    else:
        ax.plot([lo, hi], [y, y], color=BLUE, lw=12, solid_capstyle="round")
    ax.text(0.006, y, name, ha="right", va="center", fontsize=14)
ax.set_xscale("log"); ax.set_xlim(0.006, 12)
ax.set_xticks([0.01, 0.1, 1, 10]); ax.set_xticklabels(["1 cm", "10 cm", "1 m", "10 m"])
ax.set_yticks([]); ax.set_ylim(-0.7, len(ACCURACY) - 0.3)
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.grid(axis="x", color="#ddd"); ax.set_axisbelow(True)
ax.set_xlabel("typical horizontal accuracy (log scale)")
save(fig, "gps-accuracy-ladder.png")
print("written")
