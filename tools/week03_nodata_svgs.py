#!/usr/bin/env python3
"""Draw the two figures on the "NoData is not zero" slide of the Week 3 raster deck.

    python3 tools/week03_nodata_svgs.py

Writes slides/week-03/images/ra-real-world-to-raster.svg and ra-raster-value-table.svg.

Both figures are generated from one grid definition so they cannot drift apart. The scene on the
left of the first figure is drawn over the same cell coordinates as the grid on its right, so a
tree really does sit on the cells lettered F. The value attribute table in the second figure counts
its own grid rather than quoting numbers: no figure on this slide asserts anything that is not
true of the picture beside it.

They replace two JPEGs that came across in the migration with no recorded source, which meant the
slide could not cite them.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "slides" / "week-03" / "images"

CELL = 38
NAVY, INK, MUTED, RULE = "#002e5d", "#22262e", "#4b5563", "#8c98a8"

# ---------------------------------------------------------------- figure 1 ---
# The landscape, one letter per cell. F forest, R road, W water, H house, "." background.
# The scene drawn on the left panel is placed to match these cells exactly.
SCENE = [
    ".FFFFFF.",
    ".FFFFFFF",
    "R..FFF..",
    ".RRR....",
    "....RRR.",
    "WW...H.R",
    "WWW...H.",
]
CLASS_COLOR = {"F": "#1f5c22", "R": "#4b5563", "W": "#1b5378", "H": "#8a3f28"}


def cell_center(ox, oy, c, r):
    return ox + c * CELL + CELL / 2, oy + r * CELL + CELL / 2


def grid_lines(ox, oy, cols, rows, stroke=RULE, w=1):
    out = []
    for c in range(1, cols):
        x = ox + c * CELL
        out.append(f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + rows * CELL}"/>')
    for r in range(1, rows):
        y = oy + r * CELL
        out.append(f'<line x1="{ox}" y1="{y}" x2="{ox + cols * CELL}" y2="{y}"/>')
    return f'<g stroke="{stroke}" stroke-width="{w}">' + "".join(out) + "</g>"


def figure_real_world():
    rows, cols = len(SCENE), len(SCENE[0])
    w, h = cols * CELL, rows * CELL          # 304 x 266
    lx, ly = 30, 52                          # left panel origin
    rx = lx + w + 92                         # right panel origin, gap for the arrow
    vb_w, vb_h = rx + w + 30, ly + h + 46

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" '
         f'width="{vb_w}" height="{vb_h}" '
         'font-family="Segoe UI, Avenir Next, Helvetica, Arial, sans-serif" role="img" '
         'aria-label="A landscape of forest, a road, water and two houses, sampled onto a grid '
         'where every cell carries one class letter.">',
         '<defs><marker id="ar" viewBox="0 0 12 12" refX="9" refY="6" markerWidth="7" '
         f'markerHeight="7" orient="auto"><path d="M0 0 L12 6 L0 12 Z" fill="{NAVY}"/></marker>'
         # The scene is drawn on cell centres, so a feature on an edge cell reaches past the
         # frame. Clip it rather than shrink the features away from the cells they belong to.
         f'<clipPath id="panel"><rect x="{lx}" y="{ly}" width="{w}" height="{h}"/></clipPath>'
         '</defs>']

    # ---- left: the real world, drawn on the cell coordinates of SCENE ----
    p.append(f'<text x="{lx + w/2}" y="{ly - 16}" text-anchor="middle" font-size="23" '
             f'font-weight="700" fill="{NAVY}">Real world</text>')
    p.append(f'<rect x="{lx}" y="{ly}" width="{w}" height="{h}" fill="#f4f8f2"/>')
    p.append('<g clip-path="url(#panel)">')

    # water: a pond over the W cells
    wx, wy = cell_center(lx, ly, 0, 5)
    p.append(f'<ellipse cx="{wx + CELL*0.62:.0f}" cy="{wy + CELL*0.42:.0f}" rx="{CELL*1.62:.0f}" '
             f'ry="{CELL*0.92:.0f}" fill="#4a9fd8" stroke="#2b6f9c" stroke-width="2"/>')

    # road: a smooth curve threading the R cells
    pts = [cell_center(lx, ly, c, r) for r, row in enumerate(SCENE)
           for c, ch in enumerate(row) if ch == "R"]
    d = f'M{pts[0][0]:.0f} {pts[0][1]:.0f} ' + " ".join(f'L{x:.0f} {y:.0f}' for x, y in pts[1:])
    p.append(f'<path d="{d}" fill="none" stroke="#6b7280" stroke-width="17" '
             'stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(f'<path d="{d}" fill="none" stroke="#eef1f4" stroke-width="2.5" '
             'stroke-dasharray="11 11" stroke-linecap="round"/>')

    # forest: one tree per F cell
    for r, row in enumerate(SCENE):
        for c, ch in enumerate(row):
            if ch != "F":
                continue
            x, y = cell_center(lx, ly, c, r)
            p.append(f'<g transform="translate({x:.0f},{y:.0f}) scale(0.62)">'
                     '<rect x="-4" y="12" width="8" height="20" fill="#8a5a33"/>'
                     '<circle cx="0" cy="0" r="18" fill="#2f7d32"/>'
                     '<circle cx="-11" cy="12" r="12" fill="#3d9140"/>'
                     '<circle cx="11" cy="12" r="12" fill="#3d9140"/></g>')

    # houses: one per H cell
    for r, row in enumerate(SCENE):
        for c, ch in enumerate(row):
            if ch != "H":
                continue
            x, y = cell_center(lx, ly, c, r)
            p.append(f'<g transform="translate({x:.0f},{y:.0f}) scale(0.78)">'
                     '<path d="M-20 0 L0 -19 L20 0 Z" fill="#b4472e"/>'
                     '<rect x="-14" y="0" width="28" height="21" fill="#e9dcc7" '
                     'stroke="#8a7a63" stroke-width="1.5"/>'
                     '<rect x="-4" y="7" width="9" height="14" fill="#8a7a63"/></g>')

    p.append('</g>')
    p.append(f'<rect x="{lx}" y="{ly}" width="{w}" height="{h}" fill="none" '
             'stroke="#4a5568" stroke-width="2.5"/>')

    # ---- the arrow ----
    ax = lx + w + 20
    p.append(f'<line x1="{ax}" y1="{ly + h/2}" x2="{ax + 46}" y2="{ly + h/2}" stroke="{NAVY}" '
             'stroke-width="6" marker-end="url(#ar)"/>')
    p.append(f'<text x="{ax + 26}" y="{ly + h/2 - 14}" text-anchor="middle" font-size="18" '
             f'font-weight="700" fill="{NAVY}">sample</text>')

    # ---- right: the raster ----
    p.append(f'<text x="{rx + w/2}" y="{ly - 16}" text-anchor="middle" font-size="23" '
             f'font-weight="700" fill="{NAVY}">Raster</text>')
    p.append(f'<rect x="{rx}" y="{ly}" width="{w}" height="{h}" fill="#ffffff"/>')
    p.append(grid_lines(rx, ly, cols, rows))
    for r, row in enumerate(SCENE):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            x, y = cell_center(rx, ly, c, r)
            p.append(f'<text x="{x:.0f}" y="{y + 8:.0f}" text-anchor="middle" font-size="23" '
                     f'font-weight="700" fill="{CLASS_COLOR[ch]}">{ch}</text>')
    p.append(f'<rect x="{rx}" y="{ly}" width="{w}" height="{h}" fill="none" '
             'stroke="#4a5568" stroke-width="2.5"/>')

    # ---- caption and key ----
    p.append(f'<text x="{vb_w/2}" y="{ly + h + 30}" text-anchor="middle" font-size="20" '
             f'font-weight="600" fill="{NAVY}">One cell holds one class. '
             'Anything smaller than a cell is gone.</text>')
    p.append("</svg>")
    return "\n".join(p)


# ---------------------------------------------------------------- figure 2 ---
# The classified grid. 0 marks NoData: it has a colour but no value and no table row.
VALUES = [
    [0, 4, 4, 3, 3, 3],
    [4, 4, 4, 3, 1, 1],
    [4, 3, 3, 1, 1, 1],
    [4, 3, 3, 2, 2, 1],
    [4, 4, 2, 2, 2, 0],
]
CLASSES = {1: ("Forest", "#4a9a4f"), 2: ("Wetland", "#8d63c6"),
           3: ("Crop", "#c8c445"), 4: ("Urban", "#d94f4f")}
NODATA_FILL = "#b9bfc7"
CELL_M = 30                                   # cell size in metres, stated on the figure


def figure_value_table():
    rows, cols = len(VALUES), len(VALUES[0])
    size = 46
    gw, gh = cols * size, rows * size          # 276 x 230
    gx, gy = 30, 56
    tx = gx + gw + 56
    tw = 470
    vb_w, vb_h = tx + tw + 30, 400

    counts = {v: sum(row.count(v) for row in VALUES) for v in CLASSES}

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" '
         f'width="{vb_w}" height="{vb_h}" '
         'font-family="Segoe UI, Avenir Next, Helvetica, Arial, sans-serif" role="img" '
         'aria-label="A classified raster beside its value attribute table. NoData cells are gray '
         'and have no row in the table.">']

    p.append(f'<text x="{gx + gw/2}" y="{gy - 18}" text-anchor="middle" font-size="23" '
             f'font-weight="700" fill="{NAVY}">Classified raster</text>')
    for r, row in enumerate(VALUES):
        for c, v in enumerate(row):
            x, y = gx + c * size, gy + r * size
            fill = NODATA_FILL if v == 0 else CLASSES[v][1]
            p.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{fill}" '
                     'stroke="#ffffff" stroke-width="2"/>')
            cx, cy = x + size / 2, y + size / 2
            if v == 0:
                p.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="15" '
                         'font-weight="700" fill="#5d6673">no</text>'
                         f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="15" '
                         'font-weight="700" fill="#5d6673">value</text>')
            else:
                p.append(f'<text x="{cx}" y="{cy + 8}" text-anchor="middle" font-size="23" '
                         f'font-weight="700" fill="#ffffff">{v}</text>')
    p.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="none" '
             'stroke="#4a5568" stroke-width="2.5"/>')

    # ---- the value attribute table ----
    p.append(f'<text x="{tx + tw/2}" y="{gy - 18}" text-anchor="middle" font-size="23" '
             f'font-weight="700" fill="{NAVY}">Value attribute table</text>')
    rh, hh = 42, 38
    p.append(f'<rect x="{tx}" y="{gy}" width="{tw}" height="{hh}" fill="{NAVY}"/>')
    cols_x = (tx + 46, tx + 168, tx + 300, tx + 412)
    for label, cx in zip(("Value", "Class", "Count", "Area (m²)"), cols_x):
        p.append(f'<text x="{cx}" y="{gy + 26}" text-anchor="middle" font-size="19" '
                 'font-weight="700" fill="#ffffff">' + label + "</text>")
    for i, v in enumerate(sorted(CLASSES)):
        name, colour = CLASSES[v]
        y = gy + hh + i * rh
        p.append(f'<rect x="{tx}" y="{y}" width="{tw}" height="{rh}" '
                 f'fill="{"#f4f7fa" if i % 2 == 0 else "#ffffff"}"/>')
        p.append(f'<rect x="{tx + 14}" y="{y + 10}" width="22" height="22" fill="{colour}"/>')
        cells = (str(v), name, str(counts[v]), f"{counts[v] * CELL_M ** 2:,}")
        for text, cx in zip(cells, cols_x):
            anchor = "start" if cx == cols_x[0] else "middle"
            x = tx + 46 if anchor == "start" else cx
            p.append(f'<text x="{x}" y="{y + 27}" text-anchor="{anchor}" font-size="19" '
                     f'fill="{INK}">{text}</text>')
        p.append(f'<line x1="{tx}" y1="{y}" x2="{tx + tw}" y2="{y}" stroke="#c3ccd8"/>')
    th = hh + len(CLASSES) * rh
    p.append(f'<rect x="{tx}" y="{gy}" width="{tw}" height="{th}" fill="none" '
             'stroke="#4a5568" stroke-width="2"/>')

    # ---- the point of the figure ----
    by = gy + th + 18
    p.append(f'<rect x="{tx}" y="{by}" width="{tw}" height="64" rx="8" fill="#fdf1e7" '
             'stroke="#e8792b" stroke-width="2"/>')
    p.append(f'<rect x="{tx + 18}" y="{by + 19}" width="26" height="26" fill="{NODATA_FILL}" '
             'stroke="#8c98a8" stroke-width="1.5"/>')
    p.append(f'<text x="{tx + 56}" y="{by + 28}" font-size="19" font-weight="700" '
             'fill="#a8551a">NoData</text>')
    p.append(f'<text x="{tx + 56}" y="{by + 51}" font-size="17" fill="#7a4415">'
             'has no row: it is not a class and not a value</text>')

    p.append(f'<text x="{vb_w/2}" y="{vb_h - 34}" text-anchor="middle" font-size="20" '
             f'font-weight="600" fill="{NAVY}">Every value in the grid is one row in the table'
             '</text>')
    p.append(f'<text x="{vb_w/2}" y="{vb_h - 10}" text-anchor="middle" font-size="18" '
             f'fill="{MUTED}">Cell size {CELL_M} m, so one cell is {CELL_M ** 2:,} m²</text>')
    p.append("</svg>")
    return "\n".join(p), counts


def main():
    (OUT / "ra-real-world-to-raster.svg").write_bytes(figure_real_world().encode("utf-8"))
    svg, counts = figure_value_table()
    (OUT / "ra-raster-value-table.svg").write_bytes(svg.encode("utf-8"))
    valued = sum(counts.values())
    total = len(VALUES) * len(VALUES[0])
    print(f"wrote both figures; table counts {counts}, "
          f"{valued} valued cells and {total - valued} NoData of {total}")


if __name__ == "__main__":
    main()
