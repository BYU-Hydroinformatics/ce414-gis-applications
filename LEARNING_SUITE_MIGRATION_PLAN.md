# Learning Suite → course site link migration plan

**Course:** CE 414 — Engineering Applications of GIS, Fall 2026
**Learning Suite course id:** `cid-ahk3xMzyr311`
**Target site:** <https://byu-hydroinformatics.github.io/ce414-gis-applications/>
**Written:** September 3, 2026
**Status:** labs done (September 3, 2026) — all ten lab handout links now point at the course
site. Lecture decks are still pending; they are blocked on the decks themselves landing.

The job: every Learning Suite link that currently downloads a lecture `.pptx` or a lab `.docx`
becomes a link to the live page on the course site instead. Data files stay as downloads.

This mirrors what was already done for [CCE 114](https://byu-hydroinformatics.github.io/cce114-geomatics/),
whose Learning Suite course is fully converted. **CCE 114 is the reference implementation** — its
markup, link wording, and structure are copied here verbatim rather than reinvented.

> [!IMPORTANT]
> Nothing gets flipped until the destination page is live and has been read end to end. A link that
> 404s is worse for a student than a `.pptx` download. See [Gate](#the-gate) below.

---

## The two edit surfaces

Everything lives in one of two places. There is no bulk-edit and no API — each item is a rich-text
field edited through the CKEditor **Source** view.

### 1. Schedule (lecture decks)

`Schedule` tab → `Edit Schedule` → the content cell for a class day.

Current markup for an attached deck (verified on Lab 1's assignment, identical shape in schedule
cells):

```html
<span class="ck_embededFile"><span class="embededFile_Name">414 - Data Models.pptx</span>&nbsp;&nbsp;<span
 class="embededFile_FileOptions"><a class="embededFile_Download"
 href="plugins/Upload/fileDownload.php?fileId=4555c794-…" target="_blank">Download</a></span></span>
```

Replacement, following CCE 114:

```html
<a href="https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-01/data-models.html"
   target="_blank">Spatial Data Models (slides)</a>
```

### 2. Assignments (lab handouts)

`Assignments` tab → click the assignment title → `Description` → `Source`.

Current (CE 414, Lab 1):

```html
<p><span class="ck_embededFile"><span class="embededFile_Name">Lab 1 - Walmart Site Selection.docx</span>&nbsp;&nbsp;<span
 class="embededFile_FileOptions"><a class="embededFile_Download"
 href="plugins/Upload/fileDownload.php?fileId=b6a5f79b-…" target="_blank">Download</a></span></span><span>&nbsp;</span><br />
<br /><span>(2025 updated)</span><br /></p>
```

Replacement — this is the **exact** CCE 114 Lab 1 markup, retargeted:

```html
<p><a href="https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-01/"
 target="_blank">Lab 1 Assignment</a>. Read the instructions carefully. Build your lab report in
 Microsoft Word or Google Docs, then export it as a PDF for submission. Only submit one file - your
 PDF lab report - here on Learning Suite.</p>
```

---

## URL scheme (verified live)

| Kind | Pattern | Probe |
| --- | --- | --- |
| Lab page | `…/ce414-gis-applications/assignments/lab-NN/` | `/assignments/lab-01/` → 200 |
| Lecture deck | `…/ce414-gis-applications/slides/week-NN/<slug>.html` | matches `cce114-geomatics/slides/day-01/intro-to-gis.html` → 200 |
| Lecture page (optional, see below) | `…/ce414-gis-applications/lectures/week-NN/` | not built yet |

MkDocs serves `docs/assignments/lab-01/README.md` at `/assignments/lab-01/`; the Marp step in
`.github/workflows/` writes `slides/<folder>/<slug>.md` to `_site/slides/<folder>/<slug>.html`.

---

## Work item 1 — lecture decks in the Schedule

Fifteen `.pptx` download links, one per source deck. Week numbers agree with
`docs/lectures/README.md`, so no renumbering is needed.

| LS date | Schedule item | Current attachment | Target URL (`…/ce414-gis-applications/`) | Blocked by |
| --- | --- | --- | --- | --- |
| Thu Sep 3 | Spatial Data Models - Refresher | `414 - Data Models.pptx` | `slides/week-01/data-models.html` | — |
| Tue Sep 8 | Graphical Modeling and Model Builder Part 1 | `414 - ModelBuilder A.pptx` | `slides/week-02/modelbuilder-a.html` | slides 12, 17–21 still need Pro captures |
| Thu Sep 10 | Graphical Modeling and Model Builder Part 2 | `414 - ModelBuilder B.pptx` | `slides/week-02/modelbuilder-b.html` | — |
| Tue Sep 15 | NDVI Model | `414 - ModelBuilder C.pptx` | `slides/week-03/ndvi-model.html` | **deck identity unresolved** — it is NDVI content under a ModelBuilder name |
| Tue Sep 15 | Raster Analysis and Map Algebra - Part 1 | `414 - Raster Analysis and Map Algebra.pptx` | `slides/week-03/raster-analysis-and-map-algebra.html` | verify the "more heat (NIR)" claim |
| Tue Sep 22 | Image Georeferencing and Georectification | `414 - Georectifying Images.pptx` | `slides/week-04/georectifying-images.html` | deck contains no ArcGIS UI; needs new Pro captures |
| Thu Sep 24 | Satellite and Imagery Data | `414 - Remote Sensing and 3D Imaging.pptx` | `slides/week-04/remote-sensing-and-3d-imaging.html` | one broken external image link |
| Tue Sep 29 | Terrain Analysis Part 1 | `Terrain Analysis.pptx` | `slides/week-05/terrain-analysis.html` | — |
| Tue Oct 6 | Hydrologic Analysis - Part 1 | `414 - Watershed Delineation.pptx` | `slides/week-06/watershed-delineation.html` | — |
| Tue Oct 20 | Sampling and Interpolation Part 1 | `414 - Interpolation.pptx` | `slides/week-08/interpolation.html` | — |
| Thu Oct 29 | Data Services and Data Quality | `Overview_of_OGC_Web_Services.pptx` | `slides/week-09/ogc-web-services.html` | — |
| Tue Nov 3 | Raster-Based Site Suitability - Part 1 | `414 - Raster Based Spatial Analysis.pptx` | `slides/week-10/raster-based-spatial-analysis.html` | conceptual diagrams only |
| Tue Nov 10 | Least Cost Path - Part 1 | `414 - Least Cost Path Analysis.pptx` | `slides/week-11/least-cost-path-analysis.html` | **teaches deprecated `CostDistance`/`Backlink`** — fix tool choice first |
| Thu Nov 12 | Projections & Coordinate Systems review | `Coordinate Systems and Projections.pptx` | `slides/week-11/coordinate-systems-and-projections.html` | — |
| Thu Nov 19 | Differential GPS | `8 - GPS and Triangulation.pptx` | `slides/week-12/gps-and-triangulation.html` | — |

Slugs above are proposals; whatever the deck file is actually named in `slides/` wins, and this
table gets corrected rather than the file renamed after the fact.

### Link wording

CCE 114 puts the deck link inline on the topic line and keeps the sentence readable:

> Discussion: **Maps, Symbology, and Cartography (slides)**

Do the same here: keep the existing "Discussion:" / "Slides:" lead-in, drop the filename, and make
the topic phrase plus `(slides)` the link text. Never leave a bare URL in the cell.

---

## Work item 2 — lab handouts in Assignments

Ten `.docx` links, one per lab, all in assignment descriptions.

| LS assignment | Due | Target URL (`…/ce414-gis-applications/`) |
| --- | --- | --- |
| Lab 1: Walmart Site Selection with ModelBuilder | 09/12 | `assignments/lab-01/` |
| Lab 2: Normalized Difference Vegetation Index (NDVI) | 09/19 | `assignments/lab-02/` |
| Lab 3: Georectifying and Digitizing Images | 09/26 | `assignments/lab-03/` |
| Lab 4: Cell Phone Tower Placement | 10/03 | `assignments/lab-04/` |
| Lab 5: Watershed Delineation | 10/10 | `assignments/lab-05/` |
| Lab 6: Avalanche Hazard Mapper | 10/17 | `assignments/lab-06/` |
| Lab 7: Big Southern Butte | 10/24 | `assignments/lab-07/` |
| Lab 8: Practicing with Interpolation | 10/31 | `assignments/lab-08/` |
| Lab 9: Wind Farm Site Selection | 11/07 | `assignments/lab-09/` |
| Lab 10: Least Cost Path Power Lines | 11/14 | `assignments/lab-10/` |

**Done September 3, 2026.** All ten were opened, read, and edited individually; the descriptions
turned out to vary more than the plan assumed, so the edit was made **surgical** — only the
`ck_embededFile` span for the `.docx` was swapped for the site link, leaving everything else in
place. That preserved Lab 2's three Landsat `.zip` attachments and Google Drive and USGS links,
Lab 5's Rock Canyon DEM `.zip`, and Lab 10's `ElectricalLines_shp.zip`.

Stale "(updated …)" notes were dropped along with the file they described — they referred to the
Word document's revision date and would have read as claims about the linked page. Lab 1 was the
one full replacement: its description contained nothing but the attachment, a `(2025 updated)`
note, and empty `<br />`s, so it now carries the CCE 114 sentence. The other nine carry the link
alone, matching whatever prose was already around it.

Verified from **Student View**: every lab shows its `Lab N Assignment` link, no `.docx` remains in
any description, and all five data attachments survived. Removed markup is recorded in
[`learning-suite-snapshots/`](learning-suite-snapshots/).

**Lab 11: Choose Your Own Adventure has no attachment.** Its description tells students to pick one
of the prior-year example projects listed on the Nov 17 schedule page. Nothing to replace, but it
is affected by the decision in [Open questions](#open-questions) about the example-project `.docx`
files.

### Two plain-text lab mentions in the Schedule

The Schedule also names labs without linking them. Once the lab pages exist, make these links:

- Tue Sep 8 — "Lab: Walmart Site Selection Model" → `assignments/lab-01/`
- Tue Sep 22 — "Lab: Georectifying and Digitizing Images" → `assignments/lab-03/`

---

## Work item 3 — lecture pages (decision required)

CCE 114 carries **two** links per class day:

1. the inline deck link — `…/slides/day-04/maps-and-cartography.html`
2. a closing line — "Lecture materials: **Day 4 — Maps, Symbology, and Cartography, Part 1**" →
   `…/lectures/day-04/`

CE 414 has no per-week lecture pages. `docs/lectures/README.md` is a single overview and the nav
has one `Lectures → Overview` entry. Two options:

- **A (minimum):** link the deck only. Cheapest, still removes every `.pptx` download.
- **B (parity with CCE 114):** add `docs/lectures/week-NN/README.md` pages and nav entries, then add
  the "Lecture materials:" line to each schedule day.

**Recommendation: B**, but staged — do A first so the `.pptx` links die as soon as each deck lands,
then add the lecture pages and the second link as a follow-up pass. B is a repo change, not a
Learning Suite change, so it does not block anything.

---

## What stays a Learning Suite download

Do **not** convert these. They are data or artefacts, not documents:

- All `.zip` data packages — `UtahCountyData.zip`, `United States.zip`, `LehiNAIP2003-2018.zip`,
  `EdinburghCastle.zip`, `CedarCityData.zip`, `iron_ned30.zip`, `CitiesGIS.zip`, `YMountain.zip`,
  `UtahRaster.zip`
- All in-class `.xlsx` workbooks and `.txt` grids — `raster analysis in class.xlsx`,
  `utah map algebra data.xlsx` (+ solution), `terrain analysis - in class activity.xlsx`,
  `terrain analysis - in class activity - aspect and d8 flow direction.xlsx`, `UtahAvgAnnPrec.txt`
- Prior-year student submissions shown on Sep 10 (`Cooper_Hika_…pdf`, `Cordner_Cameron_…pdf`) —
  student work; leave in Learning Suite behind the login.

`engineering stamps.pptx` (Sep 3, example stamps) is a `.pptx` but not a lecture deck. Leave it
unless Dan wants an examples page.

---

## The gate

Per item, in order. Do not batch-flip.

1. The deck or lab page is committed, pushed, and the Pages build is green.
2. `curl -o /dev/null -w '%{http_code}'` on the exact target URL returns **200**.
3. The page has been opened and read end to end — deck rendered to PNGs, every slide looked at
   (`CLAUDE.md`, "Always look at what you produced").
4. **Snapshot first.** Copy the item's current Source HTML into `learning-suite-snapshots/` in this
   repo before editing. Learning Suite keeps no version history for these fields; the snapshot is
   the only rollback.
5. Edit the Source view, save, reload the page as **Student View**, and click the new link.
6. Tick the row in this file.

Bulk URL check once several are live:

```bash
for u in assignments/lab-01/ assignments/lab-02/ slides/week-01/data-models.html; do
  printf '%-50s ' "$u"
  curl -s -o /dev/null -w '%{http_code}\n' "https://byu-hydroinformatics.github.io/ce414-gis-applications/$u"
done
```

Re-scan Learning Suite for anything missed — paste into the browser console on the Schedule page:

```js
[...document.querySelectorAll('a.embededFile_Download')]
  .map(a => a.closest('.ck_embededFile').querySelector('.embededFile_Name').textContent)
  .filter(n => /\.(pptx|docx)$/i.test(n))
```

An empty array on both the Schedule and each assignment description means the migration is done.

---

## Sequencing

The migration order in `ROADMAP.md` already front-loads the cleanest sources; this plan just
follows it and flips links behind it.

| Phase | Content that must land first | Learning Suite edits |
| --- | --- | --- |
| 1 | Lab 1 | Lab 1 assignment description; Sep 8 "Lab:" mention |
| 2 | Week 1 + Week 2 decks | Sep 3, Sep 8, Sep 10 schedule cells |
| 3 | Labs 2–10, as each lands | one assignment description each; Sep 22 "Lab:" mention |
| 4 | Remaining decks, as each lands | one schedule cell each |
| 5 | Lecture pages (option B) | add the "Lecture materials:" line to each day |
| 6 | — | final re-scan; decide on example-project `.docx` files |

Phases 3 and 4 interleave. Each item is independent — a stalled deck never blocks a lab.

Rough effort: about 15 minutes per item, most of it the read-before-you-flip step. Twenty-seven
edits total (15 decks + 10 labs + 2 plain-text mentions), plus 15 more if option B is taken.

---

## Open questions

1. **Option A or B** for lecture pages (work item 3). Recommendation above is B, staged.
2. **The sixteen `Example Final Project - *.docx` files** on the Nov 17 schedule page. They are the
   menu Lab 11 points at. Migrate them into a single `docs/assignments/project-ideas.md` page, or
   leave them as downloads? A single page is better for students and kills sixteen downloads, but
   it is real conversion work and is out of scope for the current roadmap.
3. **`414 - ModelBuilder C.pptx`** is NDVI content, not ModelBuilder. Its schedule item is already
   titled "NDVI Model", so the schedule is right and the file name is wrong. Decide the deck's
   identity before it converts; that decision sets its slug.
4. **Deck slugs.** The table above proposes them. Confirm or override before the first deck lands,
   because the Learning Suite link is written once and should not need a second edit.
