"""Two hand-drawn-looking cookie models for the Week 2 Part B "Cookie model review" slide, in the
style of the student sketch already on that slide (green marker, ovals for data, boxes for tools,
loose arrows): one with a single tool, one with every intermediate step back to a chick and a
wheat seed. Drawn as SVG with jittered outlines and a handwriting font, then rendered to PNG at 3x
with headless Chrome so the font is baked in (browsers on students' machines may not have it).

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools\\week02_cookie_sketches.py

Outputs: slides/week-02/images/mbb-cookie-sketch-simple.png and mbb-cookie-sketch-detailed.png.
"""
import math
import os
import random
import subprocess
import tempfile

from PIL import Image, ImageChops

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "slides", "week-02", "images")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
INK = "#1f8a3a"
FONT = "font-family='Segoe Print, Bradley Hand, Comic Sans MS, cursive'"
rng = random.Random(414)


def jit(v, a=1.6):
    return v + rng.uniform(-a, a)


def wobbly_ellipse(cx, cy, rx, ry, n=28):
    """A closed hand-drawn loop: a polyline of jittered points around an ellipse, overshooting the
    start a little the way a marker does."""
    pts = []
    for i in range(n + 3):
        t = 2 * math.pi * i / n - 0.4
        pts.append((cx + rx * math.cos(t) + rng.uniform(-2.2, 2.2), cy + ry * math.sin(t) + rng.uniform(-2.2, 2.2)))
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/>"


def wobbly_rect(x, y, w, h):
    c = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for i in range(5):
        a = c[i % 4]; b = c[(i + 1) % 4]
        for k in range(4):
            f = k / 4
            pts.append((jit(a[0] + (b[0] - a[0]) * f), jit(a[1] + (b[1] - a[1]) * f)))
    pts.append((jit(c[1][0]), jit(c[1][1])))   # overshoot the first corner
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    return f"<path d='{d}' fill='none' stroke='{INK}' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'/>"


def arrow(x1, y1, x2, y2):
    mx, my = (x1 + x2) / 2 + rng.uniform(-6, 6), (y1 + y2) / 2 + rng.uniform(-6, 6)
    ang = math.atan2(y2 - y1, x2 - x1)
    h = 11
    a1 = (x2 - h * math.cos(ang - 0.45), y2 - h * math.sin(ang - 0.45))
    a2 = (x2 - h * math.cos(ang + 0.45), y2 - h * math.sin(ang + 0.45))
    return (f"<path d='M {x1:.1f} {y1:.1f} Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}' fill='none' stroke='{INK}' stroke-width='2.4' stroke-linecap='round'/>"
            f"<path d='M {a1[0]:.1f} {a1[1]:.1f} L {x2:.1f} {y2:.1f} L {a2[0]:.1f} {a2[1]:.1f}' fill='none' stroke='{INK}' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/>")


def text(x, y, s, size=17):
    lines = s.split("\n")
    out = []
    for i, ln in enumerate(lines):
        yy = y + (i - (len(lines) - 1) / 2) * (size + 2)
        out.append(f"<text x='{x}' y='{yy + size * 0.35:.1f}' text-anchor='middle' font-size='{size}' fill='{INK}' {FONT} transform='rotate({rng.uniform(-2.5, 2.5):.1f} {x} {yy})'>{ln}</text>")
    return "".join(out)


class Sketch:
    def __init__(self, w, h):
        self.w, self.h, self.parts, self.nodes = w, h, [], {}

    def data(self, name, cx, cy, label=None, rx=None, ry=None):
        label = label or name
        lines = label.split("\n")
        rx = rx or max(len(l) for l in lines) * 5.2 + 18
        ry = ry or 14 + 10 * len(lines)
        self.nodes[name] = (cx, cy, rx, ry)
        self.parts.append(wobbly_ellipse(cx, cy, rx, ry) + text(cx, cy, label))

    def tool(self, name, cx, cy, label=None, w=None, h=None):
        label = label or name
        lines = label.split("\n")
        w = w or max(len(l) for l in lines) * 9.5 + 22
        h = h or 22 + 20 * len(lines)
        self.nodes[name] = (cx, cy, w / 2, h / 2)
        self.parts.append(wobbly_rect(cx - w / 2, cy - h / 2, w, h) + text(cx, cy, label))

    def link(self, a, b):
        ax, ay, arx, ary = self.nodes[a]; bx, by, brx, bry = self.nodes[b]
        ang = math.atan2(by - ay, bx - ax)
        # leave each shape at its edge along the line between centers, with a marker-ish gap
        x1 = ax + (arx + 5) * math.cos(ang); y1 = ay + (ary + 5) * math.sin(ang)
        x2 = bx - (brx + 6) * math.cos(ang); y2 = by - (bry + 6) * math.sin(ang)
        self.parts.append(arrow(x1, y1, x2, y2))

    def write(self, path):
        body = "\n".join(self.parts)
        svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {self.w} {self.h}' width='{self.w}' height='{self.h}'>"
               f"<rect width='{self.w}' height='{self.h}' fill='#ffffff'/>{body}</svg>")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)


def render(svg_path, png_path, w, h, scale=3):
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", f"--force-device-scale-factor={scale}",
                    f"--window-size={w},{h}", f"--screenshot={png_path}", "file:///" + svg_path.replace("\\", "/")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(png_path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).getbbox()
    if bb:
        m = 24
        im = im.crop((max(bb[0] - m, 0), max(bb[1] - m, 0), min(bb[2] + m, im.width), min(bb[3] + m, im.height)))
    im.save(png_path, optimize=True)
    print(png_path, im.size)


tmp = tempfile.gettempdir()

# 1. the simplest model that is still a model
s = Sketch(560, 200)
s.data("ing", 110, 100, "flour, sugar,\neggs, butter,\nchocolate chips", rx=88, ry=46)
s.tool("mixbake", 300, 100, "Mix and bake", w=150, h=48)
s.data("cookies", 470, 100, "Cookies!", rx=58, ry=28)
s.link("ing", "mixbake"); s.link("mixbake", "cookies")
p = os.path.join(tmp, "cookie-simple.svg"); s.write(p)
render(p, os.path.join(OUT, "mbb-cookie-sketch-simple.png"), 560, 200)

# 2. every step back to the chick and the seed
s = Sketch(1380, 510)
# egg chain
s.data("chick", 80, 60, "Baby\nchicken", rx=52, ry=32)
s.tool("raise", 215, 60, "Raise\n(6 months)", w=112, h=50)
s.data("hen", 350, 60, "Hen", rx=40, ry=24)
s.tool("lay", 465, 60, "Lay eggs", w=100, h=40)
s.data("eggs", 585, 60, "Eggs", rx=42, ry=24)
# flour chain
s.data("seeds", 80, 220, "Wheat\nseeds", rx=50, ry=32)
s.tool("grow", 215, 220, "Plant, water,\nwait", w=124, h=50)
s.data("wheat", 350, 220, "Wheat", rx=44, ry=24)
s.tool("harvest", 465, 220, "Harvest and\nthresh", w=110, h=50)
s.data("grain", 585, 220, "Grain", rx=42, ry=24)
s.tool("mill", 700, 220, "Mill", w=70, h=40)
s.data("flour", 810, 220, "Flour", rx=42, ry=24)
# butter chain
s.data("cow", 80, 350, "Cow", rx=38, ry=24)
s.tool("milk", 215, 350, "Milk", w=76, h=40)
s.data("cream", 350, 350, "Cream", rx=44, ry=24)
s.tool("churn", 465, 350, "Churn", w=84, h=40)
s.data("butter", 585, 350, "Butter", rx=44, ry=24)
# short inputs
s.data("sugar", 720, 415, "Sugar", rx=42, ry=24)
s.data("chips", 850, 460, "Chocolate\nchips", rx=56, ry=32)
# the part everyone draws: a straight chain to the right, so nothing crosses
s.tool("mix", 930, 220, "Mix", w=76, h=44)
s.data("dough", 1050, 220, "Dough", rx=46, ry=26)
s.tool("scoop", 1160, 220, "Scoop", w=80, h=40)
s.data("balls", 1275, 220, "Dough\nballs", rx=48, ry=30)
s.tool("bake", 1275, 320, "Bake\n350°F, 11 min", w=150, h=52)
s.data("cookies2", 1275, 420, "Cookies!", rx=58, ry=28)
for a, b in [("chick", "raise"), ("raise", "hen"), ("hen", "lay"), ("lay", "eggs"),
             ("seeds", "grow"), ("grow", "wheat"), ("wheat", "harvest"), ("harvest", "grain"), ("grain", "mill"), ("mill", "flour"),
             ("cow", "milk"), ("milk", "cream"), ("cream", "churn"), ("churn", "butter"),
             ("eggs", "mix"), ("flour", "mix"), ("butter", "mix"), ("sugar", "mix"), ("chips", "mix"),
             ("mix", "dough"), ("dough", "scoop"), ("scoop", "balls"), ("balls", "bake"), ("bake", "cookies2")]:
    s.link(a, b)
p = os.path.join(tmp, "cookie-detailed.svg"); s.write(p)
render(p, os.path.join(OUT, "mbb-cookie-sketch-detailed.png"), 1380, 510)
