# Build the Lab 2 example map layout (Utah County irrigated cropland from Landsat NDVI) in a copy of the
# Lab02 project and export it. Everything is rendered by ArcGIS Pro's engine through arcpy.mp.
# Run with the ArcGIS Pro Python while Pro is signed in (basemaps need the portal):
#   "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\lab02\build_layout.py
import arcpy, os, sys, urllib.request, urllib.parse, datetime

# usage: build_layout.py [RASTER_NAME THRESHOLD OUT_BASENAME]  (defaults: NDVI_reclass 0.4 lab02-example-map-utah-county)
RASTER_NAME = sys.argv[1] if len(sys.argv) > 1 else "NDVI_reclass"
THRESH = sys.argv[2] if len(sys.argv) > 2 else "0.4"
OUT_BASE = sys.argv[3] if len(sys.argv) > 3 else "lab02-example-map-utah-county"

SRC = r"C:\Ames\Lab02\Lab02.aprx"
DST = r"C:\Ames\Lab02\Lab02_Layout.aprx"  # overwritten on every run
GDB = r"C:\Ames\Lab02\Lab02.gdb"
LAB1 = r"C:\Ames\Lab01\Lab01.gdb"
OUT = r"C:\Ames\Lab02\Exports"
os.makedirs(OUT, exist_ok=True)
arcpy.env.overwriteOutput = True
SQMI = 2589988.110336
RECLASS = os.path.join(GDB, RASTER_NAME)
SR = arcpy.Describe(RECLASS).spatialReference
print("raster CRS:", SR.name)

# ---- county polygon (from the Lab 1 run, UGRC county boundaries) and municipalities (UGRC live service)
county = os.path.join(GDB, "UtahCounty")
if not arcpy.Exists(county):
    arcpy.management.Project(os.path.join(LAB1, "Counties_Select"), county, SR)
muni = os.path.join(GDB, "Municipalities_UtahCounty")
if not arcpy.Exists(muni):
    base = "https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/UtahMunicipalBoundaries/FeatureServer/0/query?"
    q = urllib.parse.urlencode({"where": "COUNTYNBR='25'", "outFields": "NAME,POPLASTCENSUS,POPLASTESTIMATE,UPDATED",
                                "outSR": SR.factoryCode, "f": "geojson"})
    gj = os.path.join(OUT, "municipalities_utah_county.geojson")
    with urllib.request.urlopen(base + q, timeout=60) as r, open(gj, "wb") as f:
        f.write(r.read())
    arcpy.conversion.JSONToFeatures(gj, muni, "POLYGON")
cities = os.path.join(GDB, "Cities_UtahCounty")
if not arcpy.Exists(cities):
    pts = arcpy.management.FeatureToPoint(muni, os.path.join(GDB, "Municipalities_pts"), "INSIDE")
    # keep the largest municipalities by 2020 Census population for labels
    rows = sorted(arcpy.da.SearchCursor(pts, ["OID@", "POPLASTCENSUS"]), key=lambda r: -(r[1] or 0))
    # Draper is a Salt Lake County city that crosses the county line; skip it
    names = {r[0]: r[1] for r in arcpy.da.SearchCursor(pts, ["OID@", "NAME"])}
    keep = [r[0] for r in rows if names[r[0]] != "Draper"][:7]
    lyr = arcpy.management.MakeFeatureLayer(pts, "pts_lyr", "OBJECTID IN (%s)" % ",".join(map(str, keep)))
    arcpy.management.CopyFeatures(lyr, cities)
print("cities:", [r[0] for r in arcpy.da.SearchCursor(cities, ["NAME"])])

# ---- numbers for the text box, from the reclassified raster's attribute table
counts = {int(v): int(c) for v, c in arcpy.da.SearchCursor(RECLASS, ["Value", "Count"])}
cell = arcpy.Describe(RECLASS).meanCellWidth
irr_sqmi = counts.get(1, 0) * cell * cell / SQMI
tot_sqmi = sum(counts.values()) * cell * cell / SQMI
print("irrigated class: %.0f of %.0f sq mi (%.0f %%)" % (irr_sqmi, tot_sqmi, 100 * irr_sqmi / tot_sqmi))

aprx = arcpy.mp.ArcGISProject(SRC)
aprx.saveACopy(DST)
del aprx
p = arcpy.mp.ArcGISProject(DST)
for lyt in p.listLayouts():
    p.deleteItem(lyt)
for m in p.listMaps():
    p.deleteItem(m)


def rgb(r, g, b, a=100):
    return {"RGB": [r, g, b, a]}


def add_vector(m, name, fc, color=None, outline=None, width=None, size=None, gallery=None, transparency=0):
    lyr = m.addDataFromPath(fc)
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


def add_reclass(m, name, transparency=0):
    lyr = m.addDataFromPath(RECLASS)
    lyr.name = name
    sym = lyr.symbology
    sym.updateColorizer("RasterUniqueValueColorizer")
    sym.colorizer.field = "Value"
    for grp in sym.colorizer.groups:
        for it in grp.items:
            if it.values[0] == "0":
                it.label = "Non-irrigated land"
                it.color = rgb(238, 220, 170)
            else:
                it.label = "Irrigated cropland"
                it.color = rgb(60, 170, 40)
    lyr.symbology = sym
    lyr.transparency = transparency
    return lyr


def label(lyr, expr, size=8, bold=True, color=(0, 0, 0)):
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
        halo_sym = arcpy.cim.CreateCIMObjectFromClassName("CIMPolygonSymbol", "V3")
        fill = arcpy.cim.CreateCIMObjectFromClassName("CIMSolidFill", "V3")
        fill.color = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3")
        fill.color.values = [255, 255, 255, 100]
        halo_sym.symbolLayers = [fill]
        ts.haloSymbol = halo_sym
        ts.haloSize = 1.2
    lyr.setDefinition(d)


# ---- main map
m = p.createMap("NDVI classification", "MAP")
m.spatialReference = SR
try:
    m.addBasemap("Light Gray Canvas")
except Exception as e:
    print("basemap failed:", e)
# the Light Gray Canvas reference layer repeats the city labels; turn it off
for bl in m.listLayers():
    if "Reference" in bl.name:
        bl.visible = False
# addDataFromPath inserts at the top, so add bottom-most first
rec = add_reclass(m, "Irrigated cropland from NDVI")
cty = add_vector(m, "Utah County", county, color=rgb(0, 0, 0, 0), outline=rgb(50, 50, 50), width=1.5)
cit = add_vector(m, "Cities", cities, gallery="Circle 3", color=rgb(40, 40, 40), size=6)
label(cit, "$feature.NAME", size=8, bold=True)

# ---- inset: the center-pivot fields near Elberta, on imagery
inset = p.createMap("Center pivots inset", "MAP")
inset.spatialReference = SR
try:
    inset.addBasemap("Imagery")
except Exception as e:
    print("inset basemap failed:", e)
irec = add_reclass(inset, "Irrigated cropland from NDVI", transparency=45)
pivot = arcpy.PointGeometry(arcpy.Point(-111.95, 39.985), arcpy.SpatialReference(4326)).projectAs(SR).firstPoint
print("inset center UTM:", round(pivot.X), round(pivot.Y))


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1), arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


def style(cls, name):
    items = p.listStyleItems("ArcGIS 2D", cls, name)
    return items[0] if items else None


lyt = p.createLayout(8.5, 11, "INCH", "NDVI map")
p.createPredefinedGraphicElement(lyt, poly(0.35, 0.35, 8.15, 10.65), "RECTANGLE", None, "Neatline")
t = p.createTextElement(lyt, arcpy.Point(4.25, 10.28), "POINT", ("Irrigated Cropland in Utah County from Landsat NDVI" if THRESH == "0.4" else "Utah County NDVI Classification: %s Threshold Scenario" % THRESH), 18, None, "Title")
st = p.createTextElement(lyt, arcpy.Point(4.25, 9.92), "POINT",
                         "Landsat 8 OLI, path 38 row 32, acquired July 12, 2025. NDVI = (NIR - Red) / (NIR + Red), classified at %s." % THRESH, 9.5, None, "Subtitle")
for el in (t, st):
    try:
        el.setAnchor("CENTER_POINT")
        el.elementPositionX = 4.25
    except Exception as e:
        print("anchor:", e)
mf = lyt.createMapFrame(poly(0.5, 3.75, 8.0, 9.7), m, "Main")
mf.camera.setExtent(mf.getLayerExtent(cty, False, True))
mf.camera.scale = round(mf.camera.scale * 1.04, -4)
imf = lyt.createMapFrame(poly(0.5, 0.5, 3.9, 3.5), inset, "Inset")
imf.camera.X, imf.camera.Y = pivot.X, pivot.Y
imf.camera.scale = 90000
p.createTextElement(lyt, arcpy.Point(0.55, 3.55), "POINT",
                    "Inset: center-pivot fields near Elberta, 1:90,000, classified NDVI at 55 % opacity over imagery", 7.5, None, "InsetCaption")
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
leg = lyt.createMapSurroundElement(poly(4.05, 1.75, 6.9, 3.55), "LEGEND", mf, style("LEGEND", "Title and Medium Text Legend"), "Legend")
try:
    leg.title = "NDVI classified at %s" % THRESH
    for it in leg.items:
        if "Gray" in it.name:
            leg.removeItem(it)
    leg.fittingStrategy = "AdjustFontSize"
except Exception as e:
    print("legend tweak:", e)
lyt.createMapSurroundElement(arcpy.Point(7.5, 3.2), "NORTH_ARROW", mf, style("NORTH_ARROW", "ArcGIS North 1"), "North Arrow")
sb = lyt.createMapSurroundElement(poly(6.4, 2.4, 7.6, 2.8), "SCALE_BAR", mf, style("SCALE_BAR", "Scale Line 1"), "Scale Bar")
try:
    sd = sb.getDefinition("V3")
    sd.unitLabel = "Miles"
    if isinstance(sd.units, dict):
        sd.units["uwkid"] = 9093
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
p.createPredefinedGraphicElement(lyt, poly(4.05, 0.5, 8.0, 1.7), "RECTANGLE", None, "TextBoxFrame")
pct = 100 * irr_sqmi / tot_sqmi
if THRESH == "0.4":
    finding = "The forested Wasatch and Uinta slopes are included: NDVI measures greenness, not irrigation."
else:
    finding = ("Scenario: threshold raised from 0.4 (1,111 sq mi, 53 %%) to %s. Forest is still in the class; "
               "the dry benches, the town lawns and the paler pivots drop out first." % THRESH)
notes = ("Result: {:,.0f} of {:,.0f} sq mi ({:.0f} %) classified at or above NDVI {}. ".format(irr_sqmi, tot_sqmi, pct, THRESH)
         + finding + "\n"
         + "Map by Dan Ames, CE 414, {:%B %Y}. Projection: {}. ".format(datetime.date.today(), SR.name.replace("_", " "))
         + "Data: Landsat 8 OLI/TIRS Collection 2 Level-2 surface reflectance, scene LC08_L2SP_038032_20250712_20250725_02_T1, "
         + "courtesy of the U.S. Geological Survey; county and municipal boundaries UGRC (CC BY 4.0); basemaps by Esri. "
         + "Method: ModelBuilder - Float, Minus, Plus, Divide, then Reclassify (0.4) or Raster Calculator Con() with the threshold as a model parameter.")
p.createTextElement(lyt, poly(4.12, 0.53, 7.95, 1.67), "POLYGON", notes, 6.5, None, "Notes")
out = os.path.join(OUT, OUT_BASE + ".png")
lyt.exportToPNG(out, resolution=150)
print("exported", out)
p.save()
print("saved", DST)
