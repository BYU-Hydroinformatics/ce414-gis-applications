import arcpy, time, json, urllib.request, urllib.parse
arcpy.CheckOutExtension("Network"); arcpy.env.overwriteOutput = True
G = r"C:/Ames/Lab11/feas/Feas.gdb"; ND = G + "/Network/UtahRoadsNetwork"; ROOT = r"C:/Ames/Lab11/feas"
UG = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
def post(url, params):
    with urllib.request.urlopen(url, urllib.parse.urlencode(params).encode(), timeout=300) as r: return json.load(r)
if not arcpy.Exists(G + "/Blocks"):
    url = f"{UG}/CensusBlocks2020/FeatureServer/0/query"
    oids = sorted(post(url, {"where": "COUNTYFP20='049'", "returnIdsOnly": "true", "f": "json"})["objectIds"])
    parts = []
    for i in range(0, len(oids), 500):
        d = post(url, {"objectIds": ",".join(map(str, oids[i:i+500])), "outFields": "GEOID20,PP_TOTAL,HU_TOTAL,ALAND20", "returnGeometry": "true", "outSR": 26912, "f": "json"})
        jp = f"{ROOT}/blocks_{i}.json"; json.dump(d, open(jp, "w")); fc = f"{G}/blk_{i}"; arcpy.conversion.JSONToFeatures(jp, fc); parts.append(fc)
    arcpy.management.Merge(parts, G + "/Blocks")
    for fc in parts: arcpy.management.Delete(fc)
    arcpy.management.FeatureToPoint(G + "/Blocks", G + "/Block_Points", "INSIDE")
print("blocks", arcpy.management.GetCount(G + "/Blocks")[0], "points", arcpy.management.GetCount(G + "/Block_Points")[0])
tot = sum(r[0] or 0 for r in arcpy.da.SearchCursor(G + "/Block_Points", ["PP_TOTAL"]))
print("county population (blocks)", tot)
# one solve with many rings
t0 = time.time()
cuts = [2, 3, 4, 5, 6, 7, 8, 10, 12]
lyr = arcpy.na.MakeServiceAreaAnalysisLayer(ND, "SA", travel_direction="FROM_FACILITIES", cutoffs=cuts, polygon_detail="STANDARD", geometry_at_overlaps="DISSOLVE", geometry_at_cutoffs="RINGS").getOutput(0)
arcpy.na.AddLocations(lyr, "Facilities", G + "/Fire_Stations", search_tolerance="5000 Meters"); arcpy.na.Solve(lyr)
names = arcpy.na.GetNAClassNames(lyr)
arcpy.management.CopyFeatures(lyr.listLayers(names["SAPolygons"])[0], G + "/SA_rings")
print("solved rings", round(time.time()-t0, 1), "s")
# cumulative population within each break: points whose ring ToBreak <= cutoff
arcpy.analysis.SpatialJoin(G + "/Block_Points", G + "/SA_rings", G + "/BP_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", match_option="INTERSECT")
rows = [(r[0] or 0, r[1]) for r in arcpy.da.SearchCursor(G + "/BP_join", ["PP_TOTAL", "ToBreak"])]
print("cutoff_min, pop_within, pop_outside, pct_outside")
for c in cuts:
    within = sum(p for p, tb in rows if tb is not None and tb <= c)
    print(c, within, tot - within, round(100 * (tot - within) / tot, 1))
# straight-line buffers for the contrast
for km in [1.5, 2, 2.5, 3, 4]:
    arcpy.analysis.Buffer(G + "/Fire_Stations", G + f"/Buf_{int(km*10)}", f"{km} Kilometers", dissolve_option="ALL")
    sel = arcpy.management.SelectLayerByLocation(arcpy.management.MakeFeatureLayer(G + "/Block_Points", "bp"), "INTERSECT", G + f"/Buf_{int(km*10)}")
    within = sum(r[0] or 0 for r in arcpy.da.SearchCursor(sel, ["PP_TOTAL"]))
    print(f"buffer {km} km: within {within}, outside {tot - within}, {round(100*(tot-within)/tot,1)} %")
print("total", round(time.time()-t0, 1), "s")
