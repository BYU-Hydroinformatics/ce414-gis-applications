"""Lab 7 (HAND): fetch the vector layers for the Provo River study box into C:/Ames/HAND/HAND.gdb.

  Gage          USGS 10163000 point (NWIS site file coordinates, NAD83)
  NHD_Flowlines UGRC UtahStreamsNHD, clipped to the box
  FEMA_Zones    FEMA NFHL layer 28 (S_FLD_HAZ_AR), Utah County DFIRM 49049C, clipped to the box
  FEMA_XS       FEMA NFHL layer 14 (S_XS), Provo River cross-sections with WSEL_REG / STRMBED_EL
  Buildings     UGRC statewide Buildings, clipped to the box
  Parcels       UGRC Parcels_Utah_LIR (assessor attributes, no owner names), clipped to the box

The NFHL service rejects spatial queries on layer 28 (HTTP 400 "Failed to execute query", Oct 8,
2026), so the county is paged by attribute (DFIRM_ID) and clipped locally.
Run with the ArcGIS Pro python.
"""
import json
import os
import urllib.parse
import urllib.request

import arcpy

GDB = r"C:\Ames\HAND\HAND.gdb"
RAW = r"C:\Ames\HAND\raw\vec"
UTM = arcpy.SpatialReference(26912)
INFO = json.load(open(r"C:\Ames\HAND\dem\dem_info.json"))
XMIN, YMIN, XMAX, YMAX = INFO["box_utm"]
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
NFHL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer"

LAYERS = {
    "NHD_Flowlines": (f"{UGRC}/UtahStreamsNHD/FeatureServer/0", "1=1", True),
    "Buildings": (f"{UGRC}/Buildings/FeatureServer/0", "1=1", True),
    "Parcels": (f"{UGRC}/Parcels_Utah_LIR/FeatureServer/0", "1=1", True),
    "FEMA_Zones": (f"{NFHL}/28", "DFIRM_ID='49049C'", False),
    "FEMA_XS": (f"{NFHL}/14", "DFIRM_ID='49049C' AND WTR_NM='PROVO RIVER'", False),
}


def get(url, params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url + "/query", data=data, timeout=300) as r:
        return json.load(r)


def fetch(name, url, where, spatial):
    os.makedirs(RAW, exist_ok=True)
    base = {"where": where, "outFields": "*", "returnGeometry": "true", "outSR": 26912, "f": "json"}
    if spatial:
        base.update(geometry=json.dumps({"xmin": XMIN, "ymin": YMIN, "xmax": XMAX, "ymax": YMAX,
                                         "spatialReference": {"wkid": 26912}}),
                    geometryType="esriGeometryEnvelope", spatialRel="esriSpatialRelIntersects", inSR=26912)
    ids = get(url, dict(base, returnIdsOnly="true"))
    oids = sorted(ids.get("objectIds") or [])
    oid_field = ids["objectIdFieldName"]
    parts = []
    def grab(chunk, tag):
        # NFHL returns HTTP-200 {"error": 500} for some chunks (very large polygons): split and retry
        d = get(url, {"objectIds": ",".join(map(str, chunk)), "outFields": "*", "returnGeometry": "true",
                      "outSR": 26912, "f": "json"})
        if "error" in d:
            if len(chunk) == 1:
                print(name, "service error on OID", chunk[0], d["error"])
                return
            grab(chunk[:len(chunk) // 2], tag + "a")
            grab(chunk[len(chunk) // 2:], tag + "b")
            return
        p = os.path.join(RAW, f"{name}_{tag}.json")
        json.dump(d, open(p, "w"))
        parts.append(p)

    for i in range(0, len(oids), 500):
        grab(oids[i:i + 500], f"{i // 500:03d}")
    fcs = []
    skipped = []

    def load(p):
        fc = f"memory\\{name}_{len(fcs)}"
        try:
            arcpy.conversion.JSONToFeatures(p, fc)
            fcs.append(fc)
        except arcpy.ExecuteError:  # ERROR 001558 on a few parcel chunks: split and retry
            d = json.load(open(p))
            f = d["features"]
            if len(f) == 1:
                skipped.append(f[0]["attributes"].get(oid_field))
                return
            for k, sub in enumerate((f[:len(f) // 2], f[len(f) // 2:])):
                q = p.replace(".json", f"_{k}.json")
                json.dump(dict(d, features=sub), open(q, "w"))
                load(q)

    for p in parts:
        load(p)
    if skipped:
        print(name, "skipped unparseable OIDs", skipped)
    merged = f"memory\\{name}_all"
    arcpy.management.Merge(fcs, merged)
    box = arcpy.Polygon(arcpy.Array([arcpy.Point(XMIN, YMIN), arcpy.Point(XMIN, YMAX),
                                     arcpy.Point(XMAX, YMAX), arcpy.Point(XMAX, YMIN)]), UTM)
    out = os.path.join(GDB, name)
    arcpy.analysis.Clip(merged, box, out)
    return len(oids), int(arcpy.management.GetCount(out)[0])


def main():
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(os.path.dirname(GDB), os.path.basename(GDB))
    arcpy.env.overwriteOutput = True
    log = {}
    # gage point from the NWIS site file (dec_lat_va / dec_long_va, NAD83)
    gage = os.path.join(GDB, "Gage")
    arcpy.management.CreateFeatureclass(GDB, "Gage", "POINT", spatial_reference=UTM)
    arcpy.management.AddField(gage, "SITE_NO", "TEXT", field_length=15)
    pt = arcpy.PointGeometry(arcpy.Point(-111.7111944, 40.23925556), arcpy.SpatialReference(4269)).projectAs(UTM)
    with arcpy.da.InsertCursor(gage, ["SHAPE@", "SITE_NO"]) as c:
        c.insertRow([pt, "10163000"])
    log["Gage"] = [pt.firstPoint.X, pt.firstPoint.Y]
    for name, (url, where, spatial) in LAYERS.items():
        if arcpy.Exists(os.path.join(GDB, name)):
            log[name] = int(arcpy.management.GetCount(os.path.join(GDB, name))[0])
            continue
        log[name] = fetch(name, url, where, spatial)
        print(name, log[name])
    json.dump(log, open(r"C:\Ames\HAND\fetch_vectors.json", "w"), indent=2)


if __name__ == "__main__":
    main()
