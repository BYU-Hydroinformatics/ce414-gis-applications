"""Prepare the Week 3 Thursday hands-on outputs from the Lab 2 extract, headlessly, and print the
numbers the speaker notes quote. Writes to C:\\Ames\\Week03\\Week03.gdb so Lab02.gdb stays as the
lab left it.

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools\\week03_prep.py
"""
import os
import arcpy
from arcpy.sa import Float, Con, FocalStatistics, NbrRectangle, ZonalStatisticsAsTable, Raster

arcpy.CheckOutExtension("Spatial")
LAB02 = r"C:\Ames\Lab02"
RED = os.path.join(LAB02, "Data", "UtahCounty_Red_B4_SR_x10000.tif")
NIR = os.path.join(LAB02, "Data", "UtahCounty_NIR_B5_SR_x10000.tif")
if not os.path.exists(RED):
    for root, dirs, files in os.walk(LAB02):
        for f in files:
            if f == "UtahCounty_Red_B4_SR_x10000.tif": RED = os.path.join(root, f)
            if f == "UtahCounty_NIR_B5_SR_x10000.tif": NIR = os.path.join(root, f)
print("bands:", RED, NIR)
TRACTS = r"C:\Ames\Lab01\Lab01.gdb\CensusTracts2020"
OUT = r"C:\Ames\Week03"
GDB = os.path.join(OUT, "Week03.gdb")
os.makedirs(OUT, exist_ok=True)
if not arcpy.Exists(GDB):
    arcpy.management.CreateFileGDB(OUT, "Week03.gdb")
arcpy.env.workspace = GDB
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = RED
arcpy.env.cellSize = RED
arcpy.env.extent = RED

def props(name):
    r = os.path.join(GDB, name)
    d = arcpy.Describe(r)
    mn = arcpy.management.GetRasterProperties(r, "MINIMUM").getOutput(0)
    mx = arcpy.management.GetRasterProperties(r, "MAXIMUM").getOutput(0)
    mean = arcpy.management.GetRasterProperties(r, "MEAN").getOutput(0)
    print(f"{name}: {d.pixelType} min {mn} max {mx} mean {mean}")

# 1. the integer trap: Divide on the raw integer bands, versus the same division after Float
arcpy.sa.Divide(NIR, RED).save("NDVI_intdiv")     # what students get if they skip Float
red_f, nir_f = Float(Raster(RED)), Float(Raster(NIR))
ndvi = (nir_f - red_f) / (nir_f + red_f)
ndvi.save("NDVI")
props("NDVI_intdiv"); props("NDVI")
# value counts of the integer division
arcpy.management.BuildRasterAttributeTable(os.path.join(GDB, "NDVI_intdiv"), "Overwrite")
with arcpy.da.SearchCursor(os.path.join(GDB, "NDVI_intdiv"), ["Value", "Count"]) as cur:
    for row in cur: print("  intdiv value", row[0], "count", row[1])
# the difference (NIR - RED) and the sum on integers, for the prediction figure
diff_int = arcpy.sa.Minus(NIR, RED); diff_int.save("Diff_int")
props("Diff_int")

# 2. threshold sweep with Con(), the Lab 2 Step 6 numbers
total = 0
for t in (0.3, 0.4, 0.5, 0.6, 0.7):
    name = f"NDVI_class_{int(t*10):02d}"
    Con(ndvi >= t, 1, 0).save(name)
    arcpy.management.BuildRasterAttributeTable(os.path.join(GDB, name), "Overwrite")
    counts = {row[0]: row[1] for row in arcpy.da.SearchCursor(os.path.join(GDB, name), ["Value", "Count"])}
    total = sum(counts.values())
    c1 = counts.get(1, 0)
    print(f"threshold {t}: class 1 = {c1:,} cells = {c1*900/2589988:,.0f} sq mi = {100*c1/total:.1f} % (total {total:,})")

# 3. focal statistics on NDVI: 3x3 mean, 5x5 mean, 5x5 majority of the 0.4 class
FocalStatistics(ndvi, NbrRectangle(3, 3, "CELL"), "MEAN").save("NDVI_focal3_mean")
FocalStatistics(ndvi, NbrRectangle(5, 5, "CELL"), "MEAN").save("NDVI_focal5_mean")
FocalStatistics(Raster("NDVI_class_04"), NbrRectangle(5, 5, "CELL"), "MAJORITY").save("Class04_focal5_majority")
FocalStatistics(ndvi, NbrRectangle(3, 3, "CELL"), "RANGE").save("NDVI_focal3_range")
props("NDVI_focal3_mean"); props("NDVI_focal5_mean"); props("NDVI_focal3_range")
arcpy.management.BuildRasterAttributeTable(os.path.join(GDB, "Class04_focal5_majority"), "Overwrite")
counts = {row[0]: row[1] for row in arcpy.da.SearchCursor(os.path.join(GDB, "Class04_focal5_majority"), ["Value", "Count"])}
print("5x5 majority of the 0.4 class:", {k: f"{v:,}" for k, v in counts.items()},
      f"class 1 = {counts.get(1,0)*900/2589988:,.0f} sq mi")

# 4. zonal statistics by census tract
fields = [f.name for f in arcpy.ListFields(TRACTS)]
print("tract fields:", fields)
zone = "GEOID20" if "GEOID20" in fields else ("GEOID" if "GEOID" in fields else fields[2])
ZonalStatisticsAsTable(TRACTS, zone, ndvi, "NDVI_by_tract", "DATA", "ALL")
rows = [r for r in arcpy.da.SearchCursor("NDVI_by_tract", [zone, "COUNT", "MEAN", "MIN", "MAX"])]
rows.sort(key=lambda r: r[2])
print("tracts with data:", len(rows))
print("lowest mean NDVI tracts:", [(r[0], r[1], round(r[2], 3)) for r in rows[:3]])
print("highest mean NDVI tracts:", [(r[0], r[1], round(r[2], 3)) for r in rows[-3:]])
ZonalStatisticsAsTable(TRACTS, zone, Raster("NDVI_class_04"), "Class04_by_tract", "DATA", "MEAN")
rows = [r for r in arcpy.da.SearchCursor("Class04_by_tract", [zone, "COUNT", "MEAN"])]
rows.sort(key=lambda r: r[2])
print("share of tract at/above 0.4, lowest:", [(r[0], round(r[2], 3)) for r in rows[:3]], "highest:", [(r[0], round(r[2], 3)) for r in rows[-3:]])

# a sample 3x3 window of real numbers for the paper exercise, near the Elberta pivots
pt = arcpy.Point(423000, 4428000)   # UTM 12N, near Elberta
try:
    cell = arcpy.management.GetCellValue(os.path.join(GDB, "NDVI"), f"{pt.X} {pt.Y}").getOutput(0)
    print("NDVI at sample point:", cell)
except Exception as e:
    print("sample point", e)
print("done")
