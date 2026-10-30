"""Export a layout of the saved Tips project to PNG (and optionally PDF) from outside ArcGIS Pro.

    propy.bat tools\\screenshots\\tips_export_layout.py LAYOUT OUT.png [DPI] [OUT.pdf]

Used for the map-frame-credits figures: ArcGIS Pro renders the service layer credits in an export
exactly as on the page, and an outside process avoids driving the Python window. Save the project
in ArcGIS Pro first (Ctrl+S); this reads the .aprx on disk.
"""
import sys

import arcpy

name, out = sys.argv[1], sys.argv[2]
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
aprx = arcpy.mp.ArcGISProject(r"D:\Smith\Tips\Tips.aprx")
lyt = aprx.listLayouts(name)[0]
lyt.exportToPNG(out, resolution=dpi)
print("png", out, [(e.name, e.type) for e in lyt.listElements()])
if len(sys.argv) > 4:
    lyt.exportToPDF(sys.argv[4])
    print("pdf", sys.argv[4])
