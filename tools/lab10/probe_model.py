"""Lab 10 parity-plan probe: a first reference run of the proposed wind-farm model.

NOT the oracle (run_model.py comes after the instructor's decisions). It measures the numbers
the plan's decisions depend on: how much each exclusion removes, the wind-speed range, how far
the top site moves under the candidate weight sets, and what a personal parameter would do.

Run with the ArcGIS Pro Python:
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/lab10/probe_model.py [cell]
Inputs: C:\\Ames\\Lab10\\src (unzipped downloads) and raw\\USA_wind-speed_100m.tif.
Writes C:\\Ames\\Lab10\\probe.gdb and tools/lab10/probe_checks_<cell>m.json.
"""
import json, os, sys, statistics, collections
import arcpy
from arcpy import sa

CELL = int(sys.argv[1]) if len(sys.argv) > 1 else 100
MI = 1609.344
SRC = r"C:\Ames\Lab10\src"
GWA = r"C:\Ames\Lab10\raw\USA_wind-speed_100m.tif"
GDB = r"C:\Ames\Lab10\probe_%dm.gdb" % CELL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_checks_%dm.json" % CELL)
COUNTIES = ["Minnehaha", "Moody", "Lake", "McCook", "Turner", "Lincoln"]
UTM14 = arcpy.SpatialReference(26914)

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(os.path.dirname(GDB), os.path.basename(GDB))
arcpy.env.workspace = GDB
arcpy.env.outputCoordinateSystem = UTM14
res = {"cell_m": CELL, "arcgis": arcpy.GetInstallInfo()["Version"]}

# ---- study area -------------------------------------------------------------------------
cty = os.path.join(SRC, "tl_2025_us_county", "tl_2025_us_county.shp")
q = "STATEFP = '46' AND NAME IN (%s)" % ",".join("'%s'" % c for c in COUNTIES)
arcpy.analysis.Select(cty, "Counties_sel", q)
arcpy.management.Project("Counties_sel", "Counties", UTM14)
arcpy.management.Dissolve("Counties", "Study_Area")
area = sum(r[0] for r in arcpy.da.SearchCursor("Study_Area", ["SHAPE@AREA"]))
res["study_area_km2"] = round(area / 1e6, 1)
res["study_area_mi2"] = round(area / MI ** 2, 1)
res["county_areas_km2"] = {r[0]: round(r[1] / 1e6, 1) for r in arcpy.da.SearchCursor("Counties", ["NAME", "SHAPE@AREA"])}
# context: 20 mi beyond the counties, so features across the line still count
arcpy.analysis.Buffer("Study_Area", "Context", "%f Meters" % (20 * MI))

# ---- grid: snap to a round origin, extent = study area --------------------------------------
d = arcpy.Describe("Study_Area").extent
import math
x0 = math.floor(d.XMin / CELL) * CELL; y0 = math.floor(d.YMin / CELL) * CELL
x1 = math.ceil(d.XMax / CELL) * CELL; y1 = math.ceil(d.YMax / CELL) * CELL
arcpy.env.extent = arcpy.Extent(x0, y0, x1, y1)
arcpy.env.cellSize = CELL
arcpy.conversion.PolygonToRaster("Study_Area", "OBJECTID", "Study_Grid", "CELL_CENTER", "", CELL)
arcpy.env.snapRaster = "Study_Grid"
arcpy.env.mask = "Study_Grid"
RASTER_EXT = arcpy.Extent(x0, y0, x1, y1)
grid = sa.Raster("Study_Grid")
import numpy as np
n_area = int((arcpy.RasterToNumPyArray(grid, nodata_to_value=-9999) != -9999).sum())
res["grid_cells_in_study_area"] = n_area
res["grid_extent"] = [x0, y0, x1, y1]
cell_km2 = CELL * CELL / 1e6

def prop(r, p):
    path = r.catalogPath if hasattr(r, "catalogPath") else r
    arcpy.management.CalculateStatistics(path)
    return arcpy.management.GetRasterProperties(path, p)[0]

def count(r):
    """cells where r is true (nonzero), NoData counted as false."""
    a = arcpy.RasterToNumPyArray(sa.Con(sa.IsNull(r), 0, sa.Con(r, 1, 0)), nodata_to_value=0)
    return int((a == 1).sum())

# ---- wind ------------------------------------------------------------------------------
desc = arcpy.Describe(GWA)
res["gwa_sr"] = desc.spatialReference.name
res["gwa_cell_deg"] = [desc.meanCellWidth, desc.meanCellHeight]
ce = arcpy.Describe("Context").extent.projectAs(arcpy.SpatialReference(4326))
rect = "%f %f %f %f" % (ce.XMin - 0.05, ce.YMin - 0.05, ce.XMax + 0.05, ce.YMax + 0.05)
with arcpy.EnvManager(outputCoordinateSystem=None, cellSize="MAXOF", extent="MAXOF", snapRaster=None, mask=None):
    arcpy.management.Clip(GWA, rect, "GWA_clip", "", "", "NONE", "NO_MAINTAIN_EXTENT")
gd = arcpy.Describe("GWA_clip")
res["gwa_clip"] = [gd.width, gd.height, gd.spatialReference.name, gd.meanCellWidth]
arcpy.management.ProjectRaster("GWA_clip", "Wind_UTM", UTM14, "BILINEAR", CELL)
wind = sa.ExtractByMask("Wind_UTM", "Study_Grid")
wind.save("Wind100")
st = {}
for p in ["MINIMUM", "MAXIMUM", "MEAN", "STD"]:
    st[p] = round(float(prop(wind, p)), 3)
res["wind100_stats_ms"] = st
for thr in [6.5, 7.0, 7.5, 8.0, 8.5]:
    res.setdefault("wind_cells_below", {})[str(thr)] = count(wind < thr)
res["wind_cells_nodata_in_area"] = n_area - count(sa.IsNull(wind) == 0)

arcpy.env.extent = None; arcpy.env.mask = None  # vector work: an extent env clips feature outputs too
# ---- turbines --------------------------------------------------------------------------
wt = [os.path.join(r, f) for r, _, fs in os.walk(os.path.join(SRC, "uswtdbSHP")) for f in fs if f.endswith(".shp")][0]
arcpy.management.Project(wt, "Turbines_all_utm", UTM14) if not arcpy.Exists("Turbines_all_utm") else None
lyr = arcpy.management.MakeFeatureLayer("Turbines_all_utm", "tl")
arcpy.management.SelectLayerByLocation(lyr, "INTERSECT", "Study_Area")
res["turbines_inside_counties"] = int(arcpy.management.GetCount(lyr)[0])
for miles in [10, 20, 30]:
    arcpy.management.SelectLayerByLocation(lyr, "WITHIN_A_DISTANCE", "Study_Area", "%f Meters" % (miles * MI))
    rows = list(arcpy.da.SearchCursor(lyr, ["t_state", "p_name", "p_year"]))
    res["turbines_within_%dmi" % miles] = len(rows)
    res["projects_within_%dmi" % miles] = sorted({(r[0], r[1], r[2]) for r in rows})
arcpy.management.SelectLayerByLocation(lyr, "WITHIN_A_DISTANCE", "Study_Area", "%f Meters" % (40 * MI))
arcpy.management.CopyFeatures(lyr, "Turbines")
hh = [r[0] for r in arcpy.da.SearchCursor(wt, ["t_hh", "p_year"], "t_state = 'SD'") if r[0] and r[0] > 0 and r[1] and r[1] >= 2015]
res["sd_hub_height_2015plus"] = {"n": len(hh), "median": statistics.median(hh), "min": min(hh), "max": max(hh)}

# ---- rivers ----------------------------------------------------------------------------
parts = []
for hu in ["1016", "1017"]:
    fl = os.path.join(SRC, "NHD_H_%s_HU4_GDB" % hu, "NHD_H_%s_HU4_GDB.gdb" % hu, "Hydrography", "NHDFlowline")
    l = arcpy.management.MakeFeatureLayer(fl, "fl" + hu, "ftype = 460 AND gnis_name IS NOT NULL")
    arcpy.management.SelectLayerByLocation(l, "INTERSECT", "Context")
    arcpy.management.CopyFeatures(l, "Named_" + hu)  # Project fails: ERROR 001489 (network)
    parts.append("Named_" + hu)
arcpy.management.Merge(parts, "Streams_named")
names = collections.Counter(r[0] for r in arcpy.da.SearchCursor("Streams_named", ["gnis_name"]))
res["named_streams_in_context"] = len(names)
arcpy.analysis.Select("Streams_named", "Rivers", "gnis_name LIKE '%River%'")
res["river_names_in_context"] = sorted({r[0] for r in arcpy.da.SearchCursor("Rivers", ["gnis_name"])})

# ---- places, roads ---------------------------------------------------------------------
pl = os.path.join(SRC, "tl_2025_46_place", "tl_2025_46_place.shp")
arcpy.management.Project(pl, "Places_all", UTM14)
pl_l = arcpy.management.MakeFeatureLayer("Places_all", "pl", "CLASSFP = 'C5'")
arcpy.management.SelectLayerByLocation(pl_l, "INTERSECT", "Context")
arcpy.management.CopyFeatures(pl_l, "Towns")
res["sd_incorporated_places_in_context"] = int(arcpy.management.GetCount("Towns")[0])
pl_l2 = arcpy.management.MakeFeatureLayer("Places_all", "pl2", "CLASSFP = 'C5'")
arcpy.management.SelectLayerByLocation(pl_l2, "INTERSECT", "Study_Area")
res["sd_incorporated_places_in_counties"] = int(arcpy.management.GetCount(pl_l2)[0])
rd = os.path.join(SRC, "tl_2025_46_prisecroads", "tl_2025_46_prisecroads.shp")
arcpy.management.Project(rd, "Roads_all", UTM14)
rd_l = arcpy.management.MakeFeatureLayer("Roads_all", "rd")
arcpy.management.SelectLayerByLocation(rd_l, "INTERSECT", "Context")
arcpy.management.CopyFeatures(rd_l, "Roads")
res["road_mtfcc_in_context"] = collections.Counter(r[0] for r in arcpy.da.SearchCursor("Roads", ["MTFCC"])).most_common()

arcpy.env.extent = RASTER_EXT; arcpy.env.mask = None  # a Mask env drops sources outside it (extent_trap.py)
# ---- distance rasters (Distance Accumulation, planar) -----------------------------------
dist = {}
for name, fc in [("Turbines", "Turbines"), ("Rivers", "Rivers"), ("Streams", "Streams_named"),
                 ("Towns", "Towns"), ("Roads", "Roads")]:
    r = sa.DistanceAccumulation(fc)
    r.save("Dist_" + name)
    dist[name] = r
    res.setdefault("dist_max_m", {})[name] = round(float(prop(r, "MAXIMUM")), 1)

arcpy.env.mask = "Study_Grid"
# ---- exclusions ------------------------------------------------------------------------
ex = {
    "wind_lt_7": wind < 7.0,
    "turbine_20mi": dist["Turbines"] <= 20 * MI,
    "turbine_10mi": dist["Turbines"] <= 10 * MI,
    "river_1mi": dist["Rivers"] <= 1 * MI,
    "river_2mi": dist["Rivers"] <= 2 * MI,
    "named_stream_1mi": dist["Streams"] <= 1 * MI,
    "town_gt_30mi": dist["Towns"] > 30 * MI,
    "road_gt_2mi": dist["Roads"] > 2 * MI,
}
res["excluded_cells"] = {k: count(v) for k, v in ex.items()}
res["excluded_pct"] = {k: round(100.0 * v / n_area, 1) for k, v in res["excluded_cells"].items()}

def mask_for(turb_mi=20, river_mi=1, wind_min=7.0):
    return sa.Con((wind >= wind_min) & (dist["Turbines"] > turb_mi * MI) & (dist["Rivers"] > river_mi * MI), 1, 0)

base_mask = mask_for()
base_mask.save("Exclusion_Mask")
res["mask_open_cells_base"] = count(base_mask)
res["mask_open_km2_base"] = round(res["mask_open_cells_base"] * cell_km2, 1)
for k, kw in {"turb10": dict(turb_mi=10), "turb30": dict(turb_mi=30), "river2": dict(river_mi=2),
              "wind75": dict(wind_min=7.5), "wind8": dict(wind_min=8.0)}.items():
    res.setdefault("mask_open_km2_variant", {})[k] = round(count(mask_for(**kw)) * cell_km2, 1)

# ---- preferences: Rescale by Function, Linear, 1-10 ------------------------------------
wmin, wmax = st["MINIMUM"], st["MAXIMUM"]
s_wind = sa.RescaleByFunction(wind, sa.TfLinear(wmin, wmax), 1, 10); s_wind.save("Score_Wind")
s_town = sa.RescaleByFunction(dist["Towns"], sa.TfLinear(0, 30 * MI), 10, 1); s_town.save("Score_Town")
s_road = sa.RescaleByFunction(dist["Roads"], sa.TfLinear(0, 10 * MI), 10, 1); s_road.save("Score_Road")
for nm in ["Score_Wind", "Score_Town", "Score_Road"]:
    res.setdefault("score_ranges", {})[nm] = [round(float(prop(nm, p)), 3) for p in ["MINIMUM", "MAXIMUM", "MEAN"]]

def run(ww, wt_, wr, mask=base_mask, tag=None):
    ws = sa.WeightedSum(sa.WSTable([[s_wind, "VALUE", ww], [s_town, "VALUE", wt_], [s_road, "VALUE", wr]]))
    score = sa.SetNull(mask == 0, ws)
    score.save("Score_" + (tag or "tmp"))
    mx = float(prop(score, "MAXIMUM"))
    top = sa.Con(score >= mx - 1e-6, 1)
    top.save("tmp_top")
    pts = arcpy.conversion.RasterToPoint("tmp_top", "tmp_top_pts", "VALUE")
    xy = [r[0] for r in arcpy.da.SearchCursor("tmp_top_pts", ["SHAPE@XY"])]
    cx = sum(p[0] for p in xy) / len(xy); cy = sum(p[1] for p in xy) / len(xy)
    g = arcpy.PointGeometry(arcpy.Point(cx, cy), UTM14).projectAs(arcpy.SpatialReference(4269))
    # suitable = score >= 7 (on the 1-10 scale)
    good = count(sa.Con(sa.IsNull(score), 0, sa.Con(score >= 7, 1, 0)))
    mean = float(prop(score, "MEAN"))
    return {"weights": [ww, wt_, wr], "max": round(mx, 4), "mean": round(mean, 3), "n_top_cells": len(xy),
            "top_xy_utm": [round(cx), round(cy)], "top_lonlat": [round(g.firstPoint.X, 4), round(g.firstPoint.Y, 4)],
            "km2_score_ge7": round(good * cell_km2, 1)}

res["runs"] = {
    "example_0.5_0.25_0.25": run(0.5, 0.25, 0.25, tag="Example"),
    "wind_first_0.7_0.15_0.15": run(0.7, 0.15, 0.15),
    "infra_first_0.2_0.4_0.4": run(0.2, 0.4, 0.4),
    "equal_1/3": run(1 / 3., 1 / 3., 1 / 3.),
    "example_turb10": run(0.5, 0.25, 0.25, mask=mask_for(turb_mi=10)),
}

# ---- personal parameter candidates (last two digits dd of the BYU ID) --------------------
# A: wind weight = 0.30 + dd/200 (0.30-0.795); town and road split the rest equally.
# B: turbine spacing = 10 + dd/10 miles (10.0-19.9), weights fixed at the example.
pa, pb = {}, {}
for dd in range(0, 100, 11):
    w = 0.30 + dd / 200.0
    pa[dd] = run(w, (1 - w) / 2, (1 - w) / 2)
    pb[dd] = run(0.5, 0.25, 0.25, mask=mask_for(turb_mi=10 + dd / 10.0))
res["personal_A_wind_weight"] = pa
res["personal_B_turbine_spacing"] = pb

json.dump(res, open(OUT, "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
