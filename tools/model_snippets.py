# Cut per-step ModelBuilder snippets out of a finished model's SVG export (Export > Export To
# Graphic, SVG, from ModelBuilder in ArcGIS Pro). No ArcGIS Pro session is needed. Used by
# tools/lab07/render_model_snippets.py and tools/lab08/render_model_snippets.py.
#
# A snippet keeps only the named elements and the connectors that run between two of them, so it
# never shows a tool a later step adds. The green check marks of a finished run are removed (while
# the student builds, the model has not run yet, and ModelBuilder shows the same shapes without
# them), and so are the P markers of any element named in `no_p` (made a parameter in a later step).
# Rendered at 3x with headless Chrome (do NOT pass --disable-gpu, it renders blank here) and
# trimmed to content.
#
# An element is named by the first line of its label as ModelBuilder wraps it ("Flow " for Flow
# Direction, "Raster " for Raster Calculator). When a first line repeats, pin it with the position
# of the label in SVG units: "Raster @548,252" (x and y), "Flow @,270" (y only).
import os, re, subprocess, tempfile
from PIL import Image, ImageChops

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCALE = 3
NODE_W = 85.5         # every element is 85.5 SVG units wide; its colored band is the left 28.5
BAND_TO_TEXT = 30.75  # a label starts this far right of its band
CHECK = "#68AA67"     # the run's check-mark badge (and the small squares of the raster icon)
NUM = re.compile(r'-?\d+(?:\.\d+)?(?:e-?\d+)?')


def parse(path):
    """Split the export into its header and a list of elements with their bounding boxes."""
    text = open(path, encoding="utf-8").read()
    elems = []
    for m in re.finditer(r'<path\b[^>]*/>|<text\b[^>]*>.*?</text>', text, re.S):
        s = m.group(0)
        fill = re.search(r'fill="([^"]*)"', s).group(1)
        if s.startswith("<path"):
            n = [float(x) for x in NUM.findall(re.search(r'd="([^"]*)"', s).group(1))]
            pts = list(zip(n[0::2], n[1::2]))
            line = 'fill="none"' in s and 'stroke="#6A6A6A"' in s
        else:
            t = re.search(r'matrix\(([^)]*)\)', s).group(1).split()
            pts, line = [(float(t[4]), float(t[5]))], False
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        label = re.search(r'>([^<]*)</text>', s).group(1) if s.startswith("<text") else None
        elems.append(dict(s=s, fill=fill, pts=pts, line=line, label=label,
                          bb=(min(xs), min(ys), max(xs), max(ys))))
    return text[:text.index("<path")], elems


def node_rect(elems, key):
    """The rectangle of the element whose label's first line is key (see the header)."""
    word, _, pos = key.partition("@")
    px, _, py = pos.partition(",")
    for e in elems:
        if e["label"] is not None and e["label"] == word and 'y="11.06' in e["s"]:
            tx, ty = e["pts"][0]
            if (px and abs(tx - float(px)) > 3) or (py and abs(ty - float(py)) > 3):
                continue
            for b in elems:
                x0, y0, x1, y1 = b["bb"]
                if (abs(x1 - x0 - 28.5) < 0.6 and abs(y1 - y0 - 36) < 0.6
                        and abs(x0 + BAND_TO_TEXT - tx) < 1 and y0 <= ty + 8 <= y1):
                    return (x0, y0, x0 + NODE_W, y1)
    raise KeyError(key)


def inside(bb, r, pad=0.0):
    return bb[0] >= r[0] - pad and bb[1] >= r[1] - pad and bb[2] <= r[2] + pad and bb[3] <= r[3] + pad


def near(p, rects, pad=7.0):
    return any(r[0] - pad <= p[0] <= r[2] + pad and r[1] - pad <= p[1] <= r[3] + pad for r in rects)


def cut(elems, keys, no_p=()):
    rects = [node_rect(elems, k) for k in keys]
    drop = [e["bb"] for e in elems if e["fill"] == CHECK and e["bb"][2] - e["bb"][0] > 10]
    for k in no_p:  # the P badge straddles the element's top edge, left of its right end
        r = node_rect(elems, k)
        drop.append((r[2] - 30, r[1] - 14, r[2] + 2, r[1] + 12))
    keep, i = [], 0
    while i < len(elems):
        e = elems[i]
        if e["line"]:
            # a connector is the line and the two arrowhead paths after it
            group = [e] + [a for a in elems[i + 1:i + 3] if not a["line"] and len(a["pts"]) <= 5]
            if near(e["pts"][0], rects) and near(e["pts"][-1], rects):
                keep += group
            i += len(group)
            continue
        if not any(inside(e["bb"], b, 0.5) for b in drop):
            # labels and the P marker sit a little above or right of the band's box
            if any(inside(e["bb"], (r[0], r[1] - 14, r[2] + 4, r[3]), 0.5) for r in rects):
                keep.append(e)
        i += 1
    x0 = min(r[0] for r in rects) - 6
    y0 = min(r[1] for r in rects) - 14
    x1 = max(max(r[2] for r in rects), max(e["bb"][2] for e in keep)) + 6
    y1 = max(r[3] for r in rects) + 6
    return keep, (x0, y0, x1 - x0, y1 - y0)


def render(svg_text, w, h):
    path = os.path.join(tempfile.gettempdir(), "model-snippet.svg")
    open(path, "w", encoding="utf-8").write(svg_text)
    out = path + ".png"
    W, H = int(w * 4 / 3) + 2, int(h * 4 / 3) + 2  # pt -> CSS px, a hair larger so nothing clips
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", f"--force-device-scale-factor={SCALE}",
                    f"--window-size={W},{H}", f"--screenshot={out}", "file:///" + path.replace("\\", "/")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(out).convert("RGB")


def trim(im, margin=12):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).getbbox()
    if not bb:
        return im
    return im.crop((max(bb[0] - margin, 0), max(bb[1] - margin, 0),
                    min(bb[2] + margin, im.size[0]), min(bb[3] + margin, im.size[1])))


def make_snippets(images, snippets):
    """snippets: (svg file in images, element keys, output name[, keys whose P marker to drop])."""
    parsed = {}
    for svg, keys, name, *rest in snippets:
        if svg not in parsed:
            parsed[svg] = parse(os.path.join(images, svg))
        head, elems = parsed[svg]
        keep, (x, y, w, h) = cut(elems, keys, rest[0] if rest else ())
        head = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
                      f'width="{w}pt" height="{h}pt" viewBox="{x} {y} {w} {h}"', head, count=1)
        im = trim(render(head + "\n".join(e["s"] for e in keep) + "\n</svg>\n", w, h))
        im.save(os.path.join(images, name), optimize=True)
        print(name, im.size, f"display width {round(im.size[0] / SCALE)} px")
