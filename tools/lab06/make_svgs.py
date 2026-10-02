"""Generate the Lab 6 tool icons and Figure A as SVG with real text (same palette and frame as Lab 5).

    python make_svgs.py

Writes into docs/assignments/lab-06/images/:
  icon-*.svg                  the seven tool icons for the ModelBuilder Tools table
  lab06-surface-metadata.svg  Figure A, the six metadata questions applied to the Lab 6 surface

Every metadata statement comes from the USGS release's FGDC metadata
(Lake_Powell_TBDEM_FGDC_Metadata.xml, ScienceBase item 5c6c1e4be4b0fe48cb3e59e1,
doi:10.5066/P9XX0J1Y, read October 2, 2026) or from the package's READ-ME-FIRST.txt.
"""
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parents[1] / "docs" / "assignments" / "lab-06" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, GREEN, LGREEN, INK = (
    "#002e5d", "#0062b8", "#cfe3f7", "#9aa5b1", "#e6eaee", "#e8862a", "#fdebd9", "#3b8a3e", "#d7ecd4", "#1c2733")
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


def arrow(x1, y1, x2, y2, col=NAVY, w=2, head=6):
    ang = math.atan2(y2 - y1, x2 - x1)
    return (f"<line x1='{x1}' y1='{y1}' x2='{x2 - head * 0.6 * math.cos(ang):.1f}' y2='{y2 - head * 0.6 * math.sin(ang):.1f}' "
            f"stroke='{col}' stroke-width='{w}'/>" + arrowhead(x2, y2, ang, col, head))


def icons():
    # For: a loop arrow around a counter that steps by 10
    body = (f"<path d='M60,14 A32,32 0 1 1 29,52' fill='none' stroke='{ORANGE}' stroke-width='4'/>"
            + arrowhead(29, 52, math.radians(250), ORANGE, 9)
            + text(60, 42, "3,500", 13, "bold", NAVY, "middle") + text(60, 58, "+10", 12, "normal", ORANGE, "middle"))
    icon("for", "For: run the model once for every value from a start to an end by a step", body)

    # Inline variable substitution: %Elevation% in a name becomes this run's value
    body = (f"<rect x='6' y='12' width='108' height='24' rx='4' fill='{LGRAY}' stroke='{GRAY}'/>"
            + text(60, 29, "wet_%Elevation%", 12, "bold", NAVY, "middle")
            + arrow(60, 40, 60, 54, ORANGE, 2, 7)
            + f"<rect x='22' y='58' width='76' height='24' rx='4' fill='{LORANGE}' stroke='{ORANGE}'/>"
            + text(60, 75, "wet_3550", 12, "bold", INK, "middle"))
    icon("inline-variable", "Inline variable substitution: %Elevation% is replaced by the current value", body)

    # Con: cells at or below the level become 1 (blue), the rest NoData (blank)
    elev = [[3, 3, 2, 3], [3, 1, 1, 2], [2, 0, 1, 3], [3, 1, 2, 3]]
    body = grid(8, 5, 4, 4, 20, lambda r, c: BLUE if elev[r][c] <= 1 else "white")
    for r in range(4):
        for c in range(4):
            if elev[r][c] <= 1:
                body += text(18 + c * 20, 20 + r * 20, "1", 11, "bold", "white", "middle")
    body += text(104, 34, "≤", 18, "bold", NAVY, "middle") + text(104, 54, "level", 10, "normal", NAVY, "middle")
    icon("con", "Con: 1 where the surface is at or below the water level, NoData everywhere else", body)

    # Raster to Polygon: a zone of cells becomes a polygon (same as Lab 5)
    zone = {(0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (3, 2)}
    body = grid(10, 5, 4, 4, 20, lambda r, c: LORANGE if (r, c) in zone else "white")
    body += (f"<path d='M30,5 L70,5 L70,45 L90,45 L90,65 L70,65 L70,85 L50,85 L50,65 L30,65 L30,45 L10,45 L10,25 L30,25 Z' "
             f"fill='none' stroke='{ORANGE}' stroke-width='3'/>")
    icon("raster-to-polygon", "Raster to Polygon: cells with the same value become one polygon", body)

    # Select Layer By Location: of several polygons, keep the one under the seed point
    body = (f"<path d='M8,58 L22,46 L34,58 L24,74 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M92,10 L110,18 L104,32 L88,26 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M96,62 L112,70 L102,84 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M40,12 L76,18 L84,44 L70,70 L46,80 L38,52 Z' fill='{LBLUE}' stroke='{BLUE}' stroke-width='3'/>"
            f"<circle cx='60' cy='46' r='5' fill='{ORANGE}' stroke='{NAVY}' stroke-width='1.4'/>")
    icon("select-by-location", "Select Layer By Location: keep only the polygon that contains the seed point", body)

    # Collect Values: one output per pass gathered into a list
    body = ""
    for k, x in enumerate((10, 34, 58)):
        body += f"<path d='M{x},{18 + k * 4} l14,-6 l8,10 l-6,12 l-14,0 Z' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.5'/>"
        body += arrow(x + 12, 40, 92, 30 + k * 16, GRAY, 1.2, 5)
    body += f"<rect x='92' y='20' width='22' height='50' rx='3' fill='white' stroke='{NAVY}' stroke-width='2'/>"
    for k in range(3):
        body += f"<rect x='96' y='{25 + k * 15}' width='14' height='10' fill='{LBLUE}' stroke='{BLUE}'/>"
    body += text(30, 82, "pass 1, 2, 3 ...", 11, "normal", NAVY)
    icon("collect-values", "Collect Values: gather the output of every pass of the loop into one list", body)

    # Merge: several feature classes become one
    body = ""
    for k in range(3):
        y = 10 + k * 24
        body += f"<rect x='8' y='{y}' width='30' height='18' rx='3' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.5'/>"
        body += arrow(40, y + 9, 72, 45, GRAY, 1.4, 6)
    body += (f"<rect x='76' y='22' width='38' height='46' rx='4' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2.5'/>"
             + "".join(f"<line x1='80' y1='{34 + k * 11}' x2='110' y2='{34 + k * 11}' stroke='{ORANGE}' stroke-width='1.5'/>" for k in range(3)))
    icon("merge", "Merge: combine the collected shorelines into one feature class", body)


def metadata_card():
    W, H = 1000, 500
    cards = [
        ("WHAT", "What do the data represent?",
         ["A topobathymetric DEM: the lake bed and the",
          "land around it in one surface. Elevation in",
          "METERS above NAVD88 (geoid 12B). Your copy:",
          "30 m cells, each the mean of 900 one-meter cells."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["Lake Powell, Arizona and Utah, the whole",
          "reservoir. NAD83(2011) UTM zone 12N, meters.",
          "Your copy: 4,340 x 4,331 cells, mostly NoData;",
          "the surveyed area hugs the canyons."]),
        ("WHEN", "When were the data collected?",
         ["Lake bed: multibeam sonar, Oct 8 - Nov 15, 2017.",
          "Dry shore: lidar, April 2-3, 2018. Gaps: maps",
          "surveyed 1947-1959, before the dam closed.",
          "Published by USGS June 3, 2020."]),
        ("WHY", "Why were they created?",
         ["To support the USGS Utah Water Science Center's",
          "new area-capacity tables for the reservoir, with",
          "the Bureau of Reclamation: the published areas",
          "you check your answer against in Step 6."]),
        ("HOW", "How were they collected and processed?",
         ["Boat sonar, airborne lidar and digitized old",
          "surveys, put on one datum and mosaicked at 1 m,",
          "blended along 5 m seamlines. Where neither boat",
          "nor lidar reached, gaps were interpolated."]),
        ("WHO", "Who made them, and may you use them?",
         ["USGS EROS (Poppenga, Danielson and Tyler) with",
          "Reclamation. Public domain. The metadata says:",
          "not for navigation, and conditions may have",
          "changed since. Credit the USGS in your maps."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the Lake Powell surface'>",
         "<title>The six metadata questions, applied to the Lake Powell surface</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Reading the surface's metadata: the six questions from CCE 114", 20, "bold", NAVY),
         text(20, 56, "Every answer comes from the USGS release's metadata (doi:10.5066/P9XX0J1Y) and READ-ME-FIRST.txt. Check them yourself.", 12, fill="#5b6770")]
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
    s.append(text(32, H - 54, "For shorelines, WHEN matters most: the bed is as it was in fall 2017 and the shore as in spring 2018.", 12.5, "bold", "white"))
    s.append(text(32, H - 32, "Sediment settled since, and every ramp extended since, are not in it — and the datum must be converted before Step 3.", 12.5, "bold", "white"))
    s.append("</svg>")
    (OUT / "lab06-surface-metadata.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    icons()
    metadata_card()
    print("wrote icons and Figure A to", OUT)
