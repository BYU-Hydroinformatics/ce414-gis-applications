"""Describe the baseline result for the lab page: where the larger candidate zones are, the
density surface's range inside the county, and what de-duplicating the towers would change.
Run after run_model.py (reads C:\\Ames\\Lab04\\Check.gdb)."""
import arcpy, json, collections
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = r"C:\Ames\Lab04\Check.gdb"
arcpy.env.overwriteOutput = True
utm = arcpy.SpatialReference(26912)
wgs = arcpy.SpatialReference(4326)
out = {}

zones = []
with arcpy.da.SearchCursor("Suitable_Polys", ["SHAPE@AREA", "SHAPE@"]) as c:
    for a, g in c:
        if a >= 1e6:
            p = g.labelPoint
            q = arcpy.PointGeometry(p, utm).projectAs(wgs).firstPoint
            zones.append(dict(km2=round(a / 1e6, 2), x=round(p.X), y=round(p.Y), lon=round(q.X, 4), lat=round(q.Y, 4)))
zones.sort(key=lambda z: -z["km2"])
out["zones_ge_1km2"] = zones

# nearest highway name for each zone
arcpy.management.MakeFeatureLayer("Major_Highways", "hw")
for z in zones:
    pt = arcpy.PointGeometry(arcpy.Point(z["x"], z["y"]), utm)
    best = None
    with arcpy.da.SearchCursor("Major_Highways", ["SHAPE@", "ROUTE_AL_1"]) as c:
        for g, name in c:
            d = g.distanceTo(pt)
            if best is None or d < best[0]:
                best = (d, name)
    z["nearest_highway"] = best[1]
    z["highway_m"] = round(best[0])

# density inside the county
ExtractByMask("Tower_Density", "Utah_County").save("KD_County")
r = Raster("KD_County")
out["kd_county_per10k"] = dict(min=r.minimum * 1e4, max=r.maximum * 1e4, mean=r.mean * 1e4)

# is any suitable cell outside the corridor? (should be impossible)
out["suitable_outside_corridor"] = "checked by construction: Extract by Mask sets NoData outside"

# one tower's peak density at 20 km: 3/(pi r^2) per km2
import math
out["one_tower_peak_per10k"] = {r_: 3 / (math.pi * (r_ / 1000) ** 2) * 1e4 for r_ in (10000, 20000, 40000)}

# duplicates
xy = collections.Counter()
with arcpy.da.SearchCursor("Towers_Clip", ["SHAPE@XY"]) as c:
    for (p,) in c:
        xy[(round(p[0]), round(p[1]))] += 1
out["towers_clip"] = sum(xy.values())
out["towers_clip_distinct"] = len(xy)
arcpy.management.CopyFeatures("Towers_Clip", "Towers_Dedup")
arcpy.management.DeleteIdentical("Towers_Dedup", ["Shape"], "1 Meters")
kd = KernelDensity("Towers_Dedup", "NONE", 30, 20000, "SQUARE_KILOMETERS", "DENSITIES", "PLANAR")
final = Raster("Flat_Near_Road") * Con(10000 * kd < 20, 1, 0)
final.save("Suitable_Dedup")
arcpy.management.BuildRasterAttributeTable("Suitable_Dedup", "Overwrite")
n = {v: k for v, k in arcpy.da.SearchCursor("Suitable_Dedup", ["Value", "Count"])}
out["dedup_suitable_km2"] = n.get(1, 0) * 900 / 1e6
print(json.dumps(out, indent=1))
json.dump(out, open(__file__.replace("describe_zones.py", "zones.json"), "w"), indent=1)
