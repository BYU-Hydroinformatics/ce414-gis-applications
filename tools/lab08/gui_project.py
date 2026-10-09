"""Set up C:\\Ames\\Lab09GUI for the Lab 8 GUI build, as a student would after Step 0 items 1-2:
the student zip unzipped, a project Lab08.aprx with a project geodatabase and toolbox, and a map
holding the DEM, Study_Area and an imagery basemap. ModelBuilder work is done in the GUI.
ArcGIS Pro Python."""
import json
import os
import shutil
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab08-y-mountain.zip")
ROOT = r"C:\Ames\Lab09GUI"
BLANK = r"C:\Ames\Lab01\_probe.aprx"

if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
zipfile.ZipFile(ZIP).extractall(ROOT)
data = os.path.join(ROOT, "lab08-y-mountain")
arcpy.management.CreateFileGDB(ROOT, "Lab08.gdb")
# an empty .atbx (a zip holding toolbox.content), the same layout ArcGIS Pro writes
with zipfile.ZipFile(os.path.join(ROOT, "Lab08.atbx"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("toolbox.content", json.dumps({"version": "1.0", "alias": "Lab08", "displayname": "$rc:title",
                                              "toolsets": {}}, indent=4))
    z.writestr("toolbox.content.rc", json.dumps({"map": {"title": "Lab08"}}, indent=4))
p = arcpy.mp.ArcGISProject(BLANK)
p.saveACopy(os.path.join(ROOT, "Lab08.aprx"))
p = arcpy.mp.ArcGISProject(os.path.join(ROOT, "Lab08.aprx"))
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
p.defaultGeodatabase = os.path.join(ROOT, "Lab08.gdb")
p.defaultToolbox = os.path.join(ROOT, "Lab08.atbx")
m = p.createMap("Map", "MAP")
for l in m.listLayers():
    m.removeLayer(l)
m.addBasemap("Imagery")
m.addDataFromPath(os.path.join(data, "YMountain_DEM.tif"))
bb = m.addDataFromPath(os.path.join(data, "Lab08.gdb", "Study_Area"))
sym = bb.symbology
sym.renderer.symbol.color = {"RGB": [0, 0, 0, 0]}
sym.renderer.symbol.outlineColor = {"RGB": [255, 40, 40, 100]}
sym.renderer.symbol.outlineWidth = 2
bb.symbology = sym
p.updateFolderConnections([{"connectionString": ROOT, "alias": "", "isHomeFolder": True}])
p.save()
print("ok", p.defaultGeodatabase, p.defaultToolbox, [l.name for l in m.listLayers()])
