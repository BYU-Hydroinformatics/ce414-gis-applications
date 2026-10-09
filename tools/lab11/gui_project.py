"""Set up C:\\Ames\\Lab11GUI for the Lab 11 GUI build, as a student would after Step 0's first items:
the student zip unzipped, a project Lab11.aprx with its project geodatabase and toolbox, and a map
holding Elevation.tif and the PowerLineData.gdb layers, with an imagery basemap. ModelBuilder work
is done in the GUI.   ArcGIS Pro Python."""
import json
import os
import shutil
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab11-power-line.zip")
ROOT = r"C:\Ames\Lab11GUI"
BLANK = r"C:\Ames\Lab01\_probe.aprx"

if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
zipfile.ZipFile(ZIP).extractall(ROOT)
data = os.path.join(ROOT, "lab11-power-line")
arcpy.management.CreateFileGDB(ROOT, "Lab11.gdb")
with zipfile.ZipFile(os.path.join(ROOT, "Lab11.atbx"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("toolbox.content", json.dumps({"version": "1.0", "alias": "Lab11", "displayname": "$rc:title",
                                              "toolsets": {}}, indent=4))
    z.writestr("toolbox.content.rc", json.dumps({"map": {"title": "Lab11"}}, indent=4))
p = arcpy.mp.ArcGISProject(BLANK)
p.saveACopy(os.path.join(ROOT, "Lab11.aprx"))
p = arcpy.mp.ArcGISProject(os.path.join(ROOT, "Lab11.aprx"))
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
p.defaultGeodatabase = os.path.join(ROOT, "Lab11.gdb")
p.defaultToolbox = os.path.join(ROOT, "Lab11.atbx")
m = p.createMap("Map", "MAP")
for l in m.listLayers():
    m.removeLayer(l)
m.addBasemap("Imagery")
gdb = os.path.join(data, "PowerLineData.gdb")
m.addDataFromPath(os.path.join(data, "Elevation.tif"))
for fc in ("Cities", "Lakes", "Streams", "Roads", "Power_Lines", "Endpoints"):
    m.addDataFromPath(os.path.join(gdb, fc))
p.updateFolderConnections([{"connectionString": ROOT, "alias": "", "isHomeFolder": True}])
p.save()
print("ok", p.defaultGeodatabase, p.defaultToolbox, [l.name for l in m.listLayers()])
