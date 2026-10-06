"""Lab 8 example layouts, rendered by ArcGIS Pro (arcpy.mp) from the baseline points that
run_model.py leaves in C:\\Ames\\Lab08\\Check.gdb. Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-08/images/lab08-example-map-baseline.png and -scenario.png.
"""
import importlib.util
import json
import os
import pathlib

import arcpy
from arcpy.sa import ExtractByMask, Hillshade, Idw, RadiusVariable, Raster, Spline

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-08" / "images"
GDB = r"C:\Ames\Lab08\Check.gdb"
APRX = r"C:\Ames\Lab08\Lab08_Figures.aprx"
UTM = arcpy.SpatialReference(26912)
STATES = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_States_Generalized_Boundaries/FeatureServer/0"
CV = json.load(open(HERE / "check_values.json"))
rgb, poly = bf.rgb, bf.poly
bf.GDB, bf.IMG = GDB, IMG
arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = GDB
arcpy.env.overwriteOutput = True
# Height classes (m above the rebuilt plain), the same on both maps; blue for below the plain.
BREAKS = [(0, "Below the plain (< 0 m)", rgb(33, 102, 172)), (50, "0 – 50 m", rgb(255, 255, 204)),
          (100, "50 – 100 m", rgb(255, 237, 160)), (200, "100 – 200 m", rgb(254, 217, 118)),
          (300, "200 – 300 m", rgb(254, 178, 76)), (400, "300 – 400 m", rgb(253, 141, 60)),
          (500, "400 – 500 m", rgb(252, 78, 42)), (600, "500 – 600 m", rgb(227, 26, 28)),
          (750, "600 – 750 m", rgb(177, 0, 38))]


def prep():
    dem = Raster("DEM_UTM")
    arcpy.env.snapRaster = dem; arcpy.env.cellSize = dem
    b = ExtractByMask(dem, "Butte_Boundary")
    (b - ExtractByMask(Idw("NB_base", "RASTERVALU", 10, 2, RadiusVariable(12)), "Butte_Boundary")).save("Height_Base")
    (b - ExtractByMask(Spline("NB_base", "RASTERVALU", 10, "REGULARIZED", 0.1, 12), "Butte_Boundary")).save("Height_Spline")
    if not arcpy.Exists("Idaho"):
        lyr = arcpy.management.MakeFeatureLayer(STATES, "id", "STATE_NAME = 'Idaho'")
        arcpy.management.Project(lyr, "Idaho", UTM)
    if not arcpy.Exists("Butte_Point"):
        arcpy.management.FeatureToPoint("Butte_Boundary", "Butte_Point", "INSIDE")
    out = {}
    for r in ("Height_Base", "Height_Spline"):
        a = arcpy.RasterToNumPyArray(Raster(r), nodata_to_value=-9999)
        a = a[a > -9999]
        out[r] = dict(min=round(float(a.min()), 1), max=round(float(a.max()), 1), neg=int((a < 0).sum()),
                      vol=round(float(a.sum()) * 100 / 1e9, 3))
    print(out)
    return out


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    return p


def height_layer(m, ras):
    lyr = m.addDataFromPath(os.path.join(GDB, ras))
    lyr.name = "Height above the rebuilt plain"
    sym = lyr.symbology
    sym.updateColorizer("RasterClassifyColorizer")
    sym.colorizer.classificationMethod = "ManualInterval"
    sym.colorizer.breakCount = len(BREAKS)
    for brk, (ub, label, color) in zip(sym.colorizer.classBreaks, BREAKS):
        brk.upperBound, brk.label, brk.color = ub, label, color
    lyr.symbology = sym
    try:
        d = lyr.getDefinition("V3")
        d.colorizer.minimumBreak = -100.0
        for g in getattr(d.colorizer, "groups", None) or []:
            g.heading = ""
        lyr.setDefinition(d)
    except Exception as ex:
        print("min break:", ex)
    lyr.transparency = 15
    return lyr


def layout(p, ras, title, subtitle, notes, fname):
    m = bf.new_map(p, fname)
    height_layer(m, ras)
    hs = m.addDataFromPath(os.path.join(GDB, "Hillshade")); hs.name = "Hillshade"
    m.moveLayer(m.listLayers()[0], hs, "AFTER")
    bf.poly_layer(m, "Butte_Boundary", "Butte outline (reference)", fill=rgb(0, 0, 0, 0), outline=rgb(20, 20, 20), width=1.6)
    loc = bf.new_map(p, fname + " locator")
    bf.poly_layer(loc, "Idaho", "Idaho", fill=rgb(242, 242, 242), outline=rgb(90, 90, 90), width=1.0)
    bf.point_layer(loc, "Butte_Point", "Big Southern Butte", "Circle 1", rgb(230, 80, 0), 9)
    lyt = p.createLayout(8.5, 11, "INCH", fname)
    p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz in ((title, 10.28, 17), (subtitle, 9.98, 9)):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, "T")
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception:
            pass
    mf = lyt.createMapFrame(poly(0.5, 3.75, 8.0, 9.6), m, "Main")
    e = arcpy.Describe(os.path.join(GDB, "Butte_Boundary")).extent
    cx, cy = (e.XMin + e.XMax) / 2, (e.YMin + e.YMax) / 2
    w = (e.XMax - e.XMin) + 2400; hgt = w * 5.85 / 7.5
    mf.camera.setExtent(arcpy.Extent(cx - w / 2, cy - hgt / 2, cx + w / 2, cy + hgt / 2, spatial_reference=UTM))
    imf = lyt.createMapFrame(poly(0.5, 0.5, 2.7, 3.5), loc, "Locator")
    imf.camera.setExtent(bf.ext_of("Idaho", 20000))
    p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT", "Locator: Big Southern Butte (orange) in Idaho", 7.5, None, "LocCaption")
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(poly(2.9, 1.35, 6.0, 3.55), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    try:
        leg.title = ""
        for it in leg.items:
            if "Hillshade" in it.name:
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustColumnsAndFont"
        d = leg.getDefinition("V3")
        for it in d.items:
            it.showHeading = False
        leg.setDefinition(d)
        if leg.isOverflowing:
            print("legend overflowing")
    except Exception as ex:
        print("legend:", ex)
    lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(6.2, 2.4, 7.6, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "km"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"; sd.division = 1; sd.divisions = 2; sd.subdivisions = 1; sd.divisionsBeforeZero = 0
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale bar:", ex)
    p.createPredefinedGraphicElement(lyt, poly(2.9, 0.5, 8.0, 1.25), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(2.97, 0.53, 7.95, 1.22), "POLYGON", notes[0] + "\n" + " ".join(notes[1:]), 6.5, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print("exported", fname)


if __name__ == "__main__":
    st = prep()
    p = project()
    bf.p_global = p
    b, s = st["Height_Base"], st["Height_Spline"]
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 UTM zone 12N, 10 m cells.",
              "Data: USGS 3DEP 1/3 arc-second DEM, tiles n44w114 and n44w113 (April 2026); reference outline derived from the DEM for CE 414; Idaho boundary from Esri.",
              "Plain rebuilt from 560 random points (seed 1) in a 1,500 m ring around the outline."]
    vb = CV["baseline"]["volume_km3"]; vs = CV["methods"]["Spline"]["volume_km3"]
    layout(p, "Height_Base", f"Big Southern Butte: About {vb:.1f} Cubic Kilometers Above the Plain",
           "Height of the butte above a plain rebuilt by IDW (power 2, 12 points) beneath the reference outline",
           [f"Result: {vb:.3f} cubic km inside the 28.03 sq km outline; tallest cell {b['max']:.0f} m above the plain; mean height 183.5 m."] + common,
           "lab08-example-map-baseline.png")
    layout(p, "Height_Spline", f"Big Southern Butte by Spline: About {vs:.1f} Cubic Kilometers",
           "Changed: the plain rebuilt by a regularized spline (weight 0.1, 12 points) instead of IDW; same points, same outline",
           [f"Result: the volume falls from {vb:.3f} to {vs:.3f} cubic km, and {s['neg']:,} cells (blue) sit below the plain the spline drew. "
            "Chosen because the spline bulges up under the butte, where it has no points to hold it down."] + common,
           "lab08-example-map-scenario.png")
    p.save()
