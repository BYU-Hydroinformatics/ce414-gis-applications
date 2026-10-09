"""Lab 11: imagery chips around each endpoint area, with the UGRC substations and kV lines drawn
on top, so the endpoints can be placed on real features by eye.   ArcGIS Pro Python."""
import json
import os
import urllib.parse
import urllib.request

import arcpy

OUT = r"C:\Ames\Lab11\probe"
BLANK = r"C:\Ames\Lab01\_probe.aprx"
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"
UTM = arcpy.SpatialReference(26912)
WGS = arcpy.SpatialReference(4326)
CHIPS = {"source": (40.0820, -111.5880, 6000), "destination": (40.4450, -111.9330, 7000)}


def fetch(where, x, y, r, name):
    p = {"where": where, "geometry": f"{x},{y}", "geometryType": "esriGeometryPoint", "inSR": 26912,
         "distance": r, "units": "esriSRUnit_Meter", "spatialRel": "esriSpatialRelIntersects",
         "outFields": "OBJECTID,LAYER", "returnGeometry": "true", "outSR": 26912, "f": "json"}
    with urllib.request.urlopen(f"{UGRC}/TransmissionLines/FeatureServer/0/query", urllib.parse.urlencode(p).encode(), timeout=120) as f:
        d = json.load(f)
    js = os.path.join(OUT, name + ".json"); json.dump(d, open(js, "w"))
    fc = os.path.join(OUT, "probe.gdb", name)
    arcpy.conversion.JSONToFeatures(js, fc)
    return fc


os.makedirs(OUT, exist_ok=True)
arcpy.env.overwriteOutput = True
if not arcpy.Exists(os.path.join(OUT, "probe.gdb")):
    arcpy.management.CreateFileGDB(OUT, "probe.gdb")
aprx = os.path.join(OUT, "chips.aprx")
p = arcpy.mp.ArcGISProject(BLANK); p.saveACopy(aprx); p = arcpy.mp.ArcGISProject(aprx)
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
for name, (lat, lon, half) in CHIPS.items():
    g = arcpy.PointGeometry(arcpy.Point(lon, lat), WGS).projectAs(UTM).firstPoint
    m = p.createMap(name, "MAP")
    for l in m.listLayers():
        m.removeLayer(l)
    m.addBasemap("Imagery Hybrid")
    for kind, where in (("lines", "LAYER LIKE 'KV-%'"), ("subs", "LAYER LIKE 'SUB-%'")):
        lyr = m.addDataFromPath(fetch(where, g.X, g.Y, half * 1.5, f"{name}_{kind}"))
        sym = lyr.symbology
        sym.renderer.symbol.color = {"RGB": [255, 230, 0, 100]} if kind == "lines" else {"RGB": [255, 0, 255, 100]}
        sym.renderer.symbol.size = 1.5 if kind == "lines" else 3
        lyr.symbology = sym
        if kind == "subs":
            lyr.showLabels = True
            lbl = lyr.listLabelClasses()[0]; lbl.expression = "$feature.OBJECTID"
    lay = p.createLayout(8, 8, "INCH", name)
    mf = lay.createMapFrame(arcpy.Polygon(arcpy.Array([arcpy.Point(0, 0), arcpy.Point(0, 8), arcpy.Point(8, 8), arcpy.Point(8, 0)])), m, "f")
    mf.camera.setExtent(arcpy.Extent(g.X - half, g.Y - half, g.X + half, g.Y + half, spatial_reference=UTM))
    lay.exportToJPEG(os.path.join(OUT, f"chip_{name}.jpg"), resolution=150)
    print(name, g.X, g.Y)
p.save()
