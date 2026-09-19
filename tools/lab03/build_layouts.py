# Build the two example map layouts for Lab 3 -- a baseline (run 1) and a scenario (run 3,
# three clustered control points) -- from the student-style walk of the lab on the 1852 Stansbury
# sheet in C:\Ames\Lab03Walk. Everything is rendered by ArcGIS Pro's own engine through arcpy.mp;
# nothing is drawn by hand. Pattern copied from tools/lab01/build_layouts.py.
#
#   "C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe" tools/lab03/build_layouts.py
#
# Close ArcGIS Pro first: the attribute fields on the point and line classes need a schema lock.
import arcpy, os

ROOT = r"C:\Ames\Lab03Walk"
SRC = os.path.join(ROOT, "Lab03.aprx")
DST = os.path.join(ROOT, "Lab03_Layouts.aprx")
GDB = os.path.join(ROOT, "Lab03.gdb")
RUN1 = os.path.join(ROOT, "Data", "stansbury_gsl_1852.jpg")          # georeferenced by run 1 (Save)
RUN3 = os.path.join(ROOT, "stansbury_run3_clustered.tif")            # run 3, kept with Save as New
OUT = r"C:\Users\dpame\code\ce414-gis-applications\docs\assignments\lab-03\images"
UTM = arcpy.SpatialReference(26912)
arcpy.env.overwriteOutput = True

FIELDS = ["Location_Name", "Feature_Type", "Present_Day", "Confidence"]
ATTRS = {
    "Old_Places": ["Phillips", "Farmstead", "Suburban Farmington and Kaysville", "Low",
                   "Holmes", "Farmstead", "Suburban Kaysville", "Low",
                   "Haight", "Farmstead", "Suburban Kaysville and Layton", "Low",
                   "City Mill", "Mill", "Downtown Salt Lake City", "Medium"],
    "Old_Routes": ["Ford to Antelope Island", "Ford", "Antelope Island causeway corridor; shoreline has moved", "Medium"],
}

# ---- attributes on the point and line classes (the polygon was filled in by hand during the walk)
for fc, vals in ATTRS.items():
    path = os.path.join(GDB, fc)
    have = [f.name for f in arcpy.ListFields(path)]
    for f in FIELDS:
        if f not in have:
            arcpy.management.AddField(path, f, "TEXT", field_length=120)
    rows = [vals[i:i + 4] for i in range(0, len(vals), 4)]
    with arcpy.da.UpdateCursor(path, ["OID@"] + FIELDS) as cur:
        for i, row in enumerate(cur):
            if i < len(rows):
                cur.updateRow([row[0]] + rows[i])

aprx = arcpy.mp.ArcGISProject(SRC)
aprx.saveACopy(DST)
del aprx
p = arcpy.mp.ArcGISProject(DST)
for lyt in p.listLayouts():
    p.deleteItem(lyt)


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def add_fc(m, name, fc, color=None, outline=None, width=None, size=None, gallery=None, transparency=0):
    lyr = m.addDataFromPath(os.path.join(GDB, fc))
    lyr.name = name
    sym = lyr.symbology
    if gallery:
        sym.renderer.symbol.applySymbolFromGallery(gallery)
    if color is not None:
        sym.renderer.symbol.color = color
    if outline is not None:
        sym.renderer.symbol.outlineColor = outline
    if width is not None:
        sym.renderer.symbol.size = width
    if size is not None:
        sym.renderer.symbol.size = size
    lyr.symbology = sym
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


def build_map(name, sheet_path):
    m = p.createMap(name, "MAP")
    m.spatialReference = UTM
    try:
        m.addBasemap("Imagery Hybrid")
    except Exception as e:
        print("basemap failed:", e)
    sheet = m.addDataFromPath(sheet_path)
    sheet.name = "Stansbury sheet, 1852 (georeferenced)"
    sheet.transparency = 40
    lake = add_fc(m, "1850 shoreline of the Great Salt Lake", "Old_Areas",
                  color=rgb(0, 0, 0, 0), outline=rgb(230, 70, 20), width=2.2)
    ford = add_fc(m, "Vanished route (ford)", "Old_Routes", color=rgb(255, 220, 0), width=3)
    places = add_fc(m, "Vanished place (farmstead, mill)", "Old_Places",
                    gallery="Circle 3", color=rgb(255, 230, 0), size=9)
    label(lake, "$feature.Location_Name", size=9, color=(170, 40, 0))
    label(places, "$feature.Location_Name", size=7)
    label(ford, "$feature.Location_Name", size=7)
    return m, lake


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1),
                                      arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


def style(cls, name):
    items = p.listStyleItems("ArcGIS 2D", cls, name)
    return items[0] if items else None


def build_layout(title, subtitle, m, lake, lname, notes, fname):
    lyt = p.createLayout(8.5, 11, "INCH", lname)
    p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    for text, y, size, nm in ((title, 10.28, 17, "Title"), (subtitle, 9.93, 9.5, "Subtitle")):
        el = p.createTextElement(lyt, arcpy.Point(4.25, y), "POINT", text, size, None, nm)
        try:
            el.setAnchor("CENTER_POINT")
            el.elementPositionX = 4.25
        except Exception as e:
            print("anchor:", e)
    mf = lyt.createMapFrame(poly(0.5, 2.6, 8.0, 9.7), m, "Main")
    ext = mf.getLayerExtent(lake, False, True)
    mf.camera.setExtent(ext)
    mf.camera.scale = round(mf.camera.scale * 1.12, -4)
    leg = lyt.createMapSurroundElement(poly(0.5, 0.5, 3.9, 2.0), "LEGEND", mf,
                                       style("LEGEND", "Title and Medium Text Legend"), "Legend")
    try:
        leg.title = "Legend"
        for it in list(leg.items):
            if any(k in it.name for k in ("Imagery", "Hybrid", "World", "Reference")):
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustFontSize"
    except Exception as e:
        print("legend tweak:", e)
    lyt.createMapSurroundElement(arcpy.Point(7.62, 1.25), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(4.3, 2.12, 6.9, 2.45), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "Kilometers"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9036
        else:
            sd.units.uwkid = 9036
        sd.fittingStrategy = "AdjustFrame"
        sd.division = 20
        sd.divisions = 2
        sd.subdivisions = 1
        sd.divisionsBeforeZero = 0
        sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as e:
        print("scale bar tweak:", e)
    p.createPredefinedGraphicElement(lyt, poly(4.05, 0.5, 7.25, 2.0), "RECTANGLE", None, "TextBoxFrame")
    body = " ".join(notes[:2]) + "\n" + "\n".join(notes[2:])     # first two lines are one sentence
    p.createTextElement(lyt, poly(4.12, 0.53, 7.2, 1.97), "POLYGON", body, 6.5, None, "Notes")
    out = os.path.join(OUT, fname)
    lyt.exportToPNG(out, resolution=150)
    print("exported", out)


area, perim = next(arcpy.da.SearchCursor(os.path.join(GDB, "Old_Areas"), ["Area_km2", "Perim_km"]))
common = ["Map by Dan Ames, CE 414, September 2026. Coordinate system: NAD 1983 UTM Zone 12N.",
          "Historic sheet: Map of the Great Salt Lake and adjacent country in the Territory of Utah, "
          "surveyed 1849-50 by Capt. Howard Stansbury, published 1852 (Library of Congress 2018588045).",
          "Basemap: Esri World Imagery and Hybrid Reference. Features digitized by hand from the sheet."]

m1, lake1 = build_map("Baseline", RUN1)
build_layout("The Great Salt Lake and Its Shore in 1850",
             "Run 1: 1st Order Polynomial (Affine), 8 control points. Total RMS 1,688 m; mean error at 3 check features 2.4 km",
             m1, lake1, "Baseline map",
             [f"1850 lake as traced: {area:,.0f} sq km, perimeter {perim:,.0f} km, uncertain by at most about",
              f"{perim * 2.384:,.0f} sq km (perimeter x mean check error). Farmsteads and mill: Confidence Low to Medium."] + common,
             "lab03-example-map-baseline.png")

m3, lake3 = build_map("Scenario", RUN3)
build_layout("The Same Features Over a Three-Point Georeference",
             "Run 3: 1st Order Polynomial from 3 clustered control points only. Total RMS 0 m; mean check error 8.9 km",
             m3, lake3, "Scenario map",
             ["Why this run: it reports a perfect fit and is the worst of the three. The traced features have not moved;",
              "the sheet has, and it no longer sits under them. Compare the north end and the Provo corner with Map 1."] + common,
             "lab03-example-map-scenario.png")
p.save()
print("saved", DST)
