# Build C:\Ames\Week04\RemoteSensing.aprx for the Week 4 remote-sensing captures.
#
#   Part A (section 5, "Pulling Real Images Apart"): one map per example photo (Eiffel, Snow, Smoke,
#   Night). Each map holds the full-color JPEG plus three single-band layers (Band_1/2/3), each
#   symbolized as Stretch, Minimum Maximum with user-defined statistics 0 and 255 (so no
#   auto-stretch), on a two-color black-to-red / black-to-green / black-to-blue ramp.
#   Part B (section 3, band slides): one map "Landsat" with the Utah County subset of Landsat 8 scene
#   LC08_L2SP_038032_20250712_02_T1, bands B2, B3, B4 (and B5), each grayscale with the SAME
#   user-defined stretch so brightness compares across bands.
#
# Symbology is set here with the CIM and then checked (and captured) in the live ArcGIS Pro session.
# Run with the ArcGIS Pro Python while ArcGIS Pro does not have the project open.
import os, shutil, sys
import arcpy

ROOT = r"C:\Ames\Week04"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(REPO, "slides", "week-04", "images")
APRX = os.path.join(ROOT, "RemoteSensing.aprx")
TEMPLATE = r"C:\Ames\Week02\CitiesRivers.aprx"

PHOTOS = {"Eiffel": "rs-eiffel-tower-aerial.jpg", "Snow": "rs-maryland-snow.jpg",
          "Smoke": "rs-california-wildfires.jpg", "Night": "rs-europe-at-night.jpg"}
BANDS = [("Red", 1, (255, 0, 0)), ("Green", 2, (0, 255, 0)), ("Blue", 3, (0, 0, 255))]

LANDSAT = os.path.join(ROOT, "Landsat")
SCENE = "LC08_L2SP_038032_20250712_20250725_02_T1"
# Utah Lake, Provo/Orem and the farmland around them, in the scene's UTM 12N meters.
CLIP = (415000, 4430000, 460000, 4470000)
LS_BANDS = [("B2 blue", "SR_B2"), ("B3 green", "SR_B3"), ("B4 red", "SR_B4"), ("B5 near-infrared", "SR_B5")]
# One stretch for every Landsat band (raw Collection 2 SR digital numbers; reflectance =
# DN * 0.0000275 - 0.2). 7500 -> 0.006, 22000 -> 0.405 reflectance. Filled in from the data below.
LS_STRETCH = None


def rgb(c, a=100):
    return {"type": "CIMRGBColor", "values": [c[0], c[1], c[2], a]}


def set_stretch(lyr, lo, hi, to_color, from_color=(0, 0, 0)):
    cim = lyr.getDefinition("V3")
    col = cim.colorizer
    if type(col).__name__ != "CIMRasterStretchColorizer":
        col = arcpy.cim.CreateCIMObjectFromClassName("CIMRasterStretchColorizer", "V3")
        cim.colorizer = col
    col.stretchType = "MinimumMaximum"
    col.statsType = "GlobalStats"
    col.useCustomStretchMinMax = True
    col.customStretchMin = lo
    col.customStretchMax = hi
    col.useGammaStretch = False
    col.displayBackgroundValue = False
    ramp = arcpy.cim.CreateCIMObjectFromClassName("CIMLinearContinuousColorRamp", "V3")
    fc = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); fc.values = [*from_color, 100]
    tc = arcpy.cim.CreateCIMObjectFromClassName("CIMRGBColor", "V3"); tc.values = [*to_color, 100]
    ramp.fromColor, ramp.toColor = fc, tc
    ramp.colorSpace = arcpy.cim.CreateCIMObjectFromClassName("CIMICCColorSpace", "V3")
    ramp.colorSpace.url = "Default RGB"
    col.colorRamp = ramp
    col.colorScheme = f"Black to {to_color}"
    cim.colorizer = col
    lyr.setDefinition(cim)


def main():
    if os.path.exists(APRX):
        sys.exit("already exists: " + APRX)
    photos = os.path.join(ROOT, "Photos"); os.makedirs(photos, exist_ok=True)
    for f in PHOTOS.values():
        shutil.copy2(os.path.join(IMG, f), photos)

    arcpy.mp.ArcGISProject(TEMPLATE).saveACopy(APRX)
    aprx = arcpy.mp.ArcGISProject(APRX)
    for m in aprx.listMaps(): aprx.deleteItem(m)
    for l in aprx.listLayouts(): aprx.deleteItem(l)
    gdb = os.path.join(ROOT, "RemoteSensing.gdb")
    if not arcpy.Exists(gdb): arcpy.management.CreateFileGDB(ROOT, "RemoteSensing.gdb")
    aprx.defaultGeodatabase = gdb
    aprx.homeFolder = ROOT

    for name, f in PHOTOS.items():
        m = aprx.createMap(name)
        src = os.path.join(photos, f)
        full = m.addDataFromPath(src); full.name = f"{name} full color"
        for band, i, c in reversed(BANDS):
            lyr = m.addDataFromPath(src + f"\\Band_{i}")
            lyr.name = f"{name} Band_{i} ({band.lower()})"
            set_stretch(lyr, 0, 255, c)
            lyr.visible = band == "Red"
        full.visible = False

    # Landsat: clip each band to the Utah Lake window so the project stays small.
    global LS_STRETCH
    m = aprx.createMap("Landsat")
    sr = arcpy.Describe(os.path.join(LANDSAT, f"{SCENE}_SR_B4.TIF")).spatialReference
    m.spatialReference = sr
    clips = []
    for label, suf in LS_BANDS:
        src = os.path.join(LANDSAT, f"{SCENE}_{suf}.TIF")
        out = os.path.join(gdb, f"UtahLake_{suf}")
        if not arcpy.Exists(out):
            arcpy.management.Clip(src, " ".join(map(str, CLIP)), out, nodata_value="0")
        clips.append((label, out))
    # Common stretch: 0.5th to 99.5th percentile over the three visible bands together.
    import numpy as np
    vals = np.concatenate([arcpy.RasterToNumPyArray(o, nodata_to_value=0)[::4, ::4].ravel() for _, o in clips[:3]])
    vals = vals[vals > 0]
    lo, hi = [float(round(v, -2)) for v in np.percentile(vals, [0.5, 99.5])]
    LS_STRETCH = (lo, hi)
    print("common Landsat stretch", lo, hi)
    for label, out in reversed(clips):
        lyr = m.addDataFromPath(out); lyr.name = f"Landsat 8 {label}"
        set_stretch(lyr, lo, hi, (255, 255, 255))
        lyr.visible = label.startswith("B4")
    aprx.save()
    print("saved", APRX)


if __name__ == "__main__":
    main()
