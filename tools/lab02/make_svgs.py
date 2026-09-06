# Hand-authored SVG infographics for the Lab 2 draft. Real text, no image model.
#   python make_svgs.py   -> writes lab02-imagery-metadata.svg and lab02-what-ndvi-sees.svg
# into docs/assignments/lab-02/images/. The NDVI graphic reads samples.json (written by the
# sampling snippet recorded in PARITY_PLAN.md / the session notes) so its numbers are measured.
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "assignments", "lab-02", "images"))
NAVY, ORANGE, GRAY, LIGHT, INK = "#0b2a4a", "#d9741c", "#5b6770", "#eef2f6", "#1c2733"
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"


def esc(s):
    return html.escape(s, quote=True)


def text(x, y, s, size=13, weight="normal", fill=INK, anchor="start"):
    return "<text x='%s' y='%s' font-size='%s' font-weight='%s' fill='%s' text-anchor='%s' %s>%s</text>" % (
        x, y, size, weight, fill, anchor, FONT, esc(s))


def lines(x, y, items, size=12, lh=16, fill=INK):
    return "".join(text(x, y + i * lh, s, size, fill=fill) for i, s in enumerate(items))


def metadata_card():
    W, H = 1000, 580
    cards = [
        ("WHAT", "What do the data represent?",
         ["Landsat 8, OLI/TIRS sensor. Collection 2, Level-2 surface",
          "reflectance (L2SP), Tier 1 (PROCESSING_LEVEL).",
          "Band 4 = red, 0.64-0.67 um. Band 5 = NIR, 0.85-0.88 um.",
          "Stored as integers. To get reflectance:",
          "   DN x 0.0000275 - 0.2",
          "(REFLECTANCE_MULT_BAND_n, REFLECTANCE_ADD_BAND_n)."]),
        ("WHERE", "Where, and in what coordinate system?",
         ["WRS-2 path 38, row 32 (WRS_PATH, WRS_ROW).",
          "UTM zone 12, WGS 84 (MAP_PROJECTION, UTM_ZONE).",
          "30 m cells (GRID_CELL_SIZE_REFLECTIVE).",
          "Our extract is clipped to Utah County; the full",
          "scene is about 185 km on a side."]),
        ("WHEN", "When were the data collected?",
         ["DATE_ACQUIRED = 2025-07-12",
          "SCENE_CENTER_TIME = 18:08 UTC (12:08 pm local).",
          "Mid-July: irrigated crops at full canopy, everything",
          "unwatered has cured. SUN_ELEVATION = 64 degrees, so",
          "shadows are short. Product generated 2025-07-25.",
          "A May or October scene tells a different story."]),
        ("WHY", "Why were they created?",
         ["The USGS archive exists for long-term land monitoring,",
          "not for your question. Nothing in the file says",
          "'irrigation'. Whether a July NDVI answers an irrigation",
          "question is a judgement you make and defend, not a",
          "property of the data."]),
        ("HOW", "How were they collected and processed?",
         ["Measured by the OLI; corrected to surface reflectance",
          "by the USGS (Collection 2 Level-2). CLOUD_COVER = 0.02 %.",
          "Then by us: clipped to the county, scale factor applied,",
          "small negatives floored at 0, stored as reflectance",
          "x 10,000. READ-ME-FIRST.txt says exactly what was",
          "and was not done."]),
        ("WHO", "Who maintains them, and may you use them?",
         ["U.S. Geological Survey, EROS Center. Public domain:",
          "no restrictions, but credit them. ORIGIN = 'Image",
          "courtesy of the U.S. Geological Survey'.",
          "LANDSAT_PRODUCT_ID =",
          "LC08_L2SP_038032_20250712_20250725_02_T1 identifies",
          "this exact scene forever. Put it in your report."]),
    ]
    s = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d' width='%d' height='%d' role='img' "
         "aria-label='The six metadata questions applied to a Landsat scene, each answered from the MTL file'>" % (W, H, W, H),
         "<title>The six metadata questions, answered from the Landsat MTL file</title>",
         "<rect width='%d' height='%d' fill='white'/>" % (W, H),
         text(20, 34, "Reading a Landsat scene's metadata: the MTL file answers the six questions", 20, "bold", NAVY),
         text(20, 56, "Every value below is copied from LC08_L2SP_038032_20250712_20250725_02_T1_MTL.txt, which ships in the Utah County extract.", 12, fill=GRAY)]
    cw, ch, gx, gy = 310, 215, 20, 75
    for i, (tag, q, body) in enumerate(cards):
        x = gx + (i % 3) * (cw + 15)
        y = gy + (i // 3) * (ch + 15)
        s.append("<rect x='%d' y='%d' width='%d' height='%d' rx='8' fill='%s' stroke='#c9d2dc'/>" % (x, y, cw, ch, LIGHT))
        s.append("<rect x='%d' y='%d' width='%d' height='34' rx='8' fill='%s'/>" % (x, y, cw, NAVY))
        s.append(text(x + 12, y + 23, tag, 15, "bold", "white"))
        s.append(text(x + 82, y + 23, q, 11, fill="white"))
        s.append(lines(x + 12, y + 58, body, 11, 17))
    s.append("<rect x='20' y='%d' width='960' height='40' rx='8' fill='%s'/>" % (H - 55, ORANGE))
    s.append(text(32, H - 30, "For your report, copy these three MTL values: DATE_ACQUIRED, CLOUD_COVER, and REFLECTANCE_ADD_BAND_4 - and say what each one means for your result.", 12.5, "bold", "white"))
    s.append("</svg>")
    return "\n".join(s)


def ndvi_card():
    samples = json.load(open(os.path.join(HERE, "samples.json")))
    order = ["Wasatch forest above Provo", "Center-pivot field (Elberta)", "Provo, city blocks", "Dry bench (Cedar Valley)", "Utah Lake (open water)"]
    W, H = 1000, 420
    s = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %d %d' width='%d' height='%d' role='img' "
         "aria-label='Measured red and near-infrared reflectance and NDVI at five places in the Utah County scene'>" % (W, H, W, H),
         "<title>What NDVI sees: red and NIR reflectance at five places in the Utah County scene</title>",
         "<rect width='%d' height='%d' fill='white'/>" % (W, H),
         text(20, 34, "What NDVI sees: measured in the Utah County scene, July 12, 2025", 20, "bold", NAVY),
         text(20, 56, "Mean surface reflectance of the red and NIR bands inside a circle at each site, and the NDVI that follows. NDVI = (NIR - Red) / (NIR + Red).", 12, fill=GRAY)]
    x0, colw, bary, barh = 20, 190, 300, 170
    for i, name in enumerate(order):
        d = samples[name]
        x = x0 + i * colw
        s.append("<rect x='%d' y='75' width='%d' height='300' rx='8' fill='%s' stroke='#c9d2dc'/>" % (x, colw - 12, LIGHT))
        title = name.split(" (")[0] if "(" in name else name
        sub = name[name.find("("):] if "(" in name else ""
        s.append(text(x + 10, 97, title, 12.5, "bold"))
        if sub:
            s.append(text(x + 10, 113, sub, 11, fill=GRAY))
        # bars: red and nir, scaled so 0.45 reflectance = full height
        for j, (key, col, lab) in enumerate((("red", "#c0392b", "Red"), ("nir", "#7f3f98", "NIR"))):
            v = d[key]
            h = max(2, v / 0.45 * barh)
            bx = x + 30 + j * 60
            s.append("<rect x='%d' y='%.1f' width='40' height='%.1f' fill='%s'/>" % (bx, bary - h, h, col))
            s.append(text(bx + 20, bary + 16, lab, 11, anchor="middle"))
            s.append(text(bx + 20, bary - h - 5, "%.2f" % v, 11, "bold", anchor="middle"))
        s.append("<line x1='%d' y1='%d' x2='%d' y2='%d' stroke='#8a949e'/>" % (x + 15, bary, x + colw - 27, bary))
        ndvi = d["ndvi"]
        col = "#2e7d32" if ndvi >= 0.4 else ("#b26a00" if ndvi >= 0 else "#1f4e79")
        s.append("<rect x='%d' y='330' width='%d' height='34' rx='6' fill='%s'/>" % (x + 10, colw - 32, col))
        s.append(text(x + colw / 2 - 6, 353, "NDVI %.2f" % ndvi, 15, "bold", "white", "middle"))
    s.append(text(20, H - 22, "Green: at or above the 0.4 threshold. Forest scores higher than the irrigated field. Water reads -0.99 because the extract floors negative reflectance at 0 (real water is nearer -0.3).", 11.5, fill=GRAY))
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("lab02-imagery-metadata.svg", metadata_card), ("lab02-what-ndvi-sees.svg", ndvi_card)):
        p = os.path.join(OUT, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(fn())
        print("wrote", p)
