# Build the Step 12 scenario output (Walmart exclusion 3 miles) in Lab01.gdb and report
# candidate polygons for the recommended-site marker on the baseline map.
import arcpy
arcpy.env.workspace = r"C:\Ames\Lab01\Lab01.gdb"
arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(26912)  # NAD 1983 UTM zone 12N
SQMI = 2589988.110336

def area(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(fc, ["SHAPE@AREA"])) / SQMI

print("Walmarts_UtahCounty:", arcpy.management.GetCount("Walmarts_UtahCounty")[0])
arcpy.analysis.Buffer("Walmarts_UtahCounty", "Walmart_3mi_Buffer", "3 Miles", dissolve_option="ALL")
arcpy.analysis.Erase("Zones_Density_Roads", "Walmart_3mi_Buffer", "Walmart_Target_Zones_W3mi")
print("Baseline  :", arcpy.management.GetCount("Walmart_Target_Zones")[0], "polys", round(area("Walmart_Target_Zones"), 2), "sq mi")
print("Walmart3mi:", arcpy.management.GetCount("Walmart_Target_Zones_W3mi")[0], "polys", round(area("Walmart_Target_Zones_W3mi"), 2), "sq mi")

print("\nLargest baseline polygons (label point, UTM 12N and lon/lat):")
sr_gcs = arcpy.SpatialReference(4326)
rows = sorted(arcpy.da.SearchCursor("Walmart_Target_Zones", ["OID@", "SHAPE@"]), key=lambda r: -r[1].area)
for oid, shp in rows[:6]:
    lp = shp.labelPoint
    g = arcpy.PointGeometry(lp, shp.spatialReference).projectAs(sr_gcs).firstPoint
    print(f"  OID {oid:3d}  {shp.area/SQMI:5.2f} sq mi  label pt UTM ({lp.X:.0f}, {lp.Y:.0f})  lon/lat ({g.X:.5f}, {g.Y:.5f})")
print("\nScenario polygons (all):")
for oid, shp in sorted(arcpy.da.SearchCursor("Walmart_Target_Zones_W3mi", ["OID@", "SHAPE@"]), key=lambda r: -r[1].area):
    lp = shp.labelPoint
    g = arcpy.PointGeometry(lp, shp.spatialReference).projectAs(sr_gcs).firstPoint
    print(f"  OID {oid:3d}  {shp.area/SQMI:5.2f} sq mi  lon/lat ({g.X:.5f}, {g.Y:.5f})")
print("\nWalmart points:")
for nm, shp in arcpy.da.SearchCursor("Walmarts_UtahCounty", ["NAME" if "NAME" in [f.name for f in arcpy.ListFields("Walmarts_UtahCounty")] else "OID@", "SHAPE@"]):
    g = shp.projectAs(sr_gcs).firstPoint
    print(f"  {nm}: ({g.X:.5f}, {g.Y:.5f})")
print("fields:", [f.name for f in arcpy.ListFields("Walmarts_UtahCounty")])
