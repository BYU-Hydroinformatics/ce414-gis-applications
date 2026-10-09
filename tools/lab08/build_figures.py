"""Lab 8 example layouts, rendered by ArcGIS Pro (arcpy.mp) from run_model.py / tool_checks.py
outputs in C:\\Ames\\Lab07\\Check.gdb. Reuses the Lab 5 layout helpers.

    python build_figures.py
Writes docs/assignments/lab-08/images/lab08-example-map-baseline.png and -scenario.png.
"""
import importlib.util
import json
import os
import pathlib

import arcpy

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bf", HERE.parent / "lab05" / "build_figures.py")
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-08" / "images"
GDB = r"C:\Ames\Lab07\Check.gdb"
APRX = r"C:\Ames\Lab07\Lab08_Figures.aprx"
UTM = arcpy.SpatialReference(26912)
COUNTY_URL = "https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahCountyBoundaries/FeatureServer/0"
CHECKS = json.load(open(HERE / "student_route_checks.json"))
rgb, poly = bf.rgb, bf.poly
bf.GDB, bf.IMG = GDB, IMG
arcpy.env.workspace = GDB
arcpy.env.overwriteOutput = True
# North American Public Avalanche Danger Scale colors: Low green, Moderate yellow, Considerable
# orange, High red, Extreme black.
DANGER = {1: ("Low", rgb(80, 184, 72)), 2: ("Moderate", rgb(255, 242, 0)), 3: ("Considerable", rgb(247, 148, 30)),
          4: ("High", rgb(237, 28, 36)), 5: ("Extreme", rgb(35, 31, 32))}


def prep():
    if not arcpy.Exists("SaltLake_County"):
        lyr = arcpy.management.MakeFeatureLayer(COUNTY_URL, "slc", "NAME = 'SALT LAKE'")
        arcpy.management.Project(lyr, "SaltLake_County", UTM)
    for name, where in (("Snowbird_UTM", "NAME LIKE 'Snowbird%'"), ("Alta_UTM", "NAME LIKE 'Alta%'")):
        lyr = arcpy.management.MakeFeatureLayer(os.path.join(GDB, "SkiAreas"), name + "_l", where)
        arcpy.management.CopyFeatures(lyr, name)


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(bf.BLANK); p.saveACopy(APRX); p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    return p


def hazard_layer(m, ras, name):
    lyr = m.addDataFromPath(os.path.join(GDB, ras))
    lyr.name = name
    sym = lyr.symbology
    sym.updateColorizer("RasterUniqueValueColorizer")
    sym.colorizer.field = "Value"
    for grp in sym.colorizer.groups:
        for it in grp.items:
            v = int(float(it.values[0]))
            it.label, it.color = DANGER[v]
    lyr.symbology = sym
    try:
        d = lyr.getDefinition("V3")
        for grp in d.colorizer.groups:
            grp.heading = ""
        lyr.setDefinition(d)
    except Exception as ex:
        print("heading:", ex)
    lyr.transparency = 30
    return lyr


def layout(p, ras, title, subtitle, notes, fname):
    m = bf.new_map(p, fname, "Imagery")
    hazard_layer(m, ras, "Terrain hazard class")
    bf.poly_layer(m, "Alta_UTM", "Alta Ski Area boundary", fill=rgb(0, 0, 0, 0), outline=rgb(200, 200, 200), width=1.2)
    bf.poly_layer(m, "Snowbird_UTM", "Snowbird boundary", fill=rgb(0, 0, 0, 0), outline=rgb(0, 255, 255), width=2.4)
    loc = bf.new_map(p, fname + " locator")
    bf.poly_layer(loc, "SaltLake_County", "Salt Lake County", fill=rgb(242, 242, 242), outline=rgb(90, 90, 90), width=1.0)
    bf.poly_layer(loc, "Snowbird_UTM", "Snowbird", fill=rgb(230, 80, 0), outline=rgb(230, 80, 0), width=1.5)
    lyt = p.createLayout(8.5, 11, "INCH", fname)
    p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for txt, y, sz in ((title, 10.28, 17), (subtitle, 9.98, 9)):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", txt, sz, None, "T")
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception:
            pass
    mf = lyt.createMapFrame(poly(0.5, 3.75, 8.0, 9.6), m, "Main")
    e = arcpy.Describe(os.path.join(GDB, "Snowbird_UTM")).extent
    mf.camera.setExtent(arcpy.Extent(e.XMin - 700, e.YMin - 500, e.XMax + 700, e.YMax + 500, spatial_reference=UTM))
    imf = lyt.createMapFrame(poly(0.5, 0.5, 2.7, 3.5), loc, "Locator")
    imf.camera.setExtent(bf.ext_of("SaltLake_County", 3000))
    p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT", "Locator: Snowbird (orange) in Salt Lake County", 7.5, None, "LocCaption")
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(poly(2.9, 1.35, 6.0, 3.55), "LEGEND", mf, style("LEGEND", "Legend 1"), "Legend")
    try:
        leg.title = ""
        for it in leg.items:
            if any(k in it.name for k in ("Imagery", "World", "Reference", "Salt Lake")):
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustColumnsAndFont"
        d = leg.getDefinition("V3")
        d.minFontSize = 6
        leg.setDefinition(d)
        if leg.isOverflowing:
            print("legend overflowing")
    except Exception as ex:
        print("legend:", ex)
    lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(6.2, 2.4, 7.4, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "km"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"; sd.division = 0.5; sd.divisions = 2; sd.subdivisions = 1; sd.divisionsBeforeZero = 0
        sb.setDefinition(sd)
    except Exception as ex:
        print("scale bar:", ex)
    p.createPredefinedGraphicElement(lyt, poly(2.9, 0.5, 8.0, 1.25), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(2.97, 0.53, 7.95, 1.22), "POLYGON", notes[0] + "\n" + " ".join(notes[1:]), 6.5, None, "Notes")
    lyt.exportToPNG(str(IMG / fname), resolution=150)
    print("exported", fname)


if __name__ == "__main__":
    prep()
    p = project()
    g0, g4 = CHECKS["Geo_p0"], CHECKS["Geo_p400"]
    hx = lambda c: c.get("4", 0) + c.get("5", 0)
    common = ["Example map, CE 414, October 2026. Projection: NAD 1983 UTM zone 12N, 10 m cells. A classroom screening, not a forecast.",
              "Data: USGS 3DEP 1/3 arc-second DEM, tile n41w112 (May 2026); ski areas and county from UGRC; imagery basemap by Esri.",
              "Ratings: Table 1 (a Sawtooth Avalanche Center advisory), combined by the geometric mean of the three classes."]
    layout(p, "Geo_p0", "Avalanche Terrain at Snowbird: Geometric Mean, Advisory Bands",
           "Elevation, slope and aspect rated with Table 1 and combined by the geometric mean (cube root of the product)",
           [f"Result: of Snowbird's {g0['total']:.1f} sq km, {hx(g0):.1f} sq km rate High or Extreme and {g0['5']:.1f} sq km Extreme."] + common,
           "lab08-example-map-baseline.png")
    layout(p, "Geo_p400", "Avalanche Terrain at Snowbird: Elevation Bands Raised 400 m",
           "Changed: every altitude break in Table 1 raised by 400 m (Shift = 400); slope, aspect and the rule unchanged",
           [f"Result: High or Extreme falls from {hx(g0):.1f} to {hx(g4):.1f} sq km; Extreme from {g0['5']:.1f} to {g4['5']:.2f} sq km. "
            "Chosen to show what a warm spell that pushes the problem up the mountain does to the map."] + common,
           "lab08-example-map-scenario.png")
    p.save()
