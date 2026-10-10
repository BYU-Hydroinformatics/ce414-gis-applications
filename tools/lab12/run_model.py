r"""Lab 12 reference run: the page's model in arcpy, on the hosted package only.

    python run_model.py               baseline + step checks + sensitivity runs -> check_values.json
    python run_model.py personal      the personal-cutoff sweep (BYU ID digits 00-99) -> the private
                                      repo's grading-oracles/lab12_personal_lookup.csv

The model (one ModelBuilder model on the page, "Fire Response Coverage"):
  Make Service Area Analysis Layer   network Utah_County_Roads_ND, travel mode default (TravelMinutes),
                                     Cutoffs = %Cutoff_Minutes% (default 4), away from facilities,
                                     Standard polygons, Dissolve overlaps, Rings
  Add Locations (Facilities)         Fire_Stations
  Solve
  Select Data (Polygons) -> Copy Features                       -> Served_Area
  Select Layer By Location  Census_Blocks HAVE_THEIR_CENTER_IN Served_Area, INVERT
    -> Copy Features                                           -> Unserved_Blocks
    -> Summary Statistics (SUM PP_TOTAL, COUNT GEOID20)        -> Unserved_Population
  Buffer Fire_Stations %Buffer_Distance% (default 3.75 km), dissolve ALL -> Crow_Area
  Select Layer By Location  Census_Blocks HAVE_THEIR_CENTER_IN Crow_Area, INVERT
    -> Copy Features                                           -> Crow_Unserved
    -> Summary Statistics                                      -> Crow_Population
Geoprocessing tools throughout (not arcpy.nax), so every default is the tool dialog's default.
ArcGIS Pro Python (3.7.1), Network Analyst extension.
"""
import csv
import json
import os
import sys
import time
import zipfile

import arcpy

arcpy.CheckOutExtension("Network")
arcpy.env.overwriteOutput = True
HERE = os.path.dirname(os.path.abspath(__file__))


def private_path(here, name):
    """Grading oracles belong in the private companion repo (../ce414-private/grading-oracles/).
    If that checkout is absent, write beside the script; the public .gitignore keeps it out of git."""
    priv = os.path.normpath(os.path.join(here, "..", "..", "..", "ce414-private", "grading-oracles"))
    return os.path.join(priv, name) if os.path.isdir(priv) else os.path.join(here, name.split("_", 1)[1])


ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab12-fire-response.zip")
ROOT = r"C:\Ames\Lab12\ref"
DATA = os.path.join(ROOT, "lab12-fire-response")
SRC = os.path.join(DATA, "FireResponse.gdb")
ND = os.path.join(SRC, "Network", "Utah_County_Roads_ND")
STATIONS = os.path.join(SRC, "Fire_Stations")
BLOCKS = os.path.join(SRC, "Census_Blocks")
G = os.path.join(ROOT, "Ref.gdb")
DEFAULT_CUTOFF = 4.0
DEFAULT_BUFFER_KM = 3.75          # 4 minutes at 35 mph: 35 * 4 / 60 = 2.33 mi = 3.75 km
SENSITIVITY_CUTOFFS = [2, 4, 6, 8, 10, 12]
SENSITIVITY_BUFFERS_KM = [1.5, 2, 2.5, 3, 3.75, 5]


def setup():
    if not os.path.exists(DATA):
        os.makedirs(ROOT, exist_ok=True)
        zipfile.ZipFile(ZIP).extractall(ROOT)
    if not arcpy.Exists(G):
        arcpy.management.CreateFileGDB(ROOT, "Ref.gdb")
    arcpy.env.workspace = G
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(26912)


def count(fc):
    return int(arcpy.management.GetCount(fc)[0])


def area_km2(fc, where=None):
    return round(sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"], where)) / 1e6, 2)


def population(fc):
    return int(sum(r[0] or 0 for r in arcpy.da.SearchCursor(fc, ["PP_TOTAL"])))


def unserved(area_fc, tag):
    """Blocks whose center is outside area_fc: Unserved_<tag> (features) and its population and count."""
    lyr = arcpy.management.MakeFeatureLayer(BLOCKS, f"blk_{tag}")
    arcpy.management.SelectLayerByLocation(lyr, "HAVE_THEIR_CENTER_IN", area_fc, invert_spatial_relationship="INVERT")
    out = f"Unserved_{tag}"
    arcpy.management.CopyFeatures(lyr, out)
    tbl = f"Unserved_Population_{tag}"
    arcpy.analysis.Statistics(out, tbl, [["PP_TOTAL", "SUM"], ["GEOID20", "COUNT"]])
    row = next(arcpy.da.SearchCursor(tbl, ["SUM_PP_TOTAL", "COUNT_GEOID20"]))
    return {"population": int(row[0]), "blocks": int(row[1])}


def service_area(cutoffs, tag):
    """The model's network half: Served_<tag> polygons; returns facility status counts and ring areas."""
    t0 = time.time()
    cut = cutoffs if isinstance(cutoffs, list) else [cutoffs]
    lyr = arcpy.na.MakeServiceAreaAnalysisLayer(ND, f"SA_{tag}", travel_direction="FROM_FACILITIES", cutoffs=cut,
                                                polygon_detail="STANDARD", geometry_at_overlaps="DISSOLVE",
                                                geometry_at_cutoffs="RINGS").getOutput(0)
    arcpy.na.AddLocations(lyr, "Facilities", STATIONS)
    arcpy.na.Solve(lyr)
    names = arcpy.na.GetNAClassNames(lyr)
    fac = lyr.listLayers(names["Facilities"])[0]
    status = [r[0] for r in arcpy.da.SearchCursor(fac, ["Status"])]
    out = f"Served_{tag}"
    arcpy.management.CopyFeatures(lyr.listLayers(names["SAPolygons"])[0], out)
    rings = [(r[0], r[1], round(r[2] / 1e6, 2)) for r in arcpy.da.SearchCursor(out, ["FromBreak", "ToBreak", "SHAPE@AREA"])]
    return {"cutoffs": cut, "located": status.count(0), "not_located": len(status) - status.count(0),
            "rings_km2": sorted(rings), "area_km2": round(sum(r[2] for r in rings), 2), "seconds": round(time.time() - t0, 1)}


def crow(buffer_km, tag):
    out = f"Crow_{tag}"
    arcpy.analysis.Buffer(STATIONS, out, f"{buffer_km} Kilometers", dissolve_option="ALL")
    return {"buffer_km": buffer_km, "area_km2": area_km2(out), **unserved(out, f"crow_{tag}")}


def inputs(ck):
    d = arcpy.Describe(ND)
    roads = os.path.join(SRC, "Network", "Roads")
    ck["inputs"] = {"Roads": count(roads), "Junctions": count(os.path.join(SRC, "Network", "Utah_County_Roads_ND_Junctions")),
                    "Fire_Stations": count(STATIONS), "Census_Blocks": count(BLOCKS), "population": population(BLOCKS),
                    "network_attributes": [(a.name, a.usageType, a.units) for a in d.attributes],
                    "travel_modes": list(arcpy.nax.GetTravelModes(ND).keys())}
    ck["one_way"] = {"edges": count(arcpy.management.MakeFeatureLayer(roads, "ow", "ONEWAY IN ('1', '2')"))}
    # the one-way penalty, read on the longest one-way interstate segment
    with arcpy.da.SearchCursor(roads, ["FULLNAME", "ONEWAY", "F_T_IMP_MIN", "T_F_IMP_MIN", "SPEED_LMT", "SHAPE@LENGTH"],
                               "ONEWAY IN ('1', '2') AND FULLNAME LIKE 'I-15%'", sql_clause=(None, "ORDER BY Shape_Length DESC")) as cur:
        r = next(cur)
    ck["one_way"]["example"] = {"FULLNAME": r[0], "ONEWAY": r[1], "F_T_IMP_MIN": round(r[2], 4), "T_F_IMP_MIN": round(r[3], 4),
                                "SPEED_LMT": r[4], "length_m": round(r[5], 1), "ratio": round(max(r[2], r[3]) / min(r[2], r[3]), 1)}
    # total minutes and length, two-way
    tot = [0.0, 0.0]
    for ft, tf, L in arcpy.da.SearchCursor(roads, ["F_T_IMP_MIN", "T_F_IMP_MIN", "SHAPE@LENGTH"]):
        tot[0] += min(ft, tf); tot[1] += L
    ck["one_way"]["road_km"] = round(tot[1] / 1000, 1)
    ck["stations"] = {"EMS_Y": count(arcpy.management.MakeFeatureLayer(STATIONS, "e", "EMS = 'Y'")),
                      "EMS_N": count(arcpy.management.MakeFeatureLayer(STATIONS, "n", "EMS = 'N'"))}
    ck["blocks"] = {"zero_population": count(arcpy.management.MakeFeatureLayer(BLOCKS, "z", "PP_TOTAL = 0")),
                    "urban": count(arcpy.management.MakeFeatureLayer(BLOCKS, "u", "UR20 = 'U'"))}


def main():
    setup()
    ck = {"arcgis_pro": arcpy.GetInstallInfo()["Version"]}
    inputs(ck)
    pop = ck["inputs"]["population"]
    # baseline, as the model runs it (Step 4: Served_Area; Step 5: Unserved_Blocks; Step 6: Crow_Area)
    ck["baseline"] = service_area(DEFAULT_CUTOFF, "base")
    ck["baseline"].update(unserved("Served_base", "base"))
    ck["baseline"]["pct_outside"] = round(100 * ck["baseline"]["population"] / pop, 1)
    ck["crow_default"] = crow(DEFAULT_BUFFER_KM, "base")
    ck["crow_default"]["pct_outside"] = round(100 * ck["crow_default"]["population"] / pop, 1)
    # the two-ring map run (Step 4's second check, Map 1): cutoffs 4 and 8
    ck["rings_4_8"] = service_area([4, 8], "rings")
    # sensitivity: cutoffs and buffers, one solve each so each equals a dialog run at that value
    ck["sensitivity"] = {"cutoffs": [], "buffers": []}
    for c in SENSITIVITY_CUTOFFS:
        tag = f"c{c}"
        r = service_area(float(c), tag)
        r.update(unserved(f"Served_{tag}", tag))
        r["pct_outside"] = round(100 * r["population"] / pop, 1)
        ck["sensitivity"]["cutoffs"].append(r)
        print("cutoff", c, r["population"], r["pct_outside"], r["area_km2"], "km2")
    for b in SENSITIVITY_BUFFERS_KM:
        r = crow(b, f"b{str(b).replace('.', '_')}")
        r["pct_outside"] = round(100 * r["population"] / pop, 1)
        ck["sensitivity"]["buffers"].append(r)
        print("buffer", b, r["population"], r["pct_outside"])
    # the two example personal runs quoted on the page (BYU IDs ending 89 and 02)
    ck["examples"] = {}
    for digits in (89, 2):
        c = round(4 + 0.04 * digits, 2)
        tag = f"ex{digits:02d}"
        r = service_area(c, tag)
        r.update(unserved(f"Served_{tag}", tag))
        r["pct_outside"] = round(100 * r["population"] / pop, 1)
        r["digits"] = digits; r["cutoff"] = c
        ck["examples"][f"{digits:02d}"] = r
    json.dump(ck, open(os.path.join(HERE, "check_values.json"), "w"), indent=1)
    print(json.dumps(ck, indent=1))


def personal():
    """Cutoff = 4 + 0.04 x (last two BYU ID digits), 00-99: one solve each -> the private lookup."""
    setup()
    pop = population(BLOCKS)
    out = private_path(HERE, "lab12_personal_lookup.csv")
    rows = []
    for d in range(100):
        c = round(4 + 0.04 * d, 2)
        tag = f"p{d:02d}"
        r = service_area(c, tag)
        r.update(unserved(f"Served_{tag}", tag))
        rows.append([f"{d:02d}", c, r["area_km2"], r["population"], round(100 * r["population"] / pop, 1), r["blocks"]])
        print(rows[-1], r["seconds"], "s")
        for fc in (f"Served_{tag}", f"Unserved_{tag}"):
            pass  # kept: build_figures.py draws the page's example run from Served_p89
        arcpy.management.Delete(f"Unserved_Population_{tag}")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["digits", "cutoff_minutes", "served_area_km2", "people_outside", "pct_outside", "blocks_outside"])
        w.writerows(rows)
    print("wrote", out)


if __name__ == "__main__":
    personal() if "personal" in sys.argv[1:] else main()
