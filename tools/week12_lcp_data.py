r"""Data for the Week 12 Thursday deck (slides/week-12/least-cost-path-b.md): Lab 11's setting, from
the mouth of Spanish Fork Canyon to the data center at Bluffdale, fetched from public services.

- Elevation: USGS 3DEP elevation image service, exported at 100 m (Lab 11's cell size) in NAD 1983
  UTM zone 12N over a box around both endpoints.
- From the Utah Geospatial Resource Center (services1.arcgis.com/99lidPhWCzftIe9K), clipped to the box:
    Major_Roads    UtahRoads, DOT_FCLASS in Interstate, Other Freeway, Principal Arterial
    Major_Lakes    UtahLakesNHD, AreaSqKm > 1          (the field Lab 11's handout names)
    Major_Streams  UtahStreamsNHD, IsMajor = 1         (the field Lab 11's handout names)
    Cities         UtahMunicipalBoundaries
    Power_Lines    TransmissionLines, LAYER LIKE 'KV-%' (46, 138 and 345 kV lines; not substations)
- Source and destination: the coordinates Lab 11 gives (40.076955, -111.584886 and 40.460597,
  -111.935419).

Writes C:\Ames\Week12\LCP.gdb and C:\Ames\Week12\dem100.tif.   ArcGIS Pro Python.
"""
import json
import math
import os
import urllib.parse
import urllib.request

import arcpy

W = r"C:\Ames\Week12"
GDB = os.path.join(W, "LCP.gdb")
UTM = arcpy.SpatialReference(26912)
WGS = arcpy.SpatialReference(4326)
BOX_LL = (-112.05, 39.98, -111.45, 40.55)          # W, S, E, N
CELL = 100.0
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
DEM_SVC = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
LAYERS = {
    "Major_Roads": ("UtahRoads", "DOT_FCLASS IN ('Interstate', 'Other Freeway', 'Principal Arterial')", "DOT_FCLASS,DOT_RTNAME,FULLNAME"),
    "Major_Lakes": ("UtahLakesNHD", "AreaSqKm > 1", "GNIS_Name,AreaSqKm,IsMajor"),
    "Major_Streams": ("UtahStreamsNHD", "IsMajor = 1", "GNIS_Name,IsMajor"),
    "Cities": ("UtahMunicipalBoundaries", "1=1", "NAME,POPLASTESTIMATE"),
    "Power_Lines": ("TransmissionLines", "LAYER LIKE 'KV-%'", "LAYER"),
}
ENDPOINTS = {"Source": (40.076955, -111.584886, "Wind farm, mouth of Spanish Fork Canyon"),
             "Destination": (40.460597, -111.935419, "Data center, Bluffdale")}


def utm_box():
    pts = [arcpy.PointGeometry(arcpy.Point(x, y), WGS).projectAs(UTM).firstPoint
           for x in BOX_LL[0::2] for y in BOX_LL[1::2]]
    return (math.floor(min(p.X for p in pts) / CELL) * CELL, math.floor(min(p.Y for p in pts) / CELL) * CELL,
            math.ceil(max(p.X for p in pts) / CELL) * CELL, math.ceil(max(p.Y for p in pts) / CELL) * CELL)


def post(url, params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=300) as r:
        return json.load(r)


def fetch(name, service, where, fields, box):
    url = f"{UGRC}/{service}/FeatureServer/0/query"
    env = json.dumps({"xmin": box[0], "ymin": box[1], "xmax": box[2], "ymax": box[3], "spatialReference": {"wkid": 26912}})
    base = {"where": where, "geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 26912,
            "spatialRel": "esriSpatialRelIntersects", "f": "json"}
    oids = sorted(post(url, dict(base, returnIdsOnly="true")).get("objectIds") or [])
    fcs = []
    for i in range(0, len(oids), 400):
        d = post(url, {"objectIds": ",".join(map(str, oids[i:i + 400])), "outFields": fields,
                       "returnGeometry": "true", "outSR": 26912, "f": "json"})
        p = os.path.join(W, "raw", f"{name}_{i // 400:03d}.json")
        json.dump(d, open(p, "w"))
        fc = f"memory\\{name}_{i // 400}"
        arcpy.conversion.JSONToFeatures(p, fc)
        fcs.append(fc)
    merged = f"memory\\{name}_all"
    arcpy.management.Merge(fcs, merged)
    clip = arcpy.Polygon(arcpy.Array([arcpy.Point(box[0], box[1]), arcpy.Point(box[0], box[3]),
                                      arcpy.Point(box[2], box[3]), arcpy.Point(box[2], box[1])]), UTM)
    arcpy.analysis.Clip(merged, clip, os.path.join(GDB, name))
    return len(oids), int(arcpy.management.GetCount(os.path.join(GDB, name))[0])


def main():
    os.makedirs(os.path.join(W, "raw"), exist_ok=True)
    arcpy.env.overwriteOutput = True
    if not arcpy.Exists(GDB):
        arcpy.management.CreateFileGDB(W, "LCP.gdb")
    box = utm_box()
    info = {"box_utm": box, "cell": CELL}
    dem = os.path.join(W, "dem100.tif")
    if not os.path.exists(dem):
        w, h = int((box[2] - box[0]) / CELL), int((box[3] - box[1]) / CELL)
        p = {"bbox": ",".join(map(str, box)), "bboxSR": 26912, "imageSR": 26912, "size": f"{w},{h}",
             "format": "tiff", "pixelType": "F32", "noData": -9999,
             "interpolation": "RSP_BilinearInterpolation", "f": "image"}
        urllib.request.urlretrieve(DEM_SVC + "?" + urllib.parse.urlencode(p), dem)
        arcpy.management.DefineProjection(dem, UTM)
    r = arcpy.Raster(dem)
    info["dem"] = {"cols": r.width, "rows": r.height, "cell": r.meanCellWidth, "min": r.minimum, "max": r.maximum}
    for name, (svc, where, fields) in LAYERS.items():
        info[name] = fetch(name, svc, where, fields, box)
        print(name, info[name])
    pts = os.path.join(GDB, "Endpoints")
    arcpy.management.CreateFeatureclass(GDB, "Endpoints", "POINT", spatial_reference=UTM)
    arcpy.management.AddField(pts, "Role", "TEXT", field_length=20)
    arcpy.management.AddField(pts, "Label", "TEXT", field_length=60)
    with arcpy.da.InsertCursor(pts, ["SHAPE@", "Role", "Label"]) as cur:
        for role, (lat, lon, label) in ENDPOINTS.items():
            g = arcpy.PointGeometry(arcpy.Point(lon, lat), WGS).projectAs(UTM)
            cur.insertRow([g, role, label])
            info[role] = [g.firstPoint.X, g.firstPoint.Y]
    json.dump(info, open(os.path.join(W, "data_info.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
