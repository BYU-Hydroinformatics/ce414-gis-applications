"""Build the Lab 4 check maps and the two example layouts with arcpy.mp, rendered by ArcGIS Pro.

Run after run_model.py and scenario.py. Makes C:\\Ames\\Lab04\\Lab04_Figures.aprx from a blank
project, exports into docs/assignments/lab-04/images/. Nothing is drawn by hand.

    python build_figures.py            # everything
    python build_figures.py checks     # only the step check maps
    python build_figures.py layouts    # only the two example layouts
"""
import arcpy, os, sys, json, shutil, pathlib
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
HERE = pathlib.Path(__file__).resolve().parent
IMG = HERE.parents[1] / "docs" / "assignments" / "lab-04" / "images"
GDB = r"C:\Ames\Lab04\Check.gdb"
BLANK = r"C:\Ames\Lab01\_probe.aprx"
APRX = r"C:\Ames\Lab04\Lab04_Figures.aprx"
UTM = arcpy.SpatialReference(26912)
SITE = (418391, 4425403)
arcpy.env.workspace = GDB


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def prep():
    """Display-only derivatives: 1-only rasters and the 20-per-10,000 km2 contour."""
    ExtractByMask(SetNull(Raster("Flat_Enough") != 1, 1), "Utah_County").save("Show_Flat")
    SetNull(Raster("Suitable_Sites") != 1, 1).save("Show_Suitable")
    SetNull(Raster("Suitable_D40") != 1, 1).save("Show_Suitable_D40")
    (Raster("Tower_Density") * 10000).save("Density_per10k")
    ContourList("Density_per10k", "Density_20", [20])
    for fc, xy, name in (("Site", SITE, "Recommended site"),):
        if arcpy.Exists(fc):
            arcpy.management.Delete(fc)
        arcpy.management.CreateFeatureclass(GDB, fc, "POINT", spatial_reference=UTM)
        arcpy.management.AddField(fc, "NAME", "TEXT", field_length=40)
        with arcpy.da.InsertCursor(fc, ["SHAPE@XY", "NAME"]) as c:
            c.insertRow((xy, name))


def project():
    if os.path.exists(APRX):
        os.remove(APRX)
    p = arcpy.mp.ArcGISProject(BLANK)
    p.saveACopy(APRX)
    p = arcpy.mp.ArcGISProject(APRX)
    for x in p.listLayouts() + p.listMaps():
        p.deleteItem(x)
    return p


def new_map(p, name, basemap="Light Gray Canvas"):
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


def vec(m, fc, name, fill=None, outline=None, width=1.0, size=None, gallery=None, transparency=0):
    lyr = m.addDataFromPath(os.path.join(GDB, fc))
    lyr.name = name
    sym = lyr.symbology
    s = sym.renderer.symbol
    if gallery:
        s.applySymbolFromGallery(gallery)
    if fill is not None:
        s.color = fill
    if outline is not None:
        s.outlineColor = outline
    if size is not None:
        s.size = size
    elif width is not None:
        s.outlineWidth = width
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def line(m, fc, name, color, width):
    lyr = m.addDataFromPath(os.path.join(GDB, fc))
    lyr.name = name
    sym = lyr.symbology
    sym.renderer.symbol.color = color
    sym.renderer.symbol.size = width
    lyr.symbology = sym
    return lyr


def single_color_raster(m, ras, name, color, transparency=0):
    lyr = m.addDataFromPath(os.path.join(GDB, ras))
    lyr.name = name
    d = lyr.getDefinition("V3")
    col = arcpy.cim.CreateCIMObjectFromClassName("CIMRasterUniqueValueColorizer", "V3")
    grp = arcpy.cim.CreateCIMObjectFromClassName("CIMRasterUniqueValueGroup", "V3")
    cls = arcpy.cim.CreateCIMObjectFromClassName("CIMRasterUniqueValueClass", "V3")
    cls.values = ["1"]
    cls.label = name
    cls.visible = True
    c = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
    c.values = [color[0], color[1], color[2], 100]
    cls.color = c
    grp.classes = [cls]
    grp.heading = "Value"
    col.groups = [grp]
    col.fieldName = "Value"
    col.resamplingType = "NearestNeighbor"
    d.colorizer = col
    lyr.setDefinition(d)
    lyr.transparency = transparency
    return lyr


def stretch_raster(m, ras, name, lo, hi, transparency=25):
    lyr = m.addDataFromPath(os.path.join(GDB, ras))
    lyr.name = name
    sym = lyr.symbology
    sym.updateColorizer("RasterStretchColorizer")
    sym.colorizer.stretchType = "MinimumMaximum"
    try:
        ramp = p_global.listColorRamps("Yellow to Red")[0]
        sym.colorizer.colorRamp = ramp
    except Exception as e:
        print("ramp:", e)
    sym.colorizer.minLabel, sym.colorizer.maxLabel = f"{lo}", f"{hi:.0f}"
    lyr.symbology = sym
    d = lyr.getDefinition("V3")
    d.colorizer.statsType = "GlobalStats"
    d.colorizer.useCustomStretchMinMax = True
    d.colorizer.customStretchMin = lo
    d.colorizer.customStretchMax = hi
    lyr.setDefinition(d)
    lyr.transparency = transparency
    return lyr


def label(lyr, expr, size=8, color=(0, 0, 0)):
    lyr.showLabels = True
    lc = lyr.listLabelClasses()[0]
    lc.expression = expr
    lc.visible = True
    d = lyr.getDefinition("V3")
    for lcd in d.labelClasses:
        ts = lcd.textSymbol.symbol
        ts.height = size
        ts.fontStyleName = "Bold"
        ts.symbol.symbolLayers[0].color.values = [color[0], color[1], color[2], 100]
        halo = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
        fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
        fill.color = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
        fill.color.values = [255, 255, 255, 100]
        halo.symbolLayers = [fill]
        ts.haloSymbol = halo
        ts.haloSize = 1.2
    lyr.setDefinition(d)


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


def county_extent(pad=3000, bottom=14000):
    """The county plus a margin; the extra bottom margin keeps Esri's basemap credit, which
    draws in the frame's lower right corner, off the data."""
    e = arcpy.Describe(os.path.join(GDB, "Utah_County")).extent
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
    ext = county_extent()
    # Step 3: flat ground
    m = new_map(p, "Flat")
    single_color_raster(m, "Show_Flat", "Slope under 5 degrees", (60, 150, 60), 15)
    vec(m, "Utah_County", "Utah County", fill=rgb(0, 0, 0, 0), outline=rgb(40, 40, 40), width=1.5)
    export_map(p, m, "lab04-check-flat.jpg", ext)
    # Step 5: road corridor
    m = new_map(p, "Corridor")
    vec(m, "Road_Corridor", "Road corridor", fill=rgb(250, 200, 120), outline=rgb(220, 150, 60), width=0.5, transparency=20)
    line(m, "Major_Highways", "Major highways", rgb(170, 40, 40), 1.2)
    vec(m, "Utah_County", "Utah County", fill=rgb(0, 0, 0, 0), outline=rgb(40, 40, 40), width=1.5)
    export_map(p, m, "lab04-check-corridor.jpg", ext)
    # Step 8/9: density surface, towers, threshold contour
    e2 = arcpy.Describe(os.path.join(GDB, "County_Buffer")).extent if arcpy.Exists(os.path.join(GDB, "County_Buffer")) else arcpy.Describe(os.path.join(GDB, "Utah_County_Buffer")).extent
    m = new_map(p, "Density")
    stretch_raster(m, "Density_per10k", "Towers per 10,000 km2", 0, 120, 30)
    line(m, "Density_20", "20 per 10,000 km2", rgb(0, 60, 160), 1.6)
    vec(m, "Utah_County", "Utah County", fill=rgb(0, 0, 0, 0), outline=rgb(40, 40, 40), width=1.8)
    vec(m, "Towers_Clip", "Towers", gallery="Circle 3", fill=rgb(20, 20, 20), size=6)
    export_map(p, m, "lab04-check-density.jpg", arcpy.Extent(e2.XMin, e2.YMin, e2.XMax, e2.YMax, spatial_reference=UTM))
    # Step 10: result
    m = new_map(p, "Result")
    single_color_raster(m, "Show_Suitable", "Suitable", (225, 90, 20))
    line(m, "Major_Highways", "Major highways", rgb(150, 150, 150), 0.8)
    vec(m, "Utah_County", "Utah County", fill=rgb(0, 0, 0, 0), outline=rgb(40, 40, 40), width=1.5)
    vec(m, "Towers_Clip", "Towers", gallery="Circle 3", fill=rgb(20, 20, 20), size=6)
    export_map(p, m, "lab04-check-result.jpg", ext)
    # Step 12: the zone on Utah Lake, on imagery
    m = new_map(p, "Lake", "Imagery Hybrid")
    single_color_raster(m, "Show_Suitable", "Suitable", (255, 120, 20), 35)
    x, y = 426769, 4454983
    export_map(p, m, "lab04-check-utah-lake.jpg",
               arcpy.Extent(x - 6000, y - 4000, x + 6000, y + 4000, spatial_reference=UTM), w_in=6.0)


def build_layout(p, title, subtitle, show, lname, notes, fname):
    m = new_map(p, lname)
    single_color_raster(m, show, "Suitable", (225, 90, 20))
    line(m, "Major_Highways", "Major highways", rgb(150, 60, 60), 0.9)
    vec(m, "Utah_County", "Utah County", fill=rgb(0, 0, 0, 0), outline=rgb(40, 40, 40), width=1.5)
    towers = vec(m, "Towers_Clip", "Existing cellular sites", gallery="Circle 3", fill=rgb(20, 40, 120), size=6)
    site = vec(m, "Site", "Recommended site", gallery="Star 3", fill=rgb(200, 0, 0), size=16)
    label(site, "$feature.NAME", 9, (160, 0, 0))
    inset = new_map(p, lname + " inset", "Imagery Hybrid")
    single_color_raster(inset, show, "Suitable", (255, 120, 20), 40)
    s2 = vec(inset, "Site", "Recommended site", gallery="Star 3", fill=rgb(255, 0, 0), size=20)

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
    mf.camera.setExtent(county_extent(1500, 9000))
    imf = lyt.createMapFrame(poly(0.5, 0.5, 3.9, 3.5), inset, "Inset")
    imf.camera.X, imf.camera.Y = SITE
    imf.camera.scale = 50000
    p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT", "Inset: the recommended site in Goshen Valley, 1:50,000, imagery basemap", 7.5, None, "InsetCaption")
    try:
        d = mf.getDefinition("V3")
        ei = arcpy.cim.CreateCIMObjectFromClassName("CIMExtentIndicator", "V3")
        ei.sourceMapFrame = "Inset"
        sym = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
        stroke = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidStroke", "V3")
        stroke.width = 1.5
        stroke.color = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
        stroke.color.values = [200, 0, 0, 100]
        sym.symbolLayers = [stroke]
        ref = arcpy.cim.CreateCIMObjectFromClassName("CIMSymbolReference", "V3")
        ref.symbol = sym
        ei.symbol = ref
        d.extentIndicators = [ei]
        mf.setDefinition(d)
    except Exception as e:
        print("extent indicator:", e)
    style = lambda cls, name: (p.listStyleItems("ArcGIS 2D", cls, name) or [None])[0]
    leg = lyt.createMapSurroundElement(poly(4.05, 1.75, 6.6, 3.55), "LEGEND", mf, style("LEGEND", "Title and Medium Text Legend"), "Legend")
    try:
        leg.title = "Legend"
        for it in leg.items:
            if "Gray" in it.name or "Canvas" in it.name:
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustFontSize"
        d = leg.getDefinition("V3")
        d.minFontSize = 5
        leg.setDefinition(d)
        if leg.isOverflowing:
            print("legend still overflowing")
    except Exception as e:
        print("legend:", e)
    lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(6.4, 2.4, 7.7, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "km"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"
        sd.division = 10
        sd.divisions = 2
        sd.subdivisions = 1
        sd.divisionsBeforeZero = 0
        sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as e:
        print("scale bar:", e)
    p.createPredefinedGraphicElement(lyt, poly(4.05, 0.5, 8.0, 1.7), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(4.12, 0.53, 7.95, 1.67), "POLYGON", notes[0] + "\n" + " ".join(notes[1:]), 6.5, None, "Notes")
    out = IMG / fname
    lyt.exportToPNG(str(out), resolution=150)
    print("exported", out)


def layouts(p):
    cv = json.loads((HERE / "check_values.json").read_text())
    base = cv["baseline"]
    d40 = next(s for s in cv["scenarios"] if s["max_density"] == 40 and s["radius_m"] == 20000
               and s["max_slope"] == 5 and s["road_km"] == 1)
    common = ["Map by Dan Ames, CE 414, September 2026. Projection: NAD 1983 UTM zone 12N, 30 m cells.",
              "Data: USGS 3DEP 1 arc-second DEM; UDOT Routes ALRS and county boundaries (UGRC); FCC cellular",
              "license sites via HIFLD (archive, July 2024) - a small subset of real towers. Basemaps by Esri."]
    build_layout(p, "Candidate Cell Tower Sites in Utah County",
                 "Baseline: slope under 5 degrees, within 1 km of a major highway,\nunder 20 towers per 10,000 sq km at a 20 km search radius",
                 "Show_Suitable", "Baseline map",
                 [f"Result: {base['suitable_km2']:.1f} sq km suitable ({base['pct_county']:.1f} % of the county). Recommended site: Goshen Valley on SR 68, flat, beside the highway, and far from every recorded site."] + common,
                 "lab04-example-map-baseline.png")
    build_layout(p, "Utah County Cell Tower Sites: Density Threshold Doubled",
                 "Changed: maximum tower density raised from 20 to 40 per 10,000 sq km.\nSlope, road distance and search radius unchanged from the baseline.",
                 "Show_Suitable_D40", "Scenario map",
                 [f"Result: {d40['suitable_km2']:.1f} sq km, up from {base['suitable_km2']:.1f} at 20 per 10,000 sq km. Doubling the threshold more than doubles the area, and the new ground is closer to existing sites. The recommended site is inside both results."] + common,
                 "lab04-example-map-scenario.png")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    prep()
    p_global = p = project()
    if what in ("all", "checks"):
        checks(p)
    if what in ("all", "layouts"):
        layouts(p)
    p.save()
