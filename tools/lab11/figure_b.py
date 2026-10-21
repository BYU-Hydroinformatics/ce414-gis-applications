r"""Lab 11 Figure B: the study area, drawn from the hosted package (C:\Ames\Lab11\ref, extracted by
run_model.py) plus the county boundary read live from UGRC: the road network colored by road class,
the 42 fire stations, and the Census blocks shaded by population density.

    python figure_b.py      -> docs/assignments/lab-11/images/lab11-study-area.png   ArcGIS Pro Python."""
import json
import os
import urllib.parse
import urllib.request

import arcpy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "docs", "assignments", "lab-11", "images", "lab11-study-area.png")
PKG = os.path.join(r"C:\Ames\Lab11\ref", "lab11-fire-response")
SRC = os.path.join(PKG, "FireResponse.gdb")
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"


def parts(fc, where=None):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"], where):
        for part in g:
            out.append(np.array([[p.X, p.Y] if p else [np.nan, np.nan] for p in part]) / 1000)
    return out


def county():
    q = urllib.parse.urlencode({"where": "NAME = 'UTAH'", "outFields": "NAME", "returnGeometry": "true", "outSR": 26912, "f": "json"})
    with urllib.request.urlopen(f"{UGRC}/UtahCountyBoundaries/FeatureServer/0/query", q.encode(), timeout=120) as r:
        d = json.load(r)
    return [np.array(ring) / 1000 for ring in d["features"][0]["geometry"]["rings"]]


fig, ax = plt.subplots(figsize=(9.5, 7.4))
rings = county()
for ring in rings:
    ax.plot(ring[:, 0], ring[:, 1], c="#333333", lw=1.2, zorder=5)
# blocks shaded by people (quantile-ish bins), only blocks with people
polys, vals = [], []
for g, pop, land in arcpy.da.SearchCursor(os.path.join(SRC, "Census_Blocks"), ["SHAPE@", "PP_TOTAL", "ALAND20"], "PP_TOTAL > 0 AND ALAND20 > 0"):
    for part in g:
        pts = np.array([[p.X, p.Y] for p in part if p]) / 1000
        polys.append(pts); vals.append(pop / land * 1e6)   # people per square kilometer
vals = np.array(vals)
pc = PolyCollection(polys, array=vals, cmap="YlOrRd", edgecolors="none", zorder=2, alpha=0.85)
pc.set_clim(0, 4000)
ax.add_collection(pc)
# roads: local gray, major darker
local = parts(os.path.join(SRC, "Network", "Roads"), "CARTOCODE NOT IN ('1', '2', '3', '4', '5', '7')")
major = parts(os.path.join(SRC, "Network", "Roads"), "CARTOCODE IN ('1', '2', '3', '4', '5', '7')")
ax.add_collection(LineCollection(local, colors="#9a9a9a", linewidths=0.25, zorder=3))
ax.add_collection(LineCollection(major, colors="#444444", linewidths=0.9, zorder=4))
sx, sy = zip(*[(p[0] / 1000, p[1] / 1000) for (p,) in arcpy.da.SearchCursor(os.path.join(SRC, "Fire_Stations"), ["SHAPE@XY"])])
ax.scatter(sx, sy, s=46, c="#c00000", edgecolors="white", linewidths=0.8, zorder=6, label=f"Fire stations ({len(sx)})")
allxy = np.vstack(rings)
ax.set_xlim(allxy[:, 0].min() - 2, allxy[:, 0].max() + 2)
ax.set_ylim(allxy[:, 1].min() - 2, allxy[:, 1].max() + 2)
ax.set_aspect("equal")
ax.set_xlabel("Easting, km (NAD 1983 UTM zone 12N)")
ax.set_ylabel("Northing, km")
cb = fig.colorbar(pc, ax=ax, fraction=0.035, pad=0.02, extend="max")
cb.set_label("People per square kilometer, by Census block (2020)")
ax.plot([], [], c="#444444", lw=1.2, label="Highways and major roads")
ax.plot([], [], c="#9a9a9a", lw=0.6, label="Other roads in the network")
ax.plot([], [], c="#333333", lw=1.2, label="Utah County")
ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
ax.set_title("Utah County: the road network, the fire stations and where the people are", fontsize=11)
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("wrote", OUT, len(local) + len(major), "road parts;", len(polys), "populated block parts")
