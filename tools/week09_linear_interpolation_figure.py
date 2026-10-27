"""Week 9 linear-interpolation figure: the two-point equation over a rising line.

Redraws the hand-sketched source figure (a falling line from y0 down to y1) so the line rises from
low left to high right, the same direction as the growth chart it pops up over on the "Growing Up"
slide. The equation is written in the form the slide's worked example uses,
y = y0 + (y1 - y0)(x - x0)/(x1 - x0). Known points are blue and the estimate is orange, matching the
birthday points and the 12-and-a-half estimate on the growth chart.

    python tools/week09_linear_interpolation_figure.py      (any Python with matplotlib)

Writes slides/week-09/images/ip-linear-interpolation-equation.png, which the deck also uses on the
Today's Goals and "Interpolation: Many Methods" slides.
"""

import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12,
                     "mathtext.fontset": "dejavusans"})
NAVY, BLUE, ORANGE, GRAY = "#002e5d", "#0062b8", "#e07a1f", "#5b6770"

x0, x1, y0, y1 = 1.0, 9.0, 2.0, 8.0
x = 5.6
y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)

fig = plt.figure(figsize=(4.6, 4.4), dpi=200)
fig.text(0.5, 0.93, r"$y = y_0 + (y_1 - y_0)\,\dfrac{x - x_0}{x_1 - x_0}$",
         ha="center", va="center", fontsize=19, color=NAVY)
ax = fig.add_axes([0.13, 0.11, 0.82, 0.70])
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.spines[["top", "right"]].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_linewidth(2); ax.spines[s].set_color(NAVY)

for px, py in ((x0, y0), (x1, y1)):                   # guides from each known point to both axes
    ax.plot([px, px, 0], [0, py, py], color=GRAY, lw=1.1)
ax.plot([x, x, 0], [0, y, y], color=ORANGE, lw=1.6, ls=(0, (4, 3)))
ax.plot([x0, x1], [y0, y1], color=BLUE, lw=2.5, zorder=3)
ax.plot([x0, x1], [y0, y1], "o", ms=11, color=BLUE, mec="white", mew=1.8, zorder=5)
ax.plot([x], [y], "o", ms=12, color=ORANGE, mec="white", mew=2, zorder=6)

ax.set_xticks([x0, x, x1]); ax.set_yticks([y0, y, y1])
ax.set_xticklabels([r"$x_0$", r"$x$", r"$x_1$"], fontsize=18)
ax.set_yticklabels([r"$y_0$", r"$y$", r"$y_1$"], fontsize=18)
ax.tick_params(length=0, pad=6)
for t in ax.get_xticklabels() + ax.get_yticklabels():
    t.set_color(NAVY)
ax.get_xticklabels()[1].set_color(ORANGE); ax.get_yticklabels()[1].set_color(ORANGE)
ax.get_xticklabels()[1].set_fontweight("bold"); ax.get_yticklabels()[1].set_fontweight("bold")

fig.savefig(IMG / "ip-linear-interpolation-equation.png", facecolor="white")
plt.close(fig)
