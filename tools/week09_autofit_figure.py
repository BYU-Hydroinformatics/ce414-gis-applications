"""Week 9 Thursday figure: why the automatic kriging fit on the Timpanogos samples came out flat.

The same 150 samples as tools/week09_elevation_figures.py (same DEM request, same seed), with their
semivariogram binned two ways:

- careful: pairs grouped every 300 m out to 4.5 km, and the spherical model fitted to them, which
  rises steadily to a range of about 4.6 km (the "Kriging (spherical, fitted)" panel);
- automatic: pykrige's defaults, 6 groups spread over every distance in the square, out to about 8 km.
  The far groups are pairs on opposite low flanks of the mountain, so they are alike again and the
  dots rise and then fall. A spherical curve can only rise and level off, so the least-squares fit
  gives up on the rise and jumps to the average level at once: a range of a fraction of a meter. To
  that model no sample says anything about the ground next to it, so every cell gets the mean.

    python tools/week09_autofit_figure.py      (needs numpy, scipy, matplotlib, pykrige, tifffile, internet)

Writes slides/week-09/images/ie-autofit-flat.png and prints the two fits.
"""

import io
import pathlib
import urllib.parse
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tifffile
from pykrige.ok import OrdinaryKriging
from scipy.optimize import curve_fit

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-09" / "images"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "DejaVu Sans"], "font.size": 12})
NAVY, BLUE, ORANGE, GRAY, RED = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#c8102e"

# --- truth and samples, exactly as in week09_elevation_figures.py -------------------------------------
CX, CY, HALF, CELL = 445200, 4471300, 3600, 30
N = 2 * HALF // CELL
q = dict(bbox=f"{CX - HALF},{CY - HALF},{CX + HALF},{CY + HALF}", bboxSR=26912, imageSR=26912,
         size=f"{N},{N}", format="tiff", pixelType="F32", noDataInterpretation="esriNoDataMatchAny",
         interpolation="RSP_BilinearInterpolation", f="image")
url = ("https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?"
       + urllib.parse.urlencode(q))
T = tifffile.imread(io.BytesIO(urllib.request.urlopen(url, timeout=120).read())).astype(float)
assert T.shape == (N, N) and not np.isnan(T).any()
x = (np.arange(N) + 0.5) * CELL / 1000
y = (np.arange(N) + 0.5) * CELL / 1000
rng = np.random.default_rng(414)
idx = rng.choice((N - 8) ** 2, 150, replace=False)
r, c = idx // (N - 8) + 4, idx % (N - 8) + 4
P = np.c_[x[c], y[r]]
V = T[r, c]

# --- careful bins and fit ------------------------------------------------------------------------------
h = np.hypot(*(P[:, None, :] - P[None, :, :]).transpose(2, 0, 1))
g2 = 0.5 * (V[:, None] - V[None, :]) ** 2
iu = np.triu_indices(len(V), 1)
h, g2 = h[iu], g2[iu]
edges = np.arange(0, 4.8, 0.3)
mid = (edges[:-1] + edges[1:]) / 2
gam = np.array([g2[(h >= lo) & (h < hi)].mean() for lo, hi in zip(edges[:-1], edges[1:])])


def spherical(hh, c0, cc, a):
    s_ = np.where(hh < a, 1.5 * hh / a - 0.5 * (hh / a) ** 3, 1.0)
    return c0 + cc * s_


(c0, cc, a_), _ = curve_fit(spherical, mid, gam, p0=[1000, gam.max(), 2.0], bounds=([0, 0, 0.2], [np.inf, np.inf, 20]))

# --- pykrige's automatic version ------------------------------------------------------------------------
ok_auto = OrdinaryKriging(P[:, 0], P[:, 1], V, variogram_model="spherical", exact_values=False)
ps_auto, rg_auto, ng_auto = ok_auto.variogram_model_parameters
print(f"careful: nugget {c0:.0f}, partial sill {cc:.0f} m2, range {a_:.2f} km")
print(f"automatic: lags {np.round(ok_auto.lags, 2)} km, semivariance {np.round(ok_auto.semivariance)}")
print(f"automatic: nugget {ng_auto:.0f}, partial sill {ps_auto:.0f} m2, range {rg_auto * 1000:.2f} m")

K = 1000.0                                    # plot in thousands of m^2
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.3), dpi=170, sharey=True)
ymax = 200
for ax in axs:
    ax.set_xlim(0, 8.5); ax.set_ylim(0, ymax)
    ax.spines[["top", "right"]].set_visible(False); ax.grid(color="#e3e8ef", lw=0.8)
    ax.set_xlabel("Distance between the two samples (km)", color=NAVY)
axs[0].set_ylabel("How different (semivariance, 1,000 m²)", color=NAVY)

ax = axs[0]
hh = np.linspace(0, 8.5, 400)
ax.plot(hh, spherical(hh, c0, cc, a_) / K, color=ORANGE, lw=3, zorder=3)
ax.plot(mid, gam / K, "o", ms=7, color=BLUE, mec="white", mew=1.2, zorder=4)
ax.set_title("Careful: a group every 300 m, out to 4.5 km", loc="left", fontsize=13, color=NAVY, weight="bold")
ax.text(0.97, 0.06, f"rises to a range of {a_:.1f} km:\nclose samples are alike", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=12, color=GRAY)

ax = axs[1]
ax.plot([0, 0], [0, ng_auto / K], color=ORANGE, lw=3, zorder=3)
ax.plot([0, 8.5], [(ng_auto + ps_auto) / K] * 2, color=ORANGE, lw=3, zorder=3)
ax.plot([0, 0.02], [ng_auto / K, (ng_auto + ps_auto) / K], color=ORANGE, lw=3, zorder=3)
ax.plot(ok_auto.lags, ok_auto.semivariance / K, "o", ms=11, color=BLUE, mec="white", mew=1.4, zorder=4)
ax.set_title("Automatic: 6 wide groups, out to 8 km", loc="left", fontsize=13, color=NAVY, weight="bold")
ax.annotate("far pairs: both on low flanks,\nalike again", (ok_auto.lags[-1], ok_auto.semivariance[-1] / K),
            xytext=(4.4, 22), textcoords="data", fontsize=11, color=BLUE, ha="center",
            arrowprops=dict(arrowstyle="-", color=BLUE, lw=1))
ax.text(0.97, 0.97, "a flat line fits best:\nrange ≈ 0, so every cell\ngets the mean", transform=ax.transAxes,
        ha="right", va="top", fontsize=12, color=RED, weight="bold")
fig.tight_layout(w_pad=2.0)
fig.savefig(IMG / "ie-autofit-flat.png", facecolor="white"); plt.close(fig)
