"""Set up C:\\Ames\\Lab07HAND for the Lab 7 GUI build, as a student would after Step 0 items 1-2:
the student zip unzipped, a project Lab07.aprx with its project geodatabase and toolbox, and a map
holding Provo_DEM.tif and the ProvoData.gdb layers and table, with an imagery basemap. ModelBuilder
work is done in the GUI.   ArcGIS Pro Python."""
import json
import os
import shutil
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab07-provo-river-hand.zip")
ROOT = r"C:\Ames\Lab07HAND"
BLANK = r"C:\Ames\Lab01\_probe.aprx"

if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
zipfile.ZipFile(ZIP).extractall(ROOT)
data = os.path.join(ROOT, "lab07-provo-river-hand")
arcpy.management.CreateFileGDB(ROOT, "Lab07.gdb")
with zipfile.ZipFile(os.path.join(ROOT, "Lab07.atbx"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("toolbox.content", json.dumps({"version": "1.0", "alias": "Lab07", "displayname": "$rc:title",
                                              "toolsets": {}}, indent=4))
    z.writestr("toolbox.content.rc", json.dumps({"map": {"title": "Lab07"}}, indent=4))
p = arcpy.mp.ArcGISProject(BLANK)
p.saveACopy(os.path.join(ROOT, "Lab07.aprx"))
p = arcpy.mp.ArcGISProject(os.path.join(ROOT, "Lab07.aprx"))
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
p.defaultGeodatabase = os.path.join(ROOT, "Lab07.gdb")
p.defaultToolbox = os.path.join(ROOT, "Lab07.atbx")
m = p.createMap("Map", "MAP")
for l in m.listLayers():
    m.removeLayer(l)
m.addBasemap("Imagery")
gdb = os.path.join(data, "ProvoData.gdb")
m.addDataFromPath(os.path.join(data, "Provo_DEM.tif"))
for fc in ("Comparison_Area", "FEMA_Floodplain_1pct", "Buildings", "Provo_River", "Gage"):
    m.addDataFromPath(os.path.join(gdb, fc))
m.addDataFromPath(os.path.join(gdb, "Stage_Table"))
p.updateFolderConnections([{"connectionString": ROOT, "alias": "", "isHomeFolder": True}])
p.save()
print("ok", p.defaultGeodatabase, p.defaultToolbox, [l.name for l in m.listLayers()], [t.name for t in m.listTables()])
