r"""Figures and numbers for the Week 12 Thursday deck (slides/week-12/least-cost-path-b.md).

Computed in ArcGIS Pro 3.7.1 (Spatial Analyst). Two parts:

1. Toy grids. The same small cost rasters run through legacy Cost Distance and through Distance
   Accumulation, so the deck can state exactly how each one charges a step (measured, not assumed).
2. Lab 11 itself: every map is drawn from the Lab 11 reference run (tools/lab11/run_model.py, in
   C:\Ames\Lab11\ref; run it first), so the deck shows the lab's own data (30 m), scores, weights and
   sensitivity runs. Adds the corridor and the legacy Cost Distance chain on the same cost surface.

Writes slides/week-12/images/lcpb-*.png and tools/week12_lcp_numbers.json.   ArcGIS Pro Python.
"""
import json
import math
import os

import arcpy
import numpy as np
from arcpy.sa import (Con, CostDistance, CostBackLink, CostPath, DistanceAccumulation, Hillshade, IsNull, SetNull,
                      OptimalPathAsLine, Raster)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-12", "images")
W = r"C:\Ames\Week12"
L11 = r"C:\Ames\Lab11\ref\lab11-power-line"
REF = r"C:\Ames\Lab11\ref\Ref.gdb"
FG = os.path.join(W, "Lab11Fig.gdb")
DEM = os.path.join(L11, "Elevation.tif")
UTM = arcpy.SpatialReference(26912)
NUM = {}
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(name)


def arr(r):
    d = arcpy.Describe(DEM)
    r = Raster(r) if isinstance(r, str) else r
    if r.isInteger:
        a = arcpy.RasterToNumPyArray(r, arcpy.Point(d.extent.XMin, d.extent.YMin), d.width, d.height,
                                     nodata_to_value=-99999).astype("float64")
        a[a == -99999] = np.nan
        return a
    return arcpy.RasterToNumPyArray(r, arcpy.Point(d.extent.XMin, d.extent.YMin), d.width, d.height,
                                    nodata_to_value=np.nan).astype("float64")


# ------------------------------------------------------------------ 1. toy grids
def toy():
    tg = os.path.join(W, "Toy.gdb")
    if arcpy.Exists(tg):
        arcpy.management.Delete(tg)
    arcpy.management.CreateFileGDB(W, "Toy.gdb")
    res = {}
    for tag, C, (i, j) in (("row", [[1, 1, 4, 1, 1, 1]], (0, 0)),
                            ("box", [[1, 1, 1, 1, 1, 1],
                                     [1, 4, 4, 4, 4, 1],
                                     [1, 4, 1, 1, 4, 1],
                                     [1, 4, 1, 4, 4, 1],
                                     [1, 1, 1, 1, 1, 1]], (2, 2))):
        C = np.asarray(C, "float32")
        x0, y0, cs = 440000, 4450000, 100
        r = arcpy.NumPyArrayToRaster(C, arcpy.Point(x0, y0), cs, cs)
        arcpy.management.DefineProjection(r, UTM)
        cost = os.path.join(tg, f"cost_{tag}")
        r.save(cost)
        fc = os.path.join(tg, f"src_{tag}")
        arcpy.management.CreateFeatureclass(tg, f"src_{tag}", "POINT", spatial_reference=UTM)
        with arcpy.da.InsertCursor(fc, ["SHAPE@XY"]) as cur:
            cur.insertRow([(x0 + (j + 0.5) * cs, y0 + (C.shape[0] - i - 0.5) * cs)])
        with arcpy.EnvManager(extent=arcpy.Describe(cost).extent, snapRaster=cost, cellSize=cost):
            da = DistanceAccumulation(fc, in_cost_raster=cost, out_back_direction_raster=os.path.join(tg, f"bd_{tag}"))
            da.save(os.path.join(tg, f"da_{tag}"))
            cd = CostDistance(fc, cost)
            cd.save(os.path.join(tg, f"cd_{tag}"))
            bl = CostBackLink(fc, cost)
            bl.save(os.path.join(tg, f"bl_{tag}"))
        g = lambda n: arcpy.RasterToNumPyArray(os.path.join(tg, n), nodata_to_value=-1).astype(float).tolist()
        res[tag] = {"cost": C.tolist(), "src": [i, j], "da": g(f"da_{tag}"), "bd": g(f"bd_{tag}"),
                    "cd": g(f"cd_{tag}"), "bl": g(f"bl_{tag}")}
    NUM["toy"] = res
    return res


def fig_toy(res):
    # the row: two tools, same six cells
    r = res["row"]
    fig, ax = plt.subplots(figsize=(11, 3.6))
    n = len(r["cost"][0])
    for k in range(n):
        c = r["cost"][0][k]
        ax.add_patch(plt.Rectangle((k, 0), 1, 1, fc="#8c6d4f" if c > 1 else "#f2e6d0", ec="k"))
        ax.text(k + 0.5, 0.5, f"cost {c:g}", ha="center", va="center", fontsize=13, color="w" if c > 1 else "k")
        ax.text(k + 0.5, -0.35, f"{r['cd'][0][k]:g}", ha="center", va="center", fontsize=14, color="#b04a00")
        ax.text(k + 0.5, -0.8, f"{r['da'][0][k]:g}", ha="center", va="center", fontsize=14, color="#0050a0")
    ax.text(0.5, 1.25, "source", ha="center", fontsize=12)
    ax.text(-0.1, -0.35, "Cost Distance (legacy)", ha="right", va="center", fontsize=12, color="#b04a00")
    ax.text(-0.1, -0.8, "Distance Accumulation", ha="right", va="center", fontsize=12, color="#0050a0")
    ax.set_xlim(-3.2, n + 0.1); ax.set_ylim(-1.1, 1.5); ax.axis("off")
    ax.set_title("Accumulated cost along one row of 100 m cells, as each tool computes it", fontsize=13)
    save(fig, "lcpb-row.png")
    # the box: accumulation and back direction from Distance Accumulation
    b = res["box"]
    C = np.array(b["cost"]); A = np.array(b["da"]); D = np.array(b["bd"])
    fig, ax = plt.subplots(figsize=(8.2, 7))
    R, K = C.shape
    for i in range(R):
        for j in range(K):
            y = R - 1 - i
            ax.add_patch(plt.Rectangle((j, y), 1, 1, fc="#8c6d4f" if C[i, j] > 1 else "#f2e6d0", ec="k", lw=0.8))
            col = "w" if C[i, j] > 1 else "k"
            if (i, j) == tuple(b["src"]):
                ax.text(j + 0.5, y + 0.5, "source", ha="center", va="center", fontsize=11, color=col)
                continue
            ax.text(j + 0.5, y + 0.78, f"{A[i, j]:.0f}", ha="center", va="center", fontsize=12, color=col)
            az = math.radians(D[i, j])
            dx, dy = math.sin(az) * 0.28, math.cos(az) * 0.28
            ax.annotate("", xy=(j + 0.5 + dx, y + 0.38 + dy), xytext=(j + 0.5 - dx, y + 0.38 - dy),
                        arrowprops=dict(arrowstyle="-|>", color="#c00000" if col == "k" else "#ffd0d0", lw=1.6))
            ax.text(j + 0.5, y + 0.08, f"{D[i, j]:.0f}°", ha="center", va="bottom", fontsize=8, color=col)
    ax.set_xlim(0, K); ax.set_ylim(0, R); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Distance Accumulation on a cost grid (light = 1, dark = 4)\n"
                 "number: accumulated cost; arrow and angle: back direction", fontsize=12)
    save(fig, "lcpb-box.png")


# ------------------------------------------------------------------ 2. Lab 11's model
# Everything below reads the Lab 11 reference run (tools/lab11/run_model.py, C:\Ames\Lab11\ref):
# the lab's own data, cell size, scores, weights and runs. New datasets go to FG, never into REF.
def path_xy(fc):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"]):
        for part in g:
            out.append(np.array([[p.X, p.Y] for p in part if p]))
    return out


def fc_xy(fc):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"]):
        for part in g:
            out.append(np.array([[p.X, p.Y] if p else [np.nan, np.nan] for p in part]))
    return out


def extent():
    d = arcpy.Describe(DEM)
    return (d.extent.XMin, d.extent.YMin, d.extent.XMax, d.extent.YMax)


def kext():
    x0, y0, x1, y1 = extent()
    return [x0 / 1000, x1 / 1000, y0 / 1000, y1 / 1000]


def base_ax(ax, title=None, hs=None):
    x0, y0, x1, y1 = extent()
    if hs is not None:
        ax.imshow(hs, cmap="gray", extent=kext(), vmin=0, vmax=255)
    ax.set_xlim(x0 / 1000, x1 / 1000); ax.set_ylim(y0 / 1000, y1 / 1000)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=12)


def ends(ax):
    for (role, (x, y)) in arcpy.da.SearchCursor(os.path.join(L11, "PowerLineData.gdb", "Endpoints"), ["Role", "SHAPE@XY"]):
        mk, c = ("^", "#00a000") if role == "Source" else ("s", "#d00000")
        ax.plot(x / 1000, y / 1000, mk, ms=11, mfc=c, mec="w", mew=1.5, zorder=10)


def draw(ax, fc, color, lw, alpha=1.0, style="-"):
    for p in path_xy(os.path.join(REF, fc)):
        ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, style, c=color, lw=lw, alpha=alpha)


def lab11():
    if not arcpy.Exists(FG):
        arcpy.management.CreateFileGDB(W, os.path.basename(FG))
    arcpy.env.workspace = FG
    arcpy.env.extent = arcpy.env.snapRaster = arcpy.env.cellSize = DEM
    ck = json.load(open(os.path.join(REPO, "tools", "lab11", "check_values.json")))
    ex = json.load(open(os.path.join(REPO, "tools", "lab11", "explore_weights.json")))
    NUM["lab11"] = {"base": ck["base"], "straight_km": ck["straight_km"],
                    "runs": {k: ck["sensitivity"][k] for k in ("line0", "line0_5", "line2", "slope0", "slope5", "nobarrier")},
                    "explore": {k: ex[k] for k in ("road0", "city0")}}
    Hillshade(DEM, 315, 45).save("hs")
    hs = arr(Raster(os.path.join(FG, "hs")))
    r = lambda n: os.path.join(REF, n)

    # the five layers and the sum
    sc = {n: arr(Raster(r(n))) for n in ("Slope_Score", "Road_Score", "City_Score", "Line_Score", "Cost_base")}
    river = ~np.isnan(arr(Raster(r("River_Cells"))))
    fig, axs = plt.subplots(2, 3, figsize=(13, 10.4))
    panels = [(sc["Slope_Score"], "Slope score\n(0-5 degrees: 1 ... over 30: 10)", "YlOrBr", 1, 10),
              (sc["Road_Score"], "Road score\n(within 1 km: 1 ... over 5 km: 10)", "YlOrBr", 1, 10),
              (sc["City_Score"], "City score\n(inside or within 1 km: 10 ... beyond 5 km: 1)", "YlOrBr", 1, 10),
              (sc["Line_Score"], "Existing-line score\n(within 500 m: 1, 0.5-2 km: 5, else 10)", "YlOrBr", 1, 10),
              (np.where(river, 10.0, np.nan), "Major streams\n(+10 on every river cell)", ListedColormap(["#2171b5"]), 0, 10),
              (sc["Cost_base"], f"Cost surface = the sum (weights 1)\n{np.nanmin(sc['Cost_base']):.0f} to {np.nanmax(sc['Cost_base']):.0f}", "magma_r", 4, 48)]
    for ax, (a, t, cm, lo, hi) in zip(axs.flat, panels):
        base_ax(ax, t, hs if a is not sc["Cost_base"] else None)
        im = ax.imshow(np.ma.masked_invalid(a), cmap=cm, vmin=lo, vmax=hi, extent=kext(), interpolation="nearest",
                       alpha=0.85 if a is not sc["Cost_base"] else 1.0)
        ends(ax)
    save(fig, "lcpb-factors.png")

    # accumulation and route
    acc = arr(Raster(r("Acc_base")))
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, None, hs)
    im = ax.imshow(np.ma.masked_invalid(acc) / 1e3, cmap="viridis_r", alpha=0.75, extent=kext())
    x0, y0, x1, y1 = extent()
    X = np.linspace(x0, x1, acc.shape[1]) / 1000; Y = np.linspace(y1, y0, acc.shape[0]) / 1000
    ax.contour(X, Y, acc, levels=np.nanpercentile(acc, range(10, 100, 10)), colors="w", linewidths=0.6)
    for p in fc_xy(r("Major_Lakes")):
        ax.fill(p[:, 0] / 1000, p[:, 1] / 1000, fc="#9ecae1", ec="w", lw=0.6)
    draw(ax, "Route_base", "#ff2a2a", 2.6)
    ends(ax)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02); cb.set_label("accumulated cost (thousands)")
    ax.set_title("Distance Accumulation from the source, around the lakes (light blue);\n"
                 "Optimal Path As Line back from the destination", fontsize=11)
    save(fig, "lcpb-accumulation.png")

    # back direction
    bd = arr(Raster(r("Back_base")))
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, None, hs)
    im = ax.imshow(np.ma.masked_invalid(bd), cmap="twilight", vmin=0, vmax=360, alpha=0.85, extent=kext(),
                   interpolation="nearest")
    draw(ax, "Route_base", "k", 2.4)
    ends(ax)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02, ticks=[0, 90, 180, 270, 360])
    cb.set_label("back direction, degrees (0 = source; 90 = go east)")
    save(fig, "lcpb-backdirection.png")

    # what moved the line
    lines = fc_xy(r("Existing_Lines"))
    def panel(ax, fc, title, c):
        base_ax(ax, title, hs)
        for p in lines:
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, c="#e6c200", lw=0.7, alpha=0.8)
        draw(ax, "Route_base", "#ff2a2a", 5, alpha=0.5)
        draw(ax, fc, c, 1.8, style="--" if c != "#ff2a2a" else "-")
        ends(ax)
    s = NUM["lab11"]
    fig, axs = plt.subplots(1, 3, figsize=(15, 6.6))
    for ax, (fc, t, c) in zip(axs, [("Route_slope5", f"Slope_Weight 5\n{s['runs']['slope5']['length_km']:.2f} km", "#00c8ff"),
                                    ("Route_x_city0", f"City weight 0\n{s['explore']['city0']['length_km']:.2f} km", "#00c8ff"),
                                    ("Route_nobarrier", f"No lake barrier\n{s['runs']['nobarrier']['length_km']:.2f} km", "#00c8ff")]):
        panel(ax, fc, t, c)
    save(fig, "lcpb-nochange.png")
    fig, axs = plt.subplots(1, 3, figsize=(15, 6.6))
    for ax, (fc, t, c) in zip(axs, [("Route_base", f"Lab 11 defaults (weights 1)\n{s['base']['length_km']:.2f} km", "#ff2a2a"),
                                    ("Route_line0", f"Line_Weight 0\n{s['runs']['line0']['length_km']:.2f} km", "#b000ff"),
                                    ("Route_x_road0", f"Road weight 0\n{s['explore']['road0']['length_km']:.2f} km", "#ffb000")]):
        panel(ax, fc, t, c)
    save(fig, "lcpb-scenarios.png")

    # corridor: accumulation from both ends
    ep = os.path.join(L11, "PowerLineData.gdb", "Endpoints")
    dst = arcpy.management.MakeFeatureLayer(ep, "d_corr", "Role = 'Destination'")
    DistanceAccumulation(dst, in_barrier_data=r("Major_Lakes"), in_cost_raster=r("Cost_base")).save("acc_from_dest")
    (Raster(r("Acc_base")) + Raster("acc_from_dest")).save("corridor_sum")
    T = arr(Raster(os.path.join(FG, "corridor_sum")))
    m = np.nanmin(T)
    NUM["lab11"]["corridor"] = {"min_sum": float(m)}
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, None, hs)
    from matplotlib.patches import Patch
    for pct, col in ((10, "#fdd49e"), (5, "#fc8d59"), (1, "#b30000")):
        band = np.where(T <= m * (1 + pct / 100), 1.0, np.nan)
        NUM["lab11"]["corridor"][f"within_{pct}pct_km2"] = round(float(np.nansum(band) * 0.0009), 1)
        ax.imshow(np.ma.masked_invalid(band), cmap=ListedColormap([col]), alpha=0.9, extent=kext(), interpolation="nearest")
    draw(ax, "Route_base", "k", 1.4)
    ends(ax)
    ax.legend(handles=[Patch(color="#b30000", label="within 1% of the cheapest"),
                       Patch(color="#fc8d59", label="within 5%"), Patch(color="#fdd49e", label="within 10%")],
              loc="lower left", fontsize=11, framealpha=0.9)
    save(fig, "lcpb-corridor.png")



def legacy():
    """The legacy chain on Lab 11's cost surface (lakes as NoData, since Cost Distance has no barrier
    input). `python week12_lcp_figures.py legacy`, after the main run (it reads its numbers file)."""
    arcpy.env.workspace = FG
    arcpy.env.extent = arcpy.env.snapRaster = arcpy.env.cellSize = DEM
    r = lambda n: os.path.join(REF, n)
    ep = os.path.join(L11, "PowerLineData.gdb", "Endpoints")
    NUM.update(json.load(open(os.path.join(REPO, "tools", "week12_lcp_numbers.json"))))
    arcpy.conversion.PolygonToRaster(r("Major_Lakes"), "OBJECTID", "lakes_r", "CELL_CENTER", cellsize=DEM)
    Con(IsNull("lakes_r"), Raster(r("Cost_base"))).save("cost_legacy")
    # feature classes, not layers: Cost Path fails on a definition-query layer (ERROR 010511)
    src = arcpy.analysis.Select(ep, "src_pt", "Role = 'Source'")
    dstl = arcpy.analysis.Select(ep, "dest_pt", "Role = 'Destination'")
    # the back link from Cost Distance's own output: a separate Cost Back Link run made Cost Path fail
    CostDistance(src, "cost_legacy", out_backlink_raster=os.path.join(FG, "bl_legacy")).save("cd_legacy")
    CostPath(dstl, "cd_legacy", "bl_legacy", "EACH_CELL").save("cp_legacy")
    arcpy.conversion.RasterToPolyline("cp_legacy", "path_legacy", "ZERO", 0, "NO_SIMPLIFY")
    leg = [g for (g,) in arcpy.da.SearchCursor("path_legacy", ["SHAPE@"])]
    new = [g for (g,) in arcpy.da.SearchCursor(r("Route_base"), ["SHAPE@"])][0]
    d = sorted(new.distanceTo(g.positionAlongLine(k)) for g in leg for k in range(0, int(g.length), 100))
    NUM["lab11"]["legacy"] = {"length_km": round(sum(g.length for g in leg) / 1000, 2),
                              "median_m": round(d[len(d) // 2]), "p95_m": round(d[int(len(d) * .95)]), "max_m": round(d[-1])}


def main():
    import sys
    if sys.argv[1:] == ["legacy"]:
        legacy()
    else:
        os.makedirs(OUT, exist_ok=True)
        fig_toy(toy())
        lab11()
    json.dump(NUM, open(os.path.join(REPO, "tools", "week12_lcp_numbers.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in NUM.items() if k != "toy"}, indent=1))


if __name__ == "__main__":
    main()
