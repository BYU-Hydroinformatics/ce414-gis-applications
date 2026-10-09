"""Lab 11: what real infrastructure sits near the handout's two endpoints?

Lists UGRC TransmissionLines substation features (LAYER 'SUB-%') and the kV lines within 3 km of
each handout coordinate, and exports an imagery chip around each point so the site can be
checked by eye.   ArcGIS Pro Python."""
import json
import os
import urllib.parse
import urllib.request

import arcpy

OUT = r"C:\Ames\Lab11\probe"
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
PTS = {"source (handout)": (40.076955, -111.584886), "destination (handout)": (40.460597, -111.935419)}
UTM = arcpy.SpatialReference(26912)
WGS = arcpy.SpatialReference(4326)


def query(svc, where, x, y, r, fields):
    p = {"where": where, "geometry": f"{x},{y}", "geometryType": "esriGeometryPoint", "inSR": 26912,
         "distance": r, "units": "esriSRUnit_Meter", "spatialRel": "esriSpatialRelIntersects",
         "outFields": fields, "returnGeometry": "true", "outSR": 26912, "f": "json"}
    with urllib.request.urlopen(f"{UGRC}/{svc}/FeatureServer/0/query", urllib.parse.urlencode(p).encode(), timeout=120) as f:
        return json.load(f)


os.makedirs(OUT, exist_ok=True)
for name, (lat, lon) in PTS.items():
    g = arcpy.PointGeometry(arcpy.Point(lon, lat), WGS).projectAs(UTM).firstPoint
    print(f"== {name}: {lat}, {lon} -> {g.X:.0f} E, {g.Y:.0f} N")
    d = query("TransmissionLines", "LAYER LIKE 'SUB-%'", g.X, g.Y, 5000, "OBJECTID,LAYER,SGID_DES_U,COMMENTS")
    for f in d.get("features", []):
        geo = f["geometry"]
        if "paths" in geo:
            xs = [p[0] for path in geo["paths"] for p in path]; ys = [p[1] for path in geo["paths"] for p in path]
        elif "rings" in geo:
            xs = [p[0] for r in geo["rings"] for p in r]; ys = [p[1] for r in geo["rings"] for p in r]
        else:
            xs, ys = [geo["x"]], [geo["y"]]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        ll = arcpy.PointGeometry(arcpy.Point(cx, cy), UTM).projectAs(WGS).firstPoint
        print("  substation", f["attributes"], f"{((cx-g.X)**2+(cy-g.Y)**2)**0.5:.0f} m away",
              f"at {ll.Y:.5f}, {ll.X:.5f}")
    d = query("TransmissionLines", "LAYER LIKE 'KV-%'", g.X, g.Y, 3000, "OBJECTID,LAYER")
    print("  kV lines within 3 km:", sorted({f["attributes"]["LAYER"] for f in d.get("features", [])}),
          len(d.get("features", [])))
