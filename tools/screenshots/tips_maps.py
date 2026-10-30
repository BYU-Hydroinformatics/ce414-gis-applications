"""Render the ArcGIS Tips map figures from real data with arcpy (ArcGIS Pro 3.7).

    propy.bat tools\\screenshots\\tips_maps.py OUT_DIR

Each figure is a layout with one or two map frames, exported at 150 dpi as JPEG, so what the
student sees is ArcGIS Pro's own rendering. Data come from D:\\Smith\\Tips (tips_setup.py,
tips_watershed.py); the script makes its own buffers and basins in memory and prints the numbers
the captions quote.

  buffer-2m-vs-2mi.jpg   a 2 m and a 2-mile buffer around the same Walmart (wrong-answer default 1)
  buffer-dissolve.jpg    major-road buffers with No Dissolve vs Dissolve All (default 4)
  snap-tiny-basin.jpg    the basin from an outlet 30 m off the channel at snap 0 vs 50 m (default 6)
"""
import os
import sys

import arcpy
from arcpy.sa import SnapPourPoint, Watershed

OUT = sys.argv[1]
TIPS = r"D:\Smith\Tips"
GDB = os.path.join(TIPS, "Tips.gdb")
WS = os.path.join(TIPS, "Watershed.gdb")
SCR = os.path.join(TIPS, "MapFigs.gdb")
UTM = arcpy.SpatialReference(26912)
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
if not arcpy.Exists(SCR):
    arcpy.management.CreateFileGDB(TIPS, "MapFigs.gdb")

# Work on a copy: Tips.aprx is usually open in ArcGIS Pro during a capture session.
arcpy.mp.ArcGISProject(os.path.join(TIPS, "Tips.aprx")).saveACopy(os.path.join(TIPS, "TipsMaps.aprx"))
aprx = arcpy.mp.ArcGISProject(os.path.join(TIPS, "TipsMaps.aprx"))


def fresh_map(name, basemap="Imagery Hybrid"):
    for m in aprx.listMaps(name):
        aprx.deleteItem(m)
    m = aprx.createMap(name)
    for lyr in m.listLayers():
        try:
            m.removeLayer(lyr)
        except RuntimeError:
            pass
    if basemap:
        m.addBasemap(basemap)
    return m


def style(lyr, fill=None, outline=(0, 0, 0, 100), width=1.5, size=None):
    s = lyr.symbology
    if hasattr(s, "renderer"):
        sym = s.renderer.symbol
        if fill is not None:
            sym.color = {"RGB": list(fill)}
        if outline is not None:
            sym.outlineColor = {"RGB": list(outline)}
            sym.outlineWidth = width
        if size:
            sym.size = size
        lyr.symbology = s


def layout(name, frames, w=10.0, h=5.2, titles=None, gap=0.3):
    """frames: list of (map, extent). Side by side, equal width, with a title over each."""
    for l in aprx.listLayouts(name):
        aprx.deleteItem(l)
    lyt = aprx.createLayout(w, h, "INCH", name)
    n = len(frames)
    fw = (w - gap * (n + 1)) / n
    fh = h - 0.75
    for i, (m, ext) in enumerate(frames):
        x0 = gap + i * (fw + gap)
        box = arcpy.Polygon(arcpy.Array([arcpy.Point(x0, gap), arcpy.Point(x0 + fw, gap),
                                         arcpy.Point(x0 + fw, gap + fh),
                                         arcpy.Point(x0, gap + fh)]))
        mf = lyt.createMapFrame(box, m, f"Frame {i + 1}")
        mf.camera.setExtent(ext)
        if titles:
            t = aprx.createTextElement(lyt, arcpy.Point(x0, h - 0.18), "POINT", titles[i], 14)
            t.elementPositionY = h - 0.12 - t.elementHeight
    return lyt


def export(lyt, fname, dpi=150):
    path = os.path.join(OUT, fname)
    lyt.exportToJPEG(path, resolution=dpi, jpeg_quality=88)
    print("wrote", path)


def ext_around(x, y, half_w, half_h):
    return arcpy.Extent(x - half_w, y - half_h, x + half_w, y + half_h, spatial_reference=UTM)


# 1. A 2 m buffer and a 2-mile buffer around the same store -------------------------------------
store = os.path.join(SCR, "Store")
arcpy.management.CopyFeatures(os.path.join(GDB, "Walmarts_UtahCounty"), store)
oid = [r[0] for r in arcpy.da.SearchCursor(store, ["OID@"])][0]
arcpy.management.MakeFeatureLayer(store, "one_store", f"OBJECTID = {oid}")
arcpy.management.CopyFeatures("one_store", os.path.join(SCR, "OneStore"))
(sx, sy), = [r[0] for r in arcpy.da.SearchCursor(os.path.join(SCR, "OneStore"), ["SHAPE@XY"])]
arcpy.analysis.Buffer(os.path.join(SCR, "OneStore"), os.path.join(SCR, "Buf_2m"), "2 Meters")
arcpy.analysis.Buffer(os.path.join(SCR, "OneStore"), os.path.join(SCR, "Buf_2mi"), "2 Miles")
for f in ("Buf_2m", "Buf_2mi"):
    a = [r[0] for r in arcpy.da.SearchCursor(os.path.join(SCR, f), ["SHAPE@AREA"])][0]
    print(f, "area m2", round(a, 1), "sq mi", round(a / 2589988.11, 6))

m1 = fresh_map("Fig 2mi")
lyr = m1.addDataFromPath(os.path.join(SCR, "Buf_2mi"))
style(lyr, fill=(255, 215, 0, 35), outline=(255, 215, 0, 100), width=2.5)
lyr = m1.addDataFromPath(os.path.join(SCR, "OneStore"))
style(lyr, fill=(0, 112, 255, 100), outline=(255, 255, 255, 100), width=1, size=10)
# The 2 m buffer gets its own map and a tight zoom: a 4 m circle disappears under any symbol
# or under the 2-mile buffer.
m2 = fresh_map("Fig 2m")
lyr = m2.addDataFromPath(os.path.join(SCR, "Buf_2m"))
style(lyr, fill=(255, 0, 0, 45), outline=(255, 0, 0, 100), width=2.5)
lyr = m2.addDataFromPath(os.path.join(SCR, "OneStore"))
style(lyr, fill=(0, 112, 255, 100), outline=(255, 255, 255, 100), width=0.5, size=4)
lyt = layout("Fig 2m", [(m1, ext_around(sx, sy, 4400, 3600)), (m2, ext_around(sx, sy, 15, 12))],
             titles=["2 Statute Miles: the zone you meant",
                     "2 Meters: the red circle, 30 m view"])
export(lyt, "buffer-2m-vs-2mi.jpg")

# 2. Buffer major roads with No Dissolve vs Dissolve All ----------------------------------------
roads = os.path.join(GDB, "MajorRoads_UtahCounty")
cx, cy = 443800, 4455300
clip = os.path.join(SCR, "ClipBox")
arcpy.management.CreateFeatureclass(SCR, "ClipBox", "POLYGON", spatial_reference=UTM)
with arcpy.da.InsertCursor(clip, ["SHAPE@"]) as c:
    e = ext_around(cx, cy, 4200, 3000)
    c.insertRow([e.polygon])
arcpy.analysis.Clip(roads, clip, os.path.join(SCR, "Roads_Provo"))
arcpy.analysis.Buffer(os.path.join(SCR, "Roads_Provo"), os.path.join(SCR, "Buf_NoDissolve"),
                      "250 Meters", dissolve_option="NONE")
arcpy.analysis.Buffer(os.path.join(SCR, "Roads_Provo"), os.path.join(SCR, "Buf_Dissolve"),
                      "250 Meters", dissolve_option="ALL")
for f in ("Roads_Provo", "Buf_NoDissolve", "Buf_Dissolve"):
    print(f, arcpy.management.GetCount(os.path.join(SCR, f))[0])

ma = fresh_map("Fig NoDissolve")
lyr = ma.addDataFromPath(os.path.join(SCR, "Buf_NoDissolve"))
style(lyr, fill=(255, 215, 0, 18), outline=(255, 215, 0, 100), width=1.2)
mb = fresh_map("Fig Dissolve")
lyr = mb.addDataFromPath(os.path.join(SCR, "Buf_Dissolve"))
style(lyr, fill=(255, 215, 0, 30), outline=(255, 215, 0, 100), width=2)
n_none = arcpy.management.GetCount(os.path.join(SCR, "Buf_NoDissolve"))[0]
lyt = layout("Fig Dissolve", [(ma, ext_around(cx, cy, 2600, 2000)),
                              (mb, ext_around(cx, cy, 2600, 2000))],
             titles=[f"No Dissolve: {n_none} overlapping polygons",
                     "Dissolve all: one feature"])
export(lyt, "buffer-dissolve.jpg")

# 3. Snap Pour Point at 0 vs 50 m from an outlet 30 m north of the channel ----------------------
fdir = arcpy.Raster(r"C:\Ames\Lab05GUI\Lab05.gdb\Flow_Directiond8")
acc = arcpy.Raster(os.path.join(WS, "Flow_Accumulation"))
arcpy.env.snapRaster = fdir
arcpy.env.extent = fdir
arcpy.env.cellSize = fdir
(ox, oy), = [r[0] for r in arcpy.da.SearchCursor(os.path.join(WS, "Outlet_Click"), ["SHAPE@XY"])]
ox -= 40  # back to Lab 5's outlet, which tips_watershed.py moved 40 m east
click = os.path.join(SCR, "Click_30mN")
arcpy.management.CreateFeatureclass(SCR, "Click_30mN", "POINT", spatial_reference=UTM)
with arcpy.da.InsertCursor(click, ["SHAPE@XY"]) as c:
    c.insertRow([(ox, oy + 30)])
for d in (0, 50):
    w = Watershed(fdir, SnapPourPoint(click, acc, d))
    poly = os.path.join(SCR, f"Basin_snap{d}")
    arcpy.conversion.RasterToPolygon(w, poly, "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
    a = sum(r[0] for r in arcpy.da.SearchCursor(poly, ["SHAPE@AREA"]))
    print(f"snap {d} m: basin area m2", round(a), "cells", round(a / 100))
arcpy.ClearEnvironment("extent")

m0 = fresh_map("Fig Snap0")
lyr = m0.addDataFromPath(os.path.join(SCR, "Basin_snap0"))
style(lyr, fill=(255, 0, 0, 70), outline=(255, 0, 0, 100), width=2)
lyr = m0.addDataFromPath(click)
style(lyr, fill=(0, 112, 255, 100), outline=(255, 255, 255, 100), width=1, size=10)
m50 = fresh_map("Fig Snap50")
lyr = m50.addDataFromPath(os.path.join(SCR, "Basin_snap50"))
style(lyr, fill=(255, 215, 0, 25), outline=(255, 215, 0, 100), width=2.5)
lyr = m50.addDataFromPath(click)
style(lyr, fill=(0, 112, 255, 100), outline=(255, 255, 255, 100), width=1, size=10)
bext = arcpy.Describe(os.path.join(SCR, "Basin_snap50")).extent
bx, by = (bext.XMin + bext.XMax) / 2, (bext.YMin + bext.YMax) / 2
half = max(bext.width, bext.height) * 0.6
lyt = layout("Fig Snap", [(m0, ext_around(ox, oy, 70, 70)), (m50, ext_around(bx, by, half, half))],
             titles=["Snap distance 0: a basin of one cell",
                     "Snap distance 50 m: the whole canyon"])
export(lyt, "snap-tiny-basin.jpg")

aprx.save()
