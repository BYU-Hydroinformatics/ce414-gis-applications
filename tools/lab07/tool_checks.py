"""Lab 7 check values measured with the tools the draft page uses (run after run_model.py).

Cell Statistics (MAXIMUM, MINIMUM) on the three class rasters, the geometric-mean expression in
Raster Calculator form, and Tabulate Area of every result inside the Snowbird boundary (UGRC
SkiAreaBoundaries). Writes tools/lab07/tool_checks.json. ArcGIS Pro Python.
"""
import json
import os

import arcpy
from arcpy.sa import CellStatistics, Con, Float, Int, Power, Raster, TabulateArea

HERE = os.path.dirname(os.path.abspath(__file__))
G = r"C:\Ames\Lab07\Check.gdb"
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = G
dem = Raster(os.path.join(G, "DEM_UTM"))
arcpy.env.snapRaster = dem
arcpy.env.cellSize = dem
arcpy.env.extent = dem
snow = arcpy.management.MakeFeatureLayer(os.path.join(G, "SkiAreas"), "snowbird", "NAME LIKE 'Snowbird%'")
out = {}
for tag in ("p0", "m400", "m200", "p200", "p400"):
    alt = os.path.join(G, f"Alt_Class_{tag}")
    if not arcpy.Exists(alt):
        shift = int(tag[1:]) * (1 if tag[0] == "p" else -1)
        d = dem
        Con(d <= 2200 + shift, 1, Con(d <= 2400 + shift, 2, Con(d <= 2600 + shift, 3, Con(d <= 2800 + shift, 4, 5)))).save(alt)
    s, a = os.path.join(G, "Slope_Class"), os.path.join(G, "Aspect_Class")
    geo = Int(Power(Float(Raster(alt) * Raster(s) * Raster(a)), 1.0 / 3.0) + 0.5)
    geo.save(os.path.join(G, f"Geo_{tag}"))
    CellStatistics([alt, s, a], "MAXIMUM").save(os.path.join(G, f"Max_{tag}"))
    CellStatistics([alt, s, a], "MINIMUM").save(os.path.join(G, f"Min_{tag}"))
    res = {}
    for kind in ("Geo", "Max", "Min") + (("Agree",) if arcpy.Exists(os.path.join(G, f"Agree_{tag}")) else ()):
        tbl = os.path.join(G, f"TA_{kind}_{tag}")
        TabulateArea(snow, "NAME", os.path.join(G, f"{kind}_{tag}"), "Value", tbl, 10)
        flds = [f.name for f in arcpy.ListFields(tbl) if f.name.startswith("VALUE_")]
        with arcpy.da.SearchCursor(tbl, flds) as cur:
            row = next(cur)
        res[kind] = {f.split("_")[1]: round(v / 1e6, 3) for f, v in zip(flds, row)}
    out[tag] = res
    print(tag, res, flush=True)
json.dump(out, open(os.path.join(HERE, "tool_checks.json"), "w"), indent=1)
