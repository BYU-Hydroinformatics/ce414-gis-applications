#!/usr/bin/env python3
"""Dump everything needed to convert a PowerPoint deck to Marp slides.

Usage:  python3 tools/pptx_extract.py "path/to/deck.pptx" OUTDIR

Writes into OUTDIR:
  text.md            one section per slide: title guess, all text runs, speaker notes,
                     media file names, and a HIDDEN flag for slides that do not present
  media/             every image from ppt/media (original names, e.g. image12.jpeg)
  deck.pdf           LibreOffice render (hidden slides are omitted from the PDF)
  page-NN.jpg        50 dpi render of each PDF page
  sheet-N.jpg        labeled contact sheets, 12 pages per sheet, for quick viewing
  hires-NN-N.png     only if --hires N [N ...] is given: 200 dpi renders of those PDF pages,
                     for slides built from PowerPoint shapes that should be kept as images

No python-pptx or markitdown needed; only the stdlib, Pillow, LibreOffice and poppler
(`/opt/homebrew/bin/soffice`, `pdftoppm`).
"""
import argparse
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path

SOFFICE = "/opt/homebrew/bin/soffice"


def texts(xml: str) -> list[str]:
    out = []
    for p in re.findall(r"<a:p>(.*?)</a:p>", xml, re.S):
        t = "".join(re.findall(r"<a:t>(.*?)</a:t>", p, re.S))
        if t.strip():
            out.append(html.unescape(t))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("outdir")
    ap.add_argument("--hires", nargs="*", type=int, default=[], help="PDF page numbers to render at 200 dpi")
    ap.add_argument("--no-render", action="store_true", help="skip the LibreOffice/pdftoppm render")
    a = ap.parse_args()

    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    z = zipfile.ZipFile(a.pptx)
    names = z.namelist()
    slides = sorted((n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                    key=lambda n: int(re.findall(r"\d+", n)[0]))

    # Slide order as presented (ppt/presentation.xml sldIdLst -> rels).
    pres = z.read("ppt/presentation.xml").decode("utf8")
    prels = z.read("ppt/_rels/presentation.xml.rels").decode("utf8")
    rid_to_file = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(slides/slide\d+\.xml)"', prels))
    rid_to_file.update({k: v for v, k in re.findall(r'Target="(slides/slide\d+\.xml)"[^>]*Id="(rId\d+)"', prels)})
    order = [rid_to_file[r] for r in re.findall(r'<p:sldId [^>]*r:id="(rId\d+)"', pres) if r in rid_to_file]
    ordered = [f"ppt/{s}" for s in order] or slides

    lines = [f"# {Path(a.pptx).name}", "", f"{len(ordered)} slides in presentation order. "
             "HIDDEN slides do not show in the PDF render, so PDF page numbers skip them.", ""]
    page = 0
    for n in ordered:
        i = int(re.findall(r"\d+", n)[0])
        xml = z.read(n).decode("utf8")
        hidden = bool(re.search(r'<p:sld[^>]*\sshow="0"', xml))
        if not hidden:
            page += 1
        rels_name = f"ppt/slides/_rels/slide{i}.xml.rels"
        rels = z.read(rels_name).decode("utf8") if rels_name in names else ""
        media = re.findall(r'Target="\.\./media/([^"]+)"', rels)
        links = re.findall(r'Target="(https?://[^"]+)"', rels)
        notes_ref = re.findall(r'Target="\.\./notesSlides/(notesSlide\d+)\.xml"', rels)
        tx = texts(xml)
        title = tx[0] if tx else "(no text)"
        head = f"## Slide {i}" + (" HIDDEN" if hidden else f" (PDF page {page})") + f": {title}"
        lines += [head, ""]
        for t in tx:
            lines.append(f"- {t}")
        if media:
            lines.append(f"- media: {', '.join(media)}")
        if links:
            lines.append(f"- links: {', '.join(links)}")
        if notes_ref:
            nx = z.read(f"ppt/notesSlides/{notes_ref[0]}.xml").decode("utf8")
            nt = [t for t in texts(nx) if not t.strip().isdigit()]
            if nt:
                lines += ["", "NOTES: " + " ".join(nt)]
        lines.append("")
    (out / "text.md").write_text("\n".join(lines))

    (out / "media").mkdir(exist_ok=True)
    for n in names:
        if n.startswith("ppt/media/"):
            (out / "media" / Path(n).name).write_bytes(z.read(n))

    if a.no_render:
        print(f"wrote {out/'text.md'} and {len(list((out/'media').iterdir()))} media files (no render)")
        return

    subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", str(out), a.pptx],
                   check=True, capture_output=True)
    pdf = next(out.glob("*.pdf"))
    pdf.rename(out / "deck.pdf")
    subprocess.run(["pdftoppm", "-jpeg", "-r", "50", str(out / "deck.pdf"), str(out / "page")], check=True)
    for p in a.hires:
        subprocess.run(["pdftoppm", "-png", "-r", "200", "-f", str(p), "-l", str(p), str(out / "deck.pdf"),
                        str(out / f"hires-{p:02d}")], check=True)

    from PIL import Image, ImageDraw
    pages = sorted(out.glob("page-*.jpg"))
    cols, rows = 4, 3
    w, h = Image.open(pages[0]).size
    for s in range(0, len(pages), cols * rows):
        sheet = Image.new("RGB", (cols * w, rows * (h + 18)), "white"); d = ImageDraw.Draw(sheet)
        for k, f in enumerate(pages[s:s + cols * rows]):
            x = (k % cols) * w; y = (k // cols) * (h + 18)
            sheet.paste(Image.open(f), (x, y + 18)); d.text((x + 4, y + 2), f"PDF page {s + k + 1}", fill="black")
        sheet.save(out / f"sheet-{s // (cols * rows) + 1}.jpg", quality=80)
    print(f"{len(ordered)} slides, {len(pages)} PDF pages, {len(list((out/'media').iterdir()))} media files -> {out}")


if __name__ == "__main__":
    sys.exit(main())
