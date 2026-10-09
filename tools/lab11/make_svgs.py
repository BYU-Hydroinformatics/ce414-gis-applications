"""Generate the Lab 11 tool icons and Figure A as SVG with real text (Lab 6 helpers and palette).

    python make_svgs.py

Writes into docs/assignments/lab-11/images/:
  icon-distance-accumulation.svg, icon-optimal-path-as-line.svg, icon-polyline-to-raster.svg
  lab11-metadata.svg     Figure A, the six metadata questions for the lab's data

Metadata statements come from READ-ME-FIRST.txt (make_package.py) and from the UGRC feature
services' own layer descriptions and last-edit dates, read October 9, 2026 (see PLAN.md):
  UtahRoads: "Last Update: 08/05/2026"; "a multi-purpose statewide roads dataset for cartography and
    range based-address location", "the base geometry for ... UDOT's highway linear referencing system".
  UtahMunicipalBoundaries: "for cartography and approximate boundary identification"; changes
    "through certification by the Lt. Governor's Office"; service last edited 2026-10-01.
  UtahLakesNHD last edited 2026-10-01; UtahStreamsNHD 2026-03-07 (no description).
  TransmissionLines: description "Electrical transmission facilities in Utah"; last edited 2026-03-07.
"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-11" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
GREEN, LGREEN = h.GREEN, h.LGREEN
text, arrow, icon = h.text, h.arrow, h.icon


def svg_open(W, H, label, title):
    return [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
            f"aria-label='{h.esc(label)}'>", f"<title>{h.esc(title)}</title>", f"<rect width='{W}' height='{H}' fill='white'/>"]


def icons():
    # Distance Accumulation: rings of growing cost spreading from a source cell, squeezed by an expensive patch
    body = ""
    for r, op in ((40, 0.25), (30, 0.4), (20, 0.6), (10, 0.85)):
        body += f"<ellipse cx='34' cy='46' rx='{r + 8}' ry='{r}' fill='{BLUE}' fill-opacity='{op}'/>"
    body += (f"<rect x='70' y='14' width='40' height='64' fill='{LORANGE}' stroke='{ORANGE}'/>"
             + text(90, 50, "×10", 12, "bold", ORANGE, "middle")
             + f"<rect x='29' y='41' width='10' height='10' fill='{NAVY}'/>")
    icon("distance-accumulation", "Distance Accumulation: the cheapest total cost to reach every cell from a source, "
         "spreading slowly through expensive cells", body)

    # Optimal Path As Line: a line walked home from the destination to the source across a cost grid
    body = ""
    for i in range(6):
        for j in range(4):
            dark = (i, j) in ((2, 1), (2, 2), (3, 1), (3, 2))
            body += (f"<rect x='{4 + i * 19}' y='{8 + j * 19}' width='19' height='19' "
                     f"fill='{'#8c6d4f' if dark else '#f2e6d0'}' stroke='white' stroke-width='0.8'/>")
    body += (f"<polyline points='13,74 32,74 51,74 70,74 89,55 108,17' fill='none' stroke='{ORANGE}' stroke-width='3.5'/>"
             f"<line x1='13' y1='74' x2='108' y2='17' stroke='{NAVY}' stroke-width='1.2' stroke-dasharray='3,2'/>"
             f"<rect x='8' y='69' width='10' height='10' fill='{GREEN}'/><rect x='103' y='12' width='10' height='10' fill='#c00000'/>")
    icon("optimal-path-as-line", "Optimal Path As Line: the cheapest route from a destination back to the source, "
         "drawn as a line, around the expensive cells rather than straight through them", body)

    # Polyline to Raster: a river line becoming a chain of cells
    body = ""
    for i in range(6):
        for j in range(4):
            on = (i, j) in ((0, 0), (1, 0), (1, 1), (2, 1), (3, 2), (4, 2), (4, 3), (5, 3))
            body += (f"<rect x='{4 + i * 19}' y='{8 + j * 19}' width='19' height='19' "
                     f"fill='{BLUE if on else 'white'}' stroke='{LGRAY}' stroke-width='0.8'/>")
    body += f"<path d='M4,12 C30,16 34,34 52,36 S78,52 90,58 S110,80 118,84' fill='none' stroke='{NAVY}' stroke-width='2.2'/>"
    icon("polyline-to-raster", "Polyline to Raster: every cell a river line passes through becomes a river cell", body)


def metadata_card():
    W, H = 1000, 540
    cards = [
        ("WHAT", "What do the data represent?",
         ["Elevation.tif: ground elevation, METERS above",
          "NAVD 88, 30 m cells. Roads with a UDOT class;",
          "NHD lakes and streams; city limits; power",
          "lines (KV-46/138/345) and substations."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["39.98-40.55° N, 112.05-111.45° W: the mouth",
          "of Spanish Fork Canyon to Bluffdale. NAD 1983",
          "UTM zone 12N, meters, for every layer. The",
          "services themselves serve Web Mercator."]),
        ("WHEN", "When were the data collected?",
         ["All read October 9, 2026. Roads: 'Last Update",
          "08/05/2026'. Cities and lakes edited Oct 1,",
          "2026; streams and power lines Mar 7, 2026.",
          "A last-edit date is not when it was mapped."]),
        ("WHY", "Why were they created?",
         ["Roads: cartography, address location and",
          "UDOT's linear referencing. Cities: 'cartography",
          "and APPROXIMATE boundary identification'.",
          "3DEP: the national best-available elevation."]),
        ("HOW", "How were they collected and processed?",
         ["City boundaries change only when certified by",
          "the Lt. Governor's Office. We exported 3DEP at",
          "30 m (bilinear) and clipped every layer to",
          "the box. The power-line layer does not say."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["USGS (3DEP, the NHD), the Utah Geospatial",
          "Resource Center (roads with UDOT, cities,",
          "power lines). Public data; credit each",
          "source on your maps and in your report."]),
    ]
    s = svg_open(W, H, "The six metadata questions applied to the Lab 11 data",
                 "The six metadata questions, applied to the power line data")
    s += [text(20, 34, "Reading the metadata: the six questions from CCE 114", 20, "bold", NAVY),
          text(20, 56, "Every answer comes from READ-ME-FIRST.txt and the UGRC services' own layer descriptions. Check them yourself.", 12, fill="#5b6770")]
    cw, ch, gx, gy = 310, 160, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='34' rx='8' fill='{NAVY}'/>")
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s += [text(x + 12, y + 60 + k * 19, line, 11.5) for k, line in enumerate(body)]
    s.append(f"<rect x='20' y='{H - 100}' width='960' height='82' rx='8' fill='{ORANGE}'/>")
    s.append(text(32, H - 72, "The power-line layer's whole description is 'Electrical transmission facilities in Utah': no source, no date of", 12.5, "bold", "white"))
    s.append(text(32, H - 50, "mapping, no accuracy. Your route leans on it. Say in your report what you would want to know before you", 12.5, "bold", "white"))
    s.append(text(32, H - 28, "trusted it, and what a missing or misplaced line would do to your route.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab11-metadata.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    h.OUT.mkdir(parents=True, exist_ok=True)
    icons()
    metadata_card()
    print("ok", sorted(p.name for p in h.OUT.glob("*.svg")))
