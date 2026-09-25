# Generates the Lab 4 tool icons and the two infographics as SVG with real text.
#   python make_svgs.py  -> docs/assignments/lab-04/images/icon-*.svg, lab04-tower-metadata.svg,
#                           lab04-one-tower-density.svg
# Same palette and icon frame as tools/lab01/make_svgs.py. The density figure is computed from
# the kernel ArcGIS Pro documents for Kernel Density ("How Kernel Density works"):
#   density(d) = 3 / (pi r^2) * (1 - (d/r)^2)^2   for d < r, one point, no population field.
import math, pathlib

OUT = pathlib.Path(__file__).resolve().parents[2] / "docs" / "assignments" / "lab-04" / "images"
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, GREEN, LGREEN, INK = (
    "#002e5d", "#0062b8", "#cfe3f7", "#9aa5b1", "#e6eaee", "#e8862a", "#fdebd9", "#3b8a3e", "#d7ecd4", "#1c2733")
FONT = "font-family='Segoe UI, Roboto, Helvetica, Arial, sans-serif'"


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("'", "&#39;"))


def text(x, y, s, size=12, weight="normal", fill=INK, anchor="start"):
    return (f"<text x='{x}' y='{y}' font-size='{size}' font-weight='{weight}' fill='{fill}' "
            f"text-anchor='{anchor}' {FONT}>{esc(s)}</text>")


def icon(name, title, body):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 90' width='120' height='90' role='img' aria-label='{esc(title)}'>"
           f"<title>{esc(title)}</title>{body}</svg>")
    (OUT / f"icon-{name}.svg").write_text(svg, encoding="utf-8")


def grid(x, y, n, cell, fills, stroke=GRAY):
    s = ""
    for r in range(n):
        for c in range(n):
            s += (f"<rect x='{x + c * cell}' y='{y + r * cell}' width='{cell}' height='{cell}' "
                  f"fill='{fills(r, c)}' stroke='{stroke}' stroke-width='0.8'/>")
    return s


def icons():
    # Mosaic To New Raster: four tiles become one raster
    shades = [LBLUE, "#b7d3ef", "#a4c6ea", "#c3daf2"]
    body = ""
    for i, (dx, dy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
        body += f"<rect x='{8 + dx * 22}' y='{14 + dy * 32}' width='20' height='30' fill='{shades[i]}' stroke='{BLUE}' stroke-width='1.3'/>"
    body += f"<path d='M58,45 L70,45' stroke='{NAVY}' stroke-width='2.2'/><polygon points='74,45 67,40 67,50' fill='{NAVY}'/>"
    body += f"<rect x='78' y='14' width='34' height='62' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='2'/>"
    body += f"<line x1='95' y1='14' x2='95' y2='76' stroke='{ORANGE}' stroke-width='0.8' stroke-dasharray='3 3'/>"
    body += f"<line x1='78' y1='45' x2='112' y2='45' stroke='{ORANGE}' stroke-width='0.8' stroke-dasharray='3 3'/>"
    icon("mosaic", "Mosaic To New Raster: several raster tiles joined into one new raster", body)

    # Project Raster: a skewed lat/long grid resampled to a square grid
    body = (f"<polygon points='10,22 48,14 54,66 16,74' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.5'/>"
            f"<line x1='29' y1='18' x2='35' y2='70' stroke='{BLUE}' stroke-width='0.9'/>"
            f"<line x1='13' y1='48' x2='51' y2='40' stroke='{BLUE}' stroke-width='0.9'/>"
            f"<path d='M60,45 L70,45' stroke='{NAVY}' stroke-width='2.2'/><polygon points='74,45 67,40 67,50' fill='{NAVY}'/>")
    body += grid(78, 23, 3, 12, lambda r, c: LORANGE, ORANGE)
    icon("project-raster", "Project Raster: move a raster into another coordinate system and resample it to new cells", body)

    # Slope: a terrain profile with a rise-over-run triangle
    body = (f"<path d='M6,78 L30,70 L58,34 L78,26 L114,22 L114,84 L6,84 Z' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>"
            f"<path d='M30,70 L58,34 L58,70 Z' fill='{LORANGE}' stroke='{ORANGE}' stroke-width='1.8'/>"
            f"<path d='M44,70 A14,14 0 0 0 41,62' fill='none' stroke='{NAVY}' stroke-width='1.6'/>"
            + text(48, 66, "θ", 11, "bold", NAVY))
    icon("slope", "Slope: the steepness of each cell of an elevation surface, in degrees or percent", body)

    # Kernel Density: points with a smooth bump around them
    body = ""
    for r, a in ((34, 0.18), (24, 0.3), (14, 0.5)):
        body += f"<circle cx='52' cy='46' r='{r}' fill='{ORANGE}' fill-opacity='{a}'/>"
    body += f"<circle cx='86' cy='30' r='16' fill='{ORANGE}' fill-opacity='0.22'/><circle cx='86' cy='30' r='8' fill='{ORANGE}' fill-opacity='0.4'/>"
    for x, y in ((50, 44), (56, 50), (46, 52), (86, 30)):
        body += f"<circle cx='{x}' cy='{y}' r='3' fill='{NAVY}'/>"
    body += f"<circle cx='52' cy='46' r='34' fill='none' stroke='{NAVY}' stroke-width='1' stroke-dasharray='4 3'/>"
    icon("kernel-density", "Kernel Density: a smooth surface of how many points lie near each cell", body)

    # Extract by Mask: a raster cut to the shape of a mask
    def f(r, c):
        return LORANGE if (r - 2.5) ** 2 / 6 + (c - 3.5) ** 2 / 9 <= 1 else LGRAY
    body = grid(18, 9, 6, 12, f)
    body += (f"<ellipse cx='60' cy='45' rx='36' ry='29' fill='none' stroke='{ORANGE}' stroke-width='2.4'/>")
    icon("extract-by-mask", "Extract by Mask: keep only the raster cells that fall inside a mask", body)

    # Clip: points kept only inside the clip polygon
    body = f"<path d='M20,20 C44,6 92,12 100,38 C108,66 70,82 40,74 C16,68 8,40 20,20 Z' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.8'/>"
    inside = ((40, 34), (62, 26), (78, 48), (50, 58), (86, 32))
    outside = ((8, 80), (112, 12), (112, 76), (8, 10))
    for x, y in inside:
        body += f"<circle cx='{x}' cy='{y}' r='4' fill='{ORANGE}' stroke='{NAVY}' stroke-width='1'/>"
    for x, y in outside:
        body += f"<circle cx='{x}' cy='{y}' r='3.2' fill='white' stroke='{GRAY}' stroke-width='1.2'/>"
    icon("clip", "Clip: keep only the features inside another layer's boundary", body)


def metadata_card(n_ut=224, n_dup=33):
    W, H = 1000, 480
    cards = [
        ("WHAT", "What do the data represent?",
         ["Point locations of FCC cellular license sites:",
          "one record per licensee per site, not one per",
          "tower. Fields include Licensee, StrucType and",
          f"AllStruc (height, m). {n_dup} of the {n_ut} Utah records",
          "share their exact spot with another record."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["The extract is every Utah record.",
          "Stored in latitude/longitude (GCS WGS 1984),",
          "so it must be projected before you measure",
          "a distance or a density in kilometers."]),
        ("WHEN", "When were the data collected?",
         ["Source layer: 'Last Data Update: 07/06/2024'.",
          "It is an ARCHIVE: its publisher says it will",
          "no longer be updated or maintained.",
          "Every tower built since is missing."]),
        ("WHY", "Why were they created?",
         ["HIFLD gathers infrastructure layers for",
          "homeland security and emergency management,",
          "here compiled from the FCC's licensing records.",
          "Not to measure coverage, and not for your question."]),
        ("HOW", "How were they collected and processed?",
         ["Licensees report sites to the FCC for the",
          "Cellular Radiotelephone Service (the original",
          "800 MHz band) only. Sites licensed only for PCS,",
          "AWS or later spectrum are not in it at all."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["Federal Communications Commission, via the",
          "HIFLD program; hosted by Federal_User_Community.",
          "U.S. government data, no use restrictions.",
          "Credit the FCC and HIFLD in your report."]),
    ]
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='The six metadata questions applied to the cell tower layer'>",
         "<title>The six metadata questions, applied to the cell tower data</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "Reading the tower layer's metadata: the six questions from CCE 114", 20, "bold", NAVY),
         text(20, 56, "Every answer below comes from the source layer's description and READ-ME-FIRST.txt in the extract. Check them yourself.", 12, fill="#5b6770")]
    cw, ch, gx, gy = 310, 150, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
        s.append(f"<rect x='{x}' y='{y}' width='{cw}' height='34' rx='8' fill='{NAVY}'/>")
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s += [text(x + 12, y + 60 + k * 18, line, 11.5) for k, line in enumerate(body)]
    s.append(f"<rect x='20' y='{H - 70}' width='960' height='55' rx='8' fill='{ORANGE}'/>")
    s.append(text(32, H - 46, "The question that matters most here is HOW: this layer is a small, dated subset of the towers that exist.", 12.5, "bold", "white"))
    s.append(text(32, H - 26, "A 'low tower density' cell may only mean 'no FCC cellular license site recorded nearby'. Your report has to say so.", 12.5, "bold", "white"))
    s.append("</svg>")
    (OUT / "lab04-tower-metadata.svg").write_text("\n".join(s), encoding="utf-8")


def kernel(d_km, r_km):
    return 3 / (math.pi * r_km ** 2) * (1 - (d_km / r_km) ** 2) ** 2 if d_km < r_km else 0.0


def cross(r_km, thr_per10k):
    """Distance from a single point at which its density falls to the threshold (km), or None."""
    peak = 3 / (math.pi * r_km ** 2) * 1e4
    if peak <= thr_per10k:
        return None
    return r_km * math.sqrt(1 - math.sqrt(thr_per10k / peak))


def density_figure(thr=20):
    W, H = 1000, 475
    x0, y0, pw, ph = 90, 80, 560, 300          # plot box
    dmax, ymax = 30.0, 100.0                   # km, towers per 10,000 km^2
    X = lambda d: x0 + d / dmax * pw
    Y = lambda v: y0 + ph - min(v, ymax) / ymax * ph
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' "
         "aria-label='Density around a single tower for search radii of 10, 20 and 40 kilometers, against the 20 per 10,000 square kilometer threshold'>",
         "<title>What the density threshold means around one tower</title>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         text(20, 34, "What '20 towers per 10,000 km²' means around ONE tower", 20, "bold", NAVY),
         text(20, 56, "Kernel Density spreads each tower over a circle of the search radius. The curve is the density that one tower alone contributes, by distance.", 12, fill="#5b6770")]
    # axes and grid
    for v in range(0, 101, 20):
        s.append(f"<line x1='{x0}' y1='{Y(v):.1f}' x2='{x0 + pw}' y2='{Y(v):.1f}' stroke='#e3e8ed'/>")
        s.append(text(x0 - 8, Y(v) + 4, v, 11, anchor="end", fill="#5b6770"))
    for d in range(0, 31, 5):
        s.append(text(X(d), y0 + ph + 18, d, 11, anchor="middle", fill="#5b6770"))
    s.append(f"<rect x='{x0}' y='{y0}' width='{pw}' height='{ph}' fill='none' stroke='{GRAY}'/>")
    s.append(text(x0 + pw / 2, y0 + ph + 40, "Distance from the tower (km)", 12, anchor="middle"))
    s.append(f"<text transform='translate(28,{y0 + ph / 2}) rotate(-90)' font-size='12' text-anchor='middle' fill='{INK}' {FONT}>Towers per 10,000 km²</text>")
    # threshold
    s.append(f"<line x1='{x0}' y1='{Y(thr):.1f}' x2='{x0 + pw}' y2='{Y(thr):.1f}' stroke='{ORANGE}' stroke-width='2' stroke-dasharray='7 4'/>")
    s.append(text(x0 + pw - 6, Y(thr) - 6, f"threshold: {thr} per 10,000 km²", 11.5, "bold", ORANGE, "end"))
    rows = []
    for r_km, col in ((10, BLUE), (20, NAVY), (40, GREEN)):
        pts = " ".join(f"{X(d):.1f},{Y(kernel(d, r_km) * 1e4):.1f}" for d in [i * 0.1 for i in range(0, 301)])
        s.append(f"<polyline points='{pts}' fill='none' stroke='{col}' stroke-width='{3 if r_km == 20 else 2}'/>")
        peak = 3 / (math.pi * r_km ** 2) * 1e4
        c = cross(r_km, thr)
        rows.append((r_km, col, peak, c))
        if c:
            s.append(f"<circle cx='{X(c):.1f}' cy='{Y(thr):.1f}' r='4.5' fill='white' stroke='{col}' stroke-width='2'/>")
    # key
    kx, ky = 690, 90
    s.append(f"<rect x='{kx - 10}' y='{ky - 22}' width='300' height='300' rx='8' fill='#eef2f6' stroke='#c9d2dc'/>")
    s.append(text(kx, ky, "Search radius", 13, "bold", NAVY))
    for i, (r_km, col, peak, c) in enumerate(rows):
        y = ky + 34 + i * 78
        s.append(f"<line x1='{kx}' y1='{y - 4}' x2='{kx + 26}' y2='{y - 4}' stroke='{col}' stroke-width='3'/>")
        s.append(text(kx + 34, y, f"{r_km} km" + ("  (the value given)" if r_km == 20 else ""), 12.5, "bold", col))
        s.append(text(kx + 34, y + 19, f"peak {peak:.1f} per 10,000 km²", 11.5))
        s.append(text(kx + 34, y + 37, f"one tower fails the test within {c:.1f} km" if c else "one tower alone never fails the test", 11.5))
    s.append(text(20, H - 22, "Computed from the kernel ArcGIS Pro documents for Kernel Density (planar, no population field): density = 3 / (πr²) × (1 − (d/r)²)². Nearby towers add up.", 11, fill="#5b6770"))
    s.append("</svg>")
    (OUT / "lab04-one-tower-density.svg").write_text("\n".join(s), encoding="utf-8")
    return rows


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    icons()
    metadata_card()
    for r in density_figure():
        print(r)
