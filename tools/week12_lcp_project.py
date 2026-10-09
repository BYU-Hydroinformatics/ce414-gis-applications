r"""ArcGIS Pro project for the Week 12 Thursday deck's tool captures (Distance Accumulation, Optimal
Path As Line): C:\Ames\Week12\LCPDemo.aprx, a map with the hillshade, Lab 11's cost surface
(tools/week12_lcp_figures.py, cost_base), the major roads, and the Source and Destination points as
two layers. Also usable as a live demo in class.   ArcGIS Pro Python."""
import os

import arcpy

W = r"C:\Ames\Week12"
APRX = os.path.join(W, "LCPDemo.aprx")
BLANK = r"C:\Ames\Lab01\_probe.aprx"
WORK = os.path.join(W, "Work.gdb")
SRC = os.path.join(W, "LCP.gdb")

if os.path.exists(APRX):
    os.remove(APRX)
# The demo works in its own geodatabase so an open project never locks week12_lcp_figures.py's rasters.
DEMO = os.path.join(W, "Demo.gdb")
if not arcpy.Exists(DEMO):
    arcpy.management.CreateFileGDB(W, "Demo.gdb")
for n in ("hs", "cost_base"):
    arcpy.management.CopyRaster(os.path.join(WORK, n), os.path.join(DEMO, n))
WORK = DEMO
p = arcpy.mp.ArcGISProject(BLANK)
p.saveACopy(APRX)
p = arcpy.mp.ArcGISProject(APRX)
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
p.defaultGeodatabase = WORK
m = p.createMap("Power Line Route", "MAP")
for l in m.listLayers():
    m.removeLayer(l)
hs = m.addDataFromPath(os.path.join(WORK, "hs")); hs.name = "Hillshade"
c = m.addDataFromPath(os.path.join(WORK, "cost_base")); c.name = "Cost_Surface"; c.transparency = 35
r = m.addDataFromPath(os.path.join(SRC, "Major_Roads")); r.name = "Major_Roads"
for role in ("Destination", "Source"):
    lyr = m.addDataFromPath(os.path.join(SRC, "Endpoints"))
    lyr.name = role
    lyr.definitionQuery = f"Role = '{role}'"
p.updateFolderConnections([{"connectionString": W, "alias": "", "isHomeFolder": True}])
p.save()
print("ok", [l.name for l in m.listLayers()])
