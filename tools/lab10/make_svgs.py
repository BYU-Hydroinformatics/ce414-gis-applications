"""Generate the Lab 10 tool icons, Figure A and Figure B as SVG with real text (Lab 6 helpers and palette).

    python make_svgs.py

Writes into docs/assignments/lab-10/images/:
  icon-create-thiessen-polygons.svg, icon-kriging.svg, icon-zonal-statistics-as-table.svg
  lab10-dem-metadata.svg   Figure A, the six metadata questions for the Y Mountain extract
  lab10-profile.svg        Figure B, a measured east-west profile: the true DEM and three 250-point
                           rebuilds (profile.json, from profile.py)

Every metadata statement comes from the tile's metadata file (USGS_13_n41w112, published 2026-05-20,
source dates 1946-2023) and the extract's READ-ME-FIRST.txt (make_extract.py).
"""
import importlib.util
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-10" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
text, arrow, grid, icon = h.text, h.arrow, h.grid, h.icon
GREEN = "#2e7d32"


def dot(x, y, fill, r=3.2):
    return f"<circle cx='{x}' cy='{y}' r='{r}' fill='{fill}' stroke='white' stroke-width='0.8'/>"


def icons():
    # Create Thiessen Polygons: every location belongs to its nearest point
    cells = ["M6,6 L52,6 L46,40 L6,34 Z", "M52,6 L114,6 L114,30 L76,44 L46,40 Z",
             "M6,34 L46,40 L40,84 L6,84 Z", "M46,40 L76,44 L84,84 L40,84 Z", "M76,44 L114,30 L114,84 L84,84 Z"]
    fills = [LBLUE, "#d6e4f0", LORANGE, "#fbe3cf", "#e6eef5"]
    body = "".join(f"<path d='{d}' fill='{f}' stroke='{NAVY}' stroke-width='1.4'/>" for d, f in zip(cells, fills))
    body += "".join(dot(x, y, NAVY, 3.6) for x, y in ((26, 20), (84, 22), (22, 60), (62, 64), (98, 62)))
    icon("create-thiessen-polygons", "Create Thiessen Polygons: every location belongs to the polygon of its nearest point", body)

    # Kriging: a semivariogram curve rising to a sill
    body = (f"<line x1='14' y1='78' x2='112' y2='78' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<line x1='14' y1='78' x2='14' y2='8' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M14,78 C40,40 60,22 86,20 L112,20' fill='none' stroke='{ORANGE}' stroke-width='3'/>"
            f"<line x1='86' y1='20' x2='86' y2='78' stroke='{GRAY}' stroke-width='1' stroke-dasharray='3,3'/>")
    body += "".join(dot(x, y, NAVY, 3) for x, y in ((24, 66), (34, 52), (46, 44), (56, 30), (68, 28), (80, 18), (96, 24), (106, 17)))
    body += text(100, 14, "sill", 9, "bold", GRAY, "middle") + text(86, 88, "range", 9, "bold", GRAY, "middle")
    icon("kriging", "Kriging: interpolation weighted by a semivariogram fitted to how values differ with distance", body)

    # Zonal Statistics as Table: the cells inside a zone summarized into a table row
    body = grid(6, 14, 4, 4, 14, lambda r, c: LBLUE)
    body += f"<rect x='6' y='14' width='56' height='56' fill='none' stroke='{NAVY}' stroke-width='2.5'/>"
    body += arrow(66, 42, 78, 42, NAVY, 2, 6)
    body += (f"<rect x='80' y='24' width='36' height='38' fill='white' stroke='{NAVY}' stroke-width='1.5'/>"
             f"<rect x='80' y='24' width='36' height='12' fill='{NAVY}'/>")
    body += text(98, 33, "MEAN", 7.5, "bold", "white", "middle") + text(98, 53, "Σ/n", 10, "bold", NAVY, "middle")
    icon("zonal-statistics-as-table", "Zonal Statistics as Table: a statistic of the cells inside each zone, written to a table", body)


def metadata_card():
    W, H = 1000, 500
    cards = [
        ("WHAT", "What do the data represent?",
         ["Bare-earth ground elevation in METERS above",
          "NAVD 88, 32-bit floating point. Cells of",
          "1/3 arc-second: about 10.3 m north-south",
          "and 7.9 m east-west at 40.2° N."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["Provo and the mountain front east of it:",
          "111.68° to 111.57° W, 40.20° to 40.27° N.",
          "Stored in latitude/longitude (GCS NAD 1983):",
          "True_DEM is the same, projected to UTM 12N."]),
        ("WHEN", "When were the data collected?",
         ["Tile n41w112, published May 20, 2026.",
          "A mosaic of sources collected 1946–2023;",
          "the metadata does not say which source",
          "covers Provo. Cut for this course Oct 2026."]),
        ("WHY", "Why were they created?",
         ["The 3D Elevation Program's national seamless",
          "layer: general-purpose 'best available'",
          "elevation. In this lab it plays the truth",
          "that every rebuilt surface is measured against."]),
        ("HOW", "How were they collected and processed?",
         ["Sources of diverse origin resampled to one",
          "grid and one datum by the USGS. The extract",
          "is a window cut from the tile, values",
          "unchanged; nothing filled or smoothed."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["U.S. Geological Survey, The National Map.",
          "Public domain; no use restrictions.",
          "Credit the USGS 3D Elevation Program",
          "and name the tile in your report."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the Y Mountain DEM'>",
         "<title>The six metadata questions, applied to the Y Mountain DEM</title>",
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
    s.append(text(32, H - 54, "Here the DEM is the truth, so its own errors never show up in your RMSE: you measure how well you rebuilt it,", 12.5, "bold", "white"))
    s.append(text(32, H - 32, "not how well it matches the ground. Say in your report what that means for an RMSE you would quote to a client.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab10-dem-metadata.svg").write_text("\n".join(s), encoding="utf-8")


def profile():
    d = json.load(open(HERE / "profile.json"))
    W, H, L, R, T, B = 1000, 440, 70, 20, 60, 70
    n = len(d["true"])
    km = lambda i: i * d["dx"] / 1000
    xmax = km(n - 1)
    z0, z1 = 1300, 2800
    X = lambda k: L + (W - L - R) * k / xmax
    Y = lambda z: T + (H - T - B) * (z1 - z) / (z1 - z0)
    mid = (T + H - B) / 2
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='Elevation profile across the study area comparing the true DEM with Thiessen, IDW and Kriging surfaces rebuilt from 250 points'>",
         "<title>One row of the study area: the true DEM and three surfaces rebuilt from 250 random points</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(L, 28, f"One row of cells across the study area, {d['lat']:.3f}° N: the truth and three rebuilds from 250 points", 16, "bold", NAVY)]
    for z in range(1400, 2801, 200):
        s.append(f"<line x1='{L}' y1='{Y(z):.1f}' x2='{W - R}' y2='{Y(z):.1f}' stroke='#e3e7eb'/>")
        s.append(text(L - 8, Y(z) + 4, f"{z:,}", 11, fill=GRAY, anchor="end"))
    for k in range(0, int(xmax) + 1):
        s.append(text(X(k), H - B + 18, f"{k}", 11, fill=GRAY, anchor="middle"))
    s.append(text((L + W - R) / 2, H - B + 38, "kilometers east of the study area's west edge", 11.5, fill=GRAY, anchor="middle"))
    s.append(f"<g transform='rotate(-90 18 {mid})'>" + text(18, mid, "meters", 11.5, fill=GRAY, anchor="middle") + "</g>")

    def line(vals, col, w):
        pts = " ".join(f"{X(km(i)):.1f},{Y(v):.1f}" for i, v in enumerate(vals) if v is not None)
        return f"<polyline points='{pts}' fill='none' stroke='{col}' stroke-width='{w}' stroke-linejoin='round'/>"
    s.append(f"<path d='M{X(0)},{Y(z0)} " + " ".join(f"L{X(km(i)):.1f},{Y(v):.1f}" for i, v in enumerate(d['true']) if v is not None)
             + f" L{X(xmax)},{Y(z0)} Z' fill='#eef2f6'/>")
    s.append(line(d["thiessen"], ORANGE, 1.8))
    s.append(line(d["idw"], BLUE, 1.8))
    s.append(line(d["kriging"], GREEN, 1.8))
    s.append(line(d["true"], INK, 2.6))
    for x, z in d["points"]:
        s.append(dot(round(X((x - d["x0"]) / 1000), 1), round(Y(z), 1), NAVY, 4))
    lx, ly = L + 20, T + 20
    for i, (lab, col, w) in enumerate((("True DEM (the row of cells)", INK, 2.6), ("Thiessen", ORANGE, 1.8),
                                        ("IDW, power 2", BLUE, 1.8), ("Kriging, spherical", GREEN, 1.8))):
        s.append(f"<line x1='{lx}' y1='{ly + i * 20}' x2='{lx + 28}' y2='{ly + i * 20}' stroke='{col}' stroke-width='{w + 1}'/>")
        s.append(text(lx + 36, ly + i * 20 + 4, lab, 12))
    s.append(dot(lx + 14, ly + 80, NAVY, 4) + text(lx + 36, ly + 84, f"the {len(d['points'])} sample points within 150 m of the row", 12))
    s.append("</svg>")
    (h.OUT / "lab10-profile.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    h.OUT.mkdir(parents=True, exist_ok=True)
    icons()
    metadata_card()
    profile()
    print("wrote icons, Figure A and Figure B to", h.OUT)
