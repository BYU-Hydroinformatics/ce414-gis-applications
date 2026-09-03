#!/usr/bin/env python3
"""Generate docs/lectures/week-NN.md, docs/lectures/README.md, and the Lectures section of
mkdocs.yml from the DECKS table below. Everything is expressed in week numbers so the site
survives re-offering. Edit DECKS, then run:  python3 tools/build_lectures.py

Hand-written notes in a week page survive below a "<!-- notes -->" marker; everything above it
is regenerated."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = "https://byu-hydroinformatics.github.io/ce414-gis-applications"

# week, slug, title, one-line description, lab due this week (or None)
DECKS = [
    (1,  "data-models-refresher",          "Data Models Refresher",                      "What a model is, and the vector, raster, and TIN data models that every later week builds on.", None),
    (2,  "modelbuilder-a",                 "ModelBuilder, Part A",                       "Why models, then ModelBuilder in ArcGIS Pro: toolboxes, a first model, properties and environments, and the Cities Near Rivers example.", 1),
    (2,  "modelbuilder-b",                 "ModelBuilder, Part B",                       "Making a working model reusable: Add To Display, debugging gray nodes, renaming elements, exposing parameters so the model runs as a tool, and writing its metadata.", 1),
    (3,  "modelbuilder-c",                 "ModelBuilder, Part C — NDVI",                "What counts as a model, the NDVI equation and why red and near-infrared carry the vegetation signal, and the same index read at continental, farm-plot, and multi-date scale.", None),
    (3,  "raster-analysis-map-algebra",    "Raster Analysis and Map Algebra",            "Rasters as grids of numbers: cell-by-cell operations, map algebra, and NDVI as a worked example.", None),
    (4,  "georectifying-images",           "Georectifying Images",                       "Giving a scanned map or photo real-world coordinates: control points, transformations, and what can go wrong.", 2),
    (4,  "remote-sensing-3d-imaging",      "Remote Sensing and 3D Imaging",              "How sensors see the Earth — the electromagnetic spectrum, Landsat, and imagery in three dimensions.", 2),
    (5,  "terrain-analysis",               "Terrain Analysis",                           "Elevation models and the products derived from them: slope, aspect, hillshade, curvature, and viewsheds.", 3),
    (6,  "watershed-delineation",          "Watershed Delineation",                      "From a DEM to watersheds and streams: fill, flow direction, flow accumulation, thresholds, and pour points.", 4),
    (8,  "interpolation",                  "Interpolation",                              "Estimating a surface from points: Thiessen polygons, IDW, splines, and kriging, and how to judge which one to trust.", 6),
    (9,  "ogc-web-services",               "Overview of OGC Web Services",               "Interoperability and open standards for sharing spatial data over the web: WMS, WFS, WCS, and their relatives.", 7),
    (10, "raster-spatial-analysis",        "Raster-Based Spatial Analysis",              "The raster suitability workflow end to end — criteria, data, rasterization, reclassification, overlay, and heat maps.", 8),
    (11, "least-cost-path",                "Least Cost Path Analysis",                   "Cost surfaces and the cheapest route across them, with a power-line corridor as the example.", 9),
    (11, "coordinate-systems-projections", "Coordinate Systems and Projections",        "Datums, projections, and coordinate systems as decisions: distortion, units, and choosing a CRS for analysis.", 9),
    (12, "gps-triangulation",              "GPS and Positioning",                        "How satellite positioning works, what limits its accuracy, and what that means for field data.", 10),
    (12, "final-project-introduction",     "The Final Project",                          "What the capstone project is for, how big it should be, the requirements, the proposal meeting, milestones, and how it is scored.", 10),
]
LABS = {1:"Walmart Site Selection",2:"NDVI",3:"Georectifying and Digitizing Images",4:"Cell Phone Tower Placement",
        5:"Watershed Delineation",6:"Avalanche Hazard",7:"Big Southern Butte",8:"Practicing with Interpolation",
        9:"Wind Farm Site Selection",10:"Least Cost Path Power Line Analysis"}
WEEK_TITLES = {1:"Data Models Refresher",2:"ModelBuilder",3:"ModelBuilder and Raster Analysis",4:"Imagery",
               5:"Terrain Analysis",6:"Watershed Delineation",8:"Interpolation",9:"Web Services",
               10:"Raster-Based Spatial Analysis",11:"Least Cost Path and Coordinate Systems",12:"GPS and the Final Project"}

def deck_url(w, slug): return f"{SITE}/slides/week-{w:02d}/{slug}.html"

def week_page(w, decks):
    lab = next((d[4] for d in decks if d[4]), None)
    lines = [f"# Week {w}: {WEEK_TITLES[w]}", "", "## Slides", ""]
    for _, slug, title, desc, _ in decks:
        lines.append(f"- [{title}]({deck_url(w, slug)}) — {desc}")
    lines += ["", "Navigate with the arrow keys; press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view with speaker notes.", ""]
    if lab:
        lines += ["## Lab", "", f"[Lab {lab} — {LABS[lab]}](../assignments/lab-{lab:02d}/README.md)", ""]
    lines += ["> [!NOTE]", "> Which lab is due in which week is reconstructed from the deck filenames and has not been",
              "> confirmed against the Learning Suite calendar.", ""]
    return "\n".join(lines)

def index_page(weeks):
    lines = ["# Lectures", "",
             "Lecture slides are interactive web presentations built with [Marp](https://marp.app/). Navigate with",
             "the arrow keys (or swipe); press <kbd>F</kbd> for fullscreen and <kbd>P</kbd> for presenter view with",
             "speaker notes.", "",
             "Weeks are numbered from the first class meeting so the same site serves every offering; the",
             "authoritative dates live in the Learning Suite syllabus.", ""]
    for w in sorted(weeks):
        lines += [f"## Week {w}: {WEEK_TITLES[w]}", ""]
        for _, slug, title, desc, _ in weeks[w]:
            lines.append(f"- [{title}]({deck_url(w, slug)}) — {desc}")
        lines += [f"- [Week {w} page](week-{w:02d}.md)", ""]
    lines += ["> [!NOTE]", "> Every deck carries `TODO(instructor)` and `TODO(graphic)` comments from its September 2026",
              "> conversion; see each deck's closing conversion-notes comment for what still needs a decision.", ""]
    return "\n".join(lines)

def update_nav(weeks):
    yml = ROOT / "mkdocs.yml"; text = yml.read_text()
    nav = ["  - Lectures:", "      - Overview: lectures/README.md"]
    for w in sorted(weeks):
        nav.append(f'      - "Week {w} — {WEEK_TITLES[w]}": lectures/week-{w:02d}.md')
    yml.write_text(re.sub(r"  - Lectures:\n(?:      .*\n)+", "\n".join(nav) + "\n", text))

def main():
    weeks = {}
    for d in DECKS: weeks.setdefault(d[0], []).append(d)
    (DOCS / "lectures").mkdir(exist_ok=True)
    for w, decks in weeks.items():
        p = DOCS / "lectures" / f"week-{w:02d}.md"; body = week_page(w, decks)
        if p.exists() and "<!-- notes -->" in p.read_text():
            body += "\n<!-- notes -->" + p.read_text().split("<!-- notes -->", 1)[1]
        p.write_text(body)
    (DOCS / "lectures" / "README.md").write_text(index_page(weeks))
    update_nav(weeks)
    print(f"wrote {len(weeks)} week pages, lectures/README.md, and the Lectures nav")

if __name__ == "__main__":
    main()
