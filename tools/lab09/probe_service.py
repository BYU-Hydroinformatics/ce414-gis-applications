"""Probe the USGS 3DEP elevation image service from arcpy: what comes back when ArcGIS Pro adds it."""
import arcpy, json, time
URL = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer"
t = time.time()
out = {}
d = arcpy.Describe(URL)
out["dataType"] = d.dataType
for k in ("children",):
    try: out[k] = [c.name for c in d.children]
    except Exception as e: out[k] = str(e)[:100]
try:
    lyr = arcpy.management.MakeImageServerLayer(URL, "svc").getOutput(0)
    dl = arcpy.Describe(lyr)
    out["lyr_sr"] = dl.spatialReference.name
    out["lyr_cell"] = [dl.meanCellWidth, dl.meanCellHeight]
    out["lyr_type"] = dl.dataType
except Exception as e:
    out["mk_err"] = str(e)[:400]
try:
    r = arcpy.Raster(URL)
    out["raster_sr"] = r.spatialReference.name
    out["raster_cell"] = r.meanCellWidth
    sr = r.spatialReference
    pt = arcpy.PointGeometry(arcpy.Point(-111.6295, 40.2468), arcpy.SpatialReference(4269)).projectAs(sr)
    out["value_at_Y"] = arcpy.management.GetCellValue(URL, f"{pt.firstPoint.X} {pt.firstPoint.Y}").getOutput(0)
except Exception as e:
    out["raster_err"] = str(e)[:400]
out["secs"] = round(time.time() - t, 1)
print(json.dumps(out, indent=1))
