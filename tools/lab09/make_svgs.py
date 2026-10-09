"""Generate the Lab 9 tool icons and Figure A as SVG with real text (same helpers and palette as Lab 6).

    python make_svgs.py

Writes into docs/assignments/lab-09/images/:
  icon-create-random-points.svg, icon-extract-values-to-points.svg, icon-erase.svg, icon-idw.svg,
  icon-zonal-statistics.svg
  lab09-dem-metadata.svg   Figure A, the six metadata questions for the Big Southern Butte extract

Every metadata statement comes from the two tiles' metadata files (USGS_13_n44w114 and n44w113,
both published 2026-04-07; source dates 1957-2024 and 2019-2024) and the extract's
READ-ME-FIRST.txt (tools/lab09/make_extract.py).
"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-09" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
text, arrow, grid, icon = h.text, h.arrow, h.grid, h.icon

# fixed "random" positions so the icons do not change between runs
PTS = [(18, 20), (40, 14), (70, 22), (96, 16), (12, 46), (30, 62), (52, 40), (82, 52), (104, 40),
       (22, 78), (60, 74), (90, 80), (108, 66), (44, 84), (66, 50), (48, 56), (74, 38)]
POLY = [(8, 30), (40, 8), (100, 12), (114, 50), (84, 86), (20, 82)]


def in_poly(x, y, poly=POLY, margin=5):
    # ray casting, then keep a margin from every vertex-to-vertex edge
    inside = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
        dx, dy = x2 - x1, y2 - y1
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        if ((x - x1 - t * dx) ** 2 + (y - y1 - t * dy) ** 2) ** 0.5 < margin:
            return False
    return inside
INSIDE = lambda x, y: (x - 60) ** 2 / 26 ** 2 + (y - 48) ** 2 / 20 ** 2 < 1


def dot(x, y, fill, r=3.2):
    return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill}' stroke='white' stroke-width='0.8'/>"


def icons():
    # Create Random Points: dots scattered inside a polygon
    body = f"<path d='M8,30 L40,8 L100,12 L114,50 L84,86 L20,82 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
    body += "".join(dot(x, y, NAVY) for x, y in PTS if in_poly(x, y))
    icon("create-random-points", "Create Random Points: points scattered at random inside a polygon", body)

    # Extract Values to Points: a point over a cell picks up the cell's value
    body = grid(6, 18, 4, 4, 15, lambda r, c: [LBLUE, "white", LORANGE, LBLUE][(r * 3 + c) % 4])
    body += dot(28, 41, ORANGE, 5)
    body += arrow(34, 38, 74, 24, NAVY, 2, 6)
    body += f"<rect x='76' y='12' width='40' height='24' rx='4' fill='white' stroke='{NAVY}' stroke-width='1.5'/>"
    body += text(96, 29, "1559", 11, "bold", NAVY, "middle")
    body += text(96, 50, "RASTER", 7.5, "bold", GRAY, "middle") + text(96, 60, "VALU", 7.5, "bold", GRAY, "middle")
    icon("extract-values-to-points", "Extract Values to Points: each point takes the value of the cell under it", body)

    # Erase: points inside an outline are removed, the rest kept
    body = f"<ellipse cx='60' cy='48' rx='26' ry='20' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
    for x, y in PTS:
        if INSIDE(x, y):
            body += f"<path d='M{x-4},{y-4} L{x+4},{y+4} M{x-4},{y+4} L{x+4},{y-4}' stroke='{ORANGE}' stroke-width='2'/>"
        else:
            body += dot(x, y, NAVY)
    icon("erase", "Erase: removes the features that fall inside another layer", body)

    # IDW: a cell's value is a weighted average of the nearby points, the nearest weighted most
    body = ""
    for (x, y, w) in ((30, 30, 3), (86, 26, 1.6), (34, 76, 1.6), (90, 70, 1), (62, 14, 2.2)):
        body += f"<line x1='59' y1='47' x2='{x}' y2='{y}' stroke='{NAVY}' stroke-width='{w}'/>" + dot(x, y, NAVY, 4)
    body += f"<rect x='50' y='38' width='18' height='18' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='1.5'/>"
    body += text(59, 88, "1/d²", 11, "bold", NAVY, "middle")
    icon("idw", "IDW: each cell a weighted average of the nearest points, the nearest weighted most", body)

    # Zonal Statistics: the cells inside a zone summed into one value
    body = grid(6, 12, 4, 4, 15, lambda r, c: LBLUE if 0 < r < 3 and 0 < c < 3 else "white")
    body += f"<rect x='21' y='27' width='30' height='30' fill='none' stroke='{NAVY}' stroke-width='2.5'/>"
    body += arrow(72, 42, 84, 42, NAVY, 2, 6)
    body += text(103, 38, "Σ", 20, "bold", NAVY, "middle") + text(103, 56, "sum", 10, "bold", NAVY, "middle")
    icon("zonal-statistics", "Zonal Statistics: a statistic of the cells inside each zone, such as their sum", body)


def metadata_card():
    W, H = 1000, 500
    cards = [
        ("WHAT", "What do the data represent?",
         ["Bare-earth ground elevation in METERS above",
          "NAVD 88, 32-bit floating point. Cells of",
          "1/3 arc-second: about 10.3 m north-south",
          "and 7.5 m east-west at 43.4° N."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["Big Southern Butte and the plain around it:",
          "113.17° to 112.89° W, 43.32° to 43.49° N.",
          "Stored in latitude/longitude (GCS NAD 1983):",
          "project it before measuring volume (Step 1)."]),
        ("WHEN", "When were the data collected?",
         ["Tiles n44w114 and n44w113, both published",
          "April 7, 2026. Mosaics of sources collected",
          "1957–2024 and 2019–2024; the metadata does",
          "not say which one covers the butte."]),
        ("WHY", "Why were they created?",
         ["The 3D Elevation Program's national seamless",
          "layer: general-purpose 'best available'",
          "elevation for science, mapping and resource",
          "management. Not made to measure volcanoes."]),
        ("HOW", "How were they collected and processed?",
         ["Sources of diverse origin resampled to one",
          "grid and one datum. The butte straddles the",
          "113° W tile edge, so the extract joins two",
          "tiles edge to edge, values unchanged."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["U.S. Geological Survey, The National Map.",
          "Public domain; no use restrictions.",
          "Credit the USGS 3D Elevation Program",
          "and name both tiles in your report."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the Big Southern Butte DEM'>",
         "<title>The six metadata questions, applied to the Big Southern Butte DEM</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Reading the DEM's metadata: the six questions from CCE 114", 20, "bold", NAVY),
         text(20, 56, "Every answer comes from the tiles' metadata files and READ-ME-FIRST.txt in the extract. Check them yourself.", 12, fill="#5b6770")]
    cw, ch, gx, gy = 310, 155, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='34' rx='8' fill='{NAVY}'/>")
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s += [text(x + 12, y + 60 + k * 19, line, 11.5) for k, line in enumerate(body)]
    s.append(f"<rect x='20' y='{H - 80}' width='960' height='62' rx='8' fill='{ORANGE}'/>")
    s.append(text(32, H - 54, "For a volume, the cell size and the vertical unit matter most: each cell's height times its area is its volume.", 12.5, "bold", "white"))
    s.append(text(32, H - 32, "Degrees by meters is not a volume. Project to meters first, and say in your report what one meter of error does to the total.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab09-dem-metadata.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    icons()
    metadata_card()
    print("wrote icons and Figure A to", h.OUT)
