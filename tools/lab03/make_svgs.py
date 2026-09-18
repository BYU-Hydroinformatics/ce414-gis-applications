# Generates the Lab 3 tool icons as SVG with real text where text is needed.
# Same 120x90 canvas, palette and convention as tools/lab01/make_svgs.py: gray is input,
# orange is what comes out, cyan is a selection or a link the student makes.
#   python make_svgs.py   -> writes icon-*.svg into docs/assignments/lab-03/images/
import pathlib

OUT = pathlib.Path(r"C:\Users\dpame\code\ce414-gis-applications\docs\assignments\lab-03\images")
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, CYAN = (
    "#002e5d", "#0062b8", "#cfe3f7", "#9aa5b1", "#e6eaee", "#e8862a", "#fdebd9", "#19c3e6")
FONT = "font-family='Segoe UI, Roboto, Helvetica, Arial, sans-serif'"


def esc(t):
    # Attributes here are single-quoted, so apostrophes have to go too -- an unescaped one in a
    # title silently produces an SVG that browsers refuse to render as a broken image.
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("'", "&#39;").replace('"', "&quot;"))


def icon(name, title, body):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 90' width='120' height='90' "
           f"role='img' aria-label='{esc(title)}'><title>{esc(title)}</title>{body}</svg>")
    (OUT / f"icon-{name}.svg").write_text(svg, encoding="utf-8")


def grid(x, y, w, h, cols, rows, stroke, sw=1.2, opacity=1.0):
    s = ""
    for i in range(cols + 1):
        gx = x + w * i / cols
        s += f"<line x1='{gx:.1f}' y1='{y}' x2='{gx:.1f}' y2='{y + h}' stroke='{stroke}' stroke-width='{sw}' opacity='{opacity}'/>"
    for j in range(rows + 1):
        gy = y + h * j / rows
        s += f"<line x1='{x}' y1='{gy:.1f}' x2='{x + w}' y2='{gy:.1f}' stroke='{stroke}' stroke-width='{sw}' opacity='{opacity}'/>"
    return s


# ---- Georeference: a tilted scan swinging onto a north-up frame
body = (f"<rect x='24' y='20' width='72' height='54' fill='none' stroke='{GRAY}' stroke-width='2' stroke-dasharray='5 4'/>"
        f"<g transform='rotate(-13 60 47)'>"
        f"<rect x='28' y='24' width='64' height='46' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2.2'/>"
        + grid(28, 24, 64, 46, 3, 2, ORANGE, 0.9, 0.55) +
        f"</g>"
        f"<path d='M96,16 a30,30 0 0 1 8,14' fill='none' stroke='{CYAN}' stroke-width='2.6'/>"
        f"<polygon points='104,32 99,27 107,25' fill='{CYAN}'/>")
icon("georeference", "Georeference: give a scan real-world coordinates so it lands on the map", body)

# ---- Fit to Display: the sheet dropped into the current view, roughly
body = (f"<rect x='16' y='16' width='88' height='60' fill='{LGRAY}' stroke='{GRAY}' stroke-width='2'/>"
        f"<rect x='34' y='30' width='54' height='38' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2.2'/>"
        f"<path d='M60,6 L60,24' stroke='{NAVY}' stroke-width='2.4'/>"
        f"<polygon points='60,28 55,19 65,19' fill='{NAVY}'/>")
icon("fit-to-display", "Fit to Display: drop the scan into the current view as a first guess", body)

# ---- Add Control Points: one feature on the scan linked to the same feature on the map
body = (f"<rect x='8' y='20' width='44' height='50' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
        f"<rect x='68' y='20' width='44' height='50' fill='{LGRAY}' stroke='{GRAY}' stroke-width='2'/>"
        f"<line x1='34' y1='40' x2='88' y2='54' stroke='{CYAN}' stroke-width='2.6' stroke-dasharray='4 3'/>"
        f"<circle cx='34' cy='40' r='6' fill='white' stroke='{NAVY}' stroke-width='2.4'/>"
        f"<circle cx='34' cy='40' r='2' fill='{NAVY}'/>"
        f"<circle cx='88' cy='54' r='6' fill='white' stroke='{NAVY}' stroke-width='2.4'/>"
        f"<circle cx='88' cy='54' r='2' fill='{NAVY}'/>")
icon("add-control-points", "Add Control Points: link a feature on the scan to the same feature on the basemap", body)

# ---- Transformation: the same grid, straight and then bent
body = (grid(10, 24, 44, 44, 3, 3, GRAY, 1.6) +
        f"<path d='M66,26 q14,10 28,0 M66,46 q14,10 28,0 M66,66 q14,10 28,0' fill='none' stroke='{ORANGE}' stroke-width='2'/>"
        f"<path d='M66,26 q-2,20 0,40 M80,31 q-2,18 0,36 M94,26 q-2,20 0,40' fill='none' stroke='{ORANGE}' stroke-width='2'/>"
        f"<path d='M56,46 L62,46' stroke='{NAVY}' stroke-width='2.2'/>"
        f"<polygon points='65,46 59,43 59,49' fill='{NAVY}'/>")
icon("transformation", "Transformation: the equation fitted to your control points, and how far it may bend the sheet", body)

# ---- Control Point Table: rows of residuals, one of them an outlier
rows = [(30, 18), (40, 22), (50, 16), (60, 44), (70, 20), (80, 19)]
body = f"<rect x='12' y='16' width='96' height='62' fill='white' stroke='{GRAY}' stroke-width='1.8'/>"
body += f"<rect x='12' y='16' width='96' height='12' fill='{NAVY}'/>"
for y, w in rows:
    col = ORANGE if w > 30 else LBLUE
    edge = ORANGE if w > 30 else BLUE
    body += f"<rect x='20' y='{y}' width='{w}' height='7' fill='{col}' stroke='{edge}' stroke-width='1'/>"
body += f"<circle cx='92' cy='47' r='7' fill='none' stroke='{CYAN}' stroke-width='2.4'/>"
icon("control-point-table", "Control Point Table: every link with its residual, and the one that does not belong", body)

# ---- Create Feature Class: an empty container waiting to be drawn into
body = (f"<rect x='22' y='22' width='62' height='48' fill='white' stroke='{GRAY}' stroke-width='2.2' stroke-dasharray='6 4'/>"
        f"<path d='M92,28 l3,8 8,3 -8,3 -3,8 -3,-8 -8,-3 8,-3 z' fill='{ORANGE}'/>"
        f"<path d='M40,58 l10,-14 9,9 12,-16' fill='none' stroke='{LGRAY}' stroke-width='2.4'/>")
icon("create-feature-class", "Create Feature Class: make the empty layer you are about to draw into", body)

# ---- Create Features: a pen tracing a polygon, vertices showing
body = (f"<polygon points='18,58 34,28 60,22 82,40 74,66 40,72' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2.4' stroke-linejoin='round'/>")
for cx, cy in [(18, 58), (34, 28), (60, 22), (82, 40), (74, 66), (40, 72)]:
    body += f"<rect x='{cx - 3}' y='{cy - 3}' width='6' height='6' fill='white' stroke='{NAVY}' stroke-width='1.6'/>"
body += (f"<path d='M86,64 L106,44 L112,50 L92,70 L84,72 z' fill='white' stroke='{NAVY}' stroke-width='2' stroke-linejoin='round'/>"
         f"<path d='M86,64 L92,70' stroke='{NAVY}' stroke-width='1.6'/>")
icon("create-features", "Create Features: draw the points, lines and polygons you are capturing", body)

# ---- Add Field: a table gains an empty column
body = f"<rect x='14' y='18' width='92' height='58' fill='white' stroke='{GRAY}' stroke-width='1.8'/>"
body += f"<rect x='14' y='18' width='92' height='12' fill='{NAVY}'/>"
for gx in (44, 74):
    body += f"<line x1='{gx}' y1='18' x2='{gx}' y2='76' stroke='{GRAY}' stroke-width='1.4'/>"
for gy in (42, 54, 66):
    body += f"<line x1='14' y1='{gy}' x2='106' y2='{gy}' stroke='{GRAY}' stroke-width='1.2'/>"
body += f"<rect x='74' y='18' width='32' height='58' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
body += f"<text x='90' y='55' font-size='22' font-weight='bold' fill='{ORANGE}' text-anchor='middle' {FONT}>+</text>"
icon("add-field", "Add Field: append a new, empty column to the attribute table", body)

# ---- Label: a feature with its name drawn on the map
body = (f"<polygon points='16,54 34,30 58,36 68,60 44,74' fill='{LGRAY}' stroke='{GRAY}' stroke-width='2' stroke-linejoin='round'/>"
        f"<circle cx='42' cy='52' r='4' fill='{NAVY}'/>"
        f"<rect x='52' y='20' width='58' height='20' rx='3' fill='white' stroke='{ORANGE}' stroke-width='2'/>"
        f"<text x='81' y='34' font-size='12' font-weight='bold' fill='{ORANGE}' text-anchor='middle' {FONT}>Name</text>"
        f"<line x1='52' y1='40' x2='44' y2='50' stroke='{ORANGE}' stroke-width='1.8'/>")
icon("label", "Label: draw the values of a field on the map", body)

# ---- Calculate Geometry Attributes: a shape, and its own measurement written into a column
body = (f"<polygon points='14,56 30,26 56,20 72,44 60,72 26,74' fill='{LBLUE}' stroke='{BLUE}' stroke-width='2.2' stroke-linejoin='round'/>"
        f"<path d='M30,46 L54,46' stroke='{NAVY}' stroke-width='1.6' stroke-dasharray='3 2'/>"
        f"<rect x='78' y='24' width='30' height='44' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
        f"<text x='93' y='42' font-size='11' font-weight='bold' fill='{ORANGE}' text-anchor='middle' {FONT}>km</text>"
        f"<text x='99' y='36' font-size='8' font-weight='bold' fill='{ORANGE}' text-anchor='middle' {FONT}>2</text>"
        f"<line x1='86' y1='52' x2='100' y2='52' stroke='{ORANGE}' stroke-width='1.6'/>"
        f"<line x1='86' y1='60' x2='100' y2='60' stroke='{ORANGE}' stroke-width='1.6'/>")
icon("calculate-geometry", "Calculate Geometry Attributes: write a shape's own area, perimeter or length into a field", body)

# ---- Summary Statistics: many rows in, one row out
body = f"<rect x='10' y='16' width='46' height='58' fill='white' stroke='{GRAY}' stroke-width='1.8'/>"
for j in range(6):
    body += f"<rect x='16' y='{22 + j * 9}' width='34' height='6' fill='{LBLUE}' stroke='{BLUE}' stroke-width='0.9'/>"
body += (f"<path d='M60,45 L76,45' stroke='{NAVY}' stroke-width='2.4'/>"
         f"<polygon points='80,45 73,41 73,49' fill='{NAVY}'/>"
         f"<rect x='84' y='36' width='26' height='18' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2.2'/>"
         f"<rect x='88' y='42' width='18' height='6' fill='{ORANGE}'/>")
icon("summary-statistics", "Summary Statistics: read a field down every row and write one row holding the total", body)

# Buffer deliberately has no icon here: it has a row in Lab 1's tool table, and section 2 of
# tools/lab-conversion-guide.md says tools from earlier labs do not get a row in a later one.

print("written:", sorted(p.name for p in OUT.glob("icon-*.svg")))
