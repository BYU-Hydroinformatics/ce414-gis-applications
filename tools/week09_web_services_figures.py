"""Figures for slides/week-09/ogc-web-services.md (the 2026 rebuild).

Every figure is made from a live response fetched when this script runs: nothing is drawn from
made-up numbers. Run it with the ArcGIS Pro Python (it needs GDAL for the COG reads):

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/week09_web_services_figures.py

First run: 2026-10-05. Every URL it touches is listed in URLS below and in the deck's speaker notes.
The numbers it prints (record counts, bytes read, the elevation at the center pixel) are the ones
quoted in the deck; if a service changes, re-run and update the deck.
"""
import io
import json
import os
import textwrap
import urllib.parse
import urllib.request

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Polygon as MplPolygon
from PIL import Image
from osgeo import gdal, osr

gdal.UseExceptions()

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "slides", "week-09", "images")
os.makedirs(OUT, exist_ok=True)

NAVY = "#002e5d"
BLUE = "#0062b8"
GRAY = "#4a5568"
MONO = "Consolas"

# BYU campus and the Wasatch front above it: lon -111.68..-111.60, lat 40.235..40.2655.
# The latitude span is chosen so a 1000 x 500 image is not stretched (cos 40.25 deg = 0.763).
BBOX = (-111.68, 40.235, -111.60, 40.2655)
BB = ",".join(str(v) for v in BBOX)

UGRC = "https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services"
SKI = UGRC + "/SkiAreaBoundaries/FeatureServer/0"
STREAMS = UGRC + "/UtahStreamsNHD/FeatureServer/0"
TOPO_WMS = "https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/WMSServer"
TOPO_REST = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer"
DEP_WMS = "https://elevation.nationalmap.gov/arcgis/services/3DEPElevation/ImageServer/WMSServer"
DEP_WCS = "https://elevation.nationalmap.gov/arcgis/services/3DEPElevation/ImageServer/WCSServer"
DEEGREE_WFS = "https://demo.deegree.org/utah-workspace/services/wfs"
PYGEOAPI = "https://demo.pygeoapi.io/master"
EARTH_SEARCH = "https://earth-search.aws.element84.com/v1"
TNM_TILE = ("https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/13/TIFF/current/"
            "n41w112/USGS_13_n41w112.tif")


def get(url, params=None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params, safe=":,/{}*")
    req = urllib.request.Request(url, headers={"User-Agent": "ce414-course-figures"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), url


def getjson(url, params=None):
    b, u = get(url, params)
    return json.loads(b), u


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- WMS GetMap (two layers)
def wms_getmap(base, layer, fmt="image/png"):
    b, u = get(base, dict(SERVICE="WMS", VERSION="1.3.0", REQUEST="GetMap", LAYERS=layer,
                          STYLES="", CRS="CRS:84", BBOX=BB, WIDTH=1000, HEIGHT=500, FORMAT=fmt))
    print("GetMap", u)
    return Image.open(io.BytesIO(b)).convert("RGB")


topo = wms_getmap(TOPO_WMS, "0")
topo.save(os.path.join(OUT, "ws9-wms-topo-provo.png"))
dep = wms_getmap(DEP_WMS, "3DEPElevation:Hillshade Elevation Tinted")
print("wrote ws9-wms-topo-provo.png (the 3DEP GetMap goes into ws9-wms-vs-wcs.png)")

# GetFeatureInfo on the topo map: what does "ask about a pixel" return?
gfi, gfi_url = get(TOPO_WMS, dict(SERVICE="WMS", VERSION="1.3.0", REQUEST="GetFeatureInfo",
                                  LAYERS="0", QUERY_LAYERS="0", STYLES="", CRS="CRS:84", BBOX=BB,
                                  WIDTH=1000, HEIGHT=500, I=500, J=250, INFO_FORMAT="text/plain"))
print("GetFeatureInfo", gfi_url, "->", gfi.decode("utf8", "replace").strip())

# Same map from the same server through the ArcGIS REST interface
rest_b, rest_url = get(TOPO_REST + "/export", dict(bbox=BB, bboxSR=4326, imageSR=3857,
                                                   size="1000,500", format="png", f="image"))
rest = Image.open(io.BytesIO(rest_b)).convert("RGB")
print("REST export", rest_url)

fig, axs = plt.subplots(1, 2, figsize=(12, 3.9))
for ax, im, title, sub in [
        (axs[0], rest, "ArcGIS REST  ·  MapServer/export", ".../rest/services/USGSTopo/MapServer/export?bbox=...&f=image"),
        (axs[1], topo, "OGC WMS 1.3.0  ·  GetMap", ".../services/USGSTopo/MapServer/WMSServer?REQUEST=GetMap&..."),
]:
    ax.imshow(im)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=15, color=NAVY, fontweight="bold", loc="left")
    ax.text(0, -0.08, sub, transform=ax.transAxes, fontsize=10, family=MONO, color=GRAY, va="top")
fig.suptitle("One USGS map service (USGSTopo), two interfaces — both hand back a PNG", fontsize=16, color=NAVY, y=0.99)
fig.tight_layout(rect=(0, 0.02, 1, 0.95))
save(fig, "ws9-rest-vs-wms.png")

# ---------------------------------------------------------------- WCS GetCoverage: the values
wcs_b, wcs_url = get(DEP_WCS, dict(SERVICE="WCS", VERSION="1.0.0", REQUEST="GetCoverage",
                                   COVERAGE="DEP3Elevation", CRS="EPSG:4326", BBOX=BB,
                                   WIDTH=200, HEIGHT=100, FORMAT="GeoTIFF"))
print("GetCoverage", wcs_url)
gdal.FileFromMemBuffer("/vsimem/wcs.tif", wcs_b)
wds = gdal.Open("/vsimem/wcs.tif")
z = wds.GetRasterBand(1).ReadAsArray().astype(float)
print("WCS array", z.shape, "min %.1f max %.1f center %.2f" % (z.min(), z.max(), z[50, 100]),
      "type", gdal.GetDataTypeName(wds.GetRasterBand(1).DataType))

fig = plt.figure(figsize=(13, 3.9))
ax1 = fig.add_axes([0.01, 0.04, 0.43, 0.80])
ax1.imshow(dep)
ax1.set_xticks([]); ax1.set_yticks([])
ax1.set_title("WMS GetMap → a picture (PNG, RGB colors)", fontsize=13, color=NAVY, loc="left")
ax2 = fig.add_axes([0.47, 0.04, 0.43, 0.80])
im = ax2.imshow(z, cmap="terrain", vmin=1200, vmax=2900)
ax2.set_xticks([]); ax2.set_yticks([])
ax2.set_title("WCS GetCoverage → the values (GeoTIFF, Float32 meters)", fontsize=13, color=NAVY, loc="left")
ax2.plot([100], [50], marker="o", ms=7, mfc="red", mec="white")
ax2.annotate("%.1f m" % z[50, 100], (100, 50), (60, 25), fontsize=13, color="black",
             bbox=dict(fc="white", ec="red"), arrowprops=dict(arrowstyle="-", color="red"))
cax = fig.add_axes([0.915, 0.10, 0.012, 0.68])
cb = fig.colorbar(im, cax=cax)
cb.set_label("elevation, m", fontsize=10)
save(fig, "ws9-wms-vs-wcs.png")

# ---------------------------------------------------------------- ArcGIS REST: the ski areas
ski_info, _ = getjson(SKI, dict(f="pjson"))
ski_count, _ = getjson(SKI + "/query", {"where": "1=1", "returnCountOnly": "true", "f": "json"})
ski_gj, ski_url = getjson(SKI + "/query", {"where": "1=1", "outFields": "NAME", "outSR": 4326, "f": "geojson"})
print("Ski layer fields", [f["name"] for f in ski_info["fields"]], "count", ski_count["count"],
      "maxRecordCount", ski_info["maxRecordCount"])
str_count, _ = getjson(STREAMS + "/query", {"where": "1=1", "returnCountOnly": "true", "f": "json"})
print("UtahStreamsNHD count", str_count["count"])

polys = []
for f in ski_gj["features"]:
    g = f["geometry"]
    rings = g["coordinates"] if g["type"] == "Polygon" else [r for p in g["coordinates"] for r in p]
    polys.append((f["properties"]["NAME"], rings))
xs = [x for _, rings in polys for r in rings for x, y in r]
ys = [y for _, rings in polys for r in rings for x, y in r]
# Wasatch Front group only (most of the 14): crop to Salt Lake / Summit / Utah county resorts
wx0, wx1, wy0, wy1 = -111.90, -111.45, 40.33, 40.72
hs, hs_url = get(DEP_WMS, dict(SERVICE="WMS", VERSION="1.3.0", REQUEST="GetMap",
                               LAYERS="3DEPElevation:Hillshade Gray", STYLES="", CRS="CRS:84",
                               BBOX="%s,%s,%s,%s" % (wx0, wy0, wx1, wy1), WIDTH=900, HEIGHT=1000,
                               FORMAT="image/png"))
print("hillshade GetMap", hs_url)
hsim = Image.open(io.BytesIO(hs)).convert("RGB")
fig, ax = plt.subplots(figsize=(6.4, 7.0))
ax.imshow(hsim, extent=(wx0, wx1, wy0, wy1), aspect=1 / np.cos(np.radians(40.5)))
for name, rings in polys:
    hi = name.startswith("Snowbird")
    for r in rings:
        ax.add_patch(MplPolygon(r, closed=True, fc=(1, 0.3, 0.2, 0.45) if hi else (0, 0.38, 0.72, 0.35),
                                ec="red" if hi else NAVY, lw=1.6 if hi else 1.0))
    rx = np.mean([x for r in rings for x, y in r]); ry = np.mean([y for r in rings for x, y in r])
    if wx0 < rx < wx1 and wy0 < ry < wy1:
        ax.text(rx, ry, name.replace(" Ski and Summer Resort", "").replace(" Mountain Resort", "")
                .replace(" Ski Resort", "").replace(" Ski Area", "").replace(" Resort", ""),
                fontsize=10, color="black", ha="center", va="center", fontweight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=1))
ax.set_xlim(wx0, wx1); ax.set_ylim(wy0, wy1)
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("UGRC SkiAreaBoundaries /query (GeoJSON)\nover a USGS 3DEP WMS hillshade", fontsize=12, color=NAVY)
fig.tight_layout()
save(fig, "ws9-ski-areas-query.png")

# ---------------------------------------------------------------- WFS vs OGC API Features
wfs_b, wfs_url = get(DEEGREE_WFS, dict(SERVICE="WFS", VERSION="2.0.0", REQUEST="GetFeature",
                                       TYPENAMES="app:SGID93_LOCATION_UDOTMap_CityLocations", COUNT=1))
print("WFS GetFeature", wfs_url)
oaf, oaf_url = getjson(PYGEOAPI + "/collections/utah_city_locations/items", dict(f="json", limit=2))
print("OGC API Features", oaf_url, [f["id"] for f in oaf["features"]])
cols, _ = getjson(PYGEOAPI + "/collections", dict(f="json"))
conf, _ = getjson(PYGEOAPI + "/conformance", dict(f="json"))
api, _ = getjson(PYGEOAPI + "/openapi", dict(f="json"))
procs, _ = getjson(PYGEOAPI + "/processes", dict(f="json"))
recs, recs_url = getjson(PYGEOAPI + "/collections/dutch-metadata/items", dict(f="json", limit=1))
print("pygeoapi: collections", len(cols["collections"]), "conformance", len(conf["conformsTo"]),
      "openapi", api["openapi"], "paths", len(api["paths"]), "processes", len(procs["processes"]),
      "records matched", recs.get("numberMatched"))
mp, mp_url = get(PYGEOAPI + "/collections/mapserver_world_map/map",
                 dict(f="png", bbox="-125,24,-66,50", width=900, height=450))
Image.open(io.BytesIO(mp)).convert("RGB").save(os.path.join(OUT, "ws9-ogcapi-map.png"))
print("OGC API Maps", mp_url, "-> wrote ws9-ogcapi-map.png")

# Resource tree of one OGC API server, from its own landing page and listings
by_kind = {}
for c in cols["collections"]:
    rels = {l["rel"].split("/")[-1] for l in c["links"]}
    kind = ("features" if "items" in rels and c.get("itemType") == "feature" else
            "records" if c.get("itemType") == "record" else
            "map" if "map" in rels else "coverage" if "coverage" in rels else "other")
    by_kind.setdefault(kind, []).append(c["id"])
lines = [
    ("demo.pygeoapi.io/master/", NAVY, True),
    ("├── openapi          OpenAPI %s description, %d paths" % (api["openapi"], len(api["paths"])), GRAY, False),
    ("├── conformance      %d conformance classes" % len(conf["conformsTo"]), GRAY, False),
    ("├── collections/     %d collections" % len(cols["collections"]), NAVY, True),
    ("│   ├── utah_city_locations/items        Features → GeoJSON", BLUE, False),
    ("│   ├── lakes/tiles                      Tiles → vector tiles", BLUE, False),
    ("│   ├── mapserver_world_map/map          Maps → PNG", BLUE, False),
    ("│   ├── dutch-metadata/items             Records → %s metadata records" % recs.get("numberMatched"), BLUE, False),
    ("│   └── gdps-temperature/coverage        Coverages → gridded values", BLUE, False),
    ("└── processes/       %d processes (e.g. hello-world)" % len(procs["processes"]), NAVY, True),
]
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.axis("off")
for i, (t, c, b) in enumerate(lines):
    ax.text(0.01, 0.95 - i * 0.098, t, family=MONO, fontsize=13, color=c,
            fontweight="bold" if b else "normal", va="top", transform=ax.transAxes)
save(fig, "ws9-ogcapi-tree.png")

# ---------------------------------------------------------------- What comes back: four panels
wfs_txt = wfs_b.decode("utf8")
start = wfs_txt.find("<app:NAME>")
gml_all = [l.strip() for l in wfs_txt[start:].splitlines()]
keep = ("<app:NAME>", "<app:POP_2000>", "<app:STATE>", "<app:geometry>", "<gml:Point", "<gml:pos>", "</gml:Point>")
gml_lines = []
for l in gml_all:
    if l.startswith(keep):
        if l.startswith("<gml:Point"):
            l = '<gml:Point srsName="EPSG:26912">'
        gml_lines.append(l)
    if l.startswith("</gml:Point>"):
        break
rec = recs["features"][0]["properties"]
panels = [
    ("WMS  GetMap", "a picture", None),
    ("WFS  GetFeature", "the features (GML)", "\n".join(gml_lines)),
    ("WCS  GetCoverage", "the values (GeoTIFF)",
     "\n".join(" ".join("%6.1f" % z[48 + i, 98 + j] for j in range(4)) for i in range(5))
     + "\n\nFloat32 meters\n%d x %d cells" % (z.shape[1], z.shape[0])),
    ("Catalog  (CSW / Records)", "a pointer: metadata",
     "title:   %s\ntype:    %s\nupdated: %s\n\n...plus links to\nwhere the data\nactually lives"
     % (rec.get("title"), rec.get("type"), rec.get("updated")[:10])),
]


def four_panels(nrows, ncols, size, name, aspect=1.0, fs=(10.5, 13)):
    fig, axs = plt.subplots(nrows, ncols, figsize=size)
    for ax, (t, sub, body) in zip(axs.ravel(), panels):
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_box_aspect(aspect)
        for s_ in ax.spines.values():
            s_.set_color(NAVY); s_.set_linewidth(1.5)
        ax.set_title(t + "\n→ " + sub, fontsize=15, color=NAVY, loc="left", fontweight="bold")
        if body is None:
            ax.imshow(topo.crop((250, 0, 750, int(500 * aspect))))
        else:
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.text(0.04, 0.96, body, family=MONO, fontsize=fs[0] if "GML" in sub else fs[1],
                    va="top", transform=ax.transAxes)
    fig.tight_layout()
    save(fig, name)


four_panels(1, 4, (17, 4.6), "ws9-what-comes-back.png", aspect=0.72, fs=(10.3, 15))
four_panels(2, 2, (8.6, 9.4), "ws9-four-answers.png")

# ---------------------------------------------------------------- the 2011 deck's four coverages, one image
covs = [("ogc-coverage-grid-brightness.jpg", "grid: brightness"), ("ogc-coverage-landcover.png", "grid: land cover classes"),
        ("ogc-coverage-multispectral.jpg", "grid: a spectrum per pixel"), ("ogc-coverage-tin.jpg", "TIN: irregular triangles")]
fig, axs = plt.subplots(1, 4, figsize=(16, 4.2))
for ax, (f, cap) in zip(axs, covs):
    ax.imshow(Image.open(os.path.join(OUT, f)).convert("RGB"))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(cap, fontsize=15, color=NAVY)
fig.text(0.5, 0.0, "Images from the 2011 OGC overview deck: Global Science & Technology, Inc. (2003) and UCSC Remote Sensing Group",
         ha="center", fontsize=10, color=GRAY)
fig.tight_layout(rect=(0, 0.04, 1, 1))
save(fig, "ws9-coverages-four.png")

# ---------------------------------------------------------------- OGC API Features: all 31 cities, by paging
cities, url, pages = [], PYGEOAPI + "/collections/utah_city_locations/items?f=json&limit=100", 0
while url and pages < 20:
    d, _ = getjson(url); pages += 1
    cities += d["features"]
    url = next((l["href"] for l in d["links"] if l["rel"] == "next"), None)
print("OGC API Features paging:", len(cities), "cities in", pages, "pages (limit=100 asked)")
cx = [f["geometry"]["coordinates"][0] for f in cities]; cy = [f["geometry"]["coordinates"][1] for f in cities]
cx0, cx1, cy0, cy1 = min(cx) - 0.08, max(cx) + 0.08, min(cy) - 0.06, max(cy) + 0.06
hs2, hs2_url = get(DEP_WMS, dict(SERVICE="WMS", VERSION="1.3.0", REQUEST="GetMap",
                                 LAYERS="3DEPElevation:Hillshade Gray", STYLES="", CRS="CRS:84",
                                 BBOX="%s,%s,%s,%s" % (cx0, cy0, cx1, cy1), WIDTH=1000, HEIGHT=800, FORMAT="image/png"))
print("hillshade GetMap", hs2_url)
fig, ax = plt.subplots(figsize=(7.2, 6.4))
ax.imshow(Image.open(io.BytesIO(hs2)).convert("RGB"), extent=(cx0, cx1, cy0, cy1), aspect=1 / np.cos(np.radians(40.2)))
for f, x, y in zip(cities, cx, cy):
    hi = f["id"] == "Cedar Hills"
    ax.plot(x, y, "o", ms=10 if hi else 6, mfc="red" if hi else BLUE, mec="white", zorder=5)
    if hi or f["id"] in ("PROVO", "Orem", "Payson", "Spanish Fork", "Santaquin"):
        ax.text(x + (0.03 if hi else 0.012), y + (0.0 if hi else 0.01), f["id"].title() if f["id"] == "PROVO" else f["id"], fontsize=11,
                fontweight="bold" if hi else "normal", bbox=dict(fc="white", ec="none", alpha=0.75, pad=1))
ax.set_xlim(cx0, cx1); ax.set_ylim(cy0, cy1); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("utah_city_locations/items — %d cities, %d pages of 10" % (len(cities), pages), fontsize=12, color=NAVY)
save(fig, "ws9-utah-cities-oaf.png")

# ---------------------------------------------------------------- a narrower question: the Provo River
pr, pr_url = getjson(STREAMS + "/query", {"where": "GNIS_Name='Provo River'", "outFields": "GNIS_Name,FCode_Text",
                                         "outSR": 4326, "geometryPrecision": 5, "f": "geojson"})
print("Provo River query", pr_url, len(pr["features"]), "segments")
segs = []
for f in pr["features"]:
    g = f["geometry"]
    segs += [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
px_ = [c[0] for sg in segs for c in sg]; py_ = [c[1] for sg in segs for c in sg]
rx0, rx1, ry0, ry1 = min(px_) - 0.04, max(px_) + 0.04, min(py_) - 0.03, max(py_) + 0.03
hs3, hs3_url = get(DEP_WMS, dict(SERVICE="WMS", VERSION="1.3.0", REQUEST="GetMap",
                                 LAYERS="3DEPElevation:Hillshade Gray", STYLES="", CRS="CRS:84",
                                 BBOX="%s,%s,%s,%s" % (rx0, ry0, rx1, ry1), WIDTH=1100, HEIGHT=800, FORMAT="image/png"))
print("hillshade GetMap", hs3_url)
fig, ax = plt.subplots(figsize=(8, 5.6))
ax.imshow(Image.open(io.BytesIO(hs3)).convert("RGB"), extent=(rx0, rx1, ry0, ry1), aspect=1 / np.cos(np.radians(40.45)))
for sg in segs:
    ax.plot([c[0] for c in sg], [c[1] for c in sg], color=BLUE, lw=2)
ax.set_xlim(rx0, rx1); ax.set_ylim(ry0, ry1); ax.set_xticks([]); ax.set_yticks([])
ax.set_title("UtahStreamsNHD /query  where=GNIS_Name='Provo River'  →  %d segments" % len(pr["features"]),
             fontsize=12, color=NAVY)
save(fig, "ws9-provo-river-query.png")

# ---------------------------------------------------------------- COG: read a window over HTTP
gdal.SetConfigOption("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
gdal.SetConfigOption("CPL_VSIL_NETWORK_STATS_ENABLED", "YES")


def window_read(url):
    gdal.VSICurlClearCache()
    gdal.NetworkStatsReset()
    ds = gdal.Open("/vsicurl/" + url)
    size = gdal.VSIStatL("/vsicurl/" + url).size
    return ds, size


ds, tnm_size = window_read(TNM_TILE)
b = ds.GetRasterBand(1)
gt = ds.GetGeoTransform()
px = int((-111.64 - gt[0]) / gt[1]); py = int((40.25 - gt[3]) / gt[5])
win = b.ReadAsArray(px - 50, py - 50, 100, 100)
st = json.loads(gdal.NetworkStatsGetAsSerializedJSON())
tnm_bytes = st["methods"]["GET"]["downloaded_bytes"]
tnm_gets = st["methods"]["GET"]["count"]
bx, by = b.GetBlockSize()
ovr = [b.GetOverview(i).XSize for i in range(b.GetOverviewCount())]
print("3DEP COG", ds.RasterXSize, ds.RasterYSize, "block", bx, by, "overviews", ovr,
      ds.GetMetadata("IMAGE_STRUCTURE"), "file", tnm_size, "read", tnm_bytes, "in", tnm_gets, "GETs",
      "value at -111.64,40.25 = %.2f" % win[50, 50])

nb = -(-ds.RasterXSize // bx)
fig, ax = plt.subplots(figsize=(6.2, 6.2))
for i in range(nb):
    for j in range(nb):
        ax.add_patch(Rectangle((j, nb - 1 - i), 1, 1, fc="#e8eef6", ec="white", lw=0.8))
bi0, bj0 = (py - 50) // by, (px - 50) // bx
bi1, bj1 = (py + 49) // by, (px + 49) // bx
for i in range(bi0, bi1 + 1):
    for j in range(bj0, bj1 + 1):
        ax.add_patch(Rectangle((j, nb - 1 - i), 1, 1, fc="red", ec="white", lw=0.8))
ax.set_xlim(0, nb); ax.set_ylim(0, nb); ax.set_aspect("equal")
ax.set_xticks([]); ax.set_yticks([])
ax.set_title("USGS_13_n41w112.tif — %d × %d blocks of %d × %d cells" % (nb, nb, bx, by),
             fontsize=12, color=NAVY)
ax.set_xlabel("red: the block GDAL fetched for a 100 × 100-cell window at BYU\n"
              "%s of %s bytes (%.2f %%)\n%d GET requests: the header, then the block"
              % (format(tnm_bytes, ","), format(tnm_size, ","), 100 * tnm_bytes / tnm_size, tnm_gets),
              fontsize=11)
fig.tight_layout()
save(fig, "ws9-cog-blocks.png")

# ---------------------------------------------------------------- STAC search → COG window
stac, stac_url = getjson(EARTH_SEARCH + "/search", {
    "collections": "sentinel-2-l2a", "bbox": "-111.70,40.22,-111.60,40.28",
    "datetime": "2026-09-01T00:00:00Z/2026-10-04T23:59:59Z", "limit": 50})
print("STAC search", stac_url, "matched", stac.get("context", {}).get("matched", stac.get("numberMatched")))
item = [f for f in stac["features"] if f["id"] == "S2A_12TVK_20260920_0_L2A"][0]
tci = item["assets"]["visual"]["href"]
print("item", item["id"], item["properties"]["datetime"], "cloud", item["properties"]["eo:cloud_cover"], tci)
sds, s2_size = window_read(tci)
s = osr.SpatialReference(); s.ImportFromEPSG(4326); s.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
t = osr.SpatialReference(); t.ImportFromWkt(sds.GetProjection()); t.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
ct = osr.CoordinateTransformation(s, t)
x0, y0, _ = ct.TransformPoint(BBOX[0], BBOX[1]); x1, y1, _ = ct.TransformPoint(BBOX[2], BBOX[3])
gdal.Translate("/vsimem/s2.tif", sds, projWin=[x0, y1, x1, y0])
st = json.loads(gdal.NetworkStatsGetAsSerializedJSON())
s2_bytes = st["methods"]["GET"]["downloaded_bytes"]
w = gdal.Open("/vsimem/s2.tif")
rgb = np.dstack([w.GetRasterBand(k).ReadAsArray() for k in (1, 2, 3)])
Image.fromarray(rgb).resize((rgb.shape[1] * 2, rgb.shape[0] * 2), Image.LANCZOS).save(
    os.path.join(OUT, "ws9-s2-byu-cog.png"))
print("Sentinel-2 TCI", sds.RasterXSize, sds.GetMetadata("IMAGE_STRUCTURE"), "file", s2_size,
      "read", s2_bytes, "window", rgb.shape, "-> wrote ws9-s2-byu-cog.png")

# ---------------------------------------------------------------- bytes moved
fig, ax = plt.subplots(figsize=(10, 3.6))
rows = [("3DEP 1/3″ tile n41w112\nwhole file (Lab 7 source)", tnm_size, "#9aa5b1"),
        ("3DEP tile\n100 × 100-cell window", tnm_bytes, BLUE),
        ("Sentinel-2 true color\nwhole file", s2_size, "#9aa5b1"),
        ("Sentinel-2\nBYU window", s2_bytes, BLUE)]
yy = np.arange(len(rows))[::-1]
ax.barh(yy, [r[1] / 1e6 for r in rows], color=[r[2] for r in rows])
for y_, r in zip(yy, rows):
    ax.text(r[1] / 1e6 * 1.15, y_, "%.2f MB" % (r[1] / 1e6), va="center", fontsize=12)
ax.set_yticks(yy); ax.set_yticklabels([r[0] for r in rows], fontsize=11)
ax.set_xscale("log"); ax.set_xlim(0.3, 3000)
ax.set_xlabel("megabytes moved over the network (log scale), measured 2026-10-05", fontsize=11)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
fig.tight_layout()
save(fig, "ws9-bytes-moved.png")

# ---------------------------------------------------------------- standards are documents
docs = [
    ("Classic (XML, key=value)", [("WMS 1.3.0", "06-042"), ("WFS 2.0.2", "09-025r2"),
                                 ("WCS 2.1", "17-089r1"), ("CSW 3.0", "12-168r6")]),
    ("OGC API (JSON, OpenAPI)", [("Features Part 1", "17-069r4"), ("Tiles Part 1", "20-057"),
                                ("Maps Part 1", "20-058"), ("Records Part 1", "20-004r1"),
                                ("Processes Part 1", "18-062r2")]),
    ("Cloud-native", [("Cloud Optimized GeoTIFF", "21-026"), ("STAC 1.1.0 (Community Std.)", "25-004"),
                      ("STAC API 1.0.0 (Community Std.)", "25-005")]),
]
fig, ax = plt.subplots(figsize=(7.5, 6.6))
ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
y = 0.98
for head, items in docs:
    ax.text(0.0, y, head, fontsize=14, color=NAVY, fontweight="bold", va="top")
    y -= 0.065
    for name, num in items:
        ax.add_patch(Rectangle((0.02, y - 0.05), 0.96, 0.052, fc="#f2f5f9", ec="#c9d3df"))
        ax.text(0.04, y - 0.024, name, fontsize=12, va="center")
        ax.text(0.96, y - 0.024, "OGC " + num, fontsize=12, va="center", ha="right", family=MONO, color=GRAY)
        y -= 0.06
    y -= 0.03
save(fig, "ws9-standards-docs.png")
# ---------------------------------------------------------------- QR code for the activity slide
# Local qrcode package (pip install qrcode[pil]); no third-party QR service. The first run made this
# with the standalone Python 3.14, where qrcode is installed.
try:
    import qrcode
    q = qrcode.QRCode(border=3, error_correction=qrcode.constants.ERROR_CORRECT_L)
    q.add_data(SKI); q.make(fit=True)
    q.make_image(fill_color="black", back_color="white").save(os.path.join(OUT, "ws9-ski-layer-qr.png"))
    print("wrote ws9-ski-layer-qr.png,", q.modules_count, "modules")
except ImportError:
    print("qrcode not installed here: ws9-ski-layer-qr.png left as is")
print("done")
