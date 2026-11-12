r"""Week 11 Part B "what can move the line" figures: Lab 10's route under other weights, terrain terms
and constraints.

Routes come from the tools/lab10/explore_*.py runs (Route_<tag> in C:\Ames\Lab10\ref\Ref.gdb; run
run_model.py first, then explore_nimby.py, explore_elevation.py and explore_road_corridor.py), drawn
with the helpers in tools/week11_lcp_figures.py over the same hillshade. Cities are shaded from the
package's Cities layer (municipal boundaries), lakes from Major_Lakes; the pale red line in every panel
after the first is Lab 10's baseline route.

Writes slides/week-11/images/lcpb-nimby.png, lcpb-elevation.png and lcpb-corridor-barrier.png.
ArcGIS Pro Python (propy.bat).
"""
import json
import os
import sys

import numpy as np
from arcpy.sa import Raster

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import week11_lcp_figures as F

LAB10 = os.path.join(F.REPO, "tools", "lab10")
FIGURES = {
    "lcpb-nimby.png": [
        ("Route_base", "City weight 1 (Lab 10)", "#ff2a2a", False),
        ("Route_city5", "City weight 5", "#ff8c00", False),
        ("Route_city10", "City weight 10", "#b000ff", False)],
    "lcpb-elevation.png": [
        ("Route_elev_product_city1", "Elevation × scores, city 1", "#00a0e0", False),
        ("Route_elev_product_city5", "Elevation × scores, city 5", "#ff8c00", False),
        ("Route_elev_product_city10", "Elevation × scores, city 10", "#b000ff", False)],
    "lcpb-corridor-barrier.png": [
        ("Route_city10", "City weight 10, no corridor", "#b000ff", False),
        ("Route_corr_current_city10", "City weight 10, road corridor", "#ff8c00", True),
        ("Route_corr_old_city10", "Elevation × scores, road corridor\n(any city weight)", "#00a0e0", True)],
}


def lengths():
    km = {"Route_base": 55.72}
    for f in ("explore_nimby.json", "explore_elevation.json", "explore_road_corridor.json"):
        for tag, v in json.load(open(os.path.join(LAB10, f))).items():
            if isinstance(v, dict) and "length_km" in v:
                km[f"Route_{tag}"] = v["length_km"]
    return km


def main():
    import matplotlib.pyplot as plt
    km = lengths()
    hs = F.arr(Raster(os.path.join(F.FG, "hs")))
    cities = F.fc_xy(os.path.join(F.L11, "PowerLineData.gdb", "Cities"))
    lakes = F.fc_xy(os.path.join(F.REF, "Major_Lakes"))
    lines = F.fc_xy(os.path.join(F.REF, "Existing_Lines"))
    outside = np.isnan(F.arr(Raster(os.path.join(F.REF, "Road_Corridor"))))
    for name, panels in FIGURES.items():
        fig, axs = plt.subplots(1, len(panels), figsize=(15, 6.6))
        for ax, (fc, title, c, corridor) in zip(axs, panels):
            F.base_ax(ax, f"{title}\n{km[fc]:.1f} km", hs)
            for p in cities:
                ax.fill(p[:, 0] / 1000, p[:, 1] / 1000, fc="#f4a6a6", ec="none", alpha=0.45)
            if corridor:   # cells more than 2 km from a major road: a hard barrier
                ax.imshow(np.ma.masked_where(~outside, outside.astype(float)), cmap="Greys", vmin=0, vmax=1.6,
                          alpha=0.55, extent=F.kext(), interpolation="nearest")
            for p in lakes:
                ax.fill(p[:, 0] / 1000, p[:, 1] / 1000, fc="#9ecae1", ec="w", lw=0.5)
            for p in lines:
                ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, c="#e6c200", lw=0.7, alpha=0.8)
            if fc != "Route_base":
                F.draw(ax, "Route_base", "#ff2a2a", 5, alpha=0.4)
            F.draw(ax, fc, c, 2.6 if fc == "Route_base" else 2.2, style="-" if fc == "Route_base" else "--")
            F.ends(ax)
        F.save(fig, name)


if __name__ == "__main__":
    main()
