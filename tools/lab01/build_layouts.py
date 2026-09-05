# Build the two example map layouts for Lab 1 in a copy of the Lab01 project and export them.
# Everything is rendered by ArcGIS Pro's own engine through arcpy.mp; nothing is drawn by hand.
import arcpy, os, sys, json

SRC = r"C:\Ames\Lab01\Lab01.aprx"
DST = r"C:\Ames\Lab01\Lab01_Layouts.aprx"
GDB = r"C:\Ames\Lab01\Lab01.gdb"
OUT = r"C:\Ames\Lab01\Exports"
os.makedirs(OUT, exist_ok=True)
UTM = arcpy.SpatialReference(26912)
SQMI = 2589988.110336
arcpy.env.overwriteOutput = True

# ---- the recommended site (label point of the largest baseline polygon, overridable)
site_xy = tuple(map(float, sys.argv[1:3])) if len(sys.argv) >= 3 else (427112.0, 4475055.0)
site_fc = os.path.join(GDB, "Recommended_Site")
if not arcpy.Exists(site_fc):
    arcpy.management.CreateFeatureclass(GDB, "Recommended_Site", "POINT", spatial_reference=UTM)
    arcpy.management.AddField(site_fc, "SITE", "TEXT", field_length=60)
with arcpy.da.UpdateCursor(site_fc, ["OID@"]) as cur:
    for _ in cur:
        cur.deleteRow()
with arcpy.da.InsertCursor(site_fc, ["SHAPE@XY", "SITE"]) as cur:
    cur.insertRow((site_xy, "Recommended site"))

aprx = arcpy.mp.ArcGISProject(SRC)
aprx.saveACopy(DST)
del aprx
p = arcpy.mp.ArcGISProject(DST)
for lyt in p.listLayouts():
    p.deleteItem(lyt)
for m in p.listMaps():
    if m.name != "Map":
        p.deleteItem(m)


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def add(m, name, fc, color=None, outline=None, width=None, size=None, gallery=None, transparency=0, visible=True):
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
        sym.renderer.symbol.size = width if size is None else width
    if size is not None:
        sym.renderer.symbol.size = size
    lyr.symbology = sym
    lyr.transparency = transparency
    lyr.visible = visible
    return lyr


def label(lyr, expr, size=8, bold=True, halo=True, color=(0, 0, 0)):
    lyr.showLabels = True
    lc = lyr.listLabelClasses()[0]
    lc.expression = expr
    lc.visible = True
    d = lyr.getDefinition("V3")
    for lcd in d.labelClasses:
        ts = lcd.textSymbol.symbol
        ts.height = size
        ts.fontStyleName = "Bold" if bold else "Regular"
        ts.symbol.symbolLayers[0].color.values = [color[0], color[1], color[2], 100]
        if halo:
            halo_sym = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
            fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
            fill.color = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
            fill.color.values = [255, 255, 255, 100]
            halo_sym.symbolLayers = [fill]
            ts.haloSymbol = halo_sym
            ts.haloSize = 1.2
    lyr.setDefinition(d)


def build_map(name, zones_after, wm_buffer, buffer_label):
    m = p.createMap(name, "MAP")
    m.spatialReference = UTM
    try:
        m.addBasemap("Light Gray Canvas")
    except Exception as e:
        print("basemap failed:", e)
    # bottom to top; addDataFromPath inserts at the top, so add in reverse draw order
    county = add(m, "Utah County", "Counties_Select", color=rgb(0, 0, 0, 0), outline=rgb(60, 60, 60), width=1.5)
    before = add(m, "Meets density + road criteria", "Zones_Density_Roads", color=rgb(255, 235, 132), outline=rgb(190, 160, 60), width=0.4)
    wmb = add(m, f"{buffer_label} Walmart exclusion (erased)", wm_buffer, color=rgb(120, 120, 120), outline=rgb(90, 90, 90), width=0.7, transparency=65)
    roads = add(m, "Major roads (CARTOCODE 1-5)", "MajorRoads_UtahCounty", color=rgb(150, 60, 60), width=0.9)
    after = add(m, "Suitable: final result", zones_after, color=rgb(230, 100, 20), outline=rgb(150, 50, 0), width=0.6)
    wm = add(m, "Existing Walmart (labeled by city)", "Walmarts_UtahCounty", gallery="Circle 3", color=rgb(0, 60, 150), size=8)
    site = add(m, "Recommended site", "Recommended_Site", gallery="Star 3", color=rgb(200, 0, 0), size=18)
    label(wm, "$feature.CITY", size=7, bold=False)
    label(site, "$feature.SITE", size=9, bold=True, color=(160, 0, 0))
    return m, {"county": county, "after": after, "site": site, "wm": wm}


def build_inset(name, zones_after):
    m = p.createMap(name, "MAP")
    m.spatialReference = UTM
    try:
        m.addBasemap("Imagery Hybrid")
    except Exception as e:
        print("inset basemap failed:", e)
    after = add(m, "Suitable area", zones_after, color=rgb(230, 100, 20, 35), outline=rgb(255, 140, 0), width=2)
    site = add(m, "Recommended site", "Recommended_Site", gallery="Star 3", color=rgb(255, 0, 0), size=22)
    label(site, "$feature.SITE", size=10, bold=True, color=(170, 0, 0))
    return m


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


def style(cls, name):
    items = p.listStyleItems("ArcGIS 2D", cls, name)
    return items[0] if items else None


def build_layout(title, subtitle, m, inset, layers, lname, note_lines, fname):
    lyt = p.createLayout(8.5, 11, "INCH", lname)
    # neat line
    p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
    # title block
    t = p.createTextElement(lyt, arcpy.Point(4.25, 10.28), "POINT", title, 18, None, "Title")
    st = p.createTextElement(lyt, arcpy.Point(4.25, 9.92), "POINT", subtitle, 10, None, "Subtitle")
    for el in (t, st):
        try:
            el.setAnchor("CENTER_POINT")
            el.elementPositionX = 4.25
        except Exception as e:
            print("anchor:", e)
    # main map frame
    mf = lyt.createMapFrame(poly(0.5, 3.75, 8.0, 9.7), m, "Main")
    ext = mf.getLayerExtent(layers["county"], False, True)
    mf.camera.setExtent(ext)
    mf.camera.scale = round(mf.camera.scale * 1.04, -4)
    # inset frame
    imf = lyt.createMapFrame(poly(0.5, 0.5, 3.9, 3.5), inset, "Inset")
    sx, sy = site_xy
    imf.camera.X, imf.camera.Y = sx + 150, sy
    imf.camera.scale = 24000
    p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT", "Inset: recommended site, 1:24,000, imagery basemap", 7.5, None, "InsetCaption")
    # extent indicator on the main frame, via CIM
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
        ei.collapseSize = 4
        d.extentIndicators = [ei]
        mf.setDefinition(d)
    except Exception as e:
        print("extent indicator failed:", e)
    # legend
    # Same configuration as the first successful run: title shown, font-fit strategy, 1.8 in tall.
    leg = lyt.createMapSurroundElement(poly(4.05, 1.75, 6.6, 3.55), "LEGEND", mf, style("LEGEND", "Title and Medium Text Legend"), "Legend")
    try:
        leg.title = "Legend"
        for it in leg.items:
            if it.name in ("Light Gray Canvas", "World Light Gray Base", "World Light Gray Reference") or "Gray" in it.name:
                leg.removeItem(it)
        leg.fittingStrategy = "AdjustFontSize"
    except Exception as e:
        print("legend tweak:", e)
    # north arrow and scale bar
    lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
    sb = lyt.createMapSurroundElement(poly(6.4, 2.4, 7.6, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
    try:
        sd = sb.getDefinition("V3")
        sd.unitLabel = "Miles"
        if isinstance(sd.units, dict):
            sd.units["uwkid"] = 9093  # US statute miles
        else:
            sd.units.uwkid = 9093
        sd.fittingStrategy = "AdjustFrame"
        sd.division = 5
        sd.divisions = 2
        sd.subdivisions = 1
        sd.divisionsBeforeZero = 0
        sd.labelFrequency = "Divisions"
        sb.setDefinition(sd)
    except Exception as e:
        print("scale bar tweak:", e)
    # text box: author, date, projection, sources, and the scenario note
    p.createPredefinedGraphicElement(lyt, poly(4.05, 0.5, 8.0, 1.7), "RECTANGLE", None, "TextBoxFrame")
    p.createTextElement(lyt, poly(4.12, 0.53, 7.95, 1.67), "POLYGON", note_lines[0] + "\n" + " ".join(note_lines[1:]), 6.5, None, "Notes")
    out = os.path.join(OUT, fname)
    lyt.exportToPNG(out, resolution=150)
    print("exported", out)
    return lyt


base_m, base_l = build_map("Baseline", "Walmart_Target_Zones", "Walmart_2mi_Buffer", "2-mile buffer")
base_i = build_inset("Baseline inset", "Walmart_Target_Zones")
scen_m, scen_l = build_map("Scenario", "Walmart_Target_Zones_W3mi", "Walmart_3mi_Buffer", "3-mile buffer")
scen_i = build_inset("Scenario inset", "Walmart_Target_Zones_W3mi")


def area(fc):
    return sum(r[0] for r in arcpy.da.SearchCursor(os.path.join(GDB, fc), ["SHAPE@AREA"])) / SQMI


nb = int(arcpy.management.GetCount(os.path.join(GDB, "Walmart_Target_Zones"))[0])
ns = int(arcpy.management.GetCount(os.path.join(GDB, "Walmart_Target_Zones_W3mi"))[0])
ab, as_ = area("Walmart_Target_Zones"), area("Walmart_Target_Zones_W3mi")
common = ["Map by Dan Ames, CE 414, September 2026. Projection: NAD 1983 UTM Zone 12N.",
          "Data: UGRC county boundaries, 2020 census tracts and Utah Roads (CC BY 4.0). Existing Walmarts digitized",
          "from Walmart's store finder (10 stores: 9 Supercenters, 1 Neighborhood Market). Basemaps by Esri.",
          "Method: ModelBuilder - Select, Intersect, Add Field, Calculate Field, Buffer, Erase."]
build_layout("Possible Walmart Locations in Utah County",
             "Baseline criteria: density over 5,000 per sq mi, within 2 miles of a major road, more than 2 miles from an existing Walmart",
             base_m, base_i, base_l, "Baseline map",
             [f"Result: {nb} suitable polygons, {ab:.1f} sq mi (from {area('Zones_Density_Roads'):.1f} sq mi before the Erase). Recommended site: vacant land in north Lehi."] + common,
             "lab01-example-map-baseline.png")
build_layout("Utah County Walmart Sites: 3-Mile Exclusion Scenario",
             "Changed parameter: distance from existing Walmarts raised from 2 miles to 3 miles. Density and road criteria unchanged.",
             scen_m, scen_i, scen_l, "Scenario map",
             [f"Result: {ns} polygons, {as_:.1f} sq mi, down from {nb} polygons / {ab:.1f} sq mi at 2 miles. The recommended site survives; most other candidates do not."] + common,
             "lab01-example-map-scenario.png")
p.save()
print("saved", DST)
print("storenames:", [r[0] for r in arcpy.da.SearchCursor(os.path.join(GDB, "Walmarts_UtahCounty"), ["STORENAME"])])
