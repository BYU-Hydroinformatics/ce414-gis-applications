r"""Figures for the Week 9 Tuesday deck, slides/week-09/interpolation-explorer.md.

1. ie-error-row.png: the three error panels and their legend, cropped from Lab 10's example baseline
   map (docs/assignments/lab-10/images/lab10-example-map-baseline.png).
2. ie-checkpoint-spread.png + numbers: how much an RMSE measured at 200 random checkpoints wanders
   around the RMSE over every cell. Uses the baseline surfaces that tools/lab10/verify_package.py
   leaves in C:\Ames\Lab09\ZipCheck (course 2,500 points; IDW power 2; ordinary spherical Kriging).
   The 200-point draws here are NOT the lab's Checkpoints feature class, so the lab's own checkpoint
   answers are not shown.

ArcGIS Pro Python (arcpy + matplotlib).
"""
import json, os
import numpy as np
import arcpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-09", "images")
GDB = r"C:\Ames\Lab09\ZipCheck\lab10-y-mountain\Lab10.gdb"

# 1. Crop the error row (panels + legend) out of the example map.
im = Image.open(os.path.join(REPO, "docs", "assignments", "lab-10", "images", "lab10-example-map-baseline.png"))
im.crop((250, 545, 1607, 883)).save(os.path.join(OUT, "ie-error-row.png"))

# 2. Checkpoint spread.
TRUE = arcpy.Raster(os.path.join(GDB, "True_DEM"))
LL = arcpy.Point(TRUE.extent.XMin, TRUE.extent.YMin)


def arr(name):
    # Read every raster on True_DEM's grid (the surfaces are a cell or two larger).
    return arcpy.RasterToNumPyArray(arcpy.Raster(os.path.join(GDB, name)), LL, TRUE.width, TRUE.height,
                                    nodata_to_value=np.nan).astype("float64")

truth = arr("True_DEM")
errs = {m: truth - arr(r) for m, r in (("Thiessen", "TH_n2500"), ("IDW", "IDW_base"), ("Kriging", "KR_base"))}
ok = np.isfinite(truth) & np.all([np.isfinite(e) for e in errs.values()], axis=0)
idx = np.flatnonzero(ok)
rng = np.random.default_rng(2026)
draws = [rng.choice(idx, 200, replace=False) for _ in range(2000)]
res = {"cells": int(ok.sum()), "draws": len(draws), "n": 200}
flat_errs = {m: e.ravel() for m, e in errs.items()}
per_draw = [{m: np.sqrt(np.mean(f[d] ** 2)) for m, f in flat_errs.items()} for d in draws]
res["ranking_kept"] = round(sum(r["Kriging"] < r["IDW"] < r["Thiessen"] for r in per_draw) / len(draws), 3)
res["kriging_beats_idw"] = round(sum(r["Kriging"] < r["IDW"] for r in per_draw) / len(draws), 3)
colors = {"Thiessen": "#c05621", "IDW": "#2b6cb0", "Kriging": "#2f855a"}
fig, ax = plt.subplots(figsize=(11, 5.2), dpi=150)
bins = np.arange(5, 46, 0.5)
for m, e in errs.items():
    flat = e.ravel()
    full = float(np.sqrt(np.mean(flat[idx] ** 2)))
    sample = np.array([np.sqrt(np.mean(flat[d] ** 2)) for d in draws])
    lo, hi = np.percentile(sample, [5, 95])
    res[m] = dict(full=round(full, 2), p5=round(float(lo), 2), p95=round(float(hi), 2),
                  min=round(float(sample.min()), 2), max=round(float(sample.max()), 2))
    ax.hist(sample, bins=bins, color=colors[m], alpha=0.55, label=f"{m}: every cell {full:.2f} m")
    ax.axvline(full, color=colors[m], lw=2.5)
ax.set_xlabel("RMSE measured at 200 random checkpoints (m)", fontsize=13)
ax.set_ylabel("how many of 2,000 draws", fontsize=13)
ax.set_title("Same three surfaces, 2,000 different sets of 200 checkpoints  (line = RMSE over all 67,337 cells)",
             fontsize=13)
ax.legend(fontsize=12, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "ie-checkpoint-spread.png"))
json.dump(res, open(os.path.join(REPO, "tools", "week09_interpolation_numbers.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
