r"""Figures and numbers for the Week 14 decks (slides/week-14/network-analysis-a.md and -b.md).

Everything is drawn from Lab 12's data and reference run: the hosted package extracted by
tools/lab12/run_model.py to C:\Ames\Lab12\ref (run it first), its Ref.gdb outputs, and a few extra
solves made here into C:\Ames\Week14\Week14.gdb (a route by minutes and by meters, a closest-facility
solve, a one-station service area, and a location-allocation run that adds one station from the
county's schools as candidate sites). Computed in ArcGIS Pro 3.7.1 with Network Analyst, through the
same geoprocessing tools the lab uses.

Writes slides/week-14/images/na-*.png and nab-*.png and tools/week14_network_numbers.json.
ArcGIS Pro Python.
"""
import json
import os
import time
import urllib.parse
import urllib.request

import arcpy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyArrowPatch

arcpy.CheckOutExtension("Network")
arcpy.env.overwriteOutput = True
REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(REPO, "slides", "week-14", "images")
W = r"C:\Ames\Week14"
PKG = r"C:\Ames\Lab12\ref\lab12-fire-response"
SRC = os.path.join(PKG, "FireResponse.gdb")
ND = os.path.join(SRC, "Network", "Utah_County_Roads_ND")
ROADS = os.path.join(SRC, "Network", "Roads")
JUNCTIONS = os.path.join(SRC, "Network", "Utah_County_Roads_ND_Junctions")
STATIONS = os.path.join(SRC, "Fire_Stations")
BLOCKS = os.path.join(SRC, "Census_Blocks")
REF = r"C:\Ames\Lab12\ref\Ref.gdb"
G = os.path.join(W, "Week14.gdb")
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
CK = json.load(open(os.path.join(REPO, "tools", "lab12", "check_values.json")))
# the sensitivity runs live in the private companion repo (see tools/lab12/run_model.py)
_SENS = os.path.normpath(os.path.join(REPO, "..", "ce414-private", "sensitivity", "lab12_sensitivity.json"))
CK["sensitivity"] = json.load(open(_SENS if os.path.exists(_SENS) else os.path.join(REPO, "tools", "lab12", "sensitivity.json")))
NUM = {}
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
MAJOR = "CARTOCODE IN ('1', '2', '3', '4', '5', '7')"


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", name)


def parts(fc, where=None, fields=()):
    out = []
    for row in arcpy.da.SearchCursor(fc, ["SHAPE@", *fields], where):
        for part in row[0]:
            out.append((np.array([[p.X, p.Y] for p in part if p]) / 1000, row[1:]))
    return out


def polys(fc, where=None):
    out = []
    for (g,) in arcpy.da.SearchCursor(fc, ["SHAPE@"], where):
        for part in g:
            out.append(np.array([[p.X, p.Y] for p in part if p]) / 1000)
    return out


def county():
    p = os.path.join(G, "Utah_County")
    if not arcpy.Exists(p):
        q = urllib.parse.urlencode({"where": "NAME = 'UTAH'", "outFields": "NAME", "returnGeometry": "true", "outSR": 26912, "f": "json"})
        with urllib.request.urlopen(f"{UGRC}/UtahCountyBoundaries/FeatureServer/0/query", q.encode(), timeout=120) as r:
            jp = os.path.join(W, "county.json"); open(jp, "w").write(r.read().decode())
        arcpy.conversion.JSONToFeatures(jp, p)
    return polys(p)


def schools():
    p = os.path.join(G, "Schools")
    if not arcpy.Exists(p):
        url = f"{UGRC}/Schools_PreKto12/FeatureServer/0/query"
        q = urllib.parse.urlencode({"where": "1=1", "outFields": "SchoolName,City,SchoolType", "returnGeometry": "true", "outSR": 26912, "f": "json",
                                    "geometry": json.dumps({"rings": [[[float(x), float(y)] for x, y in ring * 1000] for ring in county()], "spatialReference": {"wkid": 26912}}),
                                    "geometryType": "esriGeometryPolygon", "inSR": 26912, "spatialRel": "esriSpatialRelIntersects"})
        with urllib.request.urlopen(url, q.encode(), timeout=300) as r:
            jp = os.path.join(W, "schools.json"); open(jp, "w").write(r.read().decode())
        arcpy.conversion.JSONToFeatures(jp, p)
    return p


def station(name_like):
    for oid, nm, xy in arcpy.da.SearchCursor(STATIONS, ["OID@", "NAME", "SHAPE@XY"], f"NAME LIKE '{name_like}'"):
        return oid, nm, xy


def base(ax, rings, lim=None, roads=True):
    for ring in rings:
        ax.plot(ring[:, 0], ring[:, 1], c="#333333", lw=1.0, zorder=5)
    if roads:
        ax.add_collection(LineCollection([p for p, _ in parts(ROADS, "NOT " + MAJOR)], colors="#c8c8c8", linewidths=0.2, zorder=1))
        ax.add_collection(LineCollection([p for p, _ in parts(ROADS, MAJOR)], colors="#777777", linewidths=0.7, zorder=2))
    if lim:
        ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])


def stations(ax, size=40):
    xy = np.array([p[0] for p in arcpy.da.SearchCursor(STATIONS, ["SHAPE@XY"])]) / 1000
    ax.scatter(xy[:, 0], xy[:, 1], s=size, c="#c00000", edgecolors="white", linewidths=0.8, zorder=9)


# ---------------------------------------------------------------- Part A figures
def fig_edges_junctions():
    """A few blocks of streets with one-way segments: edges, junctions, one-way arrows and the minutes on each edge."""
    oid, nm, (sx, sy) = station("PROVO FIRE AND RESCUE STATION 21")
    # center the box on the cluster of one-way local streets nearest the station
    ow = [(xy, L) for xy, L in arcpy.da.SearchCursor(ROADS, ["SHAPE@XY", "SHAPE@LENGTH"], "ONEWAY IN ('1', '2') AND CARTOCODE IN ('8', '10', '11') AND Shape_Length > 150")]
    cx, cy = min(ow, key=lambda r: (r[0][0] - sx) ** 2 + (r[0][1] - sy) ** 2)[0]
    half = 420
    lim = [(cx - half) / 1000, (cx + half) / 1000, (cy - half) / 1000, (cy + half) / 1000]
    box = arcpy.Polygon(arcpy.Array([arcpy.Point(cx - half, cy - half), arcpy.Point(cx - half, cy + half),
                                     arcpy.Point(cx + half, cy + half), arcpy.Point(cx + half, cy - half)]), arcpy.SpatialReference(26912))
    lyr = arcpy.management.MakeFeatureLayer(ROADS, "r_box")
    arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", box)
    fig, ax = plt.subplots(figsize=(8, 8))
    n_edges = n_one = 0
    inside = lambda q: lim[0] <= q[0] <= lim[1] and lim[2] <= q[1] <= lim[3]
    for p_, (ow_, ft, tf, nm2) in parts(lyr, None, ["ONEWAY", "F_T_IMP_MIN", "T_F_IMP_MIN", "FULLNAME"]):
        n_edges += 1
        one = ow_ in ("1", "2")
        col = "#d35400" if one else "#1f4e79"
        ax.plot(p_[:, 0], p_[:, 1], c=col, lw=2.4 if one else 1.6, zorder=3)
        if one:
            n_one += 1
            a, b = (p_[0], p_[-1]) if ow_ == "1" else (p_[-1], p_[0])
            mid = (a + b) / 2; d = (b - a); d = d / (np.linalg.norm(d) + 1e-9) * 0.045
            ax.add_patch(FancyArrowPatch(mid - d, mid + d, arrowstyle="-|>", mutation_scale=18, color="#d35400", lw=1.8, zorder=6))
        # label at 40 % along the edge, only when that point is inside the box
        k = int(len(p_) * 0.4); q = p_[k] if len(p_) > 2 else (p_[0] * 0.6 + p_[-1] * 0.4)
        if inside(q):
            ax.text(q[0], q[1], f"{min(ft, tf):.2f}", fontsize=7, color="#1f4e79", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9), zorder=7)
    jl = arcpy.management.MakeFeatureLayer(JUNCTIONS, "j_box")
    arcpy.management.SelectLayerByLocation(jl, "INTERSECT", box)
    jxy = np.array([q[0] for q in arcpy.da.SearchCursor(jl, ["SHAPE@XY"])]) / 1000
    ax.scatter(jxy[:, 0], jxy[:, 1], s=30, c="white", edgecolors="#1f4e79", linewidths=1.5, zorder=8)
    if inside((sx / 1000, sy / 1000)):
        ax.plot(sx / 1000, sy / 1000, "o", ms=13, mfc="#c00000", mec="white", mew=1.5, zorder=10)
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.plot([], [], c="#1f4e79", lw=1.6, label="Edge (two-way), labeled with its minutes")
    ax.plot([], [], c="#d35400", lw=2.4, label="One-way edge; the arrow is the cheap direction")
    ax.plot([], [], "o", ms=6, mfc="white", mec="#1f4e79", label="Junction")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.set_title(f"{2 * half} m of Provo as a network: {n_edges} edges, {len(jxy)} junctions, {n_one} one-way", fontsize=12)
    NUM["edges_junctions"] = {"near_station": nm, "center": [round(cx), round(cy)], "edges": n_edges, "junctions": int(len(jxy)), "one_way": n_one, "half_m": half}
    save(fig, "na-edges-junctions.png")

def fig_impedance():
    """Minutes per kilometer by road class: what UGRC's TravelMinutes actually is."""
    rows = [(cc, sp, ft, tf, L) for cc, sp, ft, tf, L in arcpy.da.SearchCursor(ROADS, ["CARTOCODE", "SPEED_LMT", "F_T_IMP_MIN", "T_F_IMP_MIN", "SHAPE@LENGTH"])]
    classes = [("1", "Interstate"), ("3", "US highway"), ("5", "State highway"), ("7", "Ramps, collectors"),
               ("8", "Major local, paved"), ("10", "Other local (federal aid)"), ("11", "Local / neighborhood")]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    labels, meds, lo, hi, counts, speeds = [], [], [], [], [], []
    for code, label in classes:
        v = np.array([min(ft, tf) / (L / 1000) for cc, sp, ft, tf, L in rows if cc == code and L > 50])
        sp = [s for cc, s, ft, tf, L in rows if cc == code and s]
        if not len(v):
            continue
        labels.append(label); meds.append(np.median(v)); lo.append(np.percentile(v, 10)); hi.append(np.percentile(v, 90)); counts.append(len(v))
        speeds.append(int(np.median(sp)) if sp else None)
    y = np.arange(len(labels))
    ax.barh(y, meds, color="#1f4e79", height=0.6)
    ax.errorbar(meds, y, xerr=[np.array(meds) - np.array(lo), np.array(hi) - np.array(meds)], fmt="none", ecolor="#d35400", elinewidth=2, capsize=4)
    for yi, m, n, s in zip(y, meds, counts, speeds):
        kmh = 60 / m
        ax.text(max(hi) * 1.02, yi, f"{m:.2f} min/km = {kmh / 1.609:.0f} mph, posted {s}", va="center", fontsize=12.5)
    ax.set_yticks(y); ax.set_yticklabels(labels); ax.invert_yaxis()
    ax.set_xlim(0, max(hi) * 1.75)
    ax.set_xlabel("TravelMinutes per kilometer (median; bar = 10th to 90th percentile)")
    ax.set_title("What a minute of UGRC's network is: travel time by road class, Utah County", fontsize=12)
    NUM["impedance"] = [{"class": l, "med_min_per_km": round(m, 3), "kmh": round(60 / m, 1), "posted_mph": s, "n": n} for l, m, s, n in zip(labels, meds, speeds, counts)]
    save(fig, "na-impedance.png")


def solve_route(stops_fc, tag, impedance=None):
    """A route between the stops; impedance None = the network default (TravelMinutes), or "Length"."""
    lyr = arcpy.na.MakeRouteAnalysisLayer(ND, f"Route_{tag}").getOutput(0)
    if impedance:
        tm = arcpy.na.GetSolverProperties(lyr).travelMode
        tm.impedance = impedance
        arcpy.management.Delete(lyr)
        lyr = arcpy.na.MakeRouteAnalysisLayer(ND, f"Route_{tag}", travel_mode=tm).getOutput(0)
    arcpy.na.AddLocations(lyr, "Stops", stops_fc)
    arcpy.na.Solve(lyr)
    names = arcpy.na.GetNAClassNames(lyr)
    out = os.path.join(G, f"Route_{tag}")
    arcpy.management.CopyFeatures(lyr.listLayers(names["Routes"])[0], out)
    fields = [f.name for f in arcpy.ListFields(out)]
    tmin = next((f for f in fields if f.startswith("Total_TravelMinutes")), None)
    tlen = next((f for f in fields if f.startswith("Total_Length")), None)
    row = next(arcpy.da.SearchCursor(out, [tmin or "SHAPE@LENGTH", tlen or "SHAPE@LENGTH", "SHAPE@LENGTH"]))
    return out, {"minutes": round(row[0], 2) if tmin else None, "meters": round(row[1]), "shape_m": round(row[2])}

def fig_shortest_vs_fastest(rings):
    """One trip two ways: the fewest meters and the fewest minutes are different roads."""
    oid, nm, (sx, sy) = station("PROVO FIRE AND RESCUE STATION 21")
    # candidates: populated block centers 5-9 km away; keep the one where the two routes differ most
    cands = []
    for pop, (bx, by) in arcpy.da.SearchCursor(BLOCKS, ["PP_TOTAL", "SHAPE@XY"], "PP_TOTAL > 100"):
        d = ((bx - sx) ** 2 + (by - sy) ** 2) ** 0.5
        if 5000 < d < 9000:
            cands.append((pop, (bx, by), d))
    cands.sort(key=lambda c: -c[0])
    best = None
    for i, (pop, xy, d) in enumerate(cands[::max(1, len(cands) // 12)][:12]):
        stops = os.path.join(G, f"Stops_{i}")
        arcpy.management.CreateFeatureclass(G, f"Stops_{i}", "POINT", spatial_reference=arcpy.SpatialReference(26912))
        with arcpy.da.InsertCursor(stops, ["SHAPE@XY"]) as cur:
            cur.insertRow([(sx, sy)]); cur.insertRow([xy])
        try:
            r_min, n_min = solve_route(stops, f"min_{i}")
            r_len, n_len = solve_route(stops, f"len_{i}", "Length")
        except Exception as e:
            print("route candidate failed:", e); continue
        # minutes of the shortest route are not reported when Length is the impedance; measure them by
        # how many meters longer the fastest route is, and how many minutes faster
        diff = n_min["meters"] - n_len["meters"]
        print("candidate", i, pop, round(d), n_min, n_len, "extra m on the fast route", diff)
        if best is None or diff > best["diff"]:
            best = {"i": i, "pop": pop, "xy": xy, "d": d, "r_min": r_min, "n_min": n_min, "r_len": r_len, "n_len": n_len, "diff": diff}
    if best is None:
        print("no route pair"); return
    # minutes along the shortest route: solve it as fixed stops? Simpler: report its meters and the fast route's minutes
    NUM["route"] = {"from": nm, "to_block_people": best["pop"], "straight_m": round(best["d"]), "by_minutes": best["n_min"],
                    "by_meters": best["n_len"], "fast_route_extra_m": best["diff"]}
    fig, ax = plt.subplots(figsize=(9, 7.5))
    pad = 0.8
    xs = [sx / 1000, best["xy"][0] / 1000]; ys = [sy / 1000, best["xy"][1] / 1000]
    allp = np.vstack([p_ for p_, _ in parts(best["r_min"])] + [p_ for p_, _ in parts(best["r_len"])])
    base(ax, rings, [allp[:, 0].min() - pad, allp[:, 0].max() + pad, allp[:, 1].min() - pad, allp[:, 1].max() + pad])
    ax.plot(xs, ys, "--", c="#555555", lw=1.5, label=f"Straight line: {best['d'] / 1000:.1f} km")
    for p_, _ in parts(best["r_len"]):
        ax.plot(p_[:, 0], p_[:, 1], c="#2e8b57", lw=5, alpha=0.9, label=f"Fewest meters: {best['n_len']['meters'] / 1000:.1f} km")
    for p_, _ in parts(best["r_min"]):
        ax.plot(p_[:, 0], p_[:, 1], c="#d35400", lw=3, label=f"Fewest minutes: {best['n_min']['meters'] / 1000:.1f} km, {best['n_min']['minutes']:.1f} min")
    ax.plot(xs[0], ys[0], "o", ms=12, mfc="#c00000", mec="white", mew=1.5, zorder=10)
    ax.plot(xs[1], ys[1], "s", ms=11, mfc="#1f4e79", mec="white", mew=1.5, zorder=10)
    h, l = ax.get_legend_handles_labels(); seen = {}
    for hh, ll in zip(h, l):
        seen.setdefault(ll, hh)
    ax.legend(seen.values(), seen.keys(), loc="lower left", fontsize=10, framealpha=0.95)
    ax.set_title(f"Shortest is not fastest: {nm.title()} to a Census block {best['d'] / 1000:.1f} km away", fontsize=12)
    save(fig, "na-shortest-vs-fastest.png")

def fig_three_distances(rings):
    """The same four minutes three ways from one station: a circle, a cost-distance surface, the roads."""
    oid, nm, (sx, sy) = station("PROVO FIRE AND RESCUE STATION 21")
    one = os.path.join(G, "Station_one")
    arcpy.management.CreateFeatureclass(G, "Station_one", "POINT", spatial_reference=arcpy.SpatialReference(26912))
    with arcpy.da.InsertCursor(one, ["SHAPE@XY"]) as cur:
        cur.insertRow([(sx, sy)])
    lyr = arcpy.na.MakeServiceAreaAnalysisLayer(ND, "SA_one", travel_direction="FROM_FACILITIES", cutoffs=[2, 4, 6, 8],
                                                polygon_detail="STANDARD", geometry_at_overlaps="DISSOLVE", geometry_at_cutoffs="RINGS").getOutput(0)
    arcpy.na.AddLocations(lyr, "Facilities", one); arcpy.na.Solve(lyr)
    names = arcpy.na.GetNAClassNames(lyr)
    sa1 = os.path.join(G, "SA_one"); arcpy.management.CopyFeatures(lyr.listLayers(names["SAPolygons"])[0], sa1)
    areas = {int(r[1]): round(r[2] / 1e6, 2) for r in arcpy.da.SearchCursor(sa1, ["FromBreak", "ToBreak", "SHAPE@AREA"])}
    NUM["one_station"] = {"station": nm, "ring_km2": areas, "buffer_3_75_km2": round(3.1415926 * 3.75 ** 2, 2)}
    pad = 4.5
    lim = [(sx) / 1000 - pad, sx / 1000 + pad, sy / 1000 - pad, sy / 1000 + pad]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.6))
    for ax, title in zip(axes, ["Straight line: 3.75 km (4 minutes at 35 mph)", "Network: 4 minutes along the roads"]):
        base(ax, rings, lim); ax.set_title(title, fontsize=12)
    th = np.linspace(0, 2 * np.pi, 200)
    axes[0].fill(sx / 1000 + 3.75 * np.cos(th), sy / 1000 + 3.75 * np.sin(th), color="#1f4e79", alpha=0.35, zorder=4)
    axes[0].text(lim[0] + 0.2, lim[2] + 0.2, f"{NUM['one_station']['buffer_3_75_km2']:.1f} km²", fontsize=13, fontweight="bold", color="#1f4e79")
    axes[1].add_collection(PolyCollection(polys(sa1, "ToBreak <= 4"), facecolors="#1f4e79", alpha=0.55, edgecolors="none", zorder=4))
    axes[1].text(lim[0] + 0.2, lim[2] + 0.2, f"{areas[4]:.1f} km²", fontsize=13, fontweight="bold", color="#1f4e79")
    for ax in axes:
        ax.plot(sx / 1000, sy / 1000, "o", ms=12, mfc="#c00000", mec="white", mew=1.5, zorder=10)
    fig.suptitle(f"The same four minutes, two ways, from {nm.title()}", fontsize=13)
    save(fig, "na-four-minutes-two-ways.png")
    # the growing rings from one station, for Part B
    fig, ax = plt.subplots(figsize=(8, 8))
    base(ax, rings, lim)
    cols = {2: "#08306b", 4: "#2171b5", 6: "#6baed6", 8: "#c6dbef"}
    for tb in (8, 6, 4, 2):
        ax.add_collection(PolyCollection(polys(sa1, f"ToBreak = {tb}"), facecolors=cols[tb], alpha=0.75, edgecolors="white", linewidths=0.3, zorder=4))
    for tb in (2, 4, 6, 8):
        ax.fill([], [], color=cols[tb], label=f"{tb - 2} to {tb} minutes: {areas[tb]:.1f} km²")
    ax.plot(sx / 1000, sy / 1000, "o", ms=12, mfc="#c00000", mec="white", mew=1.5, zorder=10)
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    ax.set_title(f"A service area grows along the roads: {nm.title()}", fontsize=12)
    save(fig, "nab-one-station-rings.png")


def fig_overpass(rings):
    """Where a freeway crosses a street with no junction: the network does not connect them."""
    # candidate: a point where an interstate segment crosses a local segment but no junction lies within 15 m
    inter = arcpy.management.MakeFeatureLayer(ROADS, "inter", "CARTOCODE = '1'")
    local = arcpy.management.MakeFeatureLayer(ROADS, "loc", "CARTOCODE IN ('8', '10', '11') AND VERT_LEVEL = '0'")
    x = os.path.join(G, "Cross_pts")
    arcpy.analysis.PairwiseIntersect([inter, local], x, output_type="POINT")
    jn = os.path.join(G, "Cross_near")
    arcpy.analysis.Near(x, JUNCTIONS)
    oid, nm, (sx, sy) = station("PROVO FIRE AND RESCUE STATION 21")
    best = None
    for (px, py), nd in arcpy.da.SearchCursor(x, ["SHAPE@XY", "NEAR_DIST"]):
        d = ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5
        if nd > 15 and (best is None or d < best[0]):
            best = (d, (px, py), nd)
    if best is None:
        print("no overpass found"); return
    (px, py), nd = best[1], best[2]
    half = 350
    lim = [(px - half) / 1000, (px + half) / 1000, (py - half) / 1000, (py + half) / 1000]
    box = arcpy.Polygon(arcpy.Array([arcpy.Point(px - half, py - half), arcpy.Point(px - half, py + half),
                                     arcpy.Point(px + half, py + half), arcpy.Point(px + half, py - half)]), arcpy.SpatialReference(26912))
    lyr = arcpy.management.MakeFeatureLayer(ROADS, "r_ov"); arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", box)
    jl = arcpy.management.MakeFeatureLayer(JUNCTIONS, "j_ov"); arcpy.management.SelectLayerByLocation(jl, "INTERSECT", box)
    fig, ax = plt.subplots(figsize=(8, 8))
    names = set()
    for p, (cc, vl, nm2) in parts(lyr, None, ["CARTOCODE", "VERT_LEVEL", "FULLNAME"]):
        ax.plot(p[:, 0], p[:, 1], c="#d35400" if cc in ("1", "7") else "#1f4e79", lw=3.5 if cc == "1" else 1.8, zorder=3)
        if nm2: names.add(nm2)
    jxy = np.array([p[0] for p in arcpy.da.SearchCursor(jl, ["SHAPE@XY"])]) / 1000
    ax.scatter(jxy[:, 0], jxy[:, 1], s=40, c="white", edgecolors="#1f4e79", linewidths=1.6, zorder=8)
    ax.plot(px / 1000, py / 1000, "x", ms=18, mew=3, color="#c00000", zorder=9)
    ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.plot([], [], c="#d35400", lw=3.5, label="Interstate and ramps")
    ax.plot([], [], c="#1f4e79", lw=1.8, label="Surface streets")
    ax.plot([], [], "o", ms=7, mfc="white", mec="#1f4e79", label="Junction (where edges connect)")
    ax.plot([], [], "x", ms=10, mew=3, color="#c00000", label=f"Lines cross, no junction: nearest is {nd:.0f} m away")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.set_title("An overpass: the lines cross on the map, the network does not connect them", fontsize=11)
    NUM["overpass"] = {"x": round(px), "y": round(py), "nearest_junction_m": round(nd, 1), "streets": sorted(names)[:6]}
    save(fig, "na-overpass.png")


def fig_turns():
    """UGRC's global turn delays, read from the network template: a table drawn as a figure."""
    rows = [("Straight on", "local to local", "0 s"), ("Straight across a major road", "local to local", "15 s"),
            ("Right turn", "local to local", "0 s"), ("Right turn", "secondary to secondary", "3 s"),
            ("Left turn", "local to local", "30 s"), ("Left turn", "secondary to secondary", "8 s"),
            ("U-turn", "local to local", "30 s")]
    fig, ax = plt.subplots(figsize=(9.5, 4.4)); ax.axis("off")
    t = ax.table(cellText=[list(r) for r in rows], colLabels=["Turn", "From and to", "Delay added"], loc="center",
                 cellLoc="left", colLoc="left", colWidths=[0.42, 0.36, 0.22])
    t.auto_set_font_size(False); t.set_fontsize(12); t.scale(1, 1.6)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#c9d2dc")
        if r == 0:
            cell.set_facecolor("#1f4e79"); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif r % 2 == 0:
            cell.set_facecolor("#eef2f6")
    ax.set_title("Global turn delays in UGRC's network (no turn features needed)", fontsize=12)
    save(fig, "na-turn-delays.png")

# ---------------------------------------------------------------- Part B figures
def fig_service_areas(rings):
    fig, ax = plt.subplots(figsize=(9, 9))
    allxy = np.vstack(rings)
    base(ax, rings, [allxy[:, 0].min() - 1, allxy[:, 0].max() + 1, allxy[:, 1].min() - 1, allxy[:, 1].max() + 1], roads=False)
    ax.add_collection(LineCollection([p for p, _ in parts(ROADS, MAJOR)], colors="#999999", linewidths=0.6, zorder=2))
    cols = {2: "#08306b", 4: "#2171b5", 6: "#6baed6", 8: "#c6dbef"}
    for c in (8, 6, 4, 2):
        ax.add_collection(PolyCollection(polys(os.path.join(REF, f"Served_c{c}")), facecolors=cols[c], alpha=0.85, edgecolors="none", zorder=4 + (8 - c) // 2))
    sens = {r["cutoffs"][0]: r for r in CK["sensitivity"]["cutoffs"]}
    for c in (2, 4, 6, 8):
        ax.fill([], [], color=cols[c], label=f"Within {c} minutes: {sens[c]['area_km2']:,.0f} km²")
    stations(ax, 34)
    ax.plot([], [], "o", ms=7, mfc="#c00000", mec="white", label="Fire stations (42)")
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    ax.set_title("Service areas from all 42 stations, dissolved, 2 to 8 minutes", fontsize=12)
    save(fig, "nab-service-areas.png")
    fig, ax = plt.subplots(figsize=(9, 9))
    base(ax, rings, [allxy[:, 0].min() - 1, allxy[:, 0].max() + 1, allxy[:, 1].min() - 1, allxy[:, 1].max() + 1], roads=False)
    ax.add_collection(LineCollection([p for p, _ in parts(ROADS, MAJOR)], colors="#999999", linewidths=0.6, zorder=2))
    ax.add_collection(PolyCollection(polys(os.path.join(REF, "Unserved_base"), "PP_TOTAL > 0"), facecolors="#f39c12", alpha=0.7, edgecolors="none", zorder=3))
    ax.add_collection(PolyCollection(polys(os.path.join(REF, "Served_base")), facecolors="#2171b5", alpha=0.75, edgecolors="none", zorder=4))
    stations(ax, 34)
    b = CK["baseline"]
    ax.fill([], [], color="#2171b5", label=f"Within 4 minutes along the roads: {b['area_km2']:.0f} km²")
    ax.fill([], [], color="#f39c12", label=f"Populated blocks outside: {b['population']:,} people ({b['pct_outside']} %)")
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    ax.set_title("Lab 12's baseline: who is more than four minutes from a station", fontsize=12)
    save(fig, "nab-baseline.png")


def fig_closest_facility(rings):
    """Eight incidents well away from the stations, each routed to its closest station by minutes."""
    arcpy.env.workspace = G
    pts = os.path.join(G, "Incidents")
    sxy = np.array([q[0] for q in arcpy.da.SearchCursor(STATIONS, ["SHAPE@XY"])])
    rows = []
    for pop, (bx, by) in arcpy.da.SearchCursor(BLOCKS, ["PP_TOTAL", "SHAPE@XY"], "PP_TOTAL > 50"):
        dmin = np.min(np.hypot(sxy[:, 0] - bx, sxy[:, 1] - by))
        if 2500 < dmin < 7000:
            rows.append((dmin, (bx, by)))
    rows.sort(key=lambda r: -r[0])
    pick = []
    for dmin, xy in rows:                      # greedy spread: at least 6 km apart
        if all(np.hypot(xy[0] - q[0], xy[1] - q[1]) > 6000 for q in pick):
            pick.append(xy)
        if len(pick) == 8:
            break
    arcpy.management.CreateFeatureclass(G, "Incidents", "POINT", spatial_reference=arcpy.SpatialReference(26912))
    with arcpy.da.InsertCursor(pts, ["SHAPE@XY"]) as cur:
        for xy in pick:
            cur.insertRow([xy])
    lyr = arcpy.na.MakeClosestFacilityAnalysisLayer(ND, "CF", travel_direction="TO_FACILITIES", number_of_facilities_to_find=1).getOutput(0)
    arcpy.na.AddLocations(lyr, "Facilities", STATIONS)
    arcpy.na.AddLocations(lyr, "Incidents", pts)
    arcpy.na.Solve(lyr)
    names = arcpy.na.GetNAClassNames(lyr)
    routes = os.path.join(G, "CF_Routes"); arcpy.management.CopyFeatures(lyr.listLayers(names["CFRoutes"])[0], routes)
    tmin = next(f.name for f in arcpy.ListFields(routes) if f.name.startswith("Total_TravelMinutes"))
    mins = [round(r[0], 1) for r in arcpy.da.SearchCursor(routes, [tmin])]
    NUM["closest_facility"] = {"incidents": len(pick), "minutes": mins}
    allp = np.vstack([p_ for p_, _ in parts(routes)])
    pad = 2.5
    fig, ax = plt.subplots(figsize=(9, 9))
    base(ax, rings, [allp[:, 0].min() - pad, allp[:, 0].max() + pad, allp[:, 1].min() - pad, allp[:, 1].max() + pad])
    for p_, (m,) in parts(routes, None, [tmin]):
        ax.plot(p_[:, 0], p_[:, 1], c="#d35400", lw=2.8, zorder=6)
        q = p_[len(p_) // 2]
        ax.annotate(f"{m:.1f} min", (q[0], q[1]), xytext=(8, 8), textcoords="offset points", fontsize=10, color="#d35400", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9), zorder=7)
    ixy = np.array(pick) / 1000
    ax.scatter(ixy[:, 0], ixy[:, 1], s=70, marker="s", c="#1f4e79", edgecolors="white", linewidths=1, zorder=9)
    stations(ax, 40)
    ax.plot([], [], "s", ms=8, mfc="#1f4e79", mec="white", label="Incident (a block center)")
    ax.plot([], [], "o", ms=7, mfc="#c00000", mec="white", label="Fire station")
    ax.plot([], [], c="#d35400", lw=2.8, label="Route from the closest station, by minutes")
    ax.legend(loc="center right", fontsize=10, framealpha=0.95)
    ax.set_title("Closest Facility: which station reaches each incident first, and in how long", fontsize=12)
    save(fig, "nab-closest-facility.png")

def fig_location_allocation(rings):
    """Maximize Coverage: keep the 42 stations, add one from the county's schools, cutoff 4 minutes."""
    sch = schools()
    cand = os.path.join(G, "Candidates")
    arcpy.management.CopyFeatures(sch, cand)
    arcpy.management.AddField(cand, "FacilityType", "SHORT"); arcpy.management.CalculateField(cand, "FacilityType", "0")
    req = os.path.join(G, "Required")
    arcpy.management.CopyFeatures(STATIONS, req)
    arcpy.management.AddField(req, "FacilityType", "SHORT"); arcpy.management.CalculateField(req, "FacilityType", "1")
    dem = os.path.join(G, "Demand")
    arcpy.management.FeatureToPoint(arcpy.management.MakeFeatureLayer(BLOCKS, "bp", "PP_TOTAL > 0"), dem, "INSIDE")
    t0 = time.time()
    lyr = arcpy.na.MakeLocationAllocationAnalysisLayer(ND, "LA", travel_direction="FROM_FACILITIES", problem_type="MAXIMIZE_COVERAGE",
                                                       cutoff=4, number_of_facilities_to_find=43).getOutput(0)
    arcpy.na.AddLocations(lyr, "Facilities", req, "Name NAME #;FacilityType FacilityType #")
    arcpy.na.AddLocations(lyr, "Facilities", cand, "Name SchoolName #;FacilityType FacilityType #", append="APPEND")
    arcpy.na.AddLocations(lyr, "Demand Points", dem, "Weight PP_TOTAL #")
    arcpy.na.Solve(lyr)
    names = arcpy.na.GetNAClassNames(lyr)
    fac = os.path.join(G, "LA_Facilities"); arcpy.management.CopyFeatures(lyr.listLayers(names["Facilities"])[0], fac)
    chosen = [(n, ft, dw, xy) for n, ft, dw, xy in arcpy.da.SearchCursor(fac, ["Name", "FacilityType", "DemandWeight", "SHAPE@XY"]) if ft == 3]
    reqw = sum(dw or 0 for n, ft, dw, xy in arcpy.da.SearchCursor(fac, ["Name", "FacilityType", "DemandWeight", "SHAPE@XY"]) if ft == 1)
    NUM["location_allocation"] = {"candidates": int(arcpy.management.GetCount(cand)[0]), "seconds": round(time.time() - t0),
                                  "chosen": [{"name": n, "people_covered": int(dw or 0), "x": round(xy[0]), "y": round(xy[1])} for n, ft, dw, xy in chosen],
                                  "required_covered": int(reqw)}
    fig, ax = plt.subplots(figsize=(9, 9))
    allxy = np.vstack(rings)
    base(ax, rings, [allxy[:, 0].min() - 1, allxy[:, 0].max() + 1, allxy[:, 1].min() - 1, allxy[:, 1].max() + 1])
    ax.add_collection(PolyCollection(polys(os.path.join(REF, "Served_base")), facecolors="#2171b5", alpha=0.45, edgecolors="none", zorder=3))
    cxy = np.array([p[0] for p in arcpy.da.SearchCursor(cand, ["SHAPE@XY"])]) / 1000
    ax.scatter(cxy[:, 0], cxy[:, 1], s=14, c="#7f8c8d", zorder=5)
    stations(ax, 34)
    for n, ft, dw, (x, y) in chosen:
        ax.plot(x / 1000, y / 1000, "*", ms=22, mfc="#f1c40f", mec="#1a202c", mew=1.2, zorder=11)
        ax.annotate(f"{n}\n+{int(dw or 0):,} people within 4 min", (x / 1000, y / 1000), xytext=(20, 25), textcoords="offset points",
                    fontsize=10, fontweight="bold", bbox=dict(boxstyle="round", fc="white", ec="#1a202c"), arrowprops=dict(arrowstyle="-"))
    ax.plot([], [], "o", ms=4, c="#7f8c8d", label=f"Candidate sites: {NUM['location_allocation']['candidates']} schools")
    ax.plot([], [], "o", ms=7, mfc="#c00000", mec="white", label="Existing stations (required)")
    ax.fill([], [], color="#2171b5", alpha=0.45, label="Within 4 minutes today")
    ax.plot([], [], "*", ms=14, mfc="#f1c40f", mec="#1a202c", label="The one site that covers the most new people")
    ax.legend(loc="lower left", fontsize=10, framealpha=0.95)
    ax.set_title("Location-Allocation, Maximize Coverage: where would one more station help most?", fontsize=12)
    save(fig, "nab-location-allocation.png")


def main(only=None):
    os.makedirs(W, exist_ok=True)
    if not arcpy.Exists(G):
        arcpy.management.CreateFileGDB(W, "Week14.gdb")
    arcpy.env.workspace = G
    rings = county()
    NUM["lab12"] = {"baseline": CK["baseline"], "crow": CK["crow_default"], "population": CK["inputs"]["population"],
                    "one_way": CK["one_way"], "inputs": {k: CK["inputs"][k] for k in ("Roads", "Junctions", "Fire_Stations", "Census_Blocks")}}
    prev = os.path.join(REPO, "tools", "week14_network_numbers.json")
    if only and os.path.exists(prev):
        NUM.update(json.load(open(prev))); NUM.pop("failed", None)
    for f in (fig_edges_junctions, fig_impedance, fig_turns):
        if not only or f.__name__ in only:
            f()
    for f in (fig_three_distances, fig_shortest_vs_fastest, fig_overpass, fig_service_areas, fig_closest_facility, fig_location_allocation):
        if only and f.__name__ not in only:
            continue
        try:
            f(rings)
        except Exception as e:
            print("FAILED", f.__name__, e)
            NUM.setdefault("failed", []).append(f"{f.__name__}: {e}")
    json.dump(NUM, open(os.path.join(REPO, "tools", "week14_network_numbers.json"), "w"), indent=1)
    print(json.dumps(NUM, indent=1)[:3000])


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
