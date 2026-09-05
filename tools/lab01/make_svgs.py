# Generates the Lab 1 tool icons and the two infographics as SVG with real text.
import pathlib
OUT = pathlib.Path(r"C:\Users\dpame\code\ce414-gis-applications\docs\assignments\lab-01\images")
NAVY, BLUE, LBLUE, GRAY, LGRAY, ORANGE, LORANGE, CYAN = "#002e5d", "#0062b8", "#cfe3f7", "#9aa5b1", "#e6eaee", "#e8862a", "#fdebd9", "#19c3e6"
FONT = "font-family='Segoe UI, Roboto, Helvetica, Arial, sans-serif'"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def icon(name, title, body):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 90' width='120' height='90' role='img' aria-label='{esc(title)}'>"
           f"<title>{esc(title)}</title>{body}</svg>")
    (OUT / f"icon-{name}.svg").write_text(svg, encoding="utf-8")


# ---- Select: several features, one picked out in ArcGIS selection cyan
polys = ["12,20 40,14 46,40 18,46", "48,12 78,10 82,34 52,38", "84,14 108,22 104,50 80,44",
         "14,52 44,46 50,74 20,80", "54,44 82,48 78,78 56,76"]
body = "".join(f"<polygon points='{p}' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.5'/>" for p in polys)
body += f"<polygon points='54,44 82,48 78,78 56,76' fill='{ORANGE}' stroke='{CYAN}' stroke-width='3' stroke-linejoin='round'/>"
body += f"<polygon points='88,58 106,66 98,69 104,80 100,82 94,71 88,77' fill='white' stroke='{NAVY}' stroke-width='1.6' stroke-linejoin='round'/>"
icon("select", "Select: pick out the features whose attributes match an expression", body)

# ---- Intersect: two shapes, only the overlap survives (orange)
body = (f"<defs><clipPath id='a'><circle cx='46' cy='45' r='28'/></clipPath></defs>"
        f"<circle cx='74' cy='45' r='28' fill='{LGRAY}' stroke='{GRAY}' stroke-width='1.8'/>"
        f"<circle cx='46' cy='45' r='28' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.8'/>"
        f"<circle cx='74' cy='45' r='28' fill='{ORANGE}' clip-path='url(#a)'/>"
        f"<circle cx='74' cy='45' r='28' fill='none' stroke='{GRAY}' stroke-width='1.8'/>"
        f"<circle cx='46' cy='45' r='28' fill='none' stroke='{BLUE}' stroke-width='1.8'/>")
icon("intersect", "Intersect: keep only the area where the inputs overlap", body)

# ---- Buffer: a band of fixed distance around a line and a point
path = "M14,66 L40,34 L70,56 L106,24"
body = (f"<path d='{path}' fill='none' stroke='{BLUE}' stroke-width='24' stroke-linejoin='round' stroke-linecap='round'/>"
        f"<path d='{path}' fill='none' stroke='{LBLUE}' stroke-width='21' stroke-linejoin='round' stroke-linecap='round'/>"
        f"<path d='{path}' fill='none' stroke='{NAVY}' stroke-width='2.4' stroke-linejoin='round' stroke-linecap='round'/>"
        f"<circle cx='22' cy='18' r='12' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.5'/>"
        f"<circle cx='22' cy='18' r='2.6' fill='{NAVY}'/>"
        f"<line x1='70' y1='56' x2='70' y2='67' stroke='{ORANGE}' stroke-width='1.8'/>"
        f"<polygon points='70,69 67,63 73,63' fill='{ORANGE}'/>")
icon("buffer", "Buffer: a zone of fixed distance around a feature", body)

# ---- Erase: a polygon with a bite taken out where the erase feature lies
blob = "M14,26 C20,10 60,8 84,18 C110,28 112,60 92,74 C70,86 30,84 16,66 C6,52 8,40 14,26 Z"
body = (f"<defs><mask id='m'><rect width='120' height='90' fill='white'/><circle cx='80' cy='40' r='22' fill='black'/></mask></defs>"
        f"<path d='{blob}' fill='{LBLUE}' stroke='{BLUE}' stroke-width='1.8' mask='url(#m)'/>"
        f"<circle cx='80' cy='40' r='22' fill='none' stroke='{ORANGE}' stroke-width='2' stroke-dasharray='5 4'/>")
icon("erase", "Erase: remove the area covered by another layer", body)


def table(extra_col_fill, header_glyph, cells):
    x0, y0, cw, rh, ncol, nrow = 12, 16, 22, 14, 3, 4
    s = f"<rect x='{x0}' y='{y0}' width='{cw*ncol}' height='{rh}' fill='{LGRAY}'/>"
    for r in range(nrow + 1):
        y = y0 + r * rh
        s += f"<line x1='{x0}' y1='{y}' x2='{x0+cw*ncol}' y2='{y}' stroke='{GRAY}' stroke-width='1.2'/>"
    for c in range(ncol + 1):
        x = x0 + c * cw
        s += f"<line x1='{x}' y1='{y0}' x2='{x}' y2='{y0+rh*nrow}' stroke='{GRAY}' stroke-width='1.2'/>"
    for r in range(1, nrow):
        for c in range(ncol):
            s += f"<rect x='{x0+c*cw+4}' y='{y0+r*rh+5}' width='{8 + (c*3+r*5) % 10}' height='4' rx='1' fill='{GRAY}'/>"
    nx = x0 + cw * ncol
    ncw = 30
    dash = "4 3" if cells is None else "none"
    s += f"<rect x='{nx}' y='{y0}' width='{ncw}' height='{rh*nrow}' fill='{extra_col_fill}' stroke='{ORANGE}' stroke-width='2' stroke-dasharray='{dash}'/>"
    s += f"<text x='{nx+ncw/2}' y='{y0+rh-3}' text-anchor='middle' font-size='11' font-weight='700' fill='{ORANGE}' {FONT}>{header_glyph}</text>"
    if cells:
        for r, w in enumerate(cells, start=1):
            s += f"<rect x='{nx+5}' y='{y0+r*rh+5}' width='{w}' height='4' rx='1' fill='{NAVY}'/>"
    return s


icon("add-field", "Add Field: append a new, empty column to the attribute table", table(LORANGE, "+", None))
icon("calculate-field", "Calculate Field: fill a column from an expression", table(LBLUE, "\u0192x", [16, 10, 20]))


def wrap(text, n):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    lines.append(cur)
    return lines


# ================= Infographic 1: the six questions metadata answers =================
W, H = 960, 516
cards = [
    ("What?", "What do the data represent, in what format, and what does each attribute mean?",
     "CARTOCODE = '4' means nothing until you find its domain."),
    ("Where?", "What area do they cover, and in which coordinate system and units?",
     "Web Mercator looks fine and measures 71% wrong in Utah."),
    ("When?", "When were they collected, when last updated, and how often are they revised?",
     "2010 census blocks are not 2020 census tracts."),
    ("Why?", "What was the dataset made for in the first place?",
     "A layer drawn for a road map is not an engineering centerline."),
    ("How?", "How were they collected, and what processing came after?",
     "Our roads extract was clipped and repackaged; its README says exactly how."),
    ("Who?", "Which organization maintains them, and who do you contact when something looks wrong?",
     "UGRC maintains Utah Roads. A stranger's copy on ArcGIS Online is not a source."),
]


def glyph(i, cx, cy):
    c = BLUE
    if i == 0:   # table (what)
        s = f"<rect x='{cx-18}' y='{cy-13}' width='36' height='28' rx='2' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
        s += f"<rect x='{cx-18}' y='{cy-13}' width='36' height='8' fill='{c}'/>"
        for k in (1, 2):
            s += f"<line x1='{cx-18}' y1='{cy-13+8+k*7}' x2='{cx+18}' y2='{cy-13+8+k*7}' stroke='{c}' stroke-width='1.2'/>"
        for k in (1, 2):
            s += f"<line x1='{cx-18+k*12}' y1='{cy-5}' x2='{cx-18+k*12}' y2='{cy+15}' stroke='{c}' stroke-width='1.2'/>"
        return s
    if i == 1:   # globe (where)
        return (f"<circle cx='{cx}' cy='{cy}' r='17' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
                f"<ellipse cx='{cx}' cy='{cy}' rx='7' ry='17' fill='none' stroke='{c}' stroke-width='1.5'/>"
                f"<line x1='{cx-17}' y1='{cy}' x2='{cx+17}' y2='{cy}' stroke='{c}' stroke-width='1.5'/>"
                f"<line x1='{cx-15}' y1='{cy-8}' x2='{cx+15}' y2='{cy-8}' stroke='{c}' stroke-width='1.5'/>"
                f"<line x1='{cx-15}' y1='{cy+8}' x2='{cx+15}' y2='{cy+8}' stroke='{c}' stroke-width='1.5'/>")
    if i == 2:   # calendar (when)
        return (f"<rect x='{cx-17}' y='{cy-14}' width='34' height='30' rx='3' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
                f"<rect x='{cx-17}' y='{cy-14}' width='34' height='9' fill='{c}'/>"
                + "".join(f"<rect x='{cx-12+k*8}' y='{cy-1}' width='5' height='5' fill='{c}'/>" for k in range(4))
                + "".join(f"<rect x='{cx-12+k*8}' y='{cy+7}' width='5' height='5' fill='{c}'/>" for k in range(2)))
    if i == 3:   # target (why / purpose)
        return (f"<circle cx='{cx}' cy='{cy}' r='17' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
                f"<circle cx='{cx}' cy='{cy}' r='10' fill='none' stroke='{c}' stroke-width='2'/>"
                f"<circle cx='{cx}' cy='{cy}' r='3.5' fill='{ORANGE}'/>")
    if i == 4:   # gears / process (how)
        return (f"<circle cx='{cx-6}' cy='{cy-2}' r='12' fill='{LBLUE}' stroke='{c}' stroke-width='2' stroke-dasharray='4 3'/>"
                f"<circle cx='{cx-6}' cy='{cy-2}' r='4' fill='{c}'/>"
                f"<circle cx='{cx+11}' cy='{cy+10}' r='8' fill='{LBLUE}' stroke='{ORANGE}' stroke-width='2' stroke-dasharray='3 2.5'/>"
                f"<circle cx='{cx+11}' cy='{cy+10}' r='2.5' fill='{ORANGE}'/>")
    # building (who)
    return (f"<rect x='{cx-16}' y='{cy-8}' width='32' height='22' rx='2' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
            f"<polygon points='{cx-20},{cy-8} {cx},{cy-20} {cx+20},{cy-8}' fill='none' stroke='{c}' stroke-width='2' stroke-linejoin='round'/>"
            f"<rect x='{cx-4}' y='{cy+2}' width='8' height='12' fill='{c}'/>")


s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' aria-label='The six questions metadata answers, plus the license check'>",
     "<title>The six questions metadata should answer before you use a dataset</title>",
     f"<rect width='{W}' height='{H}' rx='14' fill='white' stroke='{LGRAY}'/>",
     f"<text x='30' y='40' font-size='22' font-weight='700' fill='{NAVY}' {FONT}>Before you use a dataset, its metadata should answer six questions</text>",
     f"<text x='30' y='62' font-size='13' fill='#555' {FONT}>The same six you met in CCE 114. If you cannot answer one of them, you do not yet know whether the data fits your project.</text>"]
cw_, ch_, gap = 290, 165, 25
for i, (t, q, note) in enumerate(cards):
    col, row = i % 3, i // 3
    x = 30 + col * (cw_ + gap)
    y = 82 + row * (ch_ + 14)
    s.append(f"<rect x='{x}' y='{y}' width='{cw_}' height='{ch_}' rx='10' fill='#f7f9fb' stroke='{LGRAY}'/>")
    s.append(glyph(i, x + 34, y + 36))
    s.append(f"<text x='{x+68}' y='{y+42}' font-size='20' font-weight='700' fill='{NAVY}' {FONT}>{esc(t)}</text>")
    for k, ln in enumerate(wrap(q, 42)[:3]):
        s.append(f"<text x='{x+18}' y='{y+74+k*16}' font-size='12.5' fill='#333' {FONT}>{esc(ln)}</text>")
    for k, ln in enumerate(wrap(note, 44)[:2]):
        s.append(f"<text x='{x+18}' y='{y+128+k*16}' font-size='12.5' font-style='italic' fill='{BLUE}' {FONT}>{esc(ln)}</text>")
# footer: fitness for use and the license
fy = 82 + 2 * (ch_ + 14) + 4
s.append(f"<rect x='30' y='{fy}' width='920' height='68' rx='10' fill='{NAVY}'/>")
s.append(f"<text x='48' y='{fy+24}' font-size='14' font-weight='700' fill='white' {FONT}>And the one that decides whether you may use it at all: the license.</text>")
s.append(f"<text x='48' y='{fy+42}' font-size='12.5' fill='{LBLUE}' {FONT}>{esc('Public domain and CC BY (credit the source) are fine for this course. Anything that forbids redistribution, commercial use or')}</text>")
s.append(f"<text x='48' y='{fy+58}' font-size='12.5' fill='{LBLUE}' {FONT}>{esc('derived products needs a second look before you build on it. If you cannot find a license at all, treat that as a no.')}</text>")
s.append("</svg>")
(OUT / "lab01-metadata-questions.svg").write_text("\n".join(s), encoding="utf-8")

# ================= Infographic 2: where GIS data comes from =================
W, H = 960, 470
srcs = [
    ("Open data portals", "Government agencies publishing what they maintain: UGRC, USGS, the Census Bureau.", "Counties and tracts", True),
    ("Prepared for you", "An extract someone else clipped, cleaned or repackaged. Check what they did to it.", "Roads extract", True),
    ("You create it", "Digitize from imagery, survey it, collect it with GPS, or type it in from a list.", "Walmart points", True),
    ("Live web services", "Streamed from a server every time you pan. Never on your disk; not yours to edit.", "Basemap", True),
    ("Remote sensing", "Satellite, aerial and drone imagery; elevation from lidar and radar.", "Later labs", False),
    ("Commercial and licensed", "Vendor datasets, parcels, business data. Often the best, rarely free.", "Not in this lab", False),
]


def src_glyph(i, cx, cy):
    c = BLUE
    if i == 0:  # cloud download
        return (f"<path d='M{cx-22},{cy+4} a12,12 0 0 1 6,-22 a16,16 0 0 1 30,4 a10,10 0 0 1 4,18 z' fill='{LBLUE}' stroke='{c}' stroke-width='2' stroke-linejoin='round'/>"
                f"<line x1='{cx}' y1='{cy-4}' x2='{cx}' y2='{cy+18}' stroke='{ORANGE}' stroke-width='3'/>"
                f"<polyline points='{cx-7},{cy+11} {cx},{cy+19} {cx+7},{cy+11}' fill='none' stroke='{ORANGE}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>")
    if i == 1:  # zip box
        return (f"<rect x='{cx-18}' y='{cy-14}' width='36' height='32' rx='3' fill='{LBLUE}' stroke='{c}' stroke-width='2'/>"
                f"<rect x='{cx-18}' y='{cy-14}' width='36' height='9' fill='{c}'/>"
                f"<rect x='{cx-5}' y='{cy-14}' width='10' height='22' fill='{ORANGE}'/>")
    if i == 2:  # pencil over a point
        return (f"<circle cx='{cx-8}' cy='{cy+10}' r='5' fill='{ORANGE}'/>"
                f"<path d='M{cx-4},{cy+6} l22,-22 l7,7 l-22,22 l-9,2 z' fill='{LBLUE}' stroke='{c}' stroke-width='2' stroke-linejoin='round'/>")
    if i == 3:  # radio waves
        return (f"<circle cx='{cx}' cy='{cy+12}' r='4' fill='{ORANGE}'/>"
                f"<path d='M{cx-12},{cy+2} a17,17 0 0 1 24,0' fill='none' stroke='{c}' stroke-width='2.5' stroke-linecap='round'/>"
                f"<path d='M{cx-22},{cy-7} a31,31 0 0 1 44,0' fill='none' stroke='{c}' stroke-width='2.5' stroke-linecap='round'/>")
    if i == 4:  # satellite
        return (f"<rect x='{cx-7}' y='{cy-7}' width='14' height='14' fill='{LBLUE}' stroke='{c}' stroke-width='2' transform='rotate(45 {cx} {cy})'/>"
                f"<rect x='{cx-30}' y='{cy-5}' width='16' height='10' fill='{c}' transform='rotate(45 {cx} {cy})'/>"
                f"<rect x='{cx+14}' y='{cy-5}' width='16' height='10' fill='{c}' transform='rotate(45 {cx} {cy})'/>"
                f"<path d='M{cx-6},{cy+22} a12,12 0 0 1 12,0' fill='none' stroke='{ORANGE}' stroke-width='2'/>")
    # price tag
    return (f"<path d='M{cx-18},{cy-14} h20 l16,16 l-20,20 l-16,-16 z' fill='{LBLUE}' stroke='{c}' stroke-width='2' stroke-linejoin='round'/>"
            f"<circle cx='{cx-10}' cy='{cy-6}' r='3' fill='{c}'/>"
            f"<text x='{cx+3}' y='{cy+11}' font-size='14' font-weight='700' fill='{ORANGE}' text-anchor='middle' {FONT}>$</text>")


s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}' role='img' aria-label='Six places GIS data comes from, and which four this lab uses'>",
     "<title>Where GIS data comes from</title>",
     f"<rect width='{W}' height='{H}' rx='14' fill='white' stroke='{LGRAY}'/>",
     f"<text x='30' y='40' font-size='22' font-weight='700' fill='{NAVY}' {FONT}>Where GIS data comes from</text>",
     f"<text x='30' y='62' font-size='13' fill='#555' {FONT}>Real projects mix several of these. This lab deliberately uses four of them, marked in orange.</text>"]
pw, gap = 143, 10
for i, (t, note, tag, used) in enumerate(srcs):
    x = 30 + i * (pw + gap)
    y = 85
    ph = 230
    s.append(f"<rect x='{x}' y='{y}' width='{pw}' height='{ph}' rx='10' fill='#f7f9fb' stroke='{ORANGE if used else LGRAY}' stroke-width='{2 if used else 1}'/>")
    s.append(src_glyph(i, x + pw / 2, y + 40))
    tl = wrap(t, 14)
    for k, ln in enumerate(tl[:2]):
        s.append(f"<text x='{x+pw/2}' y='{y+88+k*16}' text-anchor='middle' font-size='14' font-weight='700' fill='{NAVY}' {FONT}>{esc(ln)}</text>")
    for k, ln in enumerate(wrap(note, 20)[:6]):
        s.append(f"<text x='{x+pw/2}' y='{y+122+k*15}' text-anchor='middle' font-size='11.5' fill='#333' {FONT}>{esc(ln)}</text>")
    pillw = 10 + 6.6 * len(tag)
    s.append(f"<rect x='{x+pw/2-pillw/2}' y='{y+ph-30}' width='{pillw}' height='20' rx='10' fill='{ORANGE if used else LGRAY}'/>")
    s.append(f"<text x='{x+pw/2}' y='{y+ph-16}' text-anchor='middle' font-size='11' font-weight='700' fill='{'white' if used else '#555'}' {FONT}>{esc(tag)}</text>")
    dash = "none" if used else "4 3"
    s.append(f"<line x1='{x+pw/2}' y1='{y+ph}' x2='{x+pw/2}' y2='{y+ph+30}' stroke='{ORANGE if used else GRAY}' stroke-width='{2 if used else 1}' stroke-dasharray='{dash}'/>")
bx, by, bw, bh = 30, 345, 900, 95
s.append(f"<rect x='{bx}' y='{by}' width='{bw}' height='{bh}' rx='10' fill='{NAVY}'/>")
s.append(f"<text x='{bx+24}' y='{by+36}' font-size='17' font-weight='700' fill='white' {FONT}>Your project geodatabase</text>")
s.append(f"<text x='{bx+24}' y='{by+60}' font-size='12.5' fill='{LBLUE}' {FONT}>Whatever the source, every layer ends up here: in one coordinate system, with a note of where it came from,</text>")
s.append(f"<text x='{bx+24}' y='{by+78}' font-size='12.5' fill='{LBLUE}' {FONT}>when you got it, and what license lets you use it. Your report has to be able to say all three for every layer.</text>")
s.append("</svg>")
(OUT / "lab01-data-sources.svg").write_text("\n".join(s), encoding="utf-8")
print("written:", sorted(p.name for p in OUT.glob("icon-*.svg")), "lab01-metadata-questions.svg", "lab01-data-sources.svg")
