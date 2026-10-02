"""Lab 6 example layouts and check map, rendered by ArcGIS Pro (arcpy.mp) from tools/lab06/run_model.py
outputs in C:\\Ames\\Lab06\\Check.gdb. Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-06/images/lab06-example-map-baseline.png, -scenario.png, and
lab06-check-wahweap.jpg.
"""
import importlib.util
import os
import pathlib

import arcpy

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-06" / "images"
IMG.mkdir(parents=True, exist_ok=True)
bf.IMG = IMG
GDB = r"C:\Ames\Lab06\Check.gdb"
SEED = r"C:\Ames\Lab06Pkg\CE414_Lab06_Package\data\student\main_pool_seed.shp"
APRX = r"C:\Ames\Lab06\Lab06_Figures.aprx"
SR = arcpy.SpatialReference(6341)
rgb = bf.rgb


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    return p


def shore_layer(m, fc, name):
    """Nested shorelines: sorted so the highest level draws first and the lowest last (on top),
    in five classes from light (high) to dark (low, deep water)."""
    src = os.path.join(GDB, fc)
    srt = os.path.join(GDB, fc + "_drawsort")
    arcpy.management.Sort(src, srt, [["Elevation", "DESCENDING"]])
    lyr = m.addDataFromPath(srt); lyr.name = name
    vals = sorted({r[0] for r in arcpy.da.SearchCursor(srt, ["Elevation"])})
    lo, hi = vals[0], vals[-1]
    n = 5
    edges = [lo + (hi - lo) * k / n for k in range(n + 1)]
    sym = lyr.symbology
    sym.updateRenderer("GraduatedColorsRenderer")
    sym.renderer.classificationField = "Elevation"
    sym.renderer.breakCount = n
    blues = [(8, 48, 107), (8, 81, 156), (33, 113, 181), (66, 146, 198), (158, 202, 225)]
    for k, brk in enumerate(sym.renderer.classBreaks):
        brk.upperBound = edges[k + 1]
        a_ = edges[k] if k == 0 else edges[k] + 1e-6
        lo_lab = min(v for v in vals if v >= a_)
        hi_lab = max(v for v in vals if v <= edges[k + 1] + 1e-6)
        brk.label = f"{lo_lab:,.0f} to {hi_lab:,.0f} ft" if lo_lab != hi_lab else f"{lo_lab:,.0f} ft"
        brk.symbol.color = rgb(*blues[k])
        brk.symbol.outlineColor = rgb(255, 255, 255, 60)
        brk.symbol.outlineWidth = 0.3
    lyr.symbology = sym
    labs = []
    for k in range(n):
        a_ = edges[k] if k == 0 else edges[k] + 1e-6
        lo_lab = min(v for v in vals if v >= a_)
        hi_lab = max(v for v in vals if v <= edges[k + 1] + 1e-6)
        labs.append(f"{lo_lab:,.0f} to {hi_lab:,.0f} ft")
    d = lyr.getDefinition("V3")
    for brk, lab in zip(d.renderer.breaks, labs):
        brk.label = lab
    d.renderer.heading = ""
    lyr.setDefinition(d)
    return lyr


def layout(p, fc, title, subtitle, notes, fname):
    m = bf.new_map(p, fname, "Imagery")
    shore_layer(m, fc, "Shoreline at water-surface elevation (ft NGVD29)")
    s = m.addDataFromPath(SEED); s.name = "Main-pool seed point"
    sym = s.symbology; sym.renderer.symbol.applySymbolFromGallery("Circle 3"); sym.renderer.symbol.color = rgb(255, 60, 0); sym.renderer.symbol.size = 8; s.symbology = sym
    lyt = p.createLayout(8.5, 11, "INCH", fname)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz in ((title, 10.28, 17), (subtitle, 9.98, 9)):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, "T")
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception:
            pass
    mf = lyt.createMapFrame(bf.poly(0.5, 2.6, 8.0, 9.75), m, "Main")
    e = arcpy.Describe(os.path.join(GDB, fc)).extent
    mf.camera.setExtent(arcpy.Extent(e.XMin - 3000, e.YMin - 3000, e.XMax + 3000, e.YMax + 3000, spatial_reference=SR))
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(bf.poly(0.5, 1.25, 4.8, 2.55), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    for it in leg.items:
        if any(k in it.name for k in ("Imagery", "World", "Reference")):
            leg.removeItem(it)
    leg.fittingStrategy = "AdjustColumnsAndFont"
    leg.title = ""
    lyt.createMapSurroundElement(arcpy.Point(7.6, 2.25), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North")
    sb = lyt.createMapSurroundElement(bf.poly(5.0, 2.0, 7.2, 2.4), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale")
    try:
        sd = sb.getDefinition("V3")
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9035
        else:
            sd.units.uwkid = 9035
        sd.unitLabel = "mi"; sd.fittingStrategy = "AdjustFrame"; sd.division = 10; sd.divisions = 2; sd.subdivisions = 1; sd.divisionsBeforeZero = 0
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale:", ex)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.5, 0.5, 8.0, 1.2), "RECTANGLE", None, "Box")
    p.createTextElement(lyt, bf.poly(0.57, 0.53, 7.95, 1.17), "POLYGON", "\n".join(notes), 7, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print(fname)


def wahweap(p):
    m = bf.new_map(p, "Wahweap", "Imagery")
    shore_layer(m, "shorelines_wahweap10m", "Shorelines, 10 m surface")
    e = arcpy.Describe(os.path.join(GDB, "shorelines_wahweap10m")).extent
    bf.export_map(p, m, "lab06-check-wahweap.jpg",
                  arcpy.Extent(e.XMin - 500, e.YMin - 500, e.XMax + 500, e.YMax + 500, spatial_reference=SR), w_in=6.5)


if __name__ == "__main__":
    p = project()
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 (2011) UTM zone 12N.",
              "Elevation: USGS 1 m topobathymetric DEM of Lake Powell, 1947-2018 (Poppenga et al. 2020, lake bed surveyed 2017),",
              "resampled to 30 m and converted from meters NAVD88 to feet NGVD29. Imagery: Esri."]
    layout(p, "shorelines_default", "Lake Powell Shorelines, 3,500 to 3,700 ft by 10 ft",
           "21 shorelines from one looping ModelBuilder model; main pool only (connected to the seed point near the dam)",
           ["Result: 75.6 sq mi at 3,500 ft (just below the Sept 2026 record low of 3,516.6 ft) to 247.4 sq mi at full pool, 3,700 ft."] + common,
           "lab06-example-map-baseline.png")
    layout(p, "shorelines_deadpool", "Lake Powell Shorelines Down to Dead Pool, 3,370 to 3,700 ft",
           "Changed: the low end moved from 3,500 ft to dead pool, 3,370 ft; same 10 ft step (34 shorelines)",
           ["Result: at dead pool the main pool is 28.2 sq mi, about 11% of the lake at full pool. Chosen to show how much of the lake is left at the levels operators plan around."] + common,
           "lab06-example-map-scenario.png")
    wahweap(p)
    p.save()
