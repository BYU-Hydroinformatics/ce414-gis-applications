"""Generate the Lab 12 tool icons and Figure A as SVG with real text (Lab 6 helpers and palette).

    python make_svgs.py

Writes into docs/assignments/lab-12/images/:
  icon-make-service-area-analysis-layer.svg, icon-add-locations.svg, icon-solve.svg,
  icon-select-layer-by-location.svg, icon-summary-statistics.svg
  lab12-metadata.svg     Figure A, the six metadata questions for the lab's data

Metadata statements come from READ-ME-FIRST.txt (make_package.py) and from the UGRC feature
services' own layer and service descriptions, read October 10, 2026:
  FireStations: layer description "Last Update: September 22, 2022 ... This dataset represents Fire
    Station locations in Utah"; service description "To show the locations of Fire Stations in Utah";
    service data last edited 2026-03-07.
  CensusBlocks2020: no layer or service description at all; data last edited 2026-03-06.
  UtahRoads (the network's source): "Last Update: 10/08/2026"; "a multi-purpose statewide roads
    dataset for cartography and range based-address location ... A network analysis dataset for
    route-finding can also be derived from this dataset."
  Utah Street Network page (gis.utah.gov/data/transportation/street-network-analysis/): impedance
    "estimated from the CARTOCODE field, spatial queries, and the SPEED_LMT field"; surface streets
    "multiplied by 1.5"; "relatively crude, though effective".
  Fire_Station_Travel_Times service: "based on typical network travel, and not the expedited travel
    of emergency response vehicles."
"""
import importlib.util
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-12" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
GREEN, LGREEN = h.GREEN, h.LGREEN
text, arrow, icon = h.text, h.arrow, h.icon
RED = "#c00000"

# a small road network used by three icons: a grid of streets with one diagonal
ROADS = ("M10,20 H110 M10,45 H110 M10,70 H110 M30,8 V82 M60,8 V82 M90,8 V82 M30,70 L90,20")


def roads(col=GRAY, w=2.2):
    return f"<path d='{ROADS}' fill='none' stroke='{col}' stroke-width='{w}' stroke-linecap='round'/>"


def svg_open(W, H, label, title):
    return [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
            f"aria-label='{h.esc(label)}'>", f"<title>{h.esc(title)}</title>", f"<rect width='{W}' height='{H}' fill='white'/>"]


def icons():
    # Make Service Area Analysis Layer: a station on the network with the reachable streets shaded in rings
    body = roads(LGRAY, 2.2)
    body += (f"<path d='M60,45 m-38,0 a38,26 0 1,0 76,0 a38,26 0 1,0 -76,0' fill='{BLUE}' fill-opacity='0.22'/>"
             f"<path d='M60,45 m-24,0 a24,16 0 1,0 48,0 a24,16 0 1,0 -48,0' fill='{BLUE}' fill-opacity='0.45'/>"
             f"<path d='M30,45 H90 M60,20 V70 M44,32 L76,58' fill='none' stroke='{NAVY}' stroke-width='3' stroke-linecap='round'/>"
             f"<circle cx='60' cy='45' r='5.5' fill='{RED}' stroke='white' stroke-width='1.5'/>")
    icon("make-service-area-analysis-layer", "Make Service Area Analysis Layer: an empty analysis layer whose facilities, "
         "once added and solved, get the streets reachable within the cutoff minutes", body)

    # Add Locations: three pins dropping onto the network and snapping to the nearest street
    body = roads(GRAY, 2.2)
    for x, y, sx, sy in ((26, 30, 30, 45), (64, 56, 60, 45), (96, 30, 90, 20)):
        body += (f"<line x1='{x}' y1='{y}' x2='{sx}' y2='{sy}' stroke='{ORANGE}' stroke-width='1.5' stroke-dasharray='3,2'/>"
                 f"<circle cx='{sx}' cy='{sy}' r='4' fill='{ORANGE}'/>"
                 f"<path d='M{x},{y - 4} m-7,-10 a7,7 0 1,1 14,0 c0,5 -7,14 -7,14 s-7,-9 -7,-14z' fill='{RED}' stroke='white' stroke-width='1.2'/>")
    icon("add-locations", "Add Locations: the fire stations loaded into the analysis layer as facilities, "
         "each snapped to the nearest street", body)

    # Solve: the network with the reachable streets lit up and a check mark
    body = roads(LGRAY, 2.2)
    body += (f"<path d='M30,20 H90 M30,45 H110 M60,8 V70 M30,70 L90,20 M90,20 V45' fill='none' stroke='{GREEN}' stroke-width='3.2' stroke-linecap='round'/>"
             f"<circle cx='60' cy='45' r='5.5' fill='{RED}' stroke='white' stroke-width='1.5'/>"
             f"<circle cx='98' cy='68' r='14' fill='white' stroke='{GREEN}' stroke-width='2'/>"
             f"<path d='M90,68 L96,74 L107,61' fill='none' stroke='{GREEN}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>")
    icon("solve", "Solve: runs the analysis layer and fills in its polygons; nothing is computed until it runs", body)

    # Select Layer By Location: a blob (the served area) over small block polygons; blocks whose center falls outside are picked
    body = ""
    for i in range(6):
        for j in range(4):
            cx, cy = 14 + i * 19, 14 + j * 19
            inside = (cx - 52) ** 2 / 36 ** 2 + (cy - 42) ** 2 / 28 ** 2 < 1
            body += (f"<rect x='{4 + i * 19}' y='{4 + j * 19}' width='17' height='17' rx='2' "
                     f"fill='{LGRAY if inside else LORANGE}' stroke='{GRAY if inside else ORANGE}' stroke-width='{0.8 if inside else 1.6}'/>")
            body += f"<circle cx='{cx}' cy='{cy}' r='1.6' fill='{INK}'/>"
    body += f"<ellipse cx='52' cy='42' rx='36' ry='28' fill='{BLUE}' fill-opacity='0.25' stroke='{NAVY}' stroke-width='2'/>"
    icon("select-layer-by-location", "Select Layer By Location: the blocks whose center point falls outside the served area "
         "are selected, the rest left alone", body)

    # Summary Statistics: rows of numbers collapsing into one total
    body = f"<rect x='8' y='10' width='60' height='70' rx='4' fill='white' stroke='{GRAY}'/>"
    for k in range(5):
        body += f"<rect x='14' y='{17 + k * 12}' width='{26 + (k * 7) % 20}' height='6' fill='{LBLUE}'/>"
    body += (h.arrow(72, 45, 90, 45, NAVY, 2.5, 7)
             + f"<rect x='92' y='30' width='24' height='30' rx='4' fill='{NAVY}'/>"
             + text(104, 51, "Σ", 18, "bold", "white", "middle"))
    icon("summary-statistics", "Summary Statistics: one table row with the total of a field over the selected features, "
         "here the people in the unserved blocks", body)


def metadata_card(info):
    W, H = 1000, 540
    cards = [
        ("WHAT", "What do the data represent?",
         ["A road NETWORK: segments joined at junctions,",
          f"each with minutes to drive it ({info['edges']:,} edges).",
          f"{info['stations']} fire stations (points). {info['blocks']:,} Census",
          "blocks with the 2020 count of people, PP_TOTAL."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["Utah County only: roads with the county on",
          "either side, stations and blocks inside it.",
          "NAD 1983 UTM zone 12N, meters, every layer;",
          "the services themselves serve Web Mercator."]),
        ("WHEN", "When were the data collected?",
         [f"Roads updated through {info['roads_updated']}.",
          "Stations: 'Last Update: September 22, 2022'",
          "(the service was re-saved March 2026). Blocks:",
          "Census Day, April 1, 2020. Four different dates."]),
        ("WHY", "Why were they created?",
         ["Roads: 'cartography and range based-address",
          "location' and UDOT's linear referencing; 'a",
          "network analysis dataset ... can also be derived'.",
          "Stations: 'to show the locations'. Blocks: no why."]),
        ("HOW", "How were they collected and processed?",
         ["Minutes 'estimated from the CARTOCODE field ...",
          "and the SPEED_LMT field', surface streets x 1.5:",
          "'typical network travel, and not the expedited",
          "travel of emergency response vehicles'."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["The Utah Geospatial Resource Center (roads,",
          "the network, stations); the U.S. Census Bureau",
          "(blocks, published by UGRC). Public data under",
          "CC BY: credit each source on your maps."]),
    ]
    s = svg_open(W, H, "The six metadata questions applied to the Lab 12 data",
                 "The six metadata questions, applied to the fire response data")
    s += [text(20, 34, "Reading the metadata: the six questions from CCE 114", 20, "bold", NAVY),
          text(20, 56, "Every answer comes from READ-ME-FIRST.txt and the UGRC services' own descriptions. Check them yourself.", 12, fill="#5b6770")]
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
    s.append(text(32, H - 72, "The stations layer says 'Last Update: September 22, 2022' and the blocks layer has no description at all. A station", 12.5, "bold", "white"))
    s.append(text(32, H - 50, "opened since 2022 is not in your model, and a block's people are where they slept on April 1, 2020. Say in your report", 12.5, "bold", "white"))
    s.append(text(32, H - 28, "what each of those does to your count of people outside four minutes, and which one you would fix first.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab12-metadata.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    import json
    h.OUT.mkdir(parents=True, exist_ok=True)
    pi = json.load(open(HERE / "package_info.json"))
    info = {"edges": pi["network"]["edges"], "stations": pi["Fire_Stations"][1], "blocks": pi["Census_Blocks"][1],
            "roads_updated": pi["roads_updated"]}
    icons()
    metadata_card(info)
    print("ok", sorted(p.name for p in h.OUT.glob("*.svg")))
