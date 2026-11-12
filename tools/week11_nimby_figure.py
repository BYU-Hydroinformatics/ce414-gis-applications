r"""The Week 11 Part B NIMBY figure: Lab 10's route as the city score gets heavier.

Routes come from tools/lab10/explore_nimby.py (Route_city<w> in C:\Ames\Lab10\ref\Ref.gdb; run it
first, after run_model.py), drawn with the helpers in tools/week11_lcp_figures.py over the same
hillshade. Cities are shaded from the package's Cities layer, lakes from Major_Lakes.

Writes slides/week-11/images/lcpb-nimby.png.   ArcGIS Pro Python (propy.bat).
"""
import os
import sys

import arcpy
from arcpy.sa import Raster

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import week11_lcp_figures as F

PANELS = [("Route_base", "City weight 1 (Lab 10)", "#ff2a2a"),
          ("Route_city5", "City weight 5", "#ff8c00"),
          ("Route_city10", "City weight 10", "#b000ff")]


def main():
    import json
    import matplotlib.pyplot as plt
    nums = json.load(open(os.path.join(F.REPO, "tools", "lab10", "explore_nimby.json")))
    hs = F.arr(Raster(os.path.join(F.FG, "hs")))
    cities = F.fc_xy(os.path.join(F.L11, "PowerLineData.gdb", "Cities"))
    lakes = F.fc_xy(os.path.join(F.REF, "Major_Lakes"))
    lines = F.fc_xy(os.path.join(F.REF, "Existing_Lines"))
    fig, axs = plt.subplots(1, len(PANELS), figsize=(15, 6.6))
    for ax, (fc, title, c) in zip(axs, PANELS):
        km = 55.72 if fc == "Route_base" else nums[fc.replace("Route_", "")]["length_km"]
        F.base_ax(ax, f"{title}\n{km:.1f} km", hs)
        for p in cities:
            ax.fill(p[:, 0] / 1000, p[:, 1] / 1000, fc="#f4a6a6", ec="none", alpha=0.45)
        for p in lakes:
            ax.fill(p[:, 0] / 1000, p[:, 1] / 1000, fc="#9ecae1", ec="w", lw=0.5)
        for p in lines:
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, c="#e6c200", lw=0.7, alpha=0.8)
        if fc != "Route_base":
            F.draw(ax, "Route_base", "#ff2a2a", 5, alpha=0.4)
        F.draw(ax, fc, c, 2.6 if fc == "Route_base" else 2.2, style="-" if fc == "Route_base" else "--")
        F.ends(ax)
    F.save(fig, "lcpb-nimby.png")


if __name__ == "__main__":
    main()
