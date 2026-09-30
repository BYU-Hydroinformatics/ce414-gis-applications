"""Generate the Lab 5 tool icons and infographics as SVG with real text.

    python make_svgs.py   (ArcGIS Pro Python; needs C:\\Ames\\Lab05\\Check.gdb from run_model.py)

Writes into docs/assignments/lab-05/images/:
  icon-*.svg                     the eight tool icons (same palette and frame as Labs 1, 2 and 4)
  lab05-dem-metadata.svg         Figure A, the six metadata questions for the DEM extract
  lab05-d8-patch.svg             Figure B, a real 5 x 5 patch of the filled Rock Canyon DEM, its
                                 D8 codes as ArcGIS Pro computed them, and the accumulation they give
  lab05-model-diagram.svg        Figure C, the structure of the model (a diagram, not an export)
"""
import json
import math
import pathlib

import arcpy
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / "docs" / "assignments" / "lab-05" / "images"
GDB = r"C:\Ames\Lab05\Check.gdb"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, GREEN, LGREEN, INK = (
    "#002e5d", "#0062b8", "#cfe3f7", "#9aa5b1", "#e6eaee", "#e8862a", "#fdebd9", "#3b8a3e", "#d7ecd4", "#1c2733")
YELLOW, LYELLOW = "#c9a400", "#fff4c2"
FONT = "font-family='Segoe UI, Roboto, Helvetica, Arial, sans-serif'"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def text(x, y, s, size=12, weight="normal", fill=INK, anchor="start"):
    return (f"<text x='{x}' y='{y}' font-size='{size}' font-weight='{weight}' fill='{fill}' "
            f"text-anchor='{anchor}' {FONT}>{esc(s)}</text>")


def arrowhead(x, y, ang, col, size=7):
    a1, a2 = ang + math.radians(150), ang - math.radians(150)
    return (f"<polygon points='{x:.1f},{y:.1f} {x + size * math.cos(a1):.1f},{y + size * math.sin(a1):.1f} "
            f"{x + size * math.cos(a2):.1f},{y + size * math.sin(a2):.1f}' fill='{col}'/>")


def icon(name, title, body):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 90' width='120' height='90' role='img' "
           f"aria-label='{esc(title)}'><title>{esc(title)}</title>{body}</svg>")
    (OUT / f"icon-{name}.svg").write_text(svg, encoding="utf-8")


def grid(x, y, nr, nc, cell, fills, stroke=GRAY):
    s = ""
    for r in range(nr):
        for c in range(nc):
            s += (f"<rect x='{x + c * cell}' y='{y + r * cell}' width='{cell}' height='{cell}' "
                  f"fill='{fills(r, c)}' stroke='{stroke}' stroke-width='0.8'/>")
    return s


def icons():
    # Fill: a profile with a pit, the pit filled in orange to its spill level
    body = (f"<path d='M8,30 L30,48 L44,70 L58,62 L70,44 L90,52 L112,78 L112,84 L8,84 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M38,62 L44,70 L58,62 L60,62 Z' fill='none'/>"
            f"<path d='M37.3,59 L44,70 L58,62 L60.7,59 Z' fill='{ORANGE}' fill-opacity='0.85'/>"
            f"<line x1='30' y1='59' x2='72' y2='59' stroke='{ORANGE}' stroke-width='1.2' stroke-dasharray='3 2'/>"
            f"<path d='M72,40 C84,30 96,36 104,46' fill='none' stroke='{BLUE}' stroke-width='1.8'/>" + arrowhead(104, 46, math.radians(50), BLUE))
    icon("fill", "Fill: raise every pit in an elevation surface to the level where it spills", body)

    # Flow Direction: 3 x 3 grid, arrows from each outer cell to its steepest neighbor
    body = grid(15, 5, 3, 3, 26, lambda r, c: LORANGE if (r, c) == (2, 2) else "white")
    dirs = {(0, 0): (1, 1), (0, 1): (1, 1), (0, 2): (1, 0), (1, 0): (1, 1), (1, 1): (1, 1), (1, 2): (1, 0), (2, 0): (0, 1), (2, 1): (0, 1)}
    for (r, c), (dr, dc) in dirs.items():
        cx, cy = 15 + c * 26 + 13, 5 + r * 26 + 13
        ang = math.atan2(dr, dc)
        x2, y2 = cx + 9 * math.cos(ang), cy + 9 * math.sin(ang)
        body += f"<line x1='{cx - 7 * math.cos(ang):.1f}' y1='{cy - 7 * math.sin(ang):.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{NAVY}' stroke-width='1.6'/>" + arrowhead(x2, y2, ang, NAVY, 5)
    icon("flow-direction", "Flow Direction: each cell coded with the neighbor its water flows to", body)

    # Flow Accumulation: cells shaded by how much drains through them, darkest at the outlet
    shade = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 2, 1, 0], [1, 3, 3, 4]]
    tones = ["white", LORANGE, "#f6b77a", ORANGE, "#b85f12"]
    body = grid(12, 5, 4, 4, 20, lambda r, c: tones[shade[r][c]])
    body += f"<path d='M96,75 L108,75' stroke='{NAVY}' stroke-width='2'/>" + arrowhead(112, 75, 0, NAVY, 7)
    icon("flow-accumulation", "Flow Accumulation: the number of upstream cells that drain through each cell", body)

    # Snap Pour Point: a point off the stream moves onto it
    body = (f"<path d='M6,20 C30,30 44,58 70,62 C88,65 100,70 116,84' fill='none' stroke='{BLUE}' stroke-width='5' stroke-linecap='round'/>"
            f"<circle cx='88' cy='36' r='5' fill='white' stroke='{GRAY}' stroke-width='1.8'/>"
            f"<path d='M86,42 L80,56' stroke='{NAVY}' stroke-width='1.6' stroke-dasharray='3 2'/>" + arrowhead(79, 58, math.radians(115), NAVY, 6)
            + f"<circle cx='76' cy='63' r='6' fill='{ORANGE}' stroke='{NAVY}' stroke-width='1.2'/>"
            f"<circle cx='88' cy='36' r='22' fill='none' stroke='{GRAY}' stroke-width='1' stroke-dasharray='3 3'/>")
    icon("snap-pour-point", "Snap Pour Point: move an outlet point onto the highest-accumulation cell nearby", body)

    # Watershed: the area draining to an outlet
    body = (f"<path d='M20,18 C44,4 86,8 104,26 C112,44 98,66 76,80 C60,86 40,76 28,62 C14,48 10,30 20,18 Z' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
            f"<path d='M36,24 C44,38 56,48 70,78' fill='none' stroke='{BLUE}' stroke-width='2.2'/>"
            f"<path d='M92,28 C80,40 72,52 64,62' fill='none' stroke='{BLUE}' stroke-width='1.6'/>"
            f"<circle cx='72' cy='80' r='4.5' fill='{NAVY}'/>")
    icon("watershed", "Watershed: every cell that drains to a pour point", body)

    # Stream Link: a network cut into links at junctions, each its own value
    cols = [BLUE, ORANGE, GREEN, NAVY, "#8a5cc2"]
    segs = [("M18,12 L40,40", 0), ("M70,10 L52,40", 1), ("M40,40 L52,40", 2), ("M52,40 L60,62", 2), ("M100,30 L60,62", 3), ("M60,62 L64,84", 4)]
    body = ""
    for d, k in segs:
        body += f"<path d='{d}' fill='none' stroke='{cols[k]}' stroke-width='4' stroke-linecap='round'/>"
    for x, y in ((52, 40), (60, 62)):
        body += f"<circle cx='{x}' cy='{y}' r='3.2' fill='white' stroke='{INK}' stroke-width='1.2'/>"
    icon("stream-link", "Stream Link: a unique value for each stream segment between junctions", body)

    # Stream to Feature: stair-stepped cells become a line
    stair = {(0, 0), (1, 1), (2, 1), (3, 2), (3, 3)}
    body = grid(8, 5, 4, 4, 20, lambda r, c: LBLUE if (r, c) in stair else "white")
    body += f"<path d='M92,45 L100,45' stroke='{NAVY}' stroke-width='2'/>" + arrowhead(104, 45, 0, NAVY, 6)
    body += f"<path d='M18,15 L38,35 L38,55 L58,75 L78,75' fill='none' stroke='{ORANGE}' stroke-width='3' stroke-linejoin='round'/>"
    icon("stream-to-feature", "Stream to Feature: stream cells converted to lines that follow the flow direction", body)

    # Raster to Polygon: a zone of cells becomes a polygon
    zone = {(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 2)}
    body = grid(10, 5, 4, 4, 20, lambda r, c: LORANGE if (r, c) in zone else "white")
    body += (f"<path d='M30,5 L70,5 L70,45 L90,45 L90,65 L70,65 L70,85 L50,85 L50,65 L30,65 L30,45 L10,45 L10,25 L30,25 Z' "
             f"fill='none' stroke='{ORANGE}' stroke-width='3'/>")
    icon("raster-to-polygon", "Raster to Polygon: cells with the same value become one polygon", body)


def metadata_card():
    W, H = 1000, 480
    cards = [
        ("WHAT", "What do the data represent?",
         ["Bare-earth ground elevation: buildings and trees",
          "removed. 32-bit floating point, in METERS above",
          "NAVD 88. Cells of 1/3 arc-second, about 10.3 m",
          "north-south and 7.9 m east-west at 40° N."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["A box over Rock Canyon, east of Provo:",
          "111.665° to 111.515° W, 40.225° to 40.335° N.",
          "Stored in latitude/longitude (GCS NAD 1983), so",
          "it must be projected before cells have a size in m."]),
        ("WHEN", "When were the data collected?",
         ["Tile n41w112 published May 20, 2026.",
          "It is a mosaic of sources collected between",
          "1946 and 2023, and the tile metadata does not",
          "say which one covers Rock Canyon."]),
        ("WHY", "Why were they created?",
         ["The 3D Elevation Program's national seamless",
          "layer: general-purpose 'best available' elevation",
          "for science, mapping and resource management.",
          "Not made to find small channels."]),
        ("HOW", "How were they collected and processed?",
         ["Lidar, older contour-based models and radar,",
          "resampled to one grid and one datum. Bare earth",
          "and hydro-flattened: a road fill with a culvert",
          "under it is a solid dam in these data."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["U.S. Geological Survey, The National Map.",
          "Public domain; no use restrictions.",
          "Credit the USGS 3D Elevation Program",
          "and name the tile in your report."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the Rock Canyon DEM'>",
         "<title>The six metadata questions, applied to the Rock Canyon DEM</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Reading the DEM's metadata: the six questions from CCE 114", 20, "bold", NAVY),
         text(20, 56, "Every answer below comes from the tile's metadata file and READ-ME-FIRST.txt in the extract. Check them yourself.", 12, fill="#5b6770")]
    cw, ch, gx, gy = 310, 150, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='34' rx='8' fill='{NAVY}'/>")
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s += [text(x + 12, y + 60 + k * 18, line, 11.5) for k, line in enumerate(body)]
    s.append(f"<rect x='20' y='{H - 70}' width='960' height='55' rx='8' fill='{ORANGE}'/>")
    s.append(text(32, H - 46, "For watersheds, HOW matters most: the model sees only the ground surface, not the pipes, culverts and ditches under it.", 12.5, "bold", "white"))
    s.append(text(32, H - 26, "Where people have re-plumbed the land, a DEM-derived stream can go somewhere the water does not. Your report has to say where.", 12.5, "bold", "white"))
    s.append("</svg>")
    (OUT / "lab05-dem-metadata.svg").write_text("\n".join(s), encoding="utf-8")


# Esri D8 codes: 1 E, 2 SE, 4 S, 8 SW, 16 W, 32 NW, 64 N, 128 NE
CODE = {1: (0, 1), 2: (1, 1), 4: (1, 0), 8: (1, -1), 16: (0, -1), 32: (-1, -1), 64: (-1, 0), 128: (-1, 1)}


def patch_accum(fd):
    n = fd.shape[0]
    acc = np.zeros_like(fd, dtype=int)

    def up(r, c):
        tot = 0
        for (dr, dc) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            rr, cc = r + dr, c + dc
            if 0 <= rr < n and 0 <= cc < n and CODE.get(int(fd[rr, cc])) == (-dr, -dc):
                tot += 1 + up(rr, cc)
        return tot
    for r in range(n):
        for c in range(n):
            acc[r, c] = up(r, c)
    return acc


def d8_figure():
    """Find a 5 x 5 patch inside the basin where the most flow converges, and draw it."""
    fill = arcpy.Raster(f"{GDB}/Filled_DEM")
    ll = arcpy.Point(fill.extent.XMin, fill.extent.YMin)
    z = arcpy.RasterToNumPyArray(fill, ll, nodata_to_value=np.nan)
    fd = arcpy.RasterToNumPyArray(arcpy.Raster(f"{GDB}/Flow_Direction"), ll, nodata_to_value=0)
    basin = arcpy.RasterToNumPyArray(arcpy.Raster(f"{GDB}/Basin_Raster"), ll, ncols=z.shape[1], nrows=z.shape[0], nodata_to_value=-1)
    best = None
    rows, cols = np.where(basin >= 0)
    rng = np.random.default_rng(1)
    for i in rng.choice(len(rows), 60000, replace=False):
        r, c = rows[i] - 2, cols[i] - 2
        f = fd[r:r + 5, c:c + 5]
        if f.shape != (5, 5) or not np.all(np.isin(f, list(CODE))) or np.any(basin[r:r + 5, c:c + 5] < 0):
            continue
        a = patch_accum(f)
        e = z[r:r + 5, c:c + 5]
        if np.unique(np.round(e)).size < 25:       # every rounded elevation distinct, so the drawing is unambiguous
            continue
        score = a.max() + 0.5 * np.unique(f).size   # prefer patches where flow converges from several sides
        if best is None or score > best[0]:
            best = (score, r, c, f.copy(), a, e.copy())
    score, r, c, f, a, e = best
    x = fill.extent.XMin + (c + 2.5) * 10
    y = fill.extent.YMax - (r + 2.5) * 10
    info = dict(row=int(r), col=int(c), center_utm=[round(x), round(y)], max_in_patch=int(a.max()),
                elev=np.round(e, 1).tolist(), fd=f.astype(int).tolist(), acc=a.tolist())
    (HERE / "d8_patch.json").write_text(json.dumps(info, indent=1))

    W, H, cell = 1000, 475, 56
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='A five by five patch of the filled Rock Canyon DEM, its D8 flow direction codes, and the flow accumulation inside the patch'>",
         "<title>From elevation to flow direction to flow accumulation, on 25 real cells</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Twenty-five cells of Rock Canyon, three ways", 20, "bold", NAVY),
         text(20, 56, f"A 50 m × 50 m patch of your filled DEM (center UTM {round(x):,} E, {round(y):,} N). Each cell drains to the neighbor with the steepest drop.", 12, fill="#5b6770")]
    ox = [20, 350, 680]
    oy = 100
    heads = ["1. Filled elevation (m)", "2. Flow Direction (D8 code)", "3. Flow Accumulation (in this patch)"]
    lo, hi = float(np.min(e)), float(np.max(e))
    for k in range(3):
        s.append(text(ox[k], oy - 14, heads[k], 14, "bold", NAVY))
        for rr in range(5):
            for cc in range(5):
                X, Y = ox[k] + cc * cell, oy + rr * cell
                if k == 0:
                    t = (e[rr, cc] - lo) / (hi - lo)
                    col = f"rgb({int(245 - 120 * t)},{int(240 - 100 * t)},{int(230 - 60 * t)})"
                elif k == 1:
                    col = "white"
                else:
                    col = ORANGE if a[rr, cc] >= 8 else (LORANGE if a[rr, cc] >= 2 else "white")
                s.append(f"<rect x='{X}' y='{Y}' width='{cell}' height='{cell}' fill='{col}' stroke='{GRAY}'/>")
                if k == 0:
                    s.append(text(X + cell / 2, Y + cell / 2 + 5, f"{e[rr, cc]:.1f}", 13, "normal", INK, "middle"))
                elif k == 1:
                    dr, dc = CODE[int(f[rr, cc])]
                    ang = math.atan2(dr, dc)
                    cx, cy = X + cell / 2, Y + cell / 2 + 6
                    x2, y2 = cx + 15 * math.cos(ang), cy + 15 * math.sin(ang)
                    s.append(f"<line x1='{cx - 13 * math.cos(ang):.1f}' y1='{cy - 13 * math.sin(ang):.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{BLUE}' stroke-width='1.6' opacity='0.55'/>" + arrowhead(x2, y2, ang, BLUE, 6))
                    s.append(text(X + cell / 2, Y + 17, int(f[rr, cc]), 13, "bold", NAVY, "middle"))
                else:
                    s.append(text(X + cell / 2, Y + cell / 2 + 5, int(a[rr, cc]), 15, "bold", INK, "middle"))
    # D8 key
    kx, ky = 20, oy + 5 * cell + 28
    s.append(text(kx, ky, "D8 codes:  32 NW   64 N   128 NE   16 W   1 E   8 SW   4 S   2 SE", 12.5, "bold", NAVY))
    s.append(text(kx, ky + 22, "Accumulation counts only the cells upstream inside this patch; ArcGIS Pro counts every upstream cell in the DEM, so its numbers here are much larger.", 11.5, fill="#5b6770"))
    s.append(text(kx, ky + 40, "A cell's own count never includes itself: the headwater cells read 0.", 11.5, fill="#5b6770"))
    s.append("</svg>")
    (OUT / "lab05-d8-patch.svg").write_text("\n".join(s), encoding="utf-8")
    print("D8 patch", info["center_utm"], "max", a.max(), np.unique(f))


def model_diagram():
    W, H = 1500, 545
    cw, x0, y0, rh = 196, 120, 80, 125
    ew, eh = 158, 50

    def pos(c, r):
        return x0 + c * cw, y0 + r * rh
    # kind: in (blue oval), tool (yellow box), out (green oval), param (blue oval, P)
    E = {
        "DEM_UTM": ("in", 0, 0), "Fill": ("tool", 1, 0), "Filled_DEM": ("out", 2, 0),
        "Flow Direction": ("tool", 3, 0), "Flow_Direction": ("out", 4, 0),
        "Flow Accumulation": ("tool", 5, 0), "Flow_Accumulation": ("out", 6, 0),
        "Outlet": ("in", 0, 1), "Snap Pour Point": ("tool", 1, 1), "Snapped_Outlet": ("out", 2, 1),
        "Watershed": ("tool", 3, 1), "Basin_Raster": ("out", 4, 1),
        "Raster to Polygon": ("tool", 5, 1), "Rock_Canyon_Basin": ("outp", 6, 1),
        "Threshold": ("param", 0, 2), "Raster Calculator": ("tool", 1, 2), "Stream_Cells": ("out", 2, 2),
        "Stream Link": ("tool", 3, 2), "Stream_Links": ("out", 4, 2),
        "Stream to Feature": ("tool", 5, 2), "Streams": ("outp", 6, 2),
        "Watershed (2)": ("tool", 3, 3), "Subwatershed_Raster": ("out", 4, 3),
        "Raster to Polygon (2)": ("tool", 5, 3), "Subwatersheds": ("outp", 6, 3),
    }
    edges = [("DEM_UTM", "Fill"), ("Fill", "Filled_DEM"), ("Filled_DEM", "Flow Direction"), ("Flow Direction", "Flow_Direction"),
             ("Flow_Direction", "Flow Accumulation"), ("Flow Accumulation", "Flow_Accumulation"),
             ("Outlet", "Snap Pour Point"), ("Flow_Accumulation", "Snap Pour Point"), ("Snap Pour Point", "Snapped_Outlet"),
             ("Snapped_Outlet", "Watershed"), ("Flow_Direction", "Watershed"), ("Watershed", "Basin_Raster"),
             ("Basin_Raster", "Raster to Polygon"), ("Raster to Polygon", "Rock_Canyon_Basin"),
             ("Threshold", "Raster Calculator"), ("Basin_Raster", "Raster Calculator"), ("Flow_Accumulation", "Raster Calculator"),
             ("Raster Calculator", "Stream_Cells"), ("Stream_Cells", "Stream Link"), ("Flow_Direction", "Stream Link"),
             ("Stream Link", "Stream_Links"), ("Stream_Links", "Stream to Feature"), ("Flow_Direction", "Stream to Feature"),
             ("Stream to Feature", "Streams"), ("Stream_Links", "Watershed (2)"), ("Flow_Direction", "Watershed (2)"),
             ("Watershed (2)", "Subwatershed_Raster"), ("Subwatershed_Raster", "Raster to Polygon (2)"),
             ("Raster to Polygon (2)", "Subwatersheds")]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The structure of the Lab 5 model'>",
         "<title>The Lab 5 model: DEM to basin, streams and subwatersheds</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 32, "The model, row by row: surface → basin → streams → subwatersheds", 19, "bold", NAVY),
         text(20, 52, "Blue: inputs.  Yellow: tools.  Green: outputs.  P: a model parameter that appears in the tool dialog (Step 12).", 12, fill="#5b6770")]
    ctr = {k: (pos(c, r)[0] + ew / 2, pos(c, r)[1] + eh / 2) for k, (_, c, r) in E.items()}
    lane_count = {}
    for a, b in edges:
        (xa, ya), (xb, yb) = ctr[a], ctr[b]
        sx, ex = xa + ew / 2, xb - ew / 2
        if abs(ya - yb) < 1 and ex > sx:          # same row, to the right: straight
            d = f"M{sx},{ya} H{ex}"
        else:                                      # another row: down into the gap, across, down, in from the left
            ra = round((ya - y0 - eh / 2) / rh)
            k = lane_count.get(ra, 0); lane_count[ra] = k + 1
            lane = ya + eh / 2 + 12 + 9 * k
            vx = ex - 12 - 5 * (k % 3)
            d = f"M{xa + 20 - 10 * (k % 4)},{ya + eh / 2} V{lane} H{vx} V{yb} H{ex}"
        s.append(f"<path d='{d}' fill='none' stroke='#7d8791' stroke-width='1.4'/>")
        s.append(arrowhead(ex, yb, 0, "#7d8791", 7))
    for k, (kind, c, r) in E.items():
        x, y = pos(c, r)
        if kind == "tool":
            s.append(f"<rect x='{x}' y='{y}' width='{ew}' height='{eh}' rx='6' fill='{LYELLOW}' stroke='{YELLOW}' stroke-width='1.6'/>")
        else:
            fillc, strk = (LBLUE, BLUE) if kind in ("in", "param") else (LGREEN, GREEN)
            s.append(f"<rect x='{x}' y='{y}' width='{ew}' height='{eh}' rx='25' fill='{fillc}' stroke='{strk}' stroke-width='1.6'/>")
        label = k if kind != "param" else "Threshold (5000)"
        s.append(text(x + ew / 2, y + eh / 2 + 5, label, 12.5 if len(label) < 19 else 11.5, "bold" if kind == "tool" else "normal", INK, "middle"))
        if kind in ("param", "outp"):
            s.append(f"<circle cx='{x + ew - 4}' cy='{y + 4}' r='10' fill='white' stroke='{NAVY}' stroke-width='1.4'/>")
            s.append(text(x + ew - 4, y + 8.5, "P", 12, "bold", NAVY, "middle"))
    for r, lab in enumerate(["Surface", "Basin", "Streams", "Subwatersheds"]):
        s.append(text(20, y0 + r * rh + eh / 2 + 5, lab, 13, "bold", "#5b6770"))
    s.append("</svg>")
    (OUT / "lab05-model-diagram.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    icons()
    metadata_card()
    d8_figure()
    model_diagram()
