"""Lab 10 parity-plan probe: inventory the candidate vector sources.

Run with the ArcGIS Pro Python:
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/lab10/inventory.py
Reads C:\\Ames\\Lab10\\src (unzipped downloads); writes tools/lab10/inventory.json.
"""
import json, os, collections
import arcpy

SRC = r"C:\Ames\Lab10\src"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory.json")
COUNTIES = ["Minnehaha", "Moody", "Lake", "McCook", "Turner", "Lincoln"]
res = {}

def fields(fc):
    return [(f.name, f.type, f.length) for f in arcpy.ListFields(fc)]

cty = os.path.join(SRC, "tl_2025_us_county", "tl_2025_us_county.shp")
res["county_fields"] = fields(cty)
rows = []
with arcpy.da.SearchCursor(cty, ["STATEFP", "COUNTYFP", "NAME", "NAMELSAD", "ALAND", "AWATER"],
                           "STATEFP = '46'") as cur:
    for r in cur:
        if r[2] in COUNTIES:
            rows.append(r)
res["six_counties"] = rows
res["six_counties_aland_km2"] = sum(r[4] for r in rows) / 1e6
res["six_counties_awater_km2"] = sum(r[5] for r in rows) / 1e6
res["county_sr"] = arcpy.Describe(cty).spatialReference.name

pl = os.path.join(SRC, "tl_2025_46_place", "tl_2025_46_place.shp")
res["place_fields"] = fields(pl)
res["place_count_sd"] = int(arcpy.management.GetCount(pl)[0])
res["place_lsad_classfp"] = collections.Counter(
    (r[0], r[1]) for r in arcpy.da.SearchCursor(pl, ["LSAD", "CLASSFP"])).most_common()

rd = os.path.join(SRC, "tl_2025_46_prisecroads", "tl_2025_46_prisecroads.shp")
res["road_fields"] = fields(rd)
res["road_mtfcc"] = collections.Counter(r[0] for r in arcpy.da.SearchCursor(rd, ["MTFCC"])).most_common()

wt = None
for root, _, files in os.walk(os.path.join(SRC, "uswtdbSHP")):
    for f in files:
        if f.lower().endswith(".shp"):
            wt = os.path.join(root, f)
res["uswtdb_path"] = wt
res["uswtdb_fields"] = fields(wt)
res["uswtdb_count"] = int(arcpy.management.GetCount(wt)[0])
res["uswtdb_sr"] = arcpy.Describe(wt).spatialReference.name
st = collections.Counter(r[0] for r in arcpy.da.SearchCursor(wt, ["t_state"]))
res["uswtdb_by_state"] = {k: st[k] for k in ["SD", "MN", "IA", "NE", "ND"]}
res["uswtdb_six_counties"] = collections.Counter(
    (r[0], r[1]) for r in arcpy.da.SearchCursor(wt, ["t_county", "p_name"], "t_state = 'SD'")
    if r[0] and r[0].replace(" County", "") in COUNTIES).most_common()

gdb = os.path.join(SRC, "NHD_H_1017_HU4_GDB", "NHD_H_1017_HU4_GDB.gdb")
arcpy.env.workspace = gdb
res["nhd_datasets"] = arcpy.ListDatasets() or []
fcs = []
for ds in (arcpy.ListDatasets() or []) + [""]:
    fcs += [os.path.join(ds, f) for f in (arcpy.ListFeatureClasses(feature_dataset=ds) or [])]
res["nhd_fcs"] = fcs
flow = [f for f in fcs if f.endswith("NHDFlowline")][0]
res["nhd_flowline_fields"] = [f[0] for f in fields(flow)]
ftype = collections.Counter(r[0] for r in arcpy.da.SearchCursor(flow, ["FType"]))
res["nhd_flowline_ftype"] = ftype.most_common()
named = collections.Counter(r[0] for r in arcpy.da.SearchCursor(
    flow, ["GNIS_Name"], "FType = 460 AND GNIS_Name IS NOT NULL"))
res["nhd_named_streamriver_top"] = named.most_common(25)
res["nhd_named_streamriver_n_names"] = len(named)

json.dump(res, open(OUT, "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:6000])
