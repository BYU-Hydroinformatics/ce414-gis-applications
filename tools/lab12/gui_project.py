"""Set up C:\\Ames\\Lab12GUI for the Lab 12 GUI build, as a student would after Step 0's first items:
the student zip unzipped, a project Lab12.aprx with its project geodatabase and toolbox, and a map
holding Fire_Stations, Census_Blocks, the network dataset and the county boundary (read live from
UGRC into Lab12.gdb\\Utah_County, as the student downloads it), with an imagery basemap. ModelBuilder
work is done in the GUI.   ArcGIS Pro Python."""
import json
import os
import shutil
import urllib.parse
import urllib.request
import zipfile

import arcpy

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "..", "..", "docs", "data", "lab12-fire-response.zip")
ROOT = r"C:\Ames\Lab12GUI"
BLANK = r"C:\Ames\Lab01\_probe.aprx"
UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services"

if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)
zipfile.ZipFile(ZIP).extractall(ROOT)
data = os.path.join(ROOT, "lab12-fire-response")
gdb = os.path.join(data, "FireResponse.gdb")
arcpy.management.CreateFileGDB(ROOT, "Lab12.gdb")
with zipfile.ZipFile(os.path.join(ROOT, "Lab12.atbx"), "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("toolbox.content", json.dumps({"version": "1.0", "alias": "Lab12", "displayname": "$rc:title",
                                              "toolsets": {}}, indent=4))
    z.writestr("toolbox.content.rc", json.dumps({"map": {"title": "Lab12"}}, indent=4))
# the county boundary, as the student's own download would land in the project geodatabase
q = urllib.parse.urlencode({"where": "NAME = 'UTAH'", "outFields": "NAME,FIPS", "returnGeometry": "true", "outSR": 26912, "f": "json"})
with urllib.request.urlopen(f"{UGRC}/UtahCountyBoundaries/FeatureServer/0/query", q.encode(), timeout=120) as r:
    jp = os.path.join(ROOT, "county.json"); open(jp, "w").write(r.read().decode())
arcpy.conversion.JSONToFeatures(jp, os.path.join(ROOT, "Lab12.gdb", "Utah_County"))
os.remove(jp)
p = arcpy.mp.ArcGISProject(BLANK)
p.saveACopy(os.path.join(ROOT, "Lab12.aprx"))
p = arcpy.mp.ArcGISProject(os.path.join(ROOT, "Lab12.aprx"))
for x in p.listLayouts() + p.listMaps():
    p.deleteItem(x)
p.defaultGeodatabase = os.path.join(ROOT, "Lab12.gdb")
p.defaultToolbox = os.path.join(ROOT, "Lab12.atbx")
m = p.createMap("Map", "MAP")
for l in m.listLayers():
    m.removeLayer(l)
m.addBasemap("Imagery")
m.addDataFromPath(os.path.join(ROOT, "Lab12.gdb", "Utah_County"))
m.addDataFromPath(os.path.join(gdb, "Census_Blocks"))
m.addDataFromPath(os.path.join(gdb, "Network", "Utah_County_Roads_ND"))
m.addDataFromPath(os.path.join(gdb, "Fire_Stations"))
p.updateFolderConnections([{"connectionString": ROOT, "alias": "", "isHomeFolder": True}])
p.save()
print("ok", p.defaultGeodatabase, p.defaultToolbox, [l.name for l in m.listLayers()])
