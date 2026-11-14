"""Week 13 deck (Lab 12: Choose Your Own Adventure): the diagram figures and the reel mock-up.

Writes into slides/week-13/images/:
  cyoa-question-data-recipe.svg   slide "Why choose your own?"
  cyoa-three-questions.svg        slide "Choosing a problem — three questions"
  cyoa-package-contents.svg       slide "The report and the package"
  cyoa-points-by-source.svg       slide "How Lab 12 is scored"
  cyoa-reel-frame.png             slide "Extra credit — a reel" (Lab 10 example map in a 9:16 phone frame)
  cyoa-example-map.png            slide "What separates a good project from a great one" (Lab 11 example map)

Point split in cyoa-points-by-source.svg is counted from the tags on the Lab 12 rubric bullets
(docs/assignments/lab-12/README.md): video 30, report 38, package 28, video and report together 4.
Run: python tools/week13_figures.py
"""
import pathlib
import shutil

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "slides" / "week-13" / "images"
NAVY, BLUE, GRAY, LIGHT, RED, GREEN = "#002e5d", "#0062b8", "#4a5568", "#e8eef5", "#b3261e", "#2e7d32"
FONT = "Avenir Next, Segoe UI, Helvetica, Arial, sans-serif"


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>\n')


def text(x, y, s, size=26, fill=NAVY, weight="normal", anchor="middle", extra=""):
    s = s.replace("&", "&amp;")
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def question_data_recipe():
    cards = [("Question", "where, and why?"), ("Data", "found and vetted"), ("Recipe", "the model")]
    b = []
    for i, (title, sub) in enumerate(cards):
        x = 20 + i * 250
        b.append(f'<rect x="{x}" y="20" width="230" height="460" rx="18" fill="{LIGHT}" stroke="{NAVY}" stroke-width="3"/>')
        b.append(text(x + 115, 85, title, 40, weight="bold"))
        b.append(text(x + 115, 125, sub, 24, GRAY))
        b.append(text(x + 115, 215, "Labs 1–11:", 28, GRAY))
        b.append(text(x + 115, 255, "given", 28, GRAY))
        for y in (206, 246):
            b.append(f'<line x1="{x + 35}" y1="{y}" x2="{x + 195}" y2="{y}" stroke="{RED}" stroke-width="4"/>')
        b.append(f'<rect x="{x + 20}" y="330" width="190" height="120" rx="14" fill="{NAVY}"/>')
        b.append(text(x + 115, 380, "Lab 12:", 32, "white", "bold"))
        b.append(text(x + 115, 422, "yours", 32, "white"))
    return svg(770, 500, "\n".join(b))


def three_questions():
    qs = [("Can I say the question", "in one sentence?", "If not: one place, one decision"),
          ("Can I get the data", "this week?", "If not: change the question or the data"),
          ("Would I know", "a wrong answer?", "If not: add a check you can run")]
    b = [f'<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{GRAY}"/></marker></defs>']
    for i, (q1, q2, fix) in enumerate(qs):
        y = 20 + i * 190
        b.append(f'<rect x="20" y="{y}" width="560" height="140" rx="16" fill="{LIGHT}" stroke="{NAVY}" stroke-width="3"/>')
        b.append(text(50, y + 52, f"{i + 1}.", 34, BLUE, "bold", "start"))
        b.append(text(95, y + 50, q1, 30, NAVY, "bold", "start"))
        b.append(text(95, y + 88, q2, 30, NAVY, "bold", "start"))
        b.append(text(95, y + 124, fix, 23, RED, "normal", "start"))
        b.append(f'<line x1="300" y1="{y + 140}" x2="300" y2="{y + 185}" stroke="{GRAY}" stroke-width="3" marker-end="url(#a)"/>')
        b.append(text(320, y + 172, "yes", 24, GREEN, "bold", "start"))
    b.append(f'<rect x="140" y="590" width="320" height="76" rx="38" fill="{NAVY}"/>')
    b.append(text(300, 640, "Ready to build", 32, "white", "bold"))
    return svg(600, 690, "\n".join(b))


def package_contents():
    inside = ["Maps and layouts", "Data in the maps' layers", "Your toolbox and model", "Geoprocessing history"]
    b = [f'<rect x="20" y="20" width="560" height="430" rx="20" fill="{LIGHT}" stroke="{NAVY}" stroke-width="4"/>',
         text(300, 72, "Lab12.ppkx", 36, NAVY, "bold"),
         text(300, 106, "Share ▸ Package ▸ Project", 22, GRAY)]
    for i, item in enumerate(inside):
        y = 150 + i * 70
        b.append(f'<circle cx="70" cy="{y + 18}" r="20" fill="{GREEN}"/>')
        b.append(f'<path d="M60,{y + 18} l7,8 l14,-16" stroke="white" stroke-width="4" fill="none"/>')
        b.append(text(105, y + 28, item, 27, NAVY, "normal", "start"))
    b.append(f'<rect x="620" y="150" width="300" height="190" rx="16" fill="white" stroke="{RED}" stroke-width="3" stroke-dasharray="10 7"/>')
    b.append(f'<circle cx="770" cy="200" r="22" fill="{RED}"/>')
    b.append(f'<path d="M760,190 l20,20 M780,190 l-20,20" stroke="white" stroke-width="4"/>')
    b.append(text(770, 260, "A model input", 25, RED, "bold"))
    b.append(text(770, 292, "that is not a layer", 25, RED))
    b.append(text(770, 322, "in any map: left out", 25, RED))
    b.append(text(770, 400, "Add every input to a map,", 22, GRAY))
    b.append(text(770, 430, "then run the model once", 22, GRAY))
    return svg(940, 470, "\n".join(b))


def points_by_source():
    parts = [("Video", 30, BLUE), ("Video and report", 4, "#7aa7d9"), ("Report", 38, NAVY), ("Package", 28, "#5b8c5a")]
    b, x, scale = [], 30, 8.6
    for name, pts, color in parts:
        w = pts * scale
        b.append(f'<rect x="{x:.1f}" y="60" width="{w:.1f}" height="110" fill="{color}" stroke="white" stroke-width="3"/>')
        if pts >= 10:
            b.append(text(x + w / 2, 128, str(pts), 40, "white", "bold"))
            b.append(text(x + w / 2, 210, name, 26, NAVY, "bold"))
        else:
            b.append(text(x + w / 2, 128, str(pts), 22, "white", "bold"))
            b.append(text(x + w / 2 + 14, 48, name + " (4)", 20, GRAY, "normal", "start"))
            b.append(f'<line x1="{x + w / 2:.1f}" y1="60" x2="{x + w / 2 + 10:.1f}" y2="44" stroke="{GRAY}" stroke-width="2"/>')
        x += w
    return svg(920, 240, "\n".join(b))


def reel_frame():
    src = Image.open(ROOT / "docs/assignments/lab-10/images/lab10-example-map-baseline.png").convert("RGB")
    W, H = 540, 960  # 9:16
    top = int(src.height * 0.11)  # skip the layout's title band
    crop_w = int((src.height - top) * W / H)
    left = max(0, (src.width - crop_w) // 2)
    shot = src.crop((left, top, left + crop_w, src.height)).resize((W, H))
    pad, bez = 40, 28
    canvas = Image.new("RGB", (W + 2 * (pad + bez), H + 2 * (pad + bez) + 60), "white")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([pad, pad, pad + W + 2 * bez, pad + H + 2 * bez + 60], radius=70, fill="#111111")
    canvas.paste(shot, (pad + bez, pad + bez + 30))
    d.rounded_rectangle([pad + W // 2 - 40, pad + 12, pad + W // 2 + 2 * bez + 40, pad + 24], radius=6, fill="#333333")
    # caption bar and progress line, as a reel would show them (no words, so nothing to misread)
    y0 = pad + bez + 30 + H - 150
    d.rounded_rectangle([pad + bez + 40, y0, pad + bez + W - 40, y0 + 34], radius=12, fill=(255, 255, 255))
    d.rounded_rectangle([pad + bez + 80, y0 + 48, pad + bez + W - 80, y0 + 82], radius=12, fill=(255, 255, 255))
    d.rectangle([pad + bez, pad + bez + 30 + H - 8, pad + bez + int(W * 0.38), pad + bez + 30 + H], fill="#e53935")
    canvas.save(OUT / "cyoa-reel-frame.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("cyoa-question-data-recipe.svg", question_data_recipe),
                     ("cyoa-three-questions.svg", three_questions),
                     ("cyoa-package-contents.svg", package_contents),
                     ("cyoa-points-by-source.svg", points_by_source)]:
        (OUT / name).write_text(fn(), encoding="utf-8")
    reel_frame()
    shutil.copyfile(ROOT / "docs/assignments/lab-11/images/lab11-example-map-baseline.png", OUT / "cyoa-example-map.png")
    print("wrote", sorted(p.name for p in OUT.glob("cyoa-*")))


if __name__ == "__main__":
    main()
