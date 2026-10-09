r"""Figures and numbers for the Week 12 Thursday deck (slides/week-12/least-cost-path-b.md).

Everything is computed in ArcGIS Pro 3.7.1 (Spatial Analyst) from tools/week12_lcp_data.py's download
of Lab 11's setting (C:\Ames\Week12). Three parts:

1. Toy grids. The same small cost rasters run through legacy Cost Distance and through Distance
   Accumulation, so the deck can state exactly how each one charges a step (measured, not assumed).
2. Lab 11's recipe, as its handout states it, at 100 m: within 2 km of a major road = 1, elsewhere
   NoData; within 2 km of a major river or lake = 10, else 1; cities scaled 1 to 10 by distance out to
   5 km; on an existing power line = 1, else 10; all multiplied together and by the elevation.
   Where the handout leaves a number open (the city scale, the power-line rasterization) the choice
   is written in CITY_SCALE and the docstring of cost_surface() and stated on the slide.
3. Scenarios that change one decision each, the straight line, and a near-optimal corridor.

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
SRC = os.path.join(W, "LCP.gdb")
G = os.path.join(W, "Work.gdb")
DEM = os.path.join(W, "dem100.tif")
UTM = arcpy.SpatialReference(26912)
NUM = {}
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
# Cities: inside a city or within 1 km = 10, then 8, 6, 4, 2 out to 5 km, beyond = 1
CITY_SCALE = [(0, 10), (1000, 10), (2000, 8), (3000, 6), (4000, 4), (5000, 2)]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=150)
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


# ------------------------------------------------------------------ 2. Lab 11's cost surface
def prep():
    if not arcpy.Exists(G):
        arcpy.management.CreateFileGDB(W, "Work.gdb")
    arcpy.management.CalculateStatistics(DEM)
    arcpy.env.workspace = G
    arcpy.env.extent = arcpy.env.snapRaster = arcpy.env.cellSize = DEM
    arcpy.env.outputCoordinateSystem = UTM
    s = lambda n: os.path.join(SRC, n)
    arcpy.analysis.PairwiseBuffer(s("Major_Roads"), "road_buf", "2 Kilometers", "ALL")
    arcpy.analysis.PairwiseBuffer(s("Major_Streams"), "stream_buf", "2 Kilometers", "ALL")
    arcpy.analysis.PairwiseBuffer(s("Major_Lakes"), "lake_buf", "2 Kilometers", "ALL")
    arcpy.management.Merge(["stream_buf", "lake_buf"], "water_two")
    arcpy.analysis.PairwiseDissolve("water_two", "water_buf")
    arcpy.analysis.MultipleRingBuffer(s("Cities"), "city_rings", [1, 2, 3, 4, 5], "Kilometers", "distance",
                                      "ALL", "FULL")
    for fc, val in (("road_buf", "road"), ("water_buf", "water")):
        arcpy.management.AddField(fc, "v", "SHORT"); arcpy.management.CalculateField(fc, "v", "1")
        arcpy.conversion.PolygonToRaster(fc, "v", f"{val}_r", "CELL_CENTER", cellsize=DEM)
    arcpy.conversion.PolygonToRaster("city_rings", "distance", "city_r", "CELL_CENTER", cellsize=DEM)
    pl = s("Power_Lines")
    arcpy.management.AddField(pl, "v", "SHORT"); arcpy.management.CalculateField(pl, "v", "1")
    arcpy.conversion.PolylineToRaster(pl, "v", "power_r", "MAXIMUM_LENGTH", cellsize=DEM)
    arcpy.conversion.PolygonToRaster(s("Cities"), "OBJECTID", "inside_city", "CELL_CENTER", cellsize=DEM)
    Hillshade(DEM, 315, 45).save("hs")


def cost_surface(roads="barrier", cities=True, power=True, water=True, elevation=True, name="cost"):
    """Lab 11: road = 1 within 2 km else NoData ("barrier") or 10 ("soft"); water = 10 within 2 km else
    1; city = CITY_SCALE by ring (inside a city = 10); power = 1 on a cell the line crosses (Polyline
    to Raster, 100 m) else 10; times the elevation in meters."""
    if roads == "barrier":
        road = SetNull(IsNull("road_r"), 1)
    elif roads == "soft":
        road = Con(IsNull("road_r"), 10, 1)
    else:
        road = Raster(DEM) * 0 + 1
    f = road
    if water:
        f = f * Con(IsNull("water_r"), 1, 10)
    if cities:
        ring = Raster("city_r")
        cf = Con(IsNull(ring), 1, 1)
        for d, v in CITY_SCALE[1:]:
            cf = Con(ring == d / 1000, v, cf)
        cf = Con(IsNull("inside_city"), cf, 10)
        f = f * cf
    if power:
        f = f * Con(IsNull("power_r"), 10, 1)
    if elevation:
        f = f * Raster(DEM)
    f.save(name)
    return name


def route(cost, tag):
    pts = os.path.join(SRC, "Endpoints")
    src = arcpy.management.MakeFeatureLayer(pts, f"s_{tag}", "Role = 'Source'")
    dst = arcpy.management.MakeFeatureLayer(pts, f"d_{tag}", "Role = 'Destination'")
    acc = DistanceAccumulation(src, in_cost_raster=cost, out_back_direction_raster=f"bd_{tag}")
    acc.save(f"acc_{tag}")
    OptimalPathAsLine(dst, f"acc_{tag}", f"bd_{tag}", f"path_{tag}")
    length = sum(r[0] for r in arcpy.da.SearchCursor(f"path_{tag}", ["SHAPE@LENGTH"])) / 1000
    x, y = NUM["dest_xy"]
    total = float(arcpy.management.GetCellValue(f"acc_{tag}", f"{x} {y}").getOutput(0))
    NUM[tag] = {"length_km": round(length, 2), "total_cost": total}
    return length, total


def path_xy(tag):
    out = []
    for (g,) in arcpy.da.SearchCursor(f"path_{tag}", ["SHAPE@"]):
        for part in g:
            out.append(np.array([[p.X, p.Y] for p in part if p]))
    return out


def fc_xy(fc, where=None):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"], where):
        for part in g:
            pts = [[p.X, p.Y] if p else [np.nan, np.nan] for p in part]
            out.append(np.array(pts))
    return out


def base_ax(ax, ext, title=None, hs=None):
    xmin, ymin, xmax, ymax = ext
    if hs is not None:
        ax.imshow(hs, cmap="gray", extent=[xmin / 1000, xmax / 1000, ymin / 1000, ymax / 1000], vmin=0, vmax=255)
    ax.set_xlim(xmin / 1000, xmax / 1000); ax.set_ylim(ymin / 1000, ymax / 1000)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
    if title:
        ax.set_title(title, fontsize=12)


def ends(ax):
    for k, mk, c in (("src_xy", "^", "#00a000"), ("dest_xy", "s", "#d00000")):
        x, y = NUM[k]
        ax.plot(x / 1000, y / 1000, mk, ms=11, mfc=c, mec="w", mew=1.5, zorder=10)


def main():
    os.makedirs(OUT, exist_ok=True)
    fig_toy(toy())
    prep()
    for (r, x, y) in arcpy.da.SearchCursor(os.path.join(SRC, "Endpoints"), ["Role", "SHAPE@X", "SHAPE@Y"]):
        NUM["src_xy" if r == "Source" else "dest_xy"] = [x, y]
    sx, sy = NUM["src_xy"]; dx, dy = NUM["dest_xy"]
    NUM["straight_km"] = round(math.hypot(sx - dx, sy - dy) / 1000, 2)
    d = arcpy.Describe(DEM)
    ext = (d.extent.XMin, d.extent.YMin, d.extent.XMax, d.extent.YMax)
    hs = arr(Raster("hs"))
    dem = arr(Raster(DEM))
    NUM["dem_range"] = [float(np.nanmin(dem)), float(np.nanmax(dem))]

    scen = {"base": dict(), "soft_roads": dict(roads="soft"), "no_cities": dict(cities=False),
            "no_power": dict(power=False), "no_water": dict(water=False),
            "terrain_only": dict(roads="none", cities=False, power=False, water=False)}
    for tag, kw in scen.items():
        c = cost_surface(name=f"cost_{tag}", **kw)
        route(c, tag)
        print(tag, NUM[tag])

    # the legacy chain Lab 11's handout names, on the same cost surface
    pts = os.path.join(SRC, "Endpoints")
    s_l = arcpy.management.MakeFeatureLayer(pts, "s_legacy", "Role = 'Source'")
    d_l = arcpy.management.MakeFeatureLayer(pts, "d_legacy", "Role = 'Destination'")
    CostDistance(s_l, "cost_base").save("cd_legacy")
    CostBackLink(s_l, "cost_base").save("bl_legacy")
    CostPath(d_l, "cd_legacy", "bl_legacy", "EACH_CELL").save("cp_legacy")
    arcpy.conversion.RasterToPolyline("cp_legacy", "path_legacy", "ZERO", 0, "NO_SIMPLIFY")
    NUM["legacy"] = {"length_km": round(sum(r[0] for r in arcpy.da.SearchCursor("path_legacy", ["SHAPE@LENGTH"])) / 1000, 2),
                     "total_cost": float(arcpy.management.GetCellValue("cd_legacy", f"{dx} {dy}").getOutput(0))}
    print("legacy", NUM["legacy"])

    # factor panels
    road = arr(Con(IsNull("road_r"), 0, 1))
    water = arr(Con(IsNull("water_r"), 1, 10))
    ring = arr(Raster("city_r")); inside = ~np.isnan(arr(Raster("inside_city")))
    city = np.ones_like(ring)
    for dd, v in CITY_SCALE[1:]:
        city[ring == dd / 1000] = v
    city[inside] = 10
    power = arr(Con(IsNull("power_r"), 10, 1))
    cost = arr(Raster("cost_base"))
    fig, axs = plt.subplots(2, 3, figsize=(13, 10.2))
    panels = [(road, "Major road within 2 km:\n1, else NoData (white)", ListedColormap(["white", "#4d4d4d"]), 0, 1),
              (water, "Major river or lake within 2 km:\n10, else 1", ListedColormap(["#f0f0f0", "#2171b5"]), 1, 10),
              (city, "Cities, by distance out to 5 km:\n10 inside, 8, 6, 4, 2, then 1", "Oranges", 1, 10),
              (power, "Existing power line:\n1 on the line, else 10", ListedColormap(["#d4a000", "#f0f0f0"]), 1, 10),
              (dem, f"Elevation, m (multiplier)\n{NUM['dem_range'][0]:,.0f} to {NUM['dem_range'][1]:,.0f}", "terrain", None, None),
              (np.log10(cost), "Cost = product of all five\n(log scale; white = NoData)", "magma_r", None, None)]
    for ax, (a, t, cm, lo, hi) in zip(axs.flat, panels):
        base_ax(ax, ext, t)
        ma = np.ma.masked_invalid(a.astype(float))
        if lo is not None and a is road:
            ma = np.ma.masked_where(a == 0, a)
            ax.imshow(np.ones_like(a), cmap=ListedColormap(["white"]), extent=[e / 1000 for e in (ext[0], ext[2], ext[1], ext[3])])
        ax.imshow(ma, cmap=cm, vmin=lo, vmax=hi, extent=[e / 1000 for e in (ext[0], ext[2], ext[1], ext[3])],
                  interpolation="nearest")
        ends(ax)
    save(fig, "lcpb-factors.png")

    # accumulation with the path
    acc = arr(Raster("acc_base"))
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, ext, None, hs)
    im = ax.imshow(np.ma.masked_invalid(acc) / 1e6, cmap="viridis_r", alpha=0.75,
                   extent=[e / 1000 for e in (ext[0], ext[2], ext[1], ext[3])])
    lv = np.nanpercentile(acc, [10, 20, 30, 40, 50, 60, 70, 80, 90])
    X = np.linspace(ext[0], ext[2], acc.shape[1]) / 1000; Y = np.linspace(ext[3], ext[1], acc.shape[0]) / 1000
    ax.contour(X, Y, acc, levels=lv, colors="w", linewidths=0.6)
    for p in path_xy("base"):
        ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c="#ff2a2a", lw=2.6)
    ends(ax)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02); cb.set_label("accumulated cost (millions)")
    ax.set_title("Distance Accumulation from the source; Optimal Path As Line back from the destination",
                 fontsize=11)
    save(fig, "lcpb-accumulation.png")

    # back direction near the destination
    bd = arr(Raster("bd_base"))
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, ext, None, hs)
    im = ax.imshow(np.ma.masked_invalid(bd), cmap="twilight", vmin=0, vmax=360, alpha=0.85,
                   extent=[e / 1000 for e in (ext[0], ext[2], ext[1], ext[3])], interpolation="nearest")
    for p in path_xy("base"):
        ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c="k", lw=2.4)
    ends(ax)
    cb = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02, ticks=[0, 90, 180, 270, 360])
    cb.set_label("back direction, degrees (0 = source; 90 = go east)")
    save(fig, "lcpb-backdirection.png")

    # scenarios
    roads = fc_xy(os.path.join(SRC, "Major_Roads"))
    fig, axs = plt.subplots(1, 4, figsize=(17, 6.2))
    sets = [("base", "Lab 11 recipe", "#ff2a2a"),
            ("no_power", "No reward for power lines", "#ffb000"),
            ("no_water", "No water penalty", "#b000ff"),
            ("terrain_only", "Elevation alone", "#00c8ff")]
    for ax, (tag, title, c) in zip(axs, sets):
        base_ax(ax, ext, f"{title}\n{NUM[tag]['length_km']:.1f} km", hs)
        for r in roads:
            ax.plot(r[:, 0] / 1000, r[:, 1] / 1000, c="#555555", lw=0.6)
        for p in path_xy("base"):
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c="#ff2a2a", lw=1.2, alpha=0.6)
        for p in path_xy(tag):
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c=c, lw=3)
        ax.plot([sx / 1000, dx / 1000], [sy / 1000, dy / 1000], ":", c="w", lw=1.4)
        ends(ax)
    save(fig, "lcpb-scenarios.png")

    # the two decisions that did not move the route, drawn over the recipe's
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 7.2))
    for ax, (tag, title, c) in zip(axs, [("soft_roads", "Off-road allowed at ×10", "#ffb000"),
                                          ("no_cities", "No city factor", "#00c8ff")]):
        base_ax(ax, ext, f"{title}\n{NUM[tag]['length_km']:.2f} km; recipe {NUM['base']['length_km']:.2f} km", hs)
        for p in path_xy("base"):
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c="#ff2a2a", lw=6, alpha=0.55)
        for p in path_xy(tag):
            ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "--", c=c, lw=1.8)
        ends(ax)
    save(fig, "lcpb-nochange.png")

    # corridor: accumulation from both ends
    pts = os.path.join(SRC, "Endpoints")
    dst = arcpy.management.MakeFeatureLayer(pts, "d_corr", "Role = 'Destination'")
    acc2 = DistanceAccumulation(dst, in_cost_raster="cost_base")
    acc2.save("acc_from_dest")
    tot = Raster("acc_base") + Raster("acc_from_dest")
    tot.save("corridor_sum")
    T = arr(tot)
    m = np.nanmin(T)
    NUM["corridor"] = {"min_sum": float(m)}
    fig, ax = plt.subplots(figsize=(8.4, 9.6))
    base_ax(ax, ext, None, hs)
    for pct, col in ((10, "#fdd49e"), (5, "#fc8d59"), (1, "#b30000")):
        band = np.where(T <= m * (1 + pct / 100), 1.0, np.nan)
        NUM["corridor"][f"within_{pct}pct_km2"] = float(np.nansum(band) * 0.01)
        ax.imshow(np.ma.masked_invalid(band), cmap=ListedColormap([col]), alpha=0.9,
                  extent=[e / 1000 for e in (ext[0], ext[2], ext[1], ext[3])], interpolation="nearest")
    for p in path_xy("base"):
        ax.plot(p[:, 0] / 1000, p[:, 1] / 1000, "-", c="k", lw=1.4)
    ends(ax)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color="#b30000", label="within 1% of the cheapest"),
                       Patch(color="#fc8d59", label="within 5%"), Patch(color="#fdd49e", label="within 10%")],
              loc="lower left", fontsize=11, framealpha=0.9)
    save(fig, "lcpb-corridor.png")
    json.dump(NUM, open(os.path.join(REPO, "tools", "week12_lcp_numbers.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in NUM.items() if k != "toy"}, indent=1))


if __name__ == "__main__":
    main()
