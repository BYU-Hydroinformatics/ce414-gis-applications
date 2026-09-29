"""Terrain figures for the Week 5 elevation-data deck, written into slides/week-05/images.

    python tools/week05_terrain_figures.py

All three figures use one place and one elevation dataset so they tell one story:
Mount Timpanogos, seen from Provo, Utah.

ed-surface-to-dem.png          photo of the mountain on top, the same view rendered from the DEM below
ed-four-dem-types.png          one real DEM patch drawn four ways: square grid, TIN, contours, random points
ed-elevation-grid-anatomy.png  a 6 x 8 block of real cell values with rows, columns, cell size, origin, NoData

Data
    Elevation: USGS 3D Elevation Program (3DEP) dynamic elevation service
    (elevation.nationalmap.gov .../3DEPElevation/ImageServer/exportImage), requested as 30 m cells
    in NAD83 / UTM zone 12N (EPSG:26912), bilinear. The 150 m grid used in every figure is the block
    mean of 5 x 5 of those 30 m cells, aligned to the download origin.
    Photo: "Mount Timpanogos - 01-07-08.jpg" by a4gpa (Flickr), CC BY-SA 2.0, via Wikimedia Commons,
    https://commons.wikimedia.org/wiki/File:Mount_Timpanogos_-_01-07-08.jpg

Camera
    The render in ed-surface-to-dem.png uses the viewpoint recovered by fitting the DEM skyline to a
    hand-traced skyline of the photo (27 degree horizontal field of view from the photo's 75 mm-equivalent
    focal length): camera at 443,250 E, 4,453,250 N (south Provo), ground + 15 m, looking 6 degrees east
    of north, tilted up 7.8 degrees. The RMS skyline misfit was 0.1 degree.

Downloads are cached in %TEMP%/ce414-week05-terrain so reruns are offline and fast.
Needs numpy, scipy, matplotlib, pillow, requests.
"""
import io
import os
import tempfile
import time

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm, ListedColormap
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle, FancyArrowPatch
import matplotlib.patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "slides", "week-05", "images")
CACHE = os.path.join(tempfile.gettempdir(), "ce414-week05-terrain")
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "CE414-course-figures/1.0 (+https://github.com/BYU-Hydroinformatics/ce414-gis-applications)"}

NAVY, ORANGE, GRAY, INK = "#002e5d", "#e8792b", "#5a6472", "#1b1f24"
FONT = "Segoe UI"
plt.rcParams.update({"font.family": FONT, "font.size": 16})

# Hypsometric ramp shared by all three figures (meters).
STOPS = [(1350, "#3f7f3a"), (1700, "#8db660"), (2000, "#e3d98c"), (2400, "#d2a263"),
         (2800, "#a0714c"), (3200, "#9e948c"), (3600, "#f4f2ee")]
ZMIN, ZMAX = STOPS[0][0], STOPS[-1][0]
RAMP = LinearSegmentedColormap.from_list("hyps", [((z - ZMIN) / (ZMAX - ZMIN), c) for z, c in STOPS])


def ramp(z):
    return np.asarray(RAMP(np.clip((np.asarray(z, float) - ZMIN) / (ZMAX - ZMIN), 0, 1)))[..., :3]


# ----------------------------------------------------------------------------------------------- data
X0, Y0, X1, Y1, CS = 430000, 4446000, 464000, 4482000, 30
URL = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage"


def _tile(x0, y0, x1, y1):
    w, h = round((x1 - x0) / CS), round((y1 - y0) / CS)
    p = {"bbox": f"{x0},{y0},{x1},{y1}", "bboxSR": 26912, "imageSR": 26912, "size": f"{w},{h}",
         "format": "tiff", "pixelType": "F32", "noDataInterpretation": "esriNoDataMatchAny",
         "interpolation": "RSP_BilinearInterpolation", "f": "image"}
    for _ in range(15):          # the service returns 504s under load; retry
        try:
            r = requests.get(URL, params=p, timeout=120, headers=UA)
            if r.status_code == 200 and r.content[:2] in (b"II", b"MM"):
                a = np.array(Image.open(io.BytesIO(r.content)), dtype=np.float32)
                if a.shape == (h, w):
                    return a
        except requests.RequestException:
            pass
        time.sleep(3)
    raise SystemExit(f"3DEP request failed for {x0},{y0}")


def dem30():
    f = os.path.join(CACHE, "dem30.npy")
    if not os.path.exists(f):
        T, rows = 6000, []
        for ty in range(Y1, Y0, -T):
            rows.append(np.hstack([_tile(tx, max(ty - T, Y0), min(tx + T, X1), ty) for tx in range(X0, X1, T)]))
            print("  3DEP row", ty)
        np.save(f, np.vstack(rows))
    return np.load(f)


def photo():
    f = os.path.join(CACHE, "timpanogos.jpg")
    if not os.path.exists(f):
        r = requests.get("https://commons.wikimedia.org/w/api.php", headers=UA, params={
            "action": "query", "titles": "File:Mount Timpanogos - 01-07-08.jpg", "prop": "imageinfo",
            "iiprop": "url", "iiurlwidth": 2000, "format": "json"}).json()
        url = next(iter(r["query"]["pages"].values()))["imageinfo"][0]["thumburl"]
        open(f, "wb").write(requests.get(url, headers=UA).content)
    return Image.open(f).convert("RGB")


DEM = dem30()
NR, NC = DEM.shape
C5 = 5 * CS   # 150 m
G150 = DEM[:NR // 5 * 5, :NC // 5 * 5].reshape(NR // 5, 5, NC // 5, 5).mean((1, 3))


def hillshade(z, cs, az=315, alt=45):
    gy, gx = np.gradient(z, cs)          # array rows run south, so gy is -dz/dNorth
    dzdx, dzdy = gx, -gy
    slope = np.arctan(np.hypot(dzdx, dzdy))
    aspect = np.arctan2(-dzdx, -dzdy)    # downslope direction, radians clockwise from north
    a, e = np.radians(az), np.radians(alt)
    return np.clip(np.sin(e) * np.cos(slope) + np.cos(e) * np.sin(slope) * np.cos(a - aspect), 0, 1)


def patch(grid, cs, x0, y0, x1, y1):
    """Rows/cols of `grid` (origin X0,Y1, cell cs) covering x0..x1, y0..y1, and the array."""
    c0, c1 = int((x0 - X0) / cs), int((x1 - X0) / cs)
    r0, r1 = int((Y1 - y1) / cs), int((Y1 - y0) / cs)
    return grid[r0:r1, c0:c1]


# ------------------------------------------------------------------------------ figure 1: surface → DEM
MESH = 150
CAM = dict(cx=443250.0, cy=4453250.0, az=6.0, fov=27.0, pitch=7.8)
SKY_TOP, SKY_BOT = np.array([0.80, 0.86, 0.93]), np.array([0.95, 0.96, 0.98])


def render_view(W, H, mesh=MESH):
    """Perspective render of the 30 m DEM from the photo's camera (a ray-marched height field),
    colored by elevation, hillshaded, with the outlines of `mesh`-meter grid cells drawn on it."""
    cx, cy = CAM["cx"], CAM["cy"]
    ch = float(map_coordinates(DEM, [[(Y1 - cy) / CS - .5], [(cx - X0) / CS - .5]], order=1)[0]) + 15
    f = W / 2 / np.tan(np.radians(CAM["fov"] / 2))
    horizon = H / 2 + f * np.tan(np.radians(CAM["pitch"]))
    hs = hillshade(DEM, CS, az=240, alt=35)       # low sun from the southwest models the ravines the camera sees
    u = np.arange(W) - W / 2 + 0.5
    off = np.arctan(u / f)
    ang = np.radians(CAM["az"]) + off
    yy = np.arange(H)[:, None] / H
    img = SKY_TOP * (1 - yy[..., None]) + SKY_BOT * yy[..., None]
    img = np.repeat(img, W, axis=1)
    cell = np.full((H, W), -1, dtype=np.int64)
    ybuf = np.full(W, float(H))
    for t in np.geomspace(60, 34000, 5000):
        x = cx + np.sin(ang) * t
        y = cy + np.cos(ang) * t
        r, c = (Y1 - y) / CS - 0.5, (x - X0) / CS - 0.5
        z = map_coordinates(DEM, [r, c], order=1, mode="nearest")
        h = map_coordinates(hs, [r, c], order=1, mode="nearest")
        cid = ((Y1 - y) // mesh).astype(np.int64) * 100000 + ((x - X0) // mesh).astype(np.int64)
        z = z - t * t / (2 * 6371000) * 0.87                # earth curvature less refraction
        sy = horizon - f * (z - ch) / (t * np.cos(off))
        haze = min(t / 70000, 0.3)
        col = ramp(z) * (0.35 + 0.65 * h)[:, None] * (1 - haze) + SKY_BOT * haze
        for j in np.where(sy < ybuf)[0]:
            y0, y1 = max(int(sy[j]), 0), int(ybuf[j])
            if y1 > y0:
                img[y0:y1, j] = col[j]
                cell[y0:y1, j] = cid[j]
            ybuf[j] = sy[j]
    ground = cell >= 0
    edge = np.zeros_like(ground)
    edge[:, 1:] |= (cell[:, 1:] != cell[:, :-1]) & ground[:, 1:] & ground[:, :-1]
    edge[1:, :] |= (cell[1:, :] != cell[:-1, :]) & ground[1:, :] & ground[:-1, :]
    img[edge] = img[edge] * 0.45 + np.array([0.05, 0.08, 0.12]) * 0.55
    return np.clip(img, 0, 1)


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", name), size)


def frac(box, size):
    return tuple(round(v * size[k % 2]) for k, v in enumerate(box))


def fig_surface_to_dem():
    W, H = 900, 1640
    PW, CROP = 860, (0.125, 0.36, 0.975, 1.0)     # fraction of the frame: the mountain, not the sky
    ph = photo(); ph = ph.crop(frac(CROP, ph.size))
    ph = ph.resize((PW, round(PW * ph.height / ph.width)), Image.LANCZOS)
    full = render_view(2000, 1328)
    rd = Image.fromarray((full * 255).astype(np.uint8)); rd = rd.crop(frac(CROP, rd.size)).resize(ph.size, Image.LANCZOS)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    x = (W - PW) // 2
    y = 18
    d.text((W // 2, y), "The real surface", font=font(46, True), fill=NAVY, anchor="ma")
    y += 70
    im.paste(ph, (x, y)); d.rectangle([x, y, x + PW - 1, y + ph.height - 1], outline=NAVY, width=3)
    y += ph.height + 8
    d.text((W // 2, y), "Mount Timpanogos from Provo", font=font(36), fill=GRAY, anchor="ma")
    y += 52
    # arrow
    ax, a0, a1 = W // 2, y + 6, y + 150
    d.rectangle([ax - 24, a0, ax + 24, a1 - 60], fill=ORANGE)
    d.polygon([(ax - 66, a1 - 62), (ax + 66, a1 - 62), (ax, a1)], fill=ORANGE)
    d.text((ax + 88, (a0 + a1) // 2 - 4), "measure\nand grid", font=font(34, True), fill=ORANGE, anchor="lm", spacing=2)
    y = a1 + 16
    d.text((W // 2, y), "The DEM: a grid of elevations", font=font(46, True), fill=NAVY, anchor="ma")
    y += 70
    im.paste(rd, (x, y)); d.rectangle([x, y, x + PW - 1, y + rd.height - 1], outline=NAVY, width=3)
    y += rd.height + 8
    d.text((W // 2, y), "Same view from the DEM, 150 m cells outlined", font=font(36), fill=GRAY, anchor="ma")
    y += 64
    # zoom: real 150 m cell values at the summit
    r, c = int((Y1 - 4471333) // C5), int((445181 - X0) // C5)
    vals = np.round(G150[r - 1:r + 2, c - 2:c + 3]).astype(int)
    cw, chh = 172, 78
    gx = (W - 5 * cw) // 2
    for i in range(3):
        for j in range(5):
            v = vals[i, j]
            fill = tuple(int(255 * q) for q in ramp(v))
            d.rectangle([gx + j * cw, y + i * chh, gx + (j + 1) * cw, y + (i + 1) * chh], fill=fill, outline=NAVY, width=3)
            d.text((gx + j * cw + cw // 2, y + i * chh + chh // 2), f"{v:,}", font=font(38, True), fill=INK, anchor="mm")
    y += 3 * chh + 8
    d.text((W // 2, y), "Summit cells: one number each (meters)", font=font(36), fill=GRAY, anchor="ma")
    y += 50
    im = im.crop((0, 0, W, y))
    p = os.path.join(OUT, "ed-surface-to-dem.png"); im.save(p, optimize=True); print(p, im.size)


# ------------------------------------------------------------------------- figure 2: four DEM types
PX0, PX1, PY0, PY1 = 442750, 447250, 4469700, 4472400     # 4.5 x 2.7 km over the summit ridge, on 150 m cell edges


def tin_points(z, cs, n=260):
    """Greedy TIN: start from the corners, keep adding the cell the current TIN misses by most."""
    h, w = z.shape
    yy, xx = np.mgrid[0:h, 0:w]
    pts = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    for k in range(1, 6):   # a few boundary points so edges are not one long sliver
        pts += [(0, k * (w - 1) // 6), (h - 1, k * (w - 1) // 6)]
    for k in range(1, 4):
        pts += [(k * (h - 1) // 4, 0), (k * (h - 1) // 4, w - 1)]
    while len(pts) < n:
        P = np.array(pts)
        f = LinearNDInterpolator(P[:, ::-1], z[P[:, 0], P[:, 1]])
        err = np.abs(f(xx, yy) - z)
        for rr, cc in P:                      # suppress picks right next to existing points
            err[max(rr - 3, 0):rr + 4, max(cc - 3, 0):cc + 4] = 0
        for _ in range(12):
            i = np.nanargmax(err); rr, cc = divmod(i, w)
            pts.append((rr, cc)); err[max(rr - 4, 0):rr + 5, max(cc - 4, 0):cc + 5] = 0
    P = np.array(pts[:n])
    return P[:, 1] * cs + cs / 2, (h - P[:, 0]) * cs - cs / 2, z[P[:, 0], P[:, 1]]


def fig_four_types():
    z30 = patch(DEM, CS, PX0, PY0, PX1, PY1)
    z150 = patch(G150, C5, PX0, PY0, PX1, PY1)
    h, w = z30.shape
    ext = (0, w * CS, 0, h * CS)                          # local meters from the patch's lower-left
    fig = plt.figure(figsize=(14, 9.5), dpi=100)
    axs = [fig.add_axes([0.012 + (i % 2) * 0.445, 0.525 - (i // 2) * 0.45, 0.43, 0.38]) for i in range(4)]
    titles = ["(a) Square grid of cells", "(b) Triangulated irregular network (TIN)",
              "(c) Contour lines", "(d) Randomly located points"]
    for ax, t in zip(axs, titles):
        ax.set_xlim(0, w * CS); ax.set_ylim(0, h * CS); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color(NAVY); s.set_linewidth(1.6)
        ax.set_title(t, fontsize=23, fontweight="bold", color=NAVY, loc="left", pad=8)
    norm = plt.Normalize(ZMIN, ZMAX)

    # (a) grid
    a = axs[0]
    a.imshow(z150, cmap=RAMP, norm=norm, extent=ext, interpolation="nearest")
    for k in range(z150.shape[1] + 1):
        a.axvline(k * C5, color="white", lw=0.8, alpha=0.9)
    for k in range(z150.shape[0] + 1):
        a.axhline(k * C5, color="white", lw=0.8, alpha=0.9)
    rr, cc = np.unravel_index(np.argmax(z150), z150.shape)
    a.add_patch(Rectangle((cc * C5, (z150.shape[0] - rr - 1) * C5), C5, C5, fill=False, ec=NAVY, lw=3))
    a.annotate(f"this cell: {int(round(z150[rr, cc])):,} m", ((cc + 1) * C5, (z150.shape[0] - rr - 0.5) * C5),
               xytext=((cc + 1.5) * C5, (z150.shape[0] - rr + 2.6) * C5), fontsize=19, fontweight="bold", color=NAVY,
               arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2),
               path_effects=[pe.withStroke(linewidth=4, foreground="white")])

    # (b) TIN
    b = axs[1]
    tx, ty, tz = tin_points(z30, CS, n=150)
    tri = Delaunay(np.c_[tx, ty])
    polys, cols = [], []
    L = np.array([-np.sin(np.radians(45)) * np.cos(np.radians(45)), np.cos(np.radians(45)) * np.cos(np.radians(45)),
                  np.sin(np.radians(45))])   # light from the northwest, 45 degrees up
    for s in tri.simplices:
        p = np.c_[tx[s], ty[s], tz[s]]
        nrm = np.cross(p[1] - p[0], p[2] - p[0]); nrm = nrm / np.linalg.norm(nrm)
        if nrm[2] < 0:
            nrm = -nrm
        shade = 0.62 + 0.38 * max(float(nrm @ L), 0)
        polys.append(p[:, :2]); cols.append(ramp(p[:, 2].mean()) * shade)
    b.add_collection(PolyCollection(polys, facecolors=cols, edgecolors=(0.1, 0.12, 0.15, 0.55), linewidths=0.7))
    b.plot(tx, ty, "o", ms=3, color=INK)
    b.text(0.02, 0.04, f"{len(tx)} points, {len(tri.simplices)} triangles", transform=b.transAxes, fontsize=19,
           color=INK, fontweight="bold", bbox=dict(fc="white", ec="none", alpha=0.88, pad=3))

    # (c) contours
    c = axs[2]
    c.set_facecolor("#fbfaf7")
    X = np.arange(w) * CS + CS / 2; Y = (h - np.arange(h)) * CS - CS / 2
    lv = np.arange(1800, 3601, 100)
    c.contour(X, Y, z30, levels=[v for v in lv if v % 500], colors="#8a5a2b", linewidths=0.9)
    ci = c.contour(X, Y, z30, levels=[v for v in lv if v % 500 == 0], colors="#6b3f17", linewidths=2.2)
    cl = c.clabel(ci, fmt=lambda v: f"{int(v):,}", fontsize=17, inline_spacing=6)
    for t in cl:
        t.set_fontweight("bold")
    c.text(0.02, 0.04, "100 m interval, labeled every 500 m", transform=c.transAxes, fontsize=19, color=INK,
           fontweight="bold", bbox=dict(fc="white", ec="none", alpha=0.92, pad=3))

    # (d) random points
    d = axs[3]
    d.set_facecolor("#fbfaf7")
    rng = np.random.default_rng(414)
    n = 60
    px, py = rng.uniform(0, w * CS, n), rng.uniform(0, h * CS, n)
    inner = (px > 350) & (px < w * CS - 700) & (py > 250) & (py < h * CS - 300)
    pz = map_coordinates(z30, [(h * CS - py) / CS - 0.5, px / CS - 0.5], order=1, mode="nearest")
    d.scatter(px, py, c=pz, cmap=RAMP, norm=norm, s=120, edgecolors=INK, linewidths=1.2, zorder=3)
    # label a spread-out handful
    lab = []
    for i in rng.permutation(n):
        if inner[i] and all(np.hypot(px[i] - px[j], py[i] - py[j]) > 1000 for j in lab):
            lab.append(i)
        if len(lab) == 7:
            break
    for i in lab:
        d.text(px[i] + 110, py[i], f"{int(round(pz[i])):,} m", fontsize=19, va="center",
               fontweight="bold", color=INK, zorder=4, path_effects=[pe.withStroke(linewidth=4, foreground="white")])

    # scale bar on (a) and a shared color bar
    sb = axs[0]
    x0, y0 = w * CS - 1200, 250
    sb.add_patch(Rectangle((x0, y0), 1000, 90, color="white", ec=INK, lw=1.5, zorder=5))
    sb.add_patch(Rectangle((x0, y0), 500, 90, color=INK, zorder=6))
    sb.text(x0 + 500, y0 + 150, "1 km", ha="center", fontsize=19, fontweight="bold", color=INK, zorder=6,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])
    cax = fig.add_axes([0.9, 0.12, 0.016, 0.72])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(2200, 3600), cmap=LinearSegmentedColormap.from_list(
        "sub", ramp(np.linspace(2200, 3600, 64)))), cax=cax)
    cb.set_ticks([2250, 2500, 2750, 3000, 3250, 3500]); cb.set_ticklabels([f"{v:,}" for v in (2250, 2500, 2750, 3000, 3250, 3500)]); cb.ax.tick_params(labelsize=18)
    cb.set_label("Elevation (m)", fontsize=20, color=NAVY)
    fig.text(0.012, 0.018, "Same 4.5 x 2.7 km patch of Mount Timpanogos in every panel. USGS 3DEP elevation.",
             fontsize=18, color=GRAY)
    p = os.path.join(OUT, "ed-four-dem-types.png"); fig.savefig(p, dpi=100, facecolor="white"); plt.close(fig)
    print(p)


# ---------------------------------------------------------------------- figure 3: grid anatomy
def fig_anatomy():
    NROW, NCOL = 6, 8
    # a block of 150 m cells on the summit ridge: the northwest cirque wall rising to the peak
    rs, cs0 = int((Y1 - 4471333) // C5) - 2, int((445181 - X0) // C5) - 6
    vals = np.round(G150[rs:rs + NROW, cs0:cs0 + NCOL]).astype(int)
    ox, oy = X0 + cs0 * C5, Y1 - (rs + NROW) * C5          # lower-left corner of the block
    nodata = {(0, 0), (0, 1), (1, 0)}                        # illustrative: cells outside a clip boundary
    fig = plt.figure(figsize=(14, 8.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1400); ax.set_ylim(800, 0); ax.axis("off")
    CW = 76
    gx, gy = 110, 118

    def txt(x, y, s, size=18, color=INK, weight="normal", ha="left", va="center", **kw):
        ax.text(x, y, s, fontsize=size * 0.72, color=color, fontweight=weight, ha=ha, va=va, **kw)

    txt(gx - 40, 34, "Stored: one elevation per cell (m)", 32, NAVY, "bold")
    for i in range(NROW):
        for j in range(NCOL):
            x, y = gx + j * CW, gy + i * CW
            if (i, j) in nodata:
                ax.add_patch(Rectangle((x, y), CW, CW, fc="#eceff2", ec=NAVY, lw=1.5, hatch="///", zorder=1))
                txt(x + CW / 2, y + CW / 2, "NoData", 17, NAVY, "bold", ha="center",
                    bbox=dict(fc="#eceff2", ec="none", pad=1))
            else:
                ax.add_patch(Rectangle((x, y), CW, CW, fc="white", ec=NAVY, lw=1.5))
                txt(x + CW / 2, y + CW / 2, f"{vals[i, j]:,}", 25, INK, "bold", ha="center")
    gw, gh = NCOL * CW, NROW * CW
    arr = dict(arrowstyle="<|-|>", color=NAVY, lw=2.2, mutation_scale=22)
    ax.annotate("", (gx, gy + gh + 50), (gx + gw, gy + gh + 50), arrowprops=arr)
    txt(gx + gw / 2, gy + gh + 84, f"number of columns: {NCOL}", 26, NAVY, "bold", ha="center")
    ax.annotate("", (gx - 34, gy), (gx - 34, gy + gh), arrowprops=arr)
    txt(gx - 62, gy + gh / 2, f"number of rows: {NROW}", 26, NAVY, "bold", ha="center", rotation=90)
    # cell size bracket on the top-right cell
    cxr = gx + gw - CW
    ax.annotate("", (cxr, gy - 14), (cxr + CW, gy - 14),
                arrowprops=dict(arrowstyle="|-|", color=ORANGE, lw=2.4, mutation_scale=8))
    txt(cxr + CW, gy - 44, "cell size: 150 m", 24, ORANGE, "bold", ha="right")
    # origin
    RED = "#c8102e"
    ax.plot([gx, gx], [gy + gh, gy + gh + 150], color=RED, lw=2, zorder=4)
    ax.plot([gx], [gy + gh], "o", ms=15, color=RED, zorder=5)
    txt(gx + 12, gy + gh + 150, f"(X, Y) origin, lower-left corner:  {ox:,.0f} E,  {oy:,.0f} N", 23, RED, "bold")
    txt(gx + 12, gy + gh + 182, "NAD83 / UTM zone 12N, meters", 21, GRAY)

    # right side: the same numbers with color applied
    rx, ry, SW = 905, gy + 10, 50
    txt(rx - 20, 34, "Shown: color applied", 32, NAVY, "bold")
    txt(rx - 20, 74, "to those numbers", 32, NAVY, "bold")
    ay = ry + NROW * SW / 2
    ax.add_patch(FancyArrowPatch((gx + gw + 14, ay), (rx - 14, ay),
                                 arrowstyle="simple,head_width=24,head_length=24,tail_width=10", color=ORANGE))
    txt((gx + gw + rx) / 2, ay - 36, "symbolize", 22, ORANGE, "bold", ha="center")
    breaks = [2950, 3100, 3200, 3300, 3400, 3550]
    pal = ["#4f8f45", "#a9cc6e", "#f0dc8c", "#d6995a", "#9c6a4a"]
    for i in range(NROW):
        for j in range(NCOL):
            x, y = rx + j * SW, ry + i * SW
            if (i, j) in nodata:
                ax.add_patch(Rectangle((x, y), SW, SW, fc="white", ec="#9aa3ad", lw=1, hatch="///"))
            else:
                k = int(np.searchsorted(breaks, vals[i, j], side="right")) - 1
                ax.add_patch(Rectangle((x, y), SW, SW, fc=pal[k], ec="white", lw=1.2))
    ly = ry + NROW * SW + 34
    for k in range(len(pal)):
        ax.add_patch(Rectangle((rx, ly + k * 36), 40, 28, fc=pal[k], ec=INK, lw=0.8))
        txt(rx + 52, ly + k * 36 + 14, f"{breaks[k]:,} – {breaks[k + 1]:,}", 22, INK)
    nx = rx + 250
    ax.add_patch(Rectangle((nx, ly), 40, 28, fc="white", ec="#9aa3ad", lw=1, hatch="///"))
    txt(nx + 52, ly + 14, "NoData", 22, INK)
    for n, s in enumerate(("New classes or", "colors: a new", "picture, the", "same numbers.")):
        txt(nx, ly + 72 + n * 28, s, 21, GRAY)
    p = os.path.join(OUT, "ed-elevation-grid-anatomy.png"); fig.savefig(p, dpi=100, facecolor="white"); plt.close(fig)
    print(p, "origin", ox, oy, "values", vals.min(), vals.max())


if __name__ == "__main__":
    import sys
    FIGS = {"surface": fig_surface_to_dem, "types": fig_four_types, "anatomy": fig_anatomy}
    for name in sys.argv[1:] or FIGS:     # e.g. `python tools/week05_terrain_figures.py anatomy`
        FIGS[name]()
