"""Compare the GUI build's outputs (C:\\Ames\\Lab11GUI\\Lab11.gdb) with check_values.json.
    python check_gui.py [GDB] [suffix]        ArcGIS Pro Python.
With a suffix (for example _Base), the dialog-run outputs Served_Area_Base ... are compared."""
import json
import os
import sys

import arcpy

G = sys.argv[1] if len(sys.argv) > 1 else r"C:\Ames\Lab11GUI\Lab11.gdb"
SUF = sys.argv[2] if len(sys.argv) > 2 else ""
CK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_values.json")))
arcpy.env.workspace = G
print("features", sorted(arcpy.ListFeatureClasses()))
print("tables", sorted(arcpy.ListTables()))
b, c = CK["baseline"], CK["crow_default"]


def n(fc):
    return int(arcpy.management.GetCount(fc)[0])


def km2(fc):
    return round(sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / 1e6, 2)


def stat(tbl):
    return next(arcpy.da.SearchCursor(tbl, ["SUM_PP_TOTAL", "COUNT_GEOID20"]))


ok = True
for name, got, exp in (
    (f"Served_Area{SUF} km2", km2(f"Served_Area{SUF}"), b["area_km2"]),
    (f"Unserved_Blocks{SUF} count", n(f"Unserved_Blocks{SUF}"), b["blocks"]),
    (f"Unserved_Population{SUF} sum", int(stat(f"Unserved_Population{SUF}")[0]), b["population"]),
    (f"Unserved_Population{SUF} count", int(stat(f"Unserved_Population{SUF}")[1]), b["blocks"]),
    (f"Crow_Area{SUF} km2", km2(f"Crow_Area{SUF}"), c["area_km2"]),
    (f"Crow_Unserved{SUF} count", n(f"Crow_Unserved{SUF}"), c["blocks"]),
    (f"Crow_Population{SUF} sum", int(stat(f"Crow_Population{SUF}")[0]), c["population"]),
):
    match = abs(float(got) - float(exp)) < 0.011
    ok &= match
    print(f"{name:34s} {got:>14} expected {exp:>12}  {'OK' if match else 'MISMATCH'}")
print("ALL MATCH" if ok else "SOME MISMATCH")
