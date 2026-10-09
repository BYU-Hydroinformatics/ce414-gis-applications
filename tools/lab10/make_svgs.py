"""Generate the Lab 10 tool icons and Figure A as SVG with real text (same helpers and palette as Lab 6).

    python make_svgs.py

Writes into docs/assignments/lab-10/images/:
  icon-slope.svg, icon-aspect.svg, icon-cell-statistics.svg, icon-tabulate-area.svg
  lab10-dem-metadata.svg   Figure A, the six metadata questions for the Little Cottonwood extract

Every metadata statement comes from the tile (USGS_13_n41w112, Last-Modified 2026-05-20, as
recorded for Lab 5) and the extract's READ-ME-FIRST.txt (tools/lab10/make_extract.py).
"""
import importlib.util
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-10" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
text, arrow, arrowhead, grid, icon = h.text, h.arrow, h.arrowhead, h.grid, h.icon


def icons():
    # Slope: a hillside with the angle marked
    body = (f"<path d='M8,82 L100,82 L100,22 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M8,82 L100,22' stroke='{ORANGE}' stroke-width='3'/>"
            f"<path d='M34,82 A26,26 0 0 0 30,68' fill='none' stroke='{NAVY}' stroke-width='1.8'/>"
            + text(44, 76, "38°", 13, "bold", NAVY))
    icon("slope", "Slope: the steepness of each cell, in degrees", body)

    # Aspect: a compass rose with the downslope direction
    body = (f"<circle cx='60' cy='45' r='34' fill='white' stroke='{GRAY}' stroke-width='1.5'/>"
            + text(60, 24, "N", 11, "bold", NAVY, "middle") + text(84, 49, "E", 11, "normal", GRAY, "middle")
            + text(60, 73, "S", 11, "normal", GRAY, "middle") + text(36, 49, "W", 11, "normal", GRAY, "middle")
            + arrow(60, 45, 80, 25, ORANGE, 3, 9))
    icon("aspect", "Aspect: the compass direction each slope faces", body)

    # Cell Statistics: three grids, one cell picked out, become one grid holding their maximum
    body = ""
    for k, (x, y) in enumerate(((6, 6), (14, 14), (22, 22))):
        body += grid(x, y, 3, 3, 13, lambda r, c: LORANGE if (r, c) == (1, 1) else "white")
    body += text(41, 51, "5", 10, "bold", INK, "middle")
    body += arrow(68, 45, 84, 45, NAVY, 2, 6)
    body += grid(88, 26, 3, 3, 10, lambda r, c: ORANGE if (r, c) == (1, 1) else "white")
    body += text(103, 82, "max", 11, "bold", NAVY, "middle")
    icon("cell-statistics", "Cell Statistics: a statistic of several rasters, cell by cell, such as the maximum", body)

    # Tabulate Area: a zone outlined over classed cells, and the table of areas it produces
    tones = [LBLUE, LORANGE, ORANGE, LBLUE]
    body = grid(6, 10, 4, 4, 15, lambda r, c: tones[(r + c) % 4])
    body += f"<path d='M10,16 L56,12 L62,60 L18,66 Z' fill='none' stroke='{NAVY}' stroke-width='2.5'/>"
    body += arrow(70, 40, 80, 40, NAVY, 2, 6)
    body += f"<rect x='82' y='16' width='34' height='48' fill='white' stroke='{NAVY}' stroke-width='1.5'/>"
    for k in range(4):
        body += f"<line x1='82' y1='{28 + k * 12}' x2='116' y2='{28 + k * 12}' stroke='{GRAY}' stroke-width='1'/>"
    body += f"<line x1='96' y1='16' x2='96' y2='64' stroke='{GRAY}' stroke-width='1'/>"
    body += text(89, 26, "1", 8, "bold", NAVY, "middle") + text(106, 26, "km²", 8, "bold", NAVY, "middle")
    icon("tabulate-area", "Tabulate Area: the area of each class inside each zone, in a table", body)


def metadata_card():
    W, H = 1000, 500
    cards = [
        ("WHAT", "What do the data represent?",
         ["Bare-earth ground elevation in METERS above",
          "NAVD 88, 32-bit floating point. Cells of",
          "1/3 arc-second: about 10.3 m north-south",
          "and 7.8 m east-west at 40.6° N."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["Upper Little Cottonwood Canyon, with Snowbird",
          "and Alta: 111.70° to 111.58° W, 40.53° to 40.61° N.",
          "Stored in latitude/longitude (GCS NAD 1983):",
          "project it before Slope and Aspect (Step 1)."]),
        ("WHEN", "When were the data collected?",
         ["Tile n41w112 published May 20, 2026.",
          "A mosaic of sources collected between 1946",
          "and 2023; the tile metadata does not say",
          "which one covers this canyon."]),
        ("WHY", "Why were they created?",
         ["The 3D Elevation Program's national seamless",
          "layer: general-purpose 'best available'",
          "elevation for science, mapping and resource",
          "management. Not made for avalanche terrain."]),
        ("HOW", "How were they collected and processed?",
         ["Lidar, older contour-based models and radar,",
          "resampled to one grid and one datum. Bare",
          "earth: the ground, without trees, buildings,",
          "lift towers or the winter snowpack."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["U.S. Geological Survey, The National Map.",
          "Public domain; no use restrictions.",
          "Credit the USGS 3D Elevation Program",
          "and name the tile in your report."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the Little Cottonwood Canyon DEM'>",
         "<title>The six metadata questions, applied to the Little Cottonwood Canyon DEM</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Reading the DEM's metadata: the six questions from CCE 114", 20, "bold", NAVY),
         text(20, 56, "Every answer comes from the tile's metadata file and READ-ME-FIRST.txt in the extract. Check them yourself.", 12, fill="#5b6770")]
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
    s.append(text(32, H - 54, "For avalanche terrain, HOW matters most: the model sees the ground, not the snow a skier stands on.", 12.5, "bold", "white"))
    s.append(text(32, H - 32, "Drifts, cornices and wind slabs reshape slopes every winter, and none of that is in a bare-earth DEM. Your report has to say so.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab10-dem-metadata.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    icons()
    metadata_card()
    print("wrote icons and Figure A to", h.OUT)
