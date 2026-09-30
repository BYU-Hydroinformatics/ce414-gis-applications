"""Build the Lab 5 check maps and the two example layouts with arcpy.mp, rendered by ArcGIS Pro.

Run after run_model.py. Makes C:\\Ames\\Lab05\\Lab05_Figures.aprx from a blank project and exports
into docs/assignments/lab-05/images/. Nothing is drawn by hand.

    python build_figures.py            # everything
    python build_figures.py checks     # only the step check maps
    python build_figures.py layouts    # only the two example layouts
"""
import json
import os
import pathlib
import sys

import arcpy
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-05" / "images"
GDB = r"C:\Ames\Lab05\Check.gdb"
BLANK = r"C:\Ames\Lab01\_probe.aprx"
APRX = r"C:\Ames\Lab05\Lab05_Figures.aprx"
UTM = arcpy.SpatialReference(26912)
BASE, SCEN = 5000, 10000
arcpy.env.workspace = GDB
CV = json.loads((HERE / "check_values.json").read_text())


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def prep():
    Hillshade("DEM_UTM", 315, 45).save("Hillshade")
    arcpy.management.CopyFeatures(r"C:\Ames\Lab04\Check.gdb\Utah_County", "Utah_County")   # locator only
    arcpy.conversion.RasterToPoint("Snapped_Outlet", "Snapped_Outlet_Point")
    SetNull(Raster("Flow_Accumulation") < 200, Log10(Raster("Flow_Accumulation"))).save("Log_Accumulation")
    for th in (BASE, SCEN):
        # A NAME-free copy of the NHD split into two display classes
        pass
    if not arcpy.Exists("NHD_Basin_Class"):
        arcpy.management.CopyFeatures("NHD_Basin", "NHD_Basin_Class")
        arcpy.management.AddField("NHD_Basin_Class", "Kind", "TEXT", field_length=40)
        with arcpy.da.UpdateCursor("NHD_Basin_Class", ["FCode", "Kind"]) as cur:
            for fc, _ in cur:
                cur.updateRow([fc, "NHD ephemeral" if fc == 46007 else "NHD perennial or intermittent"])


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(BLANK)
    p.saveACopy(APRX)
    p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    return p


def new_map(p, name, basemap=None):
    m = p.createMap(name, "MAP")
    m.spatialReference = UTM
    for l in m.listLayers():
        m.removeLayer(l)
    if basemap:
        try:
            m.addBasemap(basemap)
        except Exception as e:
            print("basemap failed:", e)
    return m


def add(m, ds, name):
    lyr = m.addDataFromPath(os.path.join(GDB, ds))
    lyr.name = name
    return lyr


def poly_layer(m, fc, name, fill=None, outline=None, width=1.0, transparency=0):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    s = sym.renderer.symbol
    if fill is not None:
        s.color = fill
    if outline is not None:
        s.outlineColor = outline
    s.outlineWidth = width
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def unique_polys(m, fc, name, transparency=45, outline=rgb(255, 255, 255), width=1.2):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["gridcode"]
    try:
        sym.renderer.colorRamp = p_global.listColorRamps("Basic Random")[0]
    except Exception as e:
        print("ramp:", e)
    for grp in sym.renderer.groups:
        for it in grp.items:
            it.symbol.outlineColor = outline
            it.symbol.outlineWidth = width
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def line_layer(m, fc, name, color, width):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    sym.renderer.symbol.color = color
    sym.renderer.symbol.size = width
    lyr.symbology = sym
    return lyr


def nhd_layer(m, name="NHD streams"):
    lyr = add(m, "NHD_Basin_Class", name)
    sym = lyr.symbology
    sym.updateRenderer("UniqueValueRenderer")
    sym.renderer.fields = ["Kind"]
    for grp in sym.renderer.groups:
        for it in grp.items:
            eph = "ephemeral" in it.label
            it.symbol.color = rgb(0, 200, 255) if eph else rgb(0, 90, 255)
            it.symbol.size = 1.6 if eph else 2.6
            if eph:
                try:
                    d = it.symbol  # dash through CIM below
                except Exception:
                    pass
    lyr.symbology = sym
    # dashed ephemeral lines through the CIM
    d = lyr.getDefinition("V3")
    for grp in d.renderer.groups:
        for cls in grp.classes:
            if "ephemeral" in cls.label:
                stroke = cls.symbol.symbol.symbolLayers[0]
                eff = arcpy.cim.CreateCIMObjectFromClassName("CIMGeometricEffectDashes", "V3")
                eff.dashTemplate = [4, 2.5]
                stroke.effects = [eff]
    lyr.setDefinition(d)
    return lyr


def point_layer(m, fc, name, gallery, color, size):
    lyr = add(m, fc, name)
    sym = lyr.symbology
    s = sym.renderer.symbol
    s.applySymbolFromGallery(gallery)
    s.color = color
    s.size = size
    lyr.symbology = sym
    return lyr


def gray_raster(m, ras, name, transparency=0):
    lyr = add(m, ras, name)
    lyr.transparency = transparency
    return lyr


def stretch(m, ras, name, ramp, transparency=0, lo=None, hi=None):
    lyr = add(m, ras, name)
    sym = lyr.symbology
    sym.updateColorizer("RasterStretchColorizer")
    try:
        sym.colorizer.colorRamp = p_global.listColorRamps(ramp)[0]
    except Exception as e:
        print("ramp:", e)
    lyr.symbology = sym
    if lo is not None:
        d = lyr.getDefinition("V3")
        d.colorizer.statsType = "GlobalStats"
        d.colorizer.useCustomStretchMinMax = True
        d.colorizer.customStretchMin = lo
        d.colorizer.customStretchMax = hi
        lyr.setDefinition(d)
    lyr.transparency = transparency
    return lyr


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


def ext_of(fc, pad=600, bottom=0):
    e = arcpy.Describe(os.path.join(GDB, fc)).extent
    return arcpy.Extent(e.XMin - pad, e.YMin - pad - bottom, e.XMax + pad, e.YMax + pad, spatial_reference=UTM)


def export_map(p, m, out, ext, w_in=7.0, dpi=150):
    ratio = ext.height / ext.width
    lay = p.createLayout(w_in, w_in * ratio, "INCH", "Render " + m.name)
    mf = lay.createMapFrame(poly(0, 0, w_in, w_in * ratio), m, "Frame")
    cim = mf.getDefinition("V3")
    if cim.graphicFrame:
        cim.graphicFrame.borderSymbol = None
    mf.setDefinition(cim)
    mf.camera.setExtent(ext)
    lay.exportToJPEG(str(IMG / out), resolution=dpi, jpeg_quality=90)
    print(out, os.path.getsize(IMG / out) // 1000, "KB")


def checks(p):
    dem_ext = arcpy.Describe(os.path.join(GDB, "DEM_UTM")).extent
    full = arcpy.Extent(dem_ext.XMin, dem_ext.YMin, dem_ext.XMax, dem_ext.YMax, spatial_reference=UTM)
    # Step 2: the outlet on imagery at the trailhead
    m = new_map(p, "Outlet", "Imagery Hybrid")
    point_layer(m, "Outlet", "Outlet", "Circle 3", rgb(255, 255, 0), 11)
    point_layer(m, "Snapped_Outlet_Point", "Snapped outlet", "Circle 3", rgb(255, 40, 0), 9)
    x, y = CV["outlet_utm"]
    export_map(p, m, "lab05-check-outlet.jpg", arcpy.Extent(x - 450, y - 280, x + 450, y + 280, spatial_reference=UTM), w_in=6.0)
    # Step 5: flow accumulation over the whole DEM
    m = new_map(p, "Accumulation")
    gray_raster(m, "Hillshade", "Hillshade")
    stretch(m, "Log_Accumulation", "log10(accumulation)", "Blues (Continuous)", 0, 1.0, 4.5)
    point_layer(m, "Outlet", "Outlet", "Circle 3", rgb(255, 60, 0), 9)
    export_map(p, m, "lab05-check-accumulation.jpg", full)
    # Step 7: the basin on imagery
    m = new_map(p, "Basin", "Imagery Hybrid")
    poly_layer(m, "Rock_Canyon_Basin", "Rock Canyon basin", fill=rgb(255, 170, 0, 0), outline=rgb(255, 200, 0), width=2.4)
    point_layer(m, "Snapped_Outlet_Point", "Snapped outlet", "Circle 3", rgb(255, 60, 0), 9)
    export_map(p, m, "lab05-check-basin.jpg", ext_of("Rock_Canyon_Basin", 900))
    # Step 11: baseline streams and subwatersheds
    m = new_map(p, "Baseline")
    gray_raster(m, "Hillshade", "Hillshade")
    unique_polys(m, f"Subwatersheds_{BASE}", "Subwatersheds", 45)
    line_layer(m, f"Streams_{BASE}", "Streams", rgb(0, 60, 200), 1.8)
    poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(0, 0, 0, 0), outline=rgb(30, 30, 30), width=1.6)
    export_map(p, m, "lab05-check-subwatersheds.jpg", ext_of("Rock_Canyon_Basin", 400))
    # Step 13: model streams against the NHD, on imagery
    m = new_map(p, "NHD", "Imagery Hybrid")
    nhd_layer(m)
    line_layer(m, f"Streams_{BASE}", "Model streams, 5,000 cells", rgb(255, 120, 0), 1.8)
    poly_layer(m, "Rock_Canyon_Basin", "Basin", fill=rgb(0, 0, 0, 0), outline=rgb(255, 255, 255), width=1.4)
    export_map(p, m, "lab05-check-nhd.jpg", ext_of("Rock_Canyon_Basin", 400))


def build_layout(p, title, subtitle, th, lname, notes, fname):
    m = new_map(p, lname, "Imagery")
    unique_polys(m, f"Subwatersheds_{th}", "Subwatershed colors", 55, rgb(255, 255, 255), 1.0)
    poly_layer(m, f"Subwatersheds_{th}", "Subwatersheds (one color each)", fill=rgb(0, 0, 0, 0), outline=rgb(235, 235, 235), width=1.0)
    nhd_layer(m)
    line_layer(m, f"Streams_{th}", f"Delineated streams ({th:,} cells)", rgb(255, 120, 0), 2.0)
    poly_layer(m, "Rock_Canyon_Basin", "Rock Canyon basin", fill=rgb(0, 0, 0, 0), outline=rgb(255, 255, 0), width=2.2)
    point_layer(m, "Snapped_Outlet_Point", "Outlet (Rock Canyon trailhead)", "Circle 3", rgb(255, 0, 0), 9)
    loc = new_map(p, lname + " locator")
    poly_layer(loc, "Utah_County", "Utah County", fill=rgb(242, 242, 242), outline=rgb(90, 90, 90), width=1.0)
    poly_layer(loc, "Rock_Canyon_Basin", "Rock Canyon basin", fill=rgb(230, 80, 0), outline=rgb(230, 80, 0), width=1.5)

    lyt = p.createLayout(8.5, 11, "INCH", lname)
    p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    t = p.createTextElement(lyt, arcpy.Point(4.25, 10.28), "POINT", title, 17, None, "Title")
    st = p.createTextElement(lyt, arcpy.Point(4.25, 9.98), "POINT", subtitle, 9, None, "Subtitle")
    for el in (t, st):
        try:
            el.setAnchor("CENTER_POINT"); el.elementPositionX = 4.25
        except Exception as e:
            print("anchor:", e)
    mf = lyt.createMapFrame(poly(0.5, 3.75, 8.0, 9.75), m, "Main")
    e = ext_of("Rock_Canyon_Basin", 350)
    mf.camera.setExtent(e)
    imf = lyt.createMapFrame(poly(0.5, 0.5, 2.7, 3.5), loc, "Locator")
    imf.camera.setExtent(ext_of("Utah_County", 3000))
    p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT", "Locator: Rock Canyon (orange) in Utah County", 7.5, None, "LocCaption")
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(poly(2.9, 1.35, 6.6, 3.55), "LEGEND", mf, style("LEGEND", "Title and Medium Text Legend"), "Legend")
    try:
        leg.title = "Legend"
        for it in leg.items:
            if any(k in it.name for k in ("Imagery", "Hybrid", "Reference", "World", "Subwatershed colors", "Utah County")):
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustColumnsAndFont"
        d = leg.getDefinition("V3")
        d.minFontSize = 5
        leg.setDefinition(d)
        if leg.isOverflowing:
            print("legend still overflowing")
    except Exception as e:
        print("legend:", e)
    lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(6.2, 2.4, 7.4, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "km"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"
        sd.division = 1
        sd.divisions = 2
        sd.subdivisions = 1
        sd.divisionsBeforeZero = 0
        sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as e:
        print("scale bar:", e)
    p.createPredefinedGraphicElement(lyt, poly(2.9, 0.5, 8.0, 1.25), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(2.97, 0.53, 7.95, 1.22), "POLYGON", notes[0] + "\n" + " ".join(notes[1:]), 6.5, None, "Notes")
    out = IMG / fname
    lyt.exportToPNG(str(out), resolution=150)
    print("exported", out)


def layouts(p):
    runs = {r["threshold"]: r for r in CV["runs"]}
    b, s = runs[BASE], runs[SCEN]
    nhd = CV["nhd_basin"]["km"]
    common = ["Map by Dan Ames, CE 414, September 2026. Projection: NAD 1983 UTM zone 12N, 10 m cells.",
              "Data: USGS 3DEP 1/3 arc-second DEM, tile n41w112 (May 2026); Utah Streams NHD (UGRC, 2016);",
              "imagery basemap by Esri. Streams and subwatersheds derived from the DEM with a D8 model."]
    build_layout(p, "Streams and Subwatersheds of Rock Canyon, Provo",
                 f"Baseline: stream threshold {BASE:,} cells (0.5 sq km of contributing area)\n"
                 f"Basin above the Rock Canyon trailhead: {CV['basin']['km2']:.2f} sq km",
                 BASE, "Baseline map",
                 [f"Result: {b['links']} stream segments and {b['subwatersheds']} subwatersheds; {b['stream_km']:.1f} km of stream, against "
                  f"{nhd:.1f} km in the NHD for the same basin, most of it mapped as ephemeral."] + common,
                 "lab05-example-map-baseline.png")
    build_layout(p, "Rock Canyon with a Higher Stream Threshold",
                 f"Changed: threshold raised from {BASE:,} to {SCEN:,} cells (0.5 to 1.0 sq km).\n"
                 "Outlet, DEM and every other setting unchanged from the baseline.",
                 SCEN, "Scenario map",
                 [f"Result: {s['links']} segments and {s['subwatersheds']} subwatersheds (from {b['links']}); {s['stream_km']:.1f} km of stream (from {b['stream_km']:.1f}). "
                  "Chosen to show what doubling the threshold does to a runoff model that needs 20-40 subwatersheds."] + common,
                 "lab05-example-map-scenario.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    prep()
    p_global = p = project()
    if what in ("all", "checks"):
        checks(p)
    if what in ("all", "layouts"):
        layouts(p)
    p.save()
