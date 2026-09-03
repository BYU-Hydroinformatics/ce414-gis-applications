#!/usr/bin/env python3
"""Convert a CE 414 lab Word document to Markdown + images for the course site.

Usage:  python3 tools/docx2md.py "path/to/Lab N - Title.docx" docs/assignments/lab-NN

Writes <outdir>/README.md and <outdir>/images/*. The body is walked in document order so
figures land between the right paragraphs, which a plain python-docx paragraph loop does not do.

This is a FIRST PASS, not a finished page. It always needs a human edit afterwards:
  - image filenames are positional (fig-01.png); rename them to something descriptive
  - Word's caption paragraphs become **bold** lines; check they still read as captions
  - screenshots are copied as-is, so any stale interface is still stale
  - verify every field name, expression, unit and coordinate system in ArcGIS Pro
"""
import sys, os, re, zipfile
from docx import Document
from docx.oxml.ns import qn

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def esc(t):
    return t.replace(" ", " ")


def para_md(par, rels, doc, images, outdir):
    """Render one paragraph, emitting any inline images in order."""
    style = (par.style.name or "").lower()
    out = []

    # images anchored in this paragraph
    for blip in par._p.iter(f"{A}blip"):
        rid = blip.get(f"{R}embed")
        if not rid or rid not in rels:
            continue
        part = rels[rid].target_part
        ext = os.path.splitext(part.partname)[1] or ".png"
        images.append(1)
        name = f"fig-{len(images):02d}{ext}"
        with open(os.path.join(outdir, "images", name), "wb") as fh:
            fh.write(part.blob)
        out.append(f"![]({'images/' + name})")

    # text with hyperlinks preserved
    text = ""
    for child in par._p:
        if child.tag == f"{W}hyperlink":
            rid = child.get(f"{R}id")
            inner = "".join(n.text or "" for n in child.iter(f"{W}t"))
            url = rels[rid].target_ref if rid in rels else ""
            text += f"[{inner}]({url})" if url else inner
        elif child.tag == f"{W}r":
            text += "".join(n.text or "" for n in child.iter(f"{W}t"))
    text = esc(text).strip()

    if text:
        if style.startswith("heading 1") or style == "title":
            out.append(f"# {text}")
        elif style.startswith("heading 2"):
            out.append(f"## {text}")
        elif style.startswith("heading 3"):
            out.append(f"### {text}")
        elif style.startswith("heading 4"):
            out.append(f"#### {text}")
        elif "bullet" in style or "list" in style:
            out.append(f"- {text}")
        elif "caption" in style:
            out.append(f"**{text}**")
        else:
            out.append(text)
    return out


def table_md(tbl):
    rows = [[c.text.strip().replace("\n", " ") for c in r.cells] for r in tbl.rows]
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |",
           "| " + " | ".join("---" for _ in range(ncol)) + " |"]
    for r in rows[1:]:
        out.append("| " + " | ".join(r) + " |")
    return out


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(outdir, "images"), exist_ok=True)
    doc = Document(src)
    rels = doc.part.rels
    body = doc.element.body
    from docx.text.paragraph import Paragraph
    from docx.table import Table

    images, md = [], []
    for child in body.iterchildren():
        if child.tag == f"{W}p":
            md += para_md(Paragraph(child, doc), rels, doc, images, outdir)
            md.append("")
        elif child.tag == f"{W}tbl":
            md += table_md(Table(child, doc))
            md.append("")

    # collapse runs of blank lines
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    with open(os.path.join(outdir, "README.md"), "w") as fh:
        fh.write(text)
    print(f"wrote {outdir}/README.md  ({len(text.splitlines())} lines, {len(images)} images)")
    print("NEXT: rename images descriptively, re-shoot stale screenshots, verify every")
    print("      field name / expression / unit / CRS in ArcGIS Pro, then check the rubric total.")


if __name__ == "__main__":
    main()
