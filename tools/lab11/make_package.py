r"""Lab 11 (Least Cost Path Power Line): build the student data package.

    docs/data/lab11-power-line.zip
      lab11-power-line/
        Elevation.tif          USGS 3DEP elevation, exported at 30 m in NAD 1983 UTM zone 12N
        PowerLineData.gdb/
          Roads                UGRC UtahRoads with a UDOT functional class (DOT_FCLASS not empty)
          Lakes                UGRC UtahLakesNHD (NHD High Resolution waterbodies), all in the box
          Streams              UGRC UtahStreamsNHD (NHD High Resolution flowlines), all in the box
          Cities               UGRC UtahMunicipalBoundaries
          Power_Lines          UGRC TransmissionLines: kV lines and substations
          Endpoints            two existing substations from Power_Lines, Role = Source / Destination
        READ-ME-FIRST.txt

The box is the Week 12 lecture's (tools/week12_lcp_data.py): 39.98-40.55 N, 112.05-111.45 W,
snapped outward to a 30 m grid. Endpoints are the UGRC substation features nearest the original
handout's coordinates (tools/lab11/probe_endpoints.py): OBJECTID 2185 at the mouth of Spanish Fork
Canyon (428 m from the handout's point) and OBJECTID 1350 at Point of the Mountain, Bluffdale
(1,095 m from it).   ArcGIS Pro Python.
"""
import datetime
import json
import math
import os
import shutil
import urllib.parse
import urllib.request
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "..")
W = r"C:\Ames\Lab11\build"
PKG = os.path.join(W, "lab11-power-line")
GDB = os.path.join(PKG, "PowerLineData.gdb")
ZIP = os.path.join(REPO, "docs", "data", "lab11-power-line.zip")
UTM = arcpy.SpatialReference(26912)
WGS = arcpy.SpatialReference(4326)
BOX_LL = (-112.05, 39.98, -111.45, 40.55)
CELL = 30.0
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
DEM_SVC = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"
LAYERS = {
    "Roads": ("UtahRoads", "DOT_FCLASS IS NOT NULL AND DOT_FCLASS <> ''",
              "FULLNAME,DOT_RTNAME,DOT_FCLASS,DOT_SRFTYP,DOT_AADT"),
    "Lakes": ("UtahLakesNHD", "1=1", "GNIS_Name,AreaSqKm,FType_Text,FCode_Text,IsMajor"),
    "Streams": ("UtahStreamsNHD", "1=1", "GNIS_Name,LengthKM,FType_Text,FCode_Text,IsMajor"),
    "Cities": ("UtahMunicipalBoundaries", "1=1", "NAME,COUNTYNBR,POPLASTESTIMATE"),
    "Power_Lines": ("TransmissionLines", "1=1", "LAYER"),
}
ENDPOINT_OIDS = {"Source": 2185, "Destination": 1350}


def utm_box():
    pts = [arcpy.PointGeometry(arcpy.Point(x, y), WGS).projectAs(UTM).firstPoint
           for x in BOX_LL[0::2] for y in BOX_LL[1::2]]
    return (math.floor(min(p.X for p in pts) / CELL) * CELL, math.floor(min(p.Y for p in pts) / CELL) * CELL,
            math.ceil(max(p.X for p in pts) / CELL) * CELL, math.ceil(max(p.Y for p in pts) / CELL) * CELL)


def post(url, params):
    with urllib.request.urlopen(url, urllib.parse.urlencode(params).encode(), timeout=300) as r:
        return json.load(r)


def fetch(name, svc, where, fields, box):
    url = f"{UGRC}/{svc}/FeatureServer/0/query"
    env = json.dumps({"xmin": box[0], "ymin": box[1], "xmax": box[2], "ymax": box[3], "spatialReference": {"wkid": 26912}})
    base = {"where": where, "geometry": env, "geometryType": "esriGeometryEnvelope", "inSR": 26912,
            "spatialRel": "esriSpatialRelIntersects", "f": "json"}
    oids = sorted(post(url, dict(base, returnIdsOnly="true")).get("objectIds") or [])
    fcs = []
    for i in range(0, len(oids), 400):
        d = post(url, {"objectIds": ",".join(map(str, oids[i:i + 400])), "outFields": "OBJECTID," + fields,
                       "returnGeometry": "true", "outSR": 26912, "f": "json"})
        # JSON To Features renumbers the ObjectID; keep UGRC's as its own field
        d["fields"] = [f for f in d["fields"] if f["name"] != "UGRC_OID"] + [{"name": "UGRC_OID", "type": "esriFieldTypeInteger", "alias": "UGRC_OID"}]
        for ft in d["features"]:
            ft["attributes"]["UGRC_OID"] = ft["attributes"]["OBJECTID"]
        p = os.path.join(W, "raw", f"{name}_{i // 400:03d}.json")
        json.dump(d, open(p, "w"))
        fc = f"memory\\{name}_{i // 400}"
        arcpy.conversion.JSONToFeatures(p, fc)
        fcs.append(fc)
    merged = f"memory\\{name}_all"
    arcpy.management.Merge(fcs, merged)
    clip = arcpy.Polygon(arcpy.Array([arcpy.Point(box[0], box[1]), arcpy.Point(box[0], box[3]),
                                      arcpy.Point(box[2], box[3]), arcpy.Point(box[2], box[1])]), UTM)
    out = os.path.join(GDB, name)
    arcpy.analysis.Clip(merged, clip, out)
    # keep the source OBJECTID as UGRC_OID; drop Shape__ fields the service adds
    for f in arcpy.ListFields(out):
        if f.name.lower().startswith("shape__"):
            arcpy.management.DeleteField(out, f.name)
    return len(oids), int(arcpy.management.GetCount(out)[0])


def dem(box):
    out = os.path.join(PKG, "Elevation.tif")
    tiles, step = [], 1000 * CELL
    y = box[1]
    while y < box[3]:
        x = box[0]
        while x < box[2]:
            x2, y2 = min(x + step, box[2]), min(y + step, box[3])
            p = {"bbox": f"{x},{y},{x2},{y2}", "bboxSR": 26912, "imageSR": 26912,
                 "size": f"{int(round((x2 - x) / CELL))},{int(round((y2 - y) / CELL))}", "format": "tiff",
                 "pixelType": "F32", "noData": -9999, "interpolation": "RSP_BilinearInterpolation", "f": "image"}
            t = os.path.join(W, "tiles", f"t_{int(x)}_{int(y)}.tif")
            os.makedirs(os.path.dirname(t), exist_ok=True)
            for _ in range(4):
                try:
                    if not os.path.exists(t):
                        urllib.request.urlretrieve(DEM_SVC + "?" + urllib.parse.urlencode(p), t)
                    break
                except Exception as e:
                    print("retry", t, e)
            arcpy.management.DefineProjection(t, UTM)
            tiles.append(t)
            x = x2
        y = y2
    arcpy.management.MosaicToNewRaster(tiles, W, "dem_mosaic.tif", UTM, "32_BIT_FLOAT", CELL, 1, "FIRST")
    arcpy.management.CopyRaster(os.path.join(W, "dem_mosaic.tif"), out, nodata_value="-9999")
    arcpy.management.CalculateStatistics(out)
    return out


README = """READ ME FIRST: CE 414 Lab 11, Least Cost Path Power Line
=================================================================

Built {date} by tools/lab11/make_package.py in the course repository
(github.com/BYU-Hydroinformatics/ce414-gis-applications). Every layer is clipped to one box:
39.98 to 40.55 N, 112.05 to 111.45 W (NAD 1983 UTM zone 12N: {xmin:.0f} to {xmax:.0f} E,
{ymin:.0f} to {ymax:.0f} N), from the mouth of Spanish Fork Canyon to Bluffdale.

Coordinate system: NAD 1983 UTM zone 12N (EPSG 26912), meters, for every file.

Elevation.tif
  USGS 3D Elevation Program (3DEP), best-available elevation, read from the 3DEP elevation image
  service (elevation.nationalmap.gov, 3DEPElevation/ImageServer) on {date}, exported at 30 m
  cells with bilinear resampling. Meters above NAVD 88. {cols} columns x {rows} rows,
  {zmin:.1f} to {zmax:.1f} m. Public domain (USGS).

PowerLineData.gdb (from the Utah Geospatial Resource Center, UGRC, read {date};
gis.utah.gov; State Geographic Information Database layers, public)
  Roads         UtahRoads (statewide road centerlines), only the segments UDOT gives a functional
                class (DOT_FCLASS not empty). {Roads} features.
  Lakes         UtahLakesNHD (NHD High Resolution waterbodies), every waterbody in the box.
                {Lakes} features.
  Streams       UtahStreamsNHD (NHD High Resolution flowlines), every flowline in the box.
                {Streams} features.
  Cities        UtahMunicipalBoundaries. {Cities} features.
  Power_Lines   TransmissionLines: lines (LAYER KV-46, KV-138, KV-345, by voltage in kV) and
                substations (LAYER SUB-...). {Power_Lines} features.
  Endpoints     Two existing substations copied from the TransmissionLines layer (UGRC OBJECTID
                2185 and 1350), with Role = Source (the mouth of Spanish Fork Canyon) and
                Role = Destination (Point of the Mountain, Bluffdale). Points at the center of
                each substation feature.

Nothing else was done to the data: no field values were changed. Fields were limited to the ones
listed in the lab, plus UGRC_OID (the feature's OBJECTID in the UGRC service).

Credit line for maps: Elevation: USGS 3DEP, 30 m. Roads, water, cities and power lines: Utah
Geospatial Resource Center (UGRC), {month}.
"""


def main():
    arcpy.env.overwriteOutput = True
    if os.path.exists(W):
        shutil.rmtree(W)
    os.makedirs(os.path.join(W, "raw"))
    os.makedirs(PKG)
    arcpy.management.CreateFileGDB(PKG, "PowerLineData.gdb")
    box = utm_box()
    info = {"box_utm": box}
    d = dem(box)
    r = arcpy.Raster(d)
    info["dem"] = {"cols": r.width, "rows": r.height, "min": r.minimum, "max": r.maximum}
    for name, (svc, where, fields) in LAYERS.items():
        info[name] = fetch(name, svc, where, fields, box)
        out = os.path.join(GDB, name)
        print(name, info[name])
    # endpoints: centers of the two substation features
    pl = os.path.join(GDB, "Power_Lines")
    src_field = "UGRC_OID"
    ep = os.path.join(GDB, "Endpoints")
    arcpy.management.CreateFeatureclass(GDB, "Endpoints", "POINT", spatial_reference=UTM)
    arcpy.management.AddField(ep, "Role", "TEXT", field_length=12)
    arcpy.management.AddField(ep, "UGRC_OID", "LONG")
    with arcpy.da.InsertCursor(ep, ["SHAPE@", "Role", "UGRC_OID"]) as cur:
        for role, oid in ENDPOINT_OIDS.items():
            rows = [r for r in arcpy.da.SearchCursor(pl, [src_field, "SHAPE@"]) if r[0] == oid]
            assert rows, (role, oid, src_field)
            c = rows[0][1].centroid
            cur.insertRow([arcpy.PointGeometry(c, UTM), role, oid])
            ll = arcpy.PointGeometry(c, UTM).projectAs(WGS).firstPoint
            info[role] = {"x": c.X, "y": c.Y, "lat": ll.Y, "lon": ll.X, "ugrc_oid": oid}
    today = datetime.date.today()
    open(os.path.join(PKG, "READ-ME-FIRST.txt"), "w", newline="\r\n").write(README.format(
        date=today.isoformat(), month=today.strftime("%B %Y"), xmin=box[0], ymin=box[1], xmax=box[2], ymax=box[3],
        cols=r.width, rows=r.height, zmin=r.minimum, zmax=r.maximum,
        **{k: info[k][1] for k in LAYERS}))
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(PKG):
            for f in files:
                if f.endswith(".lock"):
                    continue
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, W))
    info["zip_bytes"] = os.path.getsize(ZIP)
    json.dump(info, open(os.path.join(HERE, "package_info.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
