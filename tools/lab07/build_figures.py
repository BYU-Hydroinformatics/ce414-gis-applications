"""Lab 7 example layouts, rendered by ArcGIS Pro (arcpy.mp) from the GUI build's outputs.

Inputs: C:\\Ames\\Lab07HAND (tools/lab07/gui_project.py, then the page's Steps 2-6 in the GUI):
Lab07.gdb\\HAND and Lab07.gdb\\Floods (with RETURN_YR and Q_CFS from Step 6's Join Field), and the
downloaded ProvoData.gdb. Working data go to C:\\Ames\\Lab07Fig\\Fig.gdb. Reuses the Lab 5 layout
helpers.

    python build_figures.py

Writes docs/assignments/lab-07/images/lab07-example-map-baseline.png and -design.png, and prints
every number the layouts state, each measured here.
"""
import importlib.util
import os
import pathlib
import shutil

import arcpy
from arcpy.sa import Con, Raster

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-07" / "images"
bf.IMG = IMG
GUI = r"C:\Ames\Lab07HAND"
WORK = os.path.join(GUI, "Lab07.gdb")
DATA = os.path.join(GUI, "lab07-provo-river-hand", "ProvoData.gdb")
OUT = r"C:\Ames\Lab07Fig"
GDB = os.path.join(OUT, "Fig.gdb")
APRX = os.path.join(OUT, "Lab07_Figures.aprx")
UTM = arcpy.SpatialReference(26912)
rgb = bf.rgb

# Example design flood: the page's worked BYU ID ending 89 (Step 7)
DESIGN = {"digits": 89, "q": 1968, "gh": 7.78, "h": 1.396}
# Return period -> fill color, light (rare, large) to dark (frequent, small)
BLUES = {500: (198, 219, 239), 100: (107, 174, 214), 50: (49, 130, 189), 25: (8, 81, 156), 10: (8, 48, 107)}


HALF_W, HALF_H = 450, 330     # close-up window, m (matches the close-up frame's 2.8 x 2.65 in, roughly)


def box(x, y, name):
    e = arcpy.Polygon(arcpy.Array([arcpy.Point(x - HALF_W, y - HALF_H), arcpy.Point(x - HALF_W, y + HALF_H),
                                   arcpy.Point(x + HALF_W, y + HALF_H), arcpy.Point(x + HALF_W, y - HALF_H)]), UTM)
    arcpy.management.CopyFeatures([e], name)
    return arcpy.Extent(x - HALF_W, y - HALF_H, x + HALF_W, y + HALF_H, spatial_reference=UTM)


def prep():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    arcpy.management.CreateFileGDB(OUT, "Fig.gdb")
    arcpy.env.workspace = GDB
    arcpy.env.snapRaster = arcpy.env.extent = arcpy.env.cellSize = os.path.join(GUI, "lab07-provo-river-hand", "Provo_DEM.tif")
    arcpy.management.CopyFeatures(os.path.join(WORK, "Floods"), "Floods")
    for fc in ("Buildings", "FEMA_Floodplain_1pct", "Provo_River", "Gage", "Comparison_Area"):
        arcpy.management.CopyFeatures(os.path.join(DATA, fc), fc)
    nums = {}
    # Buildings reached by the 100-year flood
    lyr = arcpy.management.MakeFeatureLayer("Floods", "f100", "H_CM = 153")
    b = arcpy.management.SelectLayerByLocation("Buildings", "INTERSECT", lyr)
    arcpy.management.CopyFeatures(b, "Buildings_100yr")
    nums["bldg100"] = int(arcpy.management.GetCount("Buildings_100yr")[0])
    # The design flood, as in Step 7
    Con(Raster(os.path.join(WORK, "HAND")) <= DESIGN["h"], 1).save(os.path.join(GDB, "flood_mine"))
    arcpy.conversion.RasterToPolygon("flood_mine", "Design_Flood", "NO_SIMPLIFY", "Value", "MULTIPLE_OUTER_PART")
    nums["design_km2"] = sum(r[0] for r in arcpy.da.SearchCursor("Design_Flood", ["SHAPE@AREA"])) / 1e6
    b = arcpy.management.SelectLayerByLocation("Buildings", "INTERSECT", "Design_Flood")
    arcpy.management.CopyFeatures(b, "Buildings_Mine")
    nums["bldg_mine"] = int(arcpy.management.GetCount("Buildings_Mine")[0])
    # Where they disagree: FEMA's 1% floodplain that HAND's 100-year flood misses, inside the
    # comparison area; the largest single piece sets the close-up.
    arcpy.analysis.PairwiseErase("FEMA_Floodplain_1pct", lyr, "fema_only_m")
    arcpy.analysis.PairwiseClip("fema_only_m", "Comparison_Area", "fema_only_c")
    arcpy.management.MultipartToSinglepart("fema_only_c", "FEMA_Only")
    big = max(arcpy.da.SearchCursor("FEMA_Only", ["SHAPE@AREA", "SHAPE@"]), key=lambda r: r[0])
    c = big[1].centroid
    nums["miss_m2"] = big[0]
    nums["miss_xy"] = (c.X, c.Y)
    g = arcpy.PointGeometry(c, UTM).projectAs(arcpy.SpatialReference(4326))
    nums["miss_ll"] = (g.firstPoint.Y, g.firstPoint.X)
    nums["closeup_ext"] = box(c.X, c.Y, "Closeup_Box")
    # Map 2's close-up: the window holding the most buildings the design flood reaches
    pts = [r[0] for r in arcpy.da.SearchCursor("Buildings_Mine", ["SHAPE@XY"])]
    inside = lambda q, x, y: abs(q[0] - x) <= HALF_W and abs(q[1] - y) <= HALF_H
    bx, by = max(pts, key=lambda q: sum(inside(o, *q) for o in pts))
    nums["design_cluster"] = sum(inside(o, bx, by) for o in pts)
    nums["design_ext"] = box(bx, by, "Closeup_Box2")
    for r in arcpy.da.SearchCursor("Floods", ["RETURN_YR", "Q_CFS", "H_CM", "SHAPE@AREA"], sql_clause=(None, "ORDER BY H_CM")):
        nums[f"flood{r[0]}"] = (r[1], r[2], r[3] / 1e6)
    return nums


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    return p


def add(m, fc, name, query=None):
    lyr = m.addDataFromPath(os.path.join(GDB, fc))
    lyr.name = name
    if query:
        lyr.definitionQuery = query
    return lyr


def fill(m, fc, name, color, outline=None, width=0.0, transparency=0, query=None):
    lyr = add(m, fc, name, query)
    sym = lyr.symbology
    s = sym.renderer.symbol
    s.color = color
    s.outlineColor = outline if outline is not None else color
    s.outlineWidth = width
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def outline(m, fc, name, color, width, dashed=False):
    lyr = fill(m, fc, name, rgb(0, 0, 0, 0), color, width)
    if dashed:
        d = lyr.getDefinition("V3")
        for sl in d.renderer.symbol.symbol.symbolLayers:
            if sl.__class__.__name__ == "CIMSolidStroke":
                eff = arcpy.cim.CreateCIMObjectFromClassName("CIMGeometricEffectDashes", "V3")
                eff.dashTemplate = [5, 3]
                sl.effects = [eff]
        lyr.setDefinition(d)
    return lyr


def line(m, fc, name, color, width):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    sym.renderer.symbol.color = color
    sym.renderer.symbol.size = width
    lyr.symbology = sym
    return lyr


def point(m, fc, name, color, size):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    sym.renderer.symbol.applySymbolFromGallery("Triangle 3")
    sym.renderer.symbol.color = color
    sym.renderer.symbol.size = size
    lyr.symbology = sym
    return lyr


def baseline_layers(m, nums, with_box):
    """Bottom to top: the five floods (500-year first), FEMA outline, all buildings faint, buildings
    the 100-year flood reaches, the river, the gage, and the close-up box."""
    for yr in (500, 100, 50, 25, 10):
        q, hcm, km2 = nums[f"flood{yr}"]
        fill(m, "Floods", f"{yr}-year flood, {q:,} cfs, h = {hcm / 100:.2f} m ({km2:.2f} sq km)",
             rgb(*BLUES[yr]), transparency=15, query=f"RETURN_YR = {yr}")
    outline(m, "FEMA_Floodplain_1pct", "FEMA 1%-annual-chance floodplain (June 2026)", rgb(255, 80, 0), 1.6, dashed=True)
    fill(m, "Buildings", "Other buildings", rgb(200, 200, 200, 70))
    fill(m, "Buildings_100yr", f"Buildings reached by the 100-year flood ({nums['bldg100']})", rgb(255, 230, 0), rgb(120, 60, 0), 0.4)
    line(m, "Provo_River", "Provo River (NHD)", rgb(0, 200, 255), 1.4)
    point(m, "Gage", "USGS gage 10163000", rgb(255, 0, 160), 10)
    if with_box:
        outline(m, "Closeup_Box", "Close-up (lower left)", rgb(255, 255, 255), 2.0)


def design_layers(m, nums, with_box):
    q100, _, _ = nums["flood100"]
    outline(m, "Floods", f"100-year flood, {q100:,} cfs, for comparison", rgb(140, 200, 255), 1.0).definitionQuery = "RETURN_YR = 100"
    fill(m, "Design_Flood", f"Design flood, {DESIGN['q']:,} cfs, h = {DESIGN['h']:.3f} m ({nums['design_km2']:.2f} sq km)",
         rgb(33, 113, 181), transparency=15)
    outline(m, "FEMA_Floodplain_1pct", "FEMA 1%-annual-chance floodplain (June 2026)", rgb(255, 80, 0), 1.6, dashed=True)
    fill(m, "Buildings", "Other buildings", rgb(200, 200, 200, 70))
    fill(m, "Buildings_Mine", f"Buildings reached by the design flood ({nums['bldg_mine']})", rgb(255, 230, 0), rgb(120, 60, 0), 0.4)
    line(m, "Provo_River", "Provo River (NHD)", rgb(0, 200, 255), 1.4)
    point(m, "Gage", "USGS gage 10163000", rgb(255, 0, 160), 10)
    if with_box:
        outline(m, "Closeup_Box2", "Close-up (lower left)", rgb(255, 255, 255), 2.0)


def build(p, lname, layers, nums, title, subtitle, closeup_caption, ext_key, notes, fname):
    m = bf.new_map(p, lname, "Imagery")
    layers(m, nums, True)
    cm = bf.new_map(p, lname + " close-up", "Imagery")
    layers(cm, nums, False)
    lyt = p.createLayout(8.5, 11, "INCH", lname)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz, nm in ((title, 10.28, 17, "Title"), (subtitle, 9.98, 9, "Subtitle")):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, nm)
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception as ex:
            print("anchor:", ex)
    mf = lyt.createMapFrame(bf.poly(0.5, 3.35, 8.0, 9.75), m, "Main")
    e = arcpy.Describe(os.path.join(GDB, "Floods")).extent
    pad = 350
    mf.camera.setExtent(arcpy.Extent(e.XMin - pad, e.YMin - pad, e.XMax + pad, e.YMax + pad, spatial_reference=UTM))
    cf = lyt.createMapFrame(bf.poly(0.5, 0.5, 3.3, 3.15), cm, "Closeup")
    cf.camera.setExtent(nums[ext_key])
    p.createTextElement(lyt, bf.poly(0.5, 3.17, 3.3, 3.33), "POLYGON", closeup_caption, 6.5, None, "CloseupCaption")
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(bf.poly(3.45, 1.4, 8.0, 3.3), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    for it in leg.items:
        if any(k in it.name for k in ("Imagery", "World", "Reference", "Close-up")):
            leg.removeItem(it)
    leg.title = ""
    leg.fittingStrategy = "AdjustColumnsAndFont"
    if leg.isOverflowing:
        print("legend overflowing")
    lyt.createMapSurroundElement(arcpy.Point(7.75, 9.25), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North")
    sb = lyt.createMapSurroundElement(bf.poly(5.6, 3.45, 7.85, 3.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale")
    try:
        sd = sb.getDefinition("V3")
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.unitLabel = "km"; sd.fittingStrategy = "AdjustFrame"; sd.division = 1; sd.divisions = 2
        sd.subdivisions = 1; sd.divisionsBeforeZero = 0; sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale:", ex)
    p.createPredefinedGraphicElement(lyt, bf.poly(3.45, 0.5, 8.0, 1.3), "RECTANGLE", None, "Box")
    p.createTextElement(lyt, bf.poly(3.52, 0.53, 7.95, 1.27), "POLYGON", "\n".join(notes), 6.3, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print(fname)


if __name__ == "__main__":
    nums = prep()
    for k, v in nums.items():
        print(k, v)
    lat, lon = nums["miss_ll"]
    x, y = nums["miss_xy"]
    where = f"{lat:.5f} N, {abs(lon):.5f} W"
    p = project()
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 UTM zone 12N; 5 m cells.",
              "Elevation: USGS 3DEP lidar, read October 2026. Flows and floodplain: FEMA Flood Insurance Study and",
              "NFHL, Utah County, effective June 23, 2026. Gage: USGS 10163000. River, buildings: UGRC. Imagery: Esri, Vantor."]
    build(p, "Baseline", baseline_layers, nums,
          "Provo River Floods, 10- to 500-Year, by HAND",
          "Height Above Nearest Drainage, threshold 2,000 cells; flood depth h from FEMA's flows and the gage's rating",
          "Close-up (white box): FEMA floodplain HAND leaves dry", "closeup_ext",
          [f"Result: {nums['bldg100']} buildings in the 100-year flood ({nums['flood100'][2]:.2f} sq km); "
           f"{nums['flood10'][2]:.2f} sq km at 10 years to {nums['flood500'][2]:.2f} sq km at 500.",
           f"Close-up: {nums['miss_m2'] / 1e4:.1f} ha of FEMA floodplain, centered at {where}, that HAND leaves dry."] + common,
          "lab07-example-map-baseline.png")
    build(p, "Design", design_layers, nums,
          "Provo River at a Design Flow of 1,968 cfs",
          f"Changed: one flood at the example BYU ID ending {DESIGN['digits']} (Q = 900 + 12 x {DESIGN['digits']}), "
          f"gage height {DESIGN['gh']:.2f} ft, h = {DESIGN['h']:.3f} m",
          "Close-up (white box): most buildings reached", "design_ext",
          [f"Result: {nums['bldg_mine']} buildings and {nums['design_km2']:.2f} sq km; between FEMA's 25-year "
           f"({nums['flood25'][0]:,} cfs) and 50-year ({nums['flood50'][0]:,} cfs) flows, so between their maps.",
           f"Close-up: {nums['design_cluster']} of the {nums['bldg_mine']} buildings reached are in this 900 x 660 m window."] + common,
          "lab07-example-map-design.png")
    p.save()
