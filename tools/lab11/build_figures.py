r"""Lab 11 example layouts, rendered by ArcGIS Pro (arcpy.mp) from run_model.py's reference outputs in
C:\Ames\Lab11\ref\Ref.gdb (run run_model.py first). Map 1 is the baseline route with the cost surface
as an inset ("virtual terrain"); Map 2 adds the page's example personal run (BYU ID ending 89,
Line_Weight 1.09) and the Line_Weight 0 run. Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-11/images/lab11-example-map-baseline.png and -scenario.png, and prints
every number the layouts state.   ArcGIS Pro Python.
"""
import importlib.util
import math
import os
import pathlib

import arcpy

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
spec = importlib.util.spec_from_file_location("rm", HERE / "run_model.py")
rm = importlib.util.module_from_spec(spec); spec.loader.exec_module(rm)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-11" / "images"
bf.IMG = IMG
G = rm.G
SRC = rm.SRC
APRX = r"C:\Ames\Lab11\Lab11_Figures.aprx"
FIG = r"C:\Ames\Lab11\fig.gdb"   # the figure's own data, so it never writes into Ref.gdb
UTM = arcpy.SpatialReference(26912)
rgb = bf.rgb
DIGITS = 89
LW = round(0.005 * DIGITS, 3)


def length_km(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(os.path.join(G, fc), ["SHAPE@LENGTH"])) / 1000


def prep():
    rm.setup()
    arcpy.env.workspace = os.path.join(r"C:\Ames\Lab11", "fig.gdb")
    if not arcpy.Exists(arcpy.env.workspace):
        arcpy.management.CreateFileGDB(r"C:\Ames\Lab11", "fig.gdb")
    tag = f"p{DIGITS:02d}"   # written by run_model.py personal; Map 2 waits for it
    ep = os.path.join(SRC, "Endpoints")
    xy = {r[0]: r[1] for r in arcpy.da.SearchCursor(ep, ["Role", "SHAPE@XY"])}
    arcpy.management.CreateFeatureclass(FIG, "Straight_Line", "POLYLINE", spatial_reference=UTM)
    with arcpy.da.InsertCursor(os.path.join(FIG, "Straight_Line"), ["SHAPE@"]) as cur:
        cur.insertRow([arcpy.Polyline(arcpy.Array([arcpy.Point(*xy["Source"]), arcpy.Point(*xy["Destination"])]), UTM)])
    mine = length_km(f"Route_{tag}") if arcpy.Exists(os.path.join(G, f"Route_{tag}")) else None
    return {"base": length_km("Route_base"), "mine": mine, "l0": length_km("Route_line0"),
            "straight": math.dist(xy["Source"], xy["Destination"]) / 1000, "tag": tag}


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    bf.p_global = p
    return p


def add(m, path, name):
    lyr = m.addDataFromPath(path); lyr.name = name
    return lyr


def line(m, path, name, color, width, dashed=False):
    lyr = add(m, path, name)
    sym = lyr.symbology; sym.renderer.symbol.color = color; sym.renderer.symbol.size = width; lyr.symbology = sym
    if dashed:
        d = lyr.getDefinition("V3")
        for sl in d.renderer.symbol.symbol.symbolLayers:
            if sl.__class__.__name__ == "CIMSolidStroke":
                eff = arcpy.cim.CreateCIMObjectFromClassName("CIMGeometricEffectDashes", "V3")
                eff.dashTemplate = [6, 3]; sl.effects = [eff]
        lyr.setDefinition(d)
    return lyr


def poly(m, path, name, fill, outline, width, transparency=0):
    lyr = add(m, path, name)
    sym = lyr.symbology; s = sym.renderer.symbol
    s.color = fill; s.outlineColor = outline; s.outlineWidth = width
    lyr.symbology = sym; lyr.transparency = transparency
    return lyr


def endpoints(m):
    lyr = add(m, os.path.join(SRC, "Endpoints"), "Substations: source (Spanish Fork Canyon) and destination (Bluffdale)")
    sym = lyr.symbology; s = sym.renderer.symbol
    s.applySymbolFromGallery("Square 3"); s.color = rgb(255, 0, 0); s.size = 11; lyr.symbology = sym
    return lyr


def base_layers(m):
    poly(m, os.path.join(SRC, "Cities"), "City limits", rgb(255, 255, 255, 0), rgb(255, 190, 120), 0.8)
    poly(m, os.path.join(G, "Major_Lakes"), "Lakes and marshes over 1 sq km (barrier)", rgb(70, 110, 200, 60), rgb(200, 220, 255), 0.8)
    line(m, os.path.join(G, "Major_Roads"), "Major roads", rgb(200, 200, 200), 0.8)
    line(m, os.path.join(G, "Existing_Lines"), "Existing transmission lines (46-345 kV)", rgb(255, 230, 0), 1.0)
    line(m, os.path.join(FIG, "Straight_Line"), "Straight line between the substations", rgb(225, 225, 225), 1.4, dashed=True)


def layout(p, lname, m, title, subtitle, notes, fname, inset=None, inset_caption=None):
    lyt = p.createLayout(8.5, 11, "INCH", lname)
    p.createPredefinedGraphicElement(lyt, bf.poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz, nm in ((title, 10.28, 17, "Title"), (subtitle, 9.98, 9, "Subtitle")):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, nm)
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception as ex:
            print("anchor:", ex)
    mf = lyt.createMapFrame(bf.poly(0.5, 3.35, 8.0, 9.75), m, "Main")
    ext = arcpy.Describe(os.path.join(FIG, "Straight_Line")).extent
    pad = 6000
    mf.camera.setExtent(arcpy.Extent(ext.XMin - pad, ext.YMin - pad, ext.XMax + pad, ext.YMax + pad, spatial_reference=UTM))
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    lx0 = 0.5
    if inset is not None:
        imf = lyt.createMapFrame(bf.poly(0.5, 0.5, 3.0, 3.15), inset, "Inset")
        imf.camera.setExtent(mf.camera.getExtent())
        p.createTextElement(lyt, bf.poly(0.5, 3.17, 3.3, 3.33), "POLYGON", inset_caption, 6.5, None, "InsetCaption")
        lx0 = 3.15
    leg = lyt.createMapSurroundElement(bf.poly(lx0, 1.4, 8.0, 3.3), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    for it in leg.items:
        if any(k in it.name for k in ("Imagery", "World", "Reference")):
            leg.removeItem(it)
    leg.title = ""; leg.fittingStrategy = "AdjustColumnsAndFont"
    if leg.isOverflowing:
        print("legend overflowing")
    lyt.createMapSurroundElement(arcpy.Point(7.75, 9.25), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North")
    sb = lyt.createMapSurroundElement(bf.poly(0.65, 3.5, 2.9, 3.85), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale")
    try:
        sd = sb.getDefinition("V3")
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.unitLabel = "km"; sd.fittingStrategy = "AdjustFrame"; sd.division = 5; sd.divisions = 2
        sd.subdivisions = 1; sd.divisionsBeforeZero = 0; sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale:", ex)
    p.createPredefinedGraphicElement(lyt, bf.poly(lx0, 0.5, 8.0, 1.3), "RECTANGLE", None, "Box")
    p.createTextElement(lyt, bf.poly(lx0 + 0.07, 0.53, 7.95, 1.27), "POLYGON", "\n".join(notes), 6.3, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print(fname)


def main():
    n = prep()
    for k, v in n.items():
        print(k, v)
    p = project()
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 UTM zone 12N; 30 m cells.",
              "Elevation: USGS 3DEP. Roads, lakes, streams, city limits, transmission lines and substations:",
              "Utah Geospatial Resource Center, read October 2026. Imagery: Esri, Earthstar Geographics."]
    m = bf.new_map(p, "Baseline", "Imagery")
    base_layers(m)
    line(m, os.path.join(G, "Route_base"), f"Least-cost route, weights 1 and 1 ({n['base']:.2f} km)", rgb(255, 40, 40), 3.0)
    endpoints(m)
    inset = bf.new_map(p, "Cost surface")
    cs = add(inset, os.path.join(G, "Cost_base"), "Cost surface")
    sym = cs.symbology
    sym.updateColorizer("RasterStretchColorizer")
    try:
        sym.colorizer.colorRamp = p.listColorRamps("Magma")[0]
    except Exception as ex:
        print("ramp:", ex)
    cs.symbology = sym
    line(inset, os.path.join(G, "Route_base"), "Route", rgb(0, 255, 255), 1.5)
    layout(p, "Baseline", m,
           "A Least-Cost Route for a Power Line, Spanish Fork Canyon to Bluffdale",
           "Cost = slope + roads + cities + existing lines (each scored 1 to 10, weights 1) + 10 per river cell; lakes are barriers",
           [f"Result: {n['base']:.2f} km against {n['straight']:.2f} km in a straight line; nearly all of it beside existing lines."] + common,
           "lab11-example-map-baseline.png", inset, "Inset: the cost surface (dark = cheap) and the route")
    if n["mine"] is None:
        print("Route_" + n["tag"] + " not there yet: Map 2 skipped")
        p.save()
        return
    m2 = bf.new_map(p, "Scenario", "Imagery")
    base_layers(m2)
    line(m2, os.path.join(G, "Route_base"), f"Baseline, Line_Weight 1 ({n['base']:.2f} km)", rgb(255, 40, 40), 2.2)
    line(m2, os.path.join(G, f"Route_{n['tag']}"), f"Example personal run, Line_Weight {LW:.3f} ({n['mine']:.2f} km)", rgb(0, 230, 255), 2.2)
    line(m2, os.path.join(G, "Route_line0"), f"Line_Weight 0: no reward for existing lines ({n['l0']:.2f} km)", rgb(200, 90, 255), 2.2)
    endpoints(m2)
    layout(p, "Scenario", m2,
           "What Moves the Route? Three Line Weights",
           f"Changed: the weight on the existing-line score; slope weight 1 throughout. Example BYU ID ending {DIGITS}: Line_Weight {LW:.3f}",
           [f"Result: at Line_Weight 0 the route leaves the existing lines and runs {n['l0']:.2f} km; at {LW:.3f} it moves partway."] + common,
           "lab11-example-map-scenario.png")
    p.save()


if __name__ == "__main__":
    main()
