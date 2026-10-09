"""Generate the Lab 7 tool icons and figures as SVG with real text (Lab 6 helpers and palette).

    python make_svgs.py        (after verify_package.py and profile.py)

Writes into docs/assignments/lab-07/images/:
  icon-flow-distance.svg, icon-iterate-field-values.svg, icon-spatial-join.svg, icon-join-field.svg
  lab07-metadata.svg     Figure A, the six metadata questions for the lab's data
  lab07-profile.svg      Figure B, measured: the river's long profile with a bathtub level and the
                         HAND water surface, and FEMA cross-section C with HAND's wet cells
  lab07-rating.svg       Figure 1, the gage's rating with FEMA's five flows (rating_10163000.csv,
                         Stage_Table)
  lab07-model.svg        Figure C, a drawn diagram of the two models (NOT a ModelBuilder export)

Every number is read from the package (C:/Ames/HAND/PkgCheck) or from package_checks.json /
profile.json; metadata statements from READ-ME-FIRST.txt, the NWIS site and rating files, the
FEMA Study_Info table and the 3DEP service identify (see PLAN.md).
"""
import csv
import importlib.util
import json
import math
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("h", HERE.parent / "lab06" / "make_svgs.py")
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
h.OUT = HERE.parents[1] / "docs" / "assignments" / "lab-07" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, INK = h.NAVY, h.BLUE, h.LBLUE, h.GRAY, h.LGRAY, h.ORANGE, h.LORANGE, h.INK
GREEN, LGREEN = h.GREEN, h.LGREEN
text, arrow, grid, icon, arrowhead = h.text, h.arrow, h.grid, h.icon, h.arrowhead
PKG = pathlib.Path(r"C:\Ames\HAND\PkgCheck\lab07-provo-river-hand")
CHECKS = json.load(open(HERE / "package_checks.json"))


def svg_open(W, H, label, title):
    return [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
            f"aria-label='{h.esc(label)}'>", f"<title>{h.esc(title)}</title>", f"<rect width='{W}' height='{H}' fill='white'/>"]


def icons():
    # Flow Distance (vertical): a cell high on a slope, its flow path down to the stream, and the drop
    body = (f"<path d='M4,20 L40,34 L62,62 L70,70 L78,62 L100,40 L116,30 L116,86 L4,86 Z' fill='{LGRAY}' stroke='{GRAY}'/>"
            f"<rect x='64' y='64' width='12' height='8' fill='{BLUE}'/>"
            f"<circle cx='26' cy='29' r='4' fill='{ORANGE}'/>"
            f"<path d='M28,32 L42,38 L58,58 L66,66' fill='none' stroke='{NAVY}' stroke-width='2' stroke-dasharray='3,2'/>"
            f"<line x1='22' y1='29' x2='22' y2='68' stroke='{ORANGE}' stroke-width='2'/>"
            f"<line x1='16' y1='68' x2='64' y2='68' stroke='{ORANGE}' stroke-width='1' stroke-dasharray='2,2'/>"
            + text(8, 52, "h", 14, "bold", ORANGE))
    icon("flow-distance", "Flow Distance, vertical: how far a cell is above the stream cell it drains to, along its flow path", body)

    # Iterate Field Values: a table column handed out one value at a time
    body = (f"<rect x='6' y='8' width='46' height='74' fill='white' stroke='{NAVY}' stroke-width='1.4'/>"
            f"<rect x='6' y='8' width='46' height='14' fill='{NAVY}'/>" + text(29, 19, "H_CM", 9, "bold", "white", "middle"))
    for i, v in enumerate((119, 134, 143, 153, 173)):
        y = 34 + i * 11
        body += text(29, y, str(v), 9.5, "bold" if i == 3 else "normal", ORANGE if i == 3 else INK, "middle")
    body += arrow(56, 64, 76, 64, ORANGE, 2, 7)
    body += (f"<path d='M96,30 A18,18 0 1 1 79,52' fill='none' stroke='{ORANGE}' stroke-width='3'/>"
             + arrowhead(79, 52, math.radians(250), ORANGE, 8) + text(97, 52, "153", 12, "bold", NAVY, "middle"))
    icon("iterate-field-values", "Iterate Field Values: run the model once for every value in a table field", body)

    # Spatial Join: polygons gain a count of the points that touch them
    body = (f"<path d='M8,14 L58,10 L66,48 L20,60 Z' fill='{LBLUE}' stroke='{NAVY}' stroke-width='1.4'/>")
    for x, y in ((24, 26), (40, 22), (36, 44), (52, 34), (80, 20), (90, 60), (14, 74)):
        body += f"<rect x='{x - 3}' y='{y - 3}' width='7' height='7' fill='{ORANGE}' stroke='white' stroke-width='0.6'/>"
    body += arrow(70, 76, 84, 76, NAVY, 1.6, 6)
    body += (f"<rect x='86' y='66' width='30' height='20' fill='white' stroke='{NAVY}'/>" + text(101, 80, "4", 12, "bold", NAVY, "middle"))
    icon("spatial-join", "Spatial Join: each flood polygon gains a count of the buildings that intersect it", body)

    # Join Field: a table's columns attached to another by a shared key
    body = (f"<rect x='6' y='14' width='44' height='60' fill='white' stroke='{NAVY}' stroke-width='1.4'/>"
            f"<rect x='70' y='14' width='44' height='60' fill='white' stroke='{NAVY}' stroke-width='1.4'/>"
            f"<rect x='6' y='14' width='44' height='12' fill='{NAVY}'/><rect x='70' y='14' width='44' height='12' fill='{NAVY}'/>"
            + text(28, 23.5, "H_CM", 8, "bold", "white", "middle") + text(92, 23.5, "H_CM | YR", 8, "bold", "white", "middle")
            + text(28, 42, "153", 10, "bold", ORANGE, "middle") + text(92, 42, "153 | 100", 9, "bold", ORANGE, "middle")
            + arrow(66, 39, 54, 39, ORANGE, 2, 6))
    icon("join-field", "Join Field: copy the return period from the stage table onto each flood by its H_CM", body)


def metadata_card():
    W, H = 1000, 520
    cards = [
        ("WHAT", "What do the data represent?",
         ["Provo_DEM: bare-earth ground elevation, METERS",
          "above NAVD 88, 5 m cells. Stage_Table: FEMA's",
          "published peak flows (ft³/s), their gage height",
          "(ft) from the USGS rating, and h in meters."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["The Provo River from Provo Canyon's mouth to",
          "Utah Lake, 8.6 × 10.6 km, NAD 1983 UTM 12N.",
          "Gage 10163000 at 40.23926° N, 111.71119° W;",
          "its datum is 4,493.22 ft above NAVD 88."]),
        ("WHEN", "When were the data collected?",
         ["Lidar from 3DEP projects flown 2013–2023, read",
          "from the service Oct 8, 2026. Rating 30.0 in",
          "force since Apr 26, 2023 (provisional). FEMA",
          "flows and flood map effective June 23, 2026."]),
        ("WHY", "Why were they created?",
         ["3DEP: the national 'best available' elevation.",
          "The gage: to measure the river's flow. The",
          "FEMA study: flood insurance rate maps, the",
          "1%-annual-chance floodplain you compare with."]),
        ("HOW", "How were they collected and processed?",
         ["Airborne lidar, bare earth, HYDRO-FLATTENED:",
          "the river is a flat water surface on the day",
          "it was flown. We resampled 2 m to 5 m. All 90",
          "gage peaks carry code 6: affected by",
          "regulation or diversion upstream."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["USGS (3DEP, NWIS gage and rating), FEMA",
          "(flood study and map), UGRC (NHD river line,",
          "building footprints). Public data; credit",
          "each source on your maps and in your report."]),
    ]
    s = svg_open(W, H, "The six metadata questions applied to the Lab 7 data",
                 "The six metadata questions, applied to the Provo River data")
    s += [text(20, 34, "Reading the metadata: the six questions from CCE 114", 20, "bold", NAVY),
          text(20, 56, "Every answer comes from READ-ME-FIRST.txt, the raster's properties and the USGS gage page. Check them yourself.", 12, fill="#5b6770")]
    cw, ch, gx, gy = 310, 160, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='34' rx='8' fill='{NAVY}'/>")
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s += [text(x + 12, y + 60 + k * 19, line, 11.5) for k, line in enumerate(body)]
    s.append(f"<rect x='20' y='{H - 82}' width='960' height='64' rx='8' fill='{ORANGE}'/>")
    s.append(text(32, H - 56, "HAND is measured from the DEM's river cells — the water surface on the day of the flight, not the channel bed —", 12.5, "bold", "white"))
    s.append(text(32, H - 34, "while h is measured from the gage's zero-flow level. Say in your report what that mismatch does to your floods.", 12.5, "bold", "white"))
    s.append("</svg>")
    (h.OUT / "lab07-metadata.svg").write_text("\n".join(s), encoding="utf-8")


def rating():
    rows = [(float(r["gage_height_ft"]), float(r["discharge_cfs"])) for r in csv.DictReader(open(PKG / "rating_10163000.csv"))]
    st = CHECKS["stage_table"]
    W, H, L, R, T, B = 1000, 430, 80, 30, 56, 64
    q0, q1, g0, g1 = 0, 3000, 3, 9.5
    X = lambda q: L + (W - L - R) * (q - q0) / (q1 - q0)
    Y = lambda g: T + (H - T - B) * (g1 - g) / (g1 - g0)
    s = svg_open(W, H, "The gage's stage-discharge rating with FEMA's five flood flows marked",
                 "USGS rating 30.0 at 10163000, with FEMA's 10- to 500-year flows")
    s.append(text(L, 30, "The rating turns a flow into a gage height: USGS 10163000, rating 30.0, with FEMA's five flood flows", 16, "bold", NAVY))
    for g in range(3, 10):
        s.append(f"<line x1='{L}' y1='{Y(g):.1f}' x2='{W - R}' y2='{Y(g):.1f}' stroke='#e3e7eb'/>")
        s.append(text(L - 8, Y(g) + 4, f"{g}", 11, fill=GRAY, anchor="end"))
    for q in range(0, 3001, 500):
        s.append(text(X(q), H - B + 18, f"{q:,}", 11, fill=GRAY, anchor="middle"))
    s.append(text((L + W - R) / 2, H - B + 40, "discharge (ft³/s)", 11.5, fill=GRAY, anchor="middle"))
    mid = (T + H - B) / 2
    s.append(f"<g transform='rotate(-90 22 {mid})'>" + text(22, mid, "gage height (ft)", 11.5, fill=GRAY, anchor="middle") + "</g>")
    pts = " ".join(f"{X(q):.1f},{Y(g):.1f}" for g, q in rows)
    s.append(f"<polyline points='{pts}' fill='none' stroke='{NAVY}' stroke-width='2.6'/>")
    # extension above the table: Q = C (GH - 3.20)^b fitted to the top 0.5 ft (stage_table.py)
    meta = json.load(open(HERE / "stage_table_meta.json"))
    b, C = meta["extrapolation"]["b"], meta["extrapolation"]["C"]
    ext = []
    g = 8.0
    while g <= 9.2:
        ext.append(f"{X(C * (g - 3.2) ** b):.1f},{Y(g):.1f}")
        g += 0.05
    s.append(f"<polyline points='{' '.join(ext)}' fill='none' stroke='{NAVY}' stroke-width='2' stroke-dasharray='6,4'/>")
    s.append(f"<line x1='{X(0)}' y1='{Y(3.2):.1f}' x2='{W - R}' y2='{Y(3.2):.1f}' stroke='{GREEN}' stroke-width='1.4' stroke-dasharray='4,3'/>")
    s.append(text(X(1600), Y(3.2) - 6, "3.20 ft: the rating's offset, about the gage height of zero flow — h is measured from here", 11, fill=GREEN))
    s.append(f"<circle cx='{X(2150):.1f}' cy='{Y(8.0):.1f}' r='3' fill='{NAVY}'/>" + text(X(2150) + 8, Y(8.0) + 30, "top of the table: 8.00 ft, 2,150 ft³/s", 11, fill=NAVY))
    for r in st:
        q, g = r["Q_CFS"], r["GAGE_HT_FT"]
        s.append(f"<line x1='{X(q):.1f}' y1='{Y(g):.1f}' x2='{X(q):.1f}' y2='{Y(3):.1f}' stroke='{ORANGE}' stroke-width='1' stroke-dasharray='2,3'/>")
        s.append(f"<circle cx='{X(q):.1f}' cy='{Y(g):.1f}' r='5' fill='{ORANGE}' stroke='white'/>")
        lab = f"{r['RETURN_YR']}-yr: {q:,} ft³/s → {g:.2f} ft"
        if r["RETURN_YR"] in (100, 500):
            if r["RETURN_YR"] == 100:
                s.append(text(X(q) + 8, Y(g) + 16, lab, 11, "bold", ORANGE, "start"))
            else:
                s.append(text(X(q) - 10, Y(g) - 9, lab, 11, "bold", ORANGE, "end"))
        else:
            s.append(text(X(q) - 8, Y(g) - 9, lab, 11, "bold", ORANGE, "end"))
    lx, ly = L + 24, T + 24
    s.append(f"<line x1='{lx}' y1='{ly}' x2='{lx + 30}' y2='{ly}' stroke='{NAVY}' stroke-width='2.6'/>" + text(lx + 38, ly + 4, "the published rating table (rating_10163000.csv)", 12))
    s.append(f"<line x1='{lx}' y1='{ly + 20}' x2='{lx + 30}' y2='{ly + 20}' stroke='{NAVY}' stroke-width='2' stroke-dasharray='6,4'/>"
             + text(lx + 38, ly + 24, "extended above the table (the 100- and 500-year rows)", 12))
    s.append("</svg>")
    (h.OUT / "lab07-rating.svg").write_text("\n".join(s), encoding="utf-8")


def profile():
    d = json.load(open(HERE / "profile.json"))
    W, H = 1000, 780
    s = svg_open(W, H, "Two measured panels: the river's long profile with a flat bathtub level and the HAND water surface; and FEMA cross-section C with HAND's wet cells",
                 "Bathtub versus HAND along the Provo River, and HAND against FEMA at one cross-section")
    s.append(text(30, 30, "One stage, two models: the 100-year flood along the river and across it", 18, "bold", NAVY))
    # panel 1: long profile
    L, R, T, B = 80, 30, 60, 410
    pts = [(k, z) for k, z in d["long"] if z is not None]
    k1 = d["river_km"]
    z0, z1 = 1360, 1470
    X = lambda k: L + (W - L - R) * k / k1
    Y = lambda z: T + (B - T) * (z1 - z) / (z1 - z0)
    for z in range(1360, 1471, 20):
        s.append(f"<line x1='{L}' y1='{Y(z):.1f}' x2='{W - R}' y2='{Y(z):.1f}' stroke='#e3e7eb'/>" + text(L - 8, Y(z) + 4, f"{z:,}", 11, fill=GRAY, anchor="end"))
    for k in range(0, int(k1) + 1, 2):
        s.append(text(X(k), B + 18, f"{k}", 11, fill=GRAY, anchor="middle"))
    s.append(text((L + W - R) / 2, B + 38, "kilometers down the river from the top of the study area (Provo Canyon's mouth) to Utah Lake", 11.5, fill=GRAY, anchor="middle"))
    mid = (T + B) / 2
    s.append(f"<g transform='rotate(-90 22 {mid})'>" + text(22, mid, "meters above NAVD 88", 11.5, fill=GRAY, anchor="middle") + "</g>")
    hh = d["h100_m"]
    s.append("<polygon points='" + " ".join(f"{X(k):.1f},{Y(z + hh):.1f}" for k, z in pts) + " "
             + " ".join(f"{X(k):.1f},{Y(z):.1f}" for k, z in reversed(pts)) + f"' fill='{BLUE}' opacity='0.55'/>")
    s.append("<polyline points='" + " ".join(f"{X(k):.1f},{Y(z):.1f}" for k, z in pts) + f"' fill='none' stroke='{INK}' stroke-width='2'/>")
    e = d["elev100_m"]
    s.append(f"<line x1='{L}' y1='{Y(e):.1f}' x2='{W - R}' y2='{Y(e):.1f}' stroke='{ORANGE}' stroke-width='2.4' stroke-dasharray='8,4'/>")
    gx = X(d["gage_km"])
    s.append(f"<line x1='{gx:.1f}' y1='{T}' x2='{gx:.1f}' y2='{B}' stroke='{GRAY}' stroke-dasharray='3,3'/>" + text(gx - 6, T + 14, "gage 10163000", 11, "bold", GRAY, "end"))
    s.append(text(X(0.4), Y(e) - 22, f"Bathtub: one flat water surface at the 100-year stage elevation, {e:,.2f} m.", 11.5, "bold", ORANGE))
    s.append(text(X(0.4), Y(e) - 7, f"Below it lie only the lowest {d['long_summary']['km_below_bathtub']:.1f} km of the river, from the gage to Utah Lake.", 11.5, "bold", ORANGE))
    s.append(text(X(8.6), Y(1458), f"HAND: water {hh:.2f} m above the river everywhere —", 11.5, "bold", BLUE))
    s.append(text(X(8.6), Y(1458) + 16, "the thin blue band on the river line, drawn to scale", 11.5, "bold", BLUE))
    s.append(text(X(8.6), Y(1458) + 32, "river line: lowest filled-DEM cell within 15 m of the NHD line, every 25 m", 10.5, fill=GRAY))
    # panel 2: cross-section C
    L2, T2, B2 = 80, 520, 715
    xs = d["xs"]
    prof = [(x, z, hd) for x, z, hd in xs["profile"] if z is not None]
    xmax = prof[-1][0]
    zz = [z for _, z, _ in prof]
    za, zb = math.floor(min(zz)) - 1, math.ceil(max(max(zz), xs["wsel_m"])) + 1
    X2 = lambda x: L2 + (W - L2 - R) * x / xmax
    Y2 = lambda z: T2 + (B2 - T2) * (zb - z) / (zb - za)
    s.append(text(L2, T2 - 18, f"FEMA cross-section C, just upstream of the gage: ground, FEMA's 1% water surface ({xs['wsel_m']:,.2f} m), and the cells HAND floods at h = {hh:.2f} m", 13, "bold", NAVY))
    for z in range(int(za), int(zb) + 1, 2):
        s.append(f"<line x1='{L2}' y1='{Y2(z):.1f}' x2='{W - R}' y2='{Y2(z):.1f}' stroke='#e3e7eb'/>" + text(L2 - 8, Y2(z) + 4, f"{z:,}", 11, fill=GRAY, anchor="end"))
    for x in range(0, int(xmax) + 1, 20):
        s.append(text(X2(x), B2 + 18, f"{x}", 11, fill=GRAY, anchor="middle"))
    s.append(text((L2 + W - R) / 2, B2 + 38, "meters along the FEMA cross-section line (FEMA_Cross_Sections, XS_LTR = C)", 11.5, fill=GRAY, anchor="middle"))
    for x, z, hd in prof:
        if hd is not None and hd <= hh:
            bw = X2(5) - X2(0)
            s.append(f"<rect x='{X2(x) - bw / 2:.1f}' y='{Y2(z):.1f}' width='{bw:.1f}' height='{B2 - Y2(z):.1f}' fill='{BLUE}' opacity='0.45'/>")
    s.append("<polyline points='" + " ".join(f"{X2(x):.1f},{Y2(z):.1f}" for x, z, _ in prof) + f"' fill='none' stroke='{INK}' stroke-width='2'/>")
    s.append(f"<line x1='{L2}' y1='{Y2(xs['wsel_m']):.1f}' x2='{W - R}' y2='{Y2(xs['wsel_m']):.1f}' stroke='{GREEN}' stroke-width='2' stroke-dasharray='6,4'/>")
    s.append(f"<line x1='{L2}' y1='{Y2(xs['bed_m']):.1f}' x2='{L2 + 120}' y2='{Y2(xs['bed_m']):.1f}' stroke='{GRAY}' stroke-width='1.4'/>")
    s.append(text(L2 + 126, Y2(xs['bed_m']) + 4, f"FEMA streambed {xs['bed_m']:,.2f} m", 10.5, fill=GRAY))
    lx, ly = W - 330, T2 + 6
    s.append(f"<rect x='{lx}' y='{ly}' width='16' height='12' fill='{BLUE}' opacity='0.45'/>" + text(lx + 22, ly + 10, "ground HAND floods (HAND ≤ h)", 11.5))
    s.append(f"<line x1='{lx}' y1='{ly + 26}' x2='{lx + 16}' y2='{ly + 26}' stroke='{GREEN}' stroke-width='2' stroke-dasharray='6,4'/>" + text(lx + 22, ly + 30, "FEMA 1% water surface (WSEL_REG)", 11.5))
    s.append(f"<line x1='{lx}' y1='{ly + 46}' x2='{lx + 16}' y2='{ly + 46}' stroke='{INK}' stroke-width='2'/>" + text(lx + 22, ly + 50, "ground (Provo_DEM, every 5 m)", 11.5))
    s.append("</svg>")
    (h.OUT / "lab07-profile.svg").write_text("\n".join(s), encoding="utf-8")


def model():
    """A drawn diagram of the two models, in ModelBuilder's colors. Not an export."""
    W, H = 1100, 470
    s = svg_open(W, H, "Diagram of the two models: HAND Builder and Flood Loop",
                 "The two models of Lab 7, drawn as a diagram")
    BLUEV, YEL, GRN = "#9fc5e8", "#fff2a8", "#b6d7a8"

    def oval(x, y, label, fill, p=False, w=128):
        out = f"<ellipse cx='{x}' cy='{y}' rx='{w / 2}' ry='19' fill='{fill}' stroke='{GRAY}'/>" + text(x, y + 4, label, 11, "normal", INK, "middle")
        if p:
            out += text(x + w / 2 - 2, y - 14, "P", 11, "bold", NAVY, "middle")
        return out

    def tool(x, y, label, w=128):
        return f"<rect x='{x - w / 2}' y='{y - 18}' width='{w}' height='36' rx='6' fill='{YEL}' stroke='{GRAY}'/>" + text(x, y + 4, label, 11, "bold", INK, "middle")

    def link(x1, y1, x2, y2):
        return arrow(x1, y1, x2, y2, GRAY, 1.4, 7)

    s.append(text(20, 28, "Model 1 — HAND Builder (Steps 2 to 4)", 15, "bold", NAVY))
    y = 80
    xs = [70, 205, 340, 475, 610, 745, 880, 1020]
    labs = [("Provo_DEM", BLUEV, True), ("Fill", None), ("Filled_DEM", GRN), ("Flow Direction", None), ("Flow_Direction", GRN),
            ("Flow Accumulation", None), ("Flow_Accumulation", GRN)]
    for i, item in enumerate(labs):
        lab, fill = item[0], item[1]
        s.append(tool(xs[i], y, lab, 124) if fill is None else oval(xs[i], y, lab, fill, len(item) > 2 and item[2], 124))
        if i:
            s.append(link(xs[i - 1] + 62, y, xs[i] - 62, y))
    y2 = 170
    row2 = [(1020, "Raster Calculator", None), (880, "Stream_Cells", GRN), (745, "Extract by Mask", None), (610, "River_Cells", GRN),
            (475, "Flow Distance", None), (340, "HAND", GRN)]
    s.append(f"<path d='M940,{y} C1000,{y} 1020,{y + 20} 1020,{y2 - 26}' fill='none' stroke='{GRAY}' stroke-width='1.4'/>" + arrowhead(1020, y2 - 18, math.radians(90), GRAY, 7))
    for i, (x, lab, fill) in enumerate(row2):
        s.append(tool(x, y2, lab, 124) if fill is None else oval(x, y2, lab, fill, lab == "HAND", 124))
        if i:
            s.append(link(row2[i - 1][0] - 62, y2, x + 62, y2))
    s.append(oval(1020, y2 + 70, "Threshold (2000)", BLUEV, True, 124) + link(1020, y2 + 51, 1020, y2 + 18))
    s.append(oval(610, y2 + 70, "Provo_River", BLUEV, False, 110) + tool(745, y2 + 70, "Buffer 30 m", 110) + oval(880, y2 + 70, "River_Corridor", GRN, False, 120))
    s.append(link(665, y2 + 70, 690, y2 + 70) + link(800, y2 + 70, 820, y2 + 70) + link(860, y2 + 51, 770, y2 + 18))
    s.append(f"<path d='M340,{y + 19} C340,{y + 50} 470,{y + 60} 475,{y2 - 18}' fill='none' stroke='{GRAY}' stroke-width='1.2'/>")
    s.append(f"<path d='M610,{y + 19} C610,{y + 50} 490,{y + 60} 480,{y2 - 18}' fill='none' stroke='{GRAY}' stroke-width='1.2'/>")
    s.append(text(475, y2 + 40, "(also takes Filled_DEM and Flow_Direction)", 10, fill=GRAY, anchor="middle"))
    s.append(text(20, 318, "Model 2 — Flood Loop (Step 5)", 15, "bold", NAVY))
    y3 = 380
    row3 = [(70, "Stage_Table", BLUEV), (205, "Iterate Field Values", "it"), (340, "Value (H_CM)", GRN), (475, "Raster Calculator", None),
            (610, "flood_%Value%", GRN), (745, "Raster to Polygon", None), (880, "Calculate Field", None), (1020, "Collect → Merge", None)]
    for i, (x, lab, fill) in enumerate(row3):
        if fill == "it":
            s.append(f"<rect x='{x - 64}' y='{y3 - 18}' width='128' height='36' rx='18' fill='{LORANGE}' stroke='{ORANGE}'/>" + text(x, y3 + 4, lab, 11, "bold", INK, "middle"))
        elif fill is None:
            s.append(tool(x, y3, lab, 124))
        else:
            s.append(oval(x, y3, lab, fill, False, 124))
        if i:
            s.append(link(row3[i - 1][0] + 62, y3, x - 62, y3))
    s.append(oval(475, y3 + 60, "HAND", BLUEV, True, 90) + link(475, y3 + 41, 475, y3 + 18))
    s.append(oval(1020, y3 + 60, "Floods", GRN, True, 100) + link(1020, y3 + 18, 1020, y3 + 41))
    s.append(text(475, y3 - 30, 'Con("%HAND%" <= %Value% / 100, 1)', 10.5, "bold", NAVY, "middle"))
    s.append(text(W - 20, H - 8, "A drawn diagram, not a ModelBuilder export. P = model parameter.", 10, fill=GRAY, anchor="end"))
    s.append("</svg>")
    (h.OUT / "lab07-model.svg").write_text("\n".join(s), encoding="utf-8")


if __name__ == "__main__":
    h.OUT.mkdir(parents=True, exist_ok=True)
    icons()
    metadata_card()
    rating()
    profile()
    model()
    print("wrote icons and Figures A, B, C and 1 to", h.OUT)
