# CE 414 Course Site — Roadmap and Session Handoff

**Last updated:** September 3, 2026
**Repo:** https://github.com/BYU-Hydroinformatics/ce414-gis-applications
**Site:** https://byu-hydroinformatics.github.io/ce414-gis-applications/
**Sibling repo (the pattern to copy):** https://github.com/BYU-Hydroinformatics/cce114-geomatics

## The goal

Move CE 414 out of Word, PowerPoint, and Learning Suite attachments and onto a public course site:

- **Lab assignments** become Markdown under `docs/assignments/lab-NN/`, served by MkDocs Material.
- **Lecture slides** become [Marp](https://marp.app/) web decks under `slides/week-NN/`.
- Everything redeploys on push. Students get a URL, not a download.

This mirrors what was done for CCE 114 Geomatics. Where the two courses differ, CE 414 wins:
**CE 414 uses ArcGIS Pro, not QGIS.** Do not carry CCE 114's QGIS substitutions across.

## Where the source material lives

Everything originates in Dr. Ames's course folder, which is **not** in this repo:

```
/Users/dan/ames-sync/Work/Teaching/CE 414 Engineering Applications of GIS/
├── Labs/                    Lab 1–10 .docx  (Lab 1 was corrected Sept 3, 2026)
│   └── Old/2026_pre_refresh/   archived originals
├── Lectures/2026/           the 15 current .pptx decks
│   └── ../Old/2026_pre_pro_refresh/  archived originals
├── _screenshots_2026/       new ArcGIS Pro captures, with a README
├── recommended_plan.md      the living course-improvement plan — READ THIS
├── SCREENSHOT_SHOT_LIST.md  evidence-based audit of every image in every deck and lab
└── NEXT_AGENT_HANDOFF.md    prior handoff (Lab 1 data package, Citrix notes)
```

`recommended_plan.md` and `SCREENSHOT_SHOT_LIST.md` are the two documents worth reading in full
before doing anything substantial. They record an audit of all 797 embedded images across the
15 decks and 10 labs, plus a completed-work log.

## Current state

The scaffold is complete and the site builds, but **no content has been migrated**. Every lab page
is a placeholder with a migration checklist; the lectures page lists the source decks and what is
known to be wrong with each.

| Piece | State |
| --- | --- |
| MkDocs config, theme, nav | Done — mirrors CCE 114 |
| GitHub Pages workflow (MkDocs + Marp) | Done — untested until first push |
| Marp theme `slides/theme/ce414.css` | Done — BYU navy, adapted from `cce114.css` |
| `tools/docx2md.py` | Done and tested against Lab 1 |
| `tools/pptx_extract.py` | Copied from CCE 114, unchanged |
| `tools/slide-conversion-guide.md` | Adapted for ArcGIS Pro and CE 414's rhythm |
| Lab pages 1–10 | Placeholders only |
| Lecture pages and decks | None converted |
| Policies, schedule, course overview | Stubs with TODOs |

## Migration order

Work in this order. It front-loads the things students hit first and the things already repaired.

### 1. Lab 1 — Walmart Site Selection

Best first candidate: the Word version was corrected on Sept 3, 2026 (census vintage, density
units, projected CRS, Intersect-vs-Clip, rubric total), so the text is in good shape.

```bash
python3 tools/docx2md.py \
  "/Users/dan/ames-sync/Work/Teaching/CE 414 Engineering Applications of GIS/Labs/Lab 1 - Walmart Site Selection.docx" \
  docs/assignments/lab-01
```

Then rename `images/fig-NN.png` to descriptive names, fix figure captions, and check the rubric
table renders.

> [!WARNING]
> **Lab 1's screenshots are gated.** They still show the old workflow — `CensusBlocks2010`,
> `!POP100!/!SqMiles!`, `CARTO = 1/2/3/6`. Do **not** re-shoot them until the data validation in
> `Labs/Lab 1 Data/2026-09-02/ARCGIS_PRO_VALIDATION_CHECKLIST.md` passes. Migrating the text with
> the old images is fine and expected; just flag them.

### 2. Week 1 and Week 2 lecture decks

Both were updated on Sept 3, 2026 and are the two cleanest sources:

- **Week 1 — Data Models Refresher.** ArcMap reference removed, learning-objectives slide added.
- **Week 2 — ModelBuilder A.** ArcGIS 9 / Windows XP screenshots replaced with real ArcGIS Pro
  captures on slides 13–16; slide 16's ArcMap toolbar callouts replaced with the verified
  ModelBuilder ribbon group list.
- **Week 2 — ModelBuilder B** already uses current ArcGIS Pro screenshots and needs no re-shoot.

Follow `tools/slide-conversion-guide.md` exactly. The first converted deck becomes the reference
for every deck after it, so it is worth doing slowly.

### 3. Remaining labs, 2 → 10

Straight `docx2md.py` runs plus cleanup. Lab 9 and Lab 5 have the most modern screenshots; Lab 3
and Lab 10 have working Pro captures too.

### 4. Remaining lecture decks

Leave the three problem decks until their content questions are settled (see below).

## Known problems to carry forward

These came out of the September 2026 audit and are **not** cosmetic:

- **`Week 3 - ModelBuilder C.pptx` is not about ModelBuilder.** It is seven slides of NDVI content.
  Decide what this deck is before converting it.
- **`Week 11 - Least Cost Path Analysis.pptx` teaches deprecated tools.** It uses ArcMap-era
  `CostDistance` / `Backlink`. Current practice is **Distance Accumulation** + **Optimal Path As
  Line**. Fix the tool choice before converting; the screenshots cannot be fixed independently.
- **Six "screenshots" across Labs 4, 5, 7, 9, 10 and the LCP deck are illegible.** They are
  zoomed-out ModelBuilder canvas grabs. These need **re-export from ModelBuilder**, not
  re-screenshotting.
- **`Week 4 - Georectifying Images.pptx` contains no ArcGIS UI at all.** It needs new Pro captures
  of the Georeference tab, control points, and the residuals/RMSE table — not replacements.
- **ModelBuilder A slides 12, 17, 18 and 19–21 still need captures.** They require a properly saved
  ArcGIS Pro project with US cities and major rivers data. Slide 21 asserts "898 of 3,128 U.S.
  cities are within 10 miles of a major river" and slide 22 asks students to reproduce it —
  **re-verify that figure** against whatever data the rebuilt project uses.
- **The decks are 4:3.** The course standards call for 16:9. Marp decks are 16:9 by default, so
  this resolves itself during conversion — but expect images sized for 4:3 to need re-placing.

## How to capture new ArcGIS Pro screenshots

ArcGIS Pro runs through BYU Citrix (`byuapps.cloud.com` → *2025 BYU Standard Desktop*). The
constraints below were all found the hard way in September 2026:

- Drive the session through **Chrome**, not an embedded browser pane.
- Dan maps the course folder into the session as **`F:`**. The bridge works Mac → Citrix.
- **Typed paths are blocked by Citrix policy** — navigate Explorer by clicking through the tree.
- **Windows Search is dead** on that image. `PrtScn` opens Snipping Tool, which is how you reach it.
- **Snipping Tool's drag does not release** through the HTML5 client, and **PowerPoint's Save does
  not execute**, and the **image clipboard does not sync back to macOS**. So do not try to save
  files out of Citrix.
- **What works:** capture on the Mac side. `screencapture` grabs the Chrome window at full Retina
  resolution (2940×1912), then crop the region with Pillow. Bring Chrome to the front first and
  make sure its window is fully on screen, or captures clip.

Existing captures and the shot list live in the course folder under `_screenshots_2026/`.

## Conventions

- One folder per lab: `docs/assignments/lab-NN/README.md` + `images/`. Nothing references an image
  outside its own folder.
- One folder per lecture week: `slides/week-NN/<slug>.md` + `images/`.
- Do not commit built output (`site/`, deck `.html`).
- Use GitHub-style admonitions (`> [!NOTE]`, `> [!WARNING]`) — the `gh-admonitions` plugin renders
  them.
- Express the schedule in **week numbers, not calendar dates**, so it survives re-offering.
- Never fabricate a screenshot, a field name, a coded value, or a data figure. If something cannot
  be verified, leave a `<!-- TODO -->` and say so in your report.

## Definition of done, per lab

- [ ] Text converted, headings correct, tables render
- [ ] Images renamed descriptively and displaying
- [ ] Every field name, SQL expression, unit, CRS, and coded value verified in ArcGIS Pro
- [ ] All data links tested; provenance, vintage, and licence recorded
- [ ] Rubric matches the stated deliverables and the points total is correct
- [ ] ArcGIS Pro version the lab was tested against is recorded
- [ ] Page rendered and read end to end before it is linked for students
