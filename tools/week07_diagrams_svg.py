"""Week 7 explanatory diagrams (drawn, not data): bathymetry methods, the two vertical datums, and
the ModelBuilder loop for Lab 6. The one number shown, the 3.48 ft NGVD29-NAVD88 offset, is the
constant difference between the two elevation columns of the USGS GSL elevation-area-volume table
(Root, 2023, doi:10.5066/P9DGG75W), checked across every row.

    python tools/week07_diagrams_svg.py
"""
import pathlib

IMG = pathlib.Path(__file__).resolve().parent.parent / "slides" / "week-07" / "images"
IMG.mkdir(parents=True, exist_ok=True)
F = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
NAVY, BLUE, ORANGE, GRAY, SAND, WATER, GREEN = "#002e5d", "#0062b8", "#e07a1f", "#5b6770", "#e9d8b8", "#cfe3f5", "#3c8d3a"


def svg(w, h, body, label):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' width='{w}' height='{h}' role='img' aria-label='{label}'>"
            f"<rect width='{w}' height='{h}' fill='white'/>" + body + "</svg>")


def t(x, y, s, size=20, color=NAVY, weight="normal", anchor="middle"):
    return f"<text x='{x}' y='{y}' font-family='{F}' font-size='{size}' font-weight='{weight}' fill='{color}' text-anchor='{anchor}'>{s}</text>"


def methods():
    W, H = 1200, 520
    sea = 190
    b = [t(W / 2, 36, "Four ways to measure the bottom of a lake", 26, weight="bold")]
    b.append(f"<rect x='0' y='{sea}' width='{W}' height='{H - sea}' fill='{WATER}'/>")
    floor = "M0,440 C150,470 260,420 330,455 C420,500 520,430 600,470 C700,510 800,440 900,475 C1000,505 1100,450 1200,470 L1200,520 L0,520 Z"
    b.append(f"<path d='{floor}' fill='{SAND}' stroke='#8a5a2b' stroke-width='2.5'/>")
    cols = [(150, "Lead line", "a weighted rope, read by hand", "one point at a time"),
            (450, "Single-beam sonar", "an echo straight down", "a line of points under the boat"),
            (750, "Multibeam sonar", "a fan of echoes", "a swath of points, full coverage"),
            (1050, "Lidar from the air", "green laser through the water", "works only in clear, shallow water")]
    for x, name, how, gives in cols:
        b.append(t(x, 84, name, 22, weight="bold"))
        b.append(t(x, 110, how, 17, GRAY))
        b.append(t(x, 132, gives, 17, GRAY))
        if name == "Lidar from the air":
            b.append(f"<path d='M{x - 50},158 L{x + 50},158 L{x + 40},172 L{x - 40},172 Z' fill='{NAVY}'/>")
            for dx in (-45, -15, 15, 45):
                b.append(f"<line x1='{x}' y1='172' x2='{x + dx}' y2='{sea + 140}' stroke='{GREEN}' stroke-width='2.5'/>")
            continue
        b.append(f"<path d='M{x - 55},{sea - 14} L{x + 55},{sea - 14} L{x + 40},{sea + 6} L{x - 40},{sea + 6} Z' fill='{NAVY}'/>")
        if name == "Lead line":
            b.append(f"<line x1='{x}' y1='{sea}' x2='{x}' y2='452' stroke='{GRAY}' stroke-width='2' stroke-dasharray='6 4'/>")
            b.append(f"<circle cx='{x}' cy='452' r='8' fill='{GRAY}'/>")
        elif name == "Single-beam sonar":
            for r in (40, 90, 140, 190):
                b.append(f"<path d='M{x - r * 0.18},{sea + 6 + r} Q{x},{sea + 6 + r * 1.08} {x + r * 0.18},{sea + 6 + r}' fill='none' stroke='{BLUE}' stroke-width='2.5'/>")
        else:
            for dx in range(-150, 151, 30):
                b.append(f"<line x1='{x}' y1='{sea + 6}' x2='{x + dx}' y2='{sea + 260}' stroke='{BLUE}' stroke-width='1.6' stroke-opacity='0.8'/>")
    (IMG / "lb-bathymetry-methods.svg").write_text(svg(W, H, "".join(b), "Four ways to measure lake depth"), encoding="utf-8")


def datums():
    W, H = 1100, 480
    surf, z29, z88 = 120, 350, 350 + 3.48 * 13   # NAVD88 zero lies below NGVD29 zero here (schematic)
    b = [t(40, 44, "The same water surface, two vertical datums", 26, weight="bold", anchor="start")]
    b.append(f"<rect x='40' y='{surf}' width='560' height='{z29 - surf}' fill='{WATER}'/>")
    b.append(f"<line x1='40' y1='{surf}' x2='600' y2='{surf}' stroke='{BLUE}' stroke-width='5'/>")
    b.append(t(60, surf - 12, "Lake surface, Sept 30, 2026", 19, BLUE, anchor="start"))
    for y, col, lab in ((z29, NAVY, "NGVD29 zero (1929)"), (z88, ORANGE, "NAVD88 zero (1988)")):
        b.append(f"<line x1='40' y1='{y:.0f}' x2='600' y2='{y:.0f}' stroke='{col}' stroke-width='2.5' stroke-dasharray='9 6'/>")
        b.append(t(60, y + (-10 if col == NAVY else 24), lab, 17, col, anchor="start"))
    for x, y, col in ((360, z29, NAVY), (480, z88, ORANGE)):
        b.append(f"<line x1='{x}' y1='{y:.0f}' x2='{x}' y2='{surf + 4}' stroke='{col}' stroke-width='3'/>")
        b.append(f"<path d='M{x - 7},{surf + 16} L{x},{surf + 2} L{x + 7},{surf + 16} Z' fill='{col}'/>")
    b.append(t(640, 160, "4,189.7 ft above NGVD29", 24, NAVY, "bold", anchor="start"))
    b.append(t(640, 188, "the USGS gage, the news, this course", 17, GRAY, anchor="start"))
    b.append(t(640, 250, "≈ 4,193.2 ft above NAVD88", 24, ORANGE, "bold", anchor="start"))
    b.append(t(640, 278, "the datum of the USGS lake-bottom DEM", 17, GRAY, anchor="start"))
    b.append(t(640, 340, "NAVD88 height =", 22, NAVY, "bold", anchor="start"))
    b.append(t(640, 368, "NGVD29 height + 3.48 ft", 22, NAVY, "bold", anchor="start"))
    b.append(t(640, 398, "Mix them and every shoreline is 3.5 ft off", 17, GRAY, anchor="start"))
    b.append(t(40, 468, "Not to scale. The 3.48 ft offset is constant across the USGS GSL elevation–area–volume table.", 14, GRAY, anchor="start"))
    (IMG / "lb-datums.svg").write_text(svg(W, H, "".join(b), "NGVD29 and NAVD88"), encoding="utf-8")


def loop():
    W, H = 1200, 470

    def box(x, y, w, h, fill, txt, sub=None, color=NAVY):
        s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='14' fill='{fill}' stroke='{color}' stroke-width='2'/>"
        s += t(x + w / 2, y + (h / 2 if not sub else h / 2 - 6), txt, 20, color, "bold")
        if sub:
            s += t(x + w / 2, y + h / 2 + 20, sub, 15, GRAY)
        return s

    b = ["<defs><marker id='a' viewBox='0 0 10 10' refX='8' refY='5' markerWidth='6' markerHeight='6' orient='auto'><path d='M0,0 L10,5 L0,10 z' fill='#5b6770'/></marker></defs>"]
    b.append(t(40, 40, "One model, run once per water level", 26, weight="bold", anchor="start"))
    b.append(box(40, 110, 200, 90, "#fff4e0", "For", "3,500 to 3,700 by 10", ORANGE))
    b.append(box(300, 110, 150, 90, "#e3eef8", "Elevation", "this run's level"))
    b.append(box(510, 110, 220, 90, "#fff8d6", "Con", "Value &lt;= %Elevation%"))
    b.append(box(790, 110, 170, 90, "#fff8d6", "Polygon, keep", "the main pool"))
    b.append(box(1010, 110, 160, 90, "#e7f3e3", "pool_%Elevation%", "one per level", GREEN))
    b.append(box(510, 320, 220, 90, "#fff8d6", "Collect Values"))
    b.append(box(820, 320, 300, 90, "#e7f3e3", "Merge → Shorelines", "all levels, one feature class", GREEN))
    for x1, x2 in ((240, 300), (450, 510), (730, 790), (960, 1010)):
        b.append(f"<line x1='{x1}' y1='155' x2='{x2}' y2='155' stroke='{GRAY}' stroke-width='3' marker-end='url(#a)'/>")
    b.append(f"<path d='M1090,200 L1090,260 L620,260 L620,320' fill='none' stroke='{GRAY}' stroke-width='3' marker-end='url(#a)'/>")
    b.append(f"<line x1='730' y1='365' x2='820' y2='365' stroke='{GRAY}' stroke-width='3' marker-end='url(#a)'/>")
    b.append(f"<path d='M140,200 C140,300 300,300 360,220' fill='none' stroke='{ORANGE}' stroke-width='3' stroke-dasharray='7 5' marker-end='url(#a)'/>")
    b.append(t(150, 330, "next level, until the list is done", 17, ORANGE, anchor="start"))
    b.append(t(40, 450, "A sketch of the Lab 6 model. The model as built in ArcGIS Pro is on the Collect Values slide.", 15, GRAY, anchor="start"))
    (IMG / "lb-iterator-loop.svg").write_text(svg(W, H, "".join(b), "A ModelBuilder loop over water levels"), encoding="utf-8")


if __name__ == "__main__":
    methods(); datums(); loop()
    print("wrote lb-bathymetry-methods.svg, lb-datums.svg, lb-iterator-loop.svg")


PLACEHOLDERS = {
    "lb-todo-dem.svg": ("The Great Salt Lake surface in ArcGIS Pro",
                        "the Great Salt Lake lake-bottom surface, symbolized by elevation"),
    "lb-todo-iterators-menu.svg": ("ModelBuilder ▸ Iterators",
                                   "the Iterators menu on the ModelBuilder tab, For highlighted"),
    "lb-todo-for-dialog.svg": ("The For iterator dialog",
                               "From value, To value, By value, and the Value output"),
    "lb-todo-rastercalc-value.svg": ("Con with %Elevation%",
                                     "the expression Value &lt;= %Elevation% and the output name wet_%Elevation%"),
    "lb-todo-model.svg": ("The finished Lab 6 model",
                          "ModelBuilder Export To Graphic: For, Con, Raster to Polygon, Select Layer By Location, Collect Values, Merge"),
    "lb-todo-run-result.svg": ("A run of the model",
                               "the merged shorelines and their Elevation and AreaSqMi fields"),
}


def placeholders():
    for name, (title, what) in PLACEHOLDERS.items():
        W, H = 1100, 560
        b = (f"<rect x='12' y='12' width='{W - 24}' height='{H - 24}' rx='18' fill='#f4f6f8' stroke='#9aa5ae' stroke-width='4' stroke-dasharray='18 12'/>"
             + t(W / 2, H / 2 - 50, "ArcGIS Pro screenshot to come", 40, GRAY, "bold")
             + t(W / 2, H / 2 + 10, title, 30, NAVY, "bold")
             + t(W / 2, H / 2 + 56, what, 20, GRAY)
             + t(W / 2, H - 50, "Placeholder — to be captured from the real model once it is built in ArcGIS Pro", 17, ORANGE))
        (IMG / name).write_text(svg(W, H, b, "Placeholder: " + title), encoding="utf-8")
    print("wrote", len(PLACEHOLDERS), "placeholders")


placeholders()
