"""Feasibility: clip UGRC's Utah Street Network to Utah County, rebuild it from UGRC's own template, solve a service area."""
import arcpy, os, time, json, urllib.request, urllib.parse
arcpy.CheckOutExtension("Network")
arcpy.env.overwriteOutput = True
SRC = r"C:/Ames/Lab11/ugrc_network/UtahRoadsNetworkAnalysis.gdb"
SRC_ND = SRC + "/NetworkDataset/UtahRoadsNetwork"
ROOT = r"C:/Ames/Lab11/feas"
os.makedirs(ROOT, exist_ok=True)
G = ROOT + "/Feas.gdb"
XML = ROOT + "/ugrc_nd_template.xml"
t0 = time.time()
if not arcpy.Exists(G):
    arcpy.management.CreateFileGDB(ROOT, "Feas.gdb")
arcpy.nax.CreateTemplateFromNetworkDataset(SRC_ND, XML)
print("template", os.path.getsize(XML), "bytes", round(time.time()-t0))
txt = open(XML, encoding="utf-8", errors="ignore").read()
import re
print("evaluator fields in template:", sorted(set(re.findall(r"\[([A-Z_]+)\]", txt)))[:20], "| oneway mentioned:", "ONEWAY" in txt, "| restriction count:", txt.count("<UsageType>esriNAUTRestriction"))
# feature dataset + Utah County roads
sr = arcpy.Describe(SRC + "/NetworkDataset").spatialReference
if not arcpy.Exists(G + "/Network"):
    arcpy.management.CreateFeatureDataset(G, "Network", sr)
    arcpy.conversion.ExportFeatures(SRC + "/NetworkDataset/Roads", G + "/Network/Roads", "COUNTY_L = '49049' OR COUNTY_R = '49049'")
print("roads", arcpy.management.GetCount(G + "/Network/Roads")[0], round(time.time()-t0))
# one-way check in the source impedance fields
n1 = n_big = 0
with arcpy.da.SearchCursor(G + "/Network/Roads", ["ONEWAY", "F_T_IMP_MIN", "T_F_IMP_MIN"], "ONEWAY IN ('1','2')") as cur:
    for ow, ft, tf in cur:
        n1 += 1
        if (ft is None or tf is None) or abs(ft - tf) > 1e-9 or ft > 1e4 or tf > 1e4: n_big += 1
print("one-way edges", n1, "with asymmetric/blocked impedance", n_big)
ND = G + "/Network/UtahCountyNetwork"
if not arcpy.Exists(ND):
    arcpy.nax.CreateNetworkDatasetFromTemplate(XML, G + "/Network")
    # the template names the ND as in the source; find it
for c in arcpy.Describe(G + "/Network").children:
    if c.dataType == "NetworkDataset": ND = G + "/Network/" + c.name
print("ND:", ND, round(time.time()-t0))
arcpy.nax.BuildNetwork(ND)
print("built", round(time.time()-t0))
d = arcpy.Describe(ND)
print("attrs:", [(a.name, a.usageType, a.units) for a in d.attributes])
# fire stations in Utah County from UGRC
UG = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
def post(url, params):
    with urllib.request.urlopen(url, urllib.parse.urlencode(params).encode(), timeout=300) as r: return json.load(r)
if not arcpy.Exists(G + "/Fire_Stations"):
    js = post(f"{UG}/FireStations/FeatureServer/0/query", {"where": "COUNTY = 'UTAH'", "outFields": "*", "returnGeometry": "true", "outSR": 26912, "f": "json"})
    jp = ROOT + "/fire.json"; json.dump(js, open(jp, "w"))
    arcpy.conversion.JSONToFeatures(jp, G + "/Fire_Stations")
print("stations", arcpy.management.GetCount(G + "/Fire_Stations")[0])
# service area via arcpy.nax
t1 = time.time()
sa = arcpy.nax.ServiceArea(ND)
sa.travelMode = None
sa.timeUnits = arcpy.nax.TimeUnits.Minutes
sa.defaultImpedanceCutoffs = [4, 8]
sa.travelDirection = arcpy.nax.TravelDirection.FromFacility
sa.geometryAtOverlap = arcpy.nax.ServiceAreaOverlapGeometry.Dissolve
sa.polygonDetail = arcpy.nax.ServiceAreaPolygonDetail.Standard
sa.load(arcpy.nax.ServiceAreaInputDataType.Facilities, G + "/Fire_Stations")
res = sa.solve()
print("solved", res.solveSucceeded, round(time.time()-t1), "s; msgs", res.solverMessages(arcpy.nax.MessageSeverity.Warning)[:3])
res.export(arcpy.nax.ServiceAreaOutputDataType.Polygons, G + "/SA_4_8")
with arcpy.da.SearchCursor(G + "/SA_4_8", ["FromBreak", "ToBreak", "SHAPE@AREA"]) as cur:
    for r in cur: print("  ring", r[0], r[1], round(r[2]/1e6, 1), "km2")
print("total", round(time.time()-t0), "s")
