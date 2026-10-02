"""Week 7 Thursday figures for Lab 6 (Lake Powell).

- lb-powell-area.png: main-pool area against water-surface elevation from the Lab 6 model run in
  arcpy (tools/lab06/levels_deadpool.csv, 3,370-3,700 ft by 10), with the USGS published areas
  (SIR 2022-5017, as interpolated in the Lab 6 package's instructor key) for comparison, and the
  Sept 15, 2026 record low (3,516.62 ft, Reclamation record in the Lab 6 data package).
- copies of the Lab 6 example map and the Wahweap check map into slides/week-07/images/.

    python tools/week07_powell_figures.py   (needs matplotlib; the ArcGIS Pro Python has it)
"""
import csv
import pathlib
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "slides" / "week-07" / "images"
LAB = ROOT / "docs" / "assignments" / "lab-06" / "images"
KEY = pathlib.Path(r"C:\Ames\Lab06Pkg\CE414_Lab06_Package\data\instructor\powell_check_values.csv")
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 13, "axes.spines.top": False, "axes.spines.right": False})

runs = [(float(r["elevation_ft"]), float(r["pool_sqmi"])) for r in csv.DictReader(open(ROOT / "tools" / "lab06" / "levels_deadpool.csv"))]
usgs = [(float(r["elevation_ft_ngvd29"]), float(r["usgs_sir2022_5017_sqmi"])) for r in csv.DictReader(open(KEY))
        if r["surface"] == "powell_30m" and r["usgs_sir2022_5017_sqmi"]]
fig, ax = plt.subplots(figsize=(11, 4.8), dpi=150)
ax.plot([a for _, a in runs], [z for z, _ in runs], "o-", color="#0062b8", ms=4, lw=2, label="Lab 6 model, 30 m surface")
ax.plot([a for _, a in usgs], [z for z, _ in usgs], "--", color="#002e5d", lw=1.5, label="USGS published (SIR 2022-5017)")
for z, lab, col in ((3700, "full pool, 3,700 ft", "#002e5d"), (3516.62, "record low, Sept 15, 2026: 3,516.6 ft", "#b3261e"),
                    (3490, "minimum power pool, 3,490 ft", "#e07a1f"), (3370, "dead pool, 3,370 ft", "#5b6770")):
    ax.axhline(z, color=col, lw=1, ls=":")
    ax.text(250, z + 3, lab, ha="right", color=col, fontsize=11)
ax.set_xlabel("Lake area, main pool (sq mi)"); ax.set_ylabel("Water-surface elevation (ft, NGVD29)")
ax.set_xlim(0, 255); ax.grid(color="#e5e8eb"); ax.legend(frameon=False, loc="upper left")
ax.set_title("Lake Powell: area at every 10 ft, from one looping model", loc="left", color="#002e5d", fontsize=15)
fig.tight_layout(); fig.savefig(IMG / "lb-powell-area.png"); plt.close(fig)
shutil.copy(LAB / "lab06-example-map-baseline.png", IMG / "lb-powell-example-map.png")
shutil.copy(LAB / "lab06-check-wahweap.jpg", IMG / "lb-powell-wahweap.jpg")
print("lb-powell-area.png, lb-powell-example-map.png, lb-powell-wahweap.jpg")
