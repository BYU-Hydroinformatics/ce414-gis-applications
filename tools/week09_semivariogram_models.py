"""Week 9 Thursday figure: the three semivariogram models Lab 8 offers, at one range and sill.

Formulas as ArcGIS Pro's Spatial Analyst Kriging documents them (range r, partial sill c, nugget c0):
  spherical    c0 + c * (1.5 h/r - 0.5 (h/r)^3) for h <= r, else c0 + c
  exponential  c0 + c * (1 - exp(-3 h / r))
  Gaussian     c0 + c * (1 - exp(-3 (h / r)^2))
The exponential and Gaussian models only approach the sill, so r is their "effective" range (95 %).
Writes slides/week-09/images/ie-semivariogram-models.png.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "slides", "week-09", "images")
r, c0, c = 1.0, 0.15, 0.85
h = np.linspace(0, 1.8, 400)

sph = np.where(h <= r, c0 + c * (1.5 * h / r - 0.5 * (h / r) ** 3), c0 + c)
exp = c0 + c * (1 - np.exp(-3 * h / r))
gau = c0 + c * (1 - np.exp(-3 * (h / r) ** 2))
for y in (sph, exp, gau):
    y[0] = 0.0          # by definition the semivariance at exactly zero distance is zero

fig, ax = plt.subplots(figsize=(9, 6.4), dpi=150)
ax.plot(h[1:], sph[1:], color="#0062b8", lw=3, label="Spherical — rises steadily, flat at the range")
ax.plot(h[1:], exp[1:], color="#c2410c", lw=3, label="Exponential — steep near zero, levels off slowly")
ax.plot(h[1:], gau[1:], color="#15803d", lw=3, label="Gaussian — flat near zero: assumes a very smooth surface")

ax.axhline(c0 + c, color="#4a5568", lw=1, ls="--")
ax.axvline(r, color="#4a5568", lw=1, ls="--")
ax.plot([0], [c0], "o", color="#4a5568")
ax.annotate("nugget", xy=(0, c0), xytext=(0.08, 0.05), fontsize=13, color="#4a5568",
            arrowprops=dict(arrowstyle="->", color="#4a5568"))
ax.annotate("", xy=(1.62, c0), xytext=(1.62, c0 + c),
            arrowprops=dict(arrowstyle="<->", color="#4a5568"))
ax.text(1.645, c0 + c / 2, "partial\nsill", fontsize=13, color="#4a5568", va="center")
ax.axhline(c0, xmin=0.86, xmax=0.93, color="#4a5568", lw=1)
ax.text(1.25, c0 + c + 0.03, "sill = nugget + partial sill", fontsize=13, color="#4a5568")
ax.text(r + 0.02, 0.04, "range", fontsize=13, color="#4a5568")

ax.set_xlim(0, 1.8)
ax.set_ylim(0, 1.15)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("distance between points, h", fontsize=14)
ax.set_ylabel("semivariance (squared units)", fontsize=14)
ax.legend(fontsize=12, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=1)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ie-semivariogram-models.png"))
print("wrote ie-semivariogram-models.png")
