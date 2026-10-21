# Render the Week 11 registration figure from C:\Ames\Week11\Week11.aprx (built by
# tools/week11_arcgis_project.py): BYU drawn from its NAD 1983 coordinates (blue) and from its NAD 1927
# coordinates stored as if they were NAD 1983 (red), over the Topographic basemap, by a layout map frame
# export. Writes slides/week-11/images/crs-registration-byu.png. Run with the ArcGIS Pro Python while
# ArcGIS Pro does not have the project open; the project itself is not saved.
import json, os
import arcpy

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "slides", "week-11", "images", "crs-registration-byu.png")
aprx = arcpy.mp.ArcGISProject(r"C:\Ames\Week11\Week11.aprx")
m = aprx.listMaps("Registration")[0]
for l in m.listLayers():
    if l.name == "Campuses_NAD27": l.visible = False
    if l.name == "Campuses_NAD83":
        for lc in l.listLabelClasses(): lc.expression = '"right: NAD 1983 coordinates"'
    if l.name == "Campuses_DefinedWrong":
        for lc in l.listLabelClasses(): lc.expression = '"wrong: NAD 1927 numbers read as NAD 1983"'
lay = aprx.createLayout(8, 5.6, "INCH", "Registration")
mf = lay.createMapFrame(arcpy.Extent(0.05, 0.05, 7.95, 5.55), m, "Frame")
utm = arcpy.SpatialReference(26912)
byu = arcpy.PointGeometry(arcpy.Point(-111.6493, 40.2518), arcpy.SpatialReference(4269)).projectAs(utm).firstPoint
w, h = 520, 520 * 5.5 / 7.9
mf.camera.setExtent(arcpy.Extent(byu.X - w / 2 + 30, byu.Y - h / 2, byu.X + w / 2 + 30, byu.Y + h / 2, spatial_reference=utm))
lay.exportToPNG(OUT, resolution=200)
print(OUT, "scale 1:%d" % mf.camera.scale)
