# CE 414 Course Site — Roadmap and Session Handoff

**Last updated:** September 3, 2026
**Repo:** https://github.com/BYU-Hydroinformatics/ce414-gis-applications
**Site:** https://byu-hydroinformatics.github.io/ce414-gis-applications/
**Sibling repo (the pattern to copy):** https://github.com/BYU-Hydroinformatics/cce114-geomatics

> [!IMPORTANT]
> **New session? Read [`CLAUDE.md`](CLAUDE.md) first**, then this file. `CLAUDE.md` has the hard
> rules (ArcGIS Pro not QGIS; never fabricate a screenshot or a field name; verify before
> asserting). This file has the plan and the order of work.

## The goal

Move CE 414 out of Word, PowerPoint, and Learning Suite attachments and onto a public course site:

- **Lab assignments** become Markdown under `docs/assignments/lab-NN/`, served by MkDocs Material.
- **Lecture slides** become [Marp](https://marp.app/) web decks under `slides/week-NN/`.
- Everything redeploys on push. Students get a URL, not a download.
- **Learning Suite holds as little as possible**: due dates, submission boxes, quizzes, and links to
  this site. The course moves to Canvas in Fall 2027, and anything that lives here rather than in an
  LMS attachment or schedule entry is one less thing to migrate. When something can be a page or a
  hosted file on this site, put it here and link it from the LMS.

This mirrors what was done for CCE 114 Geomatics. Where the two courses differ, CE 414 wins:
**CE 414 uses ArcGIS Pro, not QGIS.** Do not carry CCE 114's QGIS substitutions across.

## Where the source material lives

Everything originates in Dr. Ames's course folder, which is **not** in this repo:

```
/Users/danames/ames-sync/Work/Teaching/CE 414 Engineering Applications of GIS/
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

All ten lab handouts are migrated (Sept 3, 2026). Each page was converted with `tools/docx2md.py`,
hand-cleaned, checked for source coverage, and flagged rather than "fixed" wherever a claim could
not be verified without ArcGIS Pro. **Read the migration-notes comment at the foot of each lab
page** — it lists that lab's stale screenshots, unverified expressions, dead links, and instructor
decisions. Three images were redacted for student privacy (Lab 5 Figure 17, Lab 9 Figures 22 and
28); the notes record exactly what was covered.

The lecture decks followed the same day: fifteen PowerPoints converted to Marp under `slides/week-NN/`
by fifteen parallel agents, each verified by a second independent render; plus
`slides/week-12/final-project-introduction.md`, written new from the one-page Learning Suite
project description and the peer scoresheet. **Every deck ends with a conversion-notes comment**
listing dropped slides, stale screenshots, `TODO(instructor)`, `TODO(graphic)`, and `VERIFY` items.
No AI images were generated in that pass — every slide lacking a graphic carries a `TODO(graphic)`
instead, so image generation can be run as a separate, visible step. Browser captures in Week 5
had their tab strips cropped for the same privacy reason as the labs.

`docs/lectures/` is generated: edit the `DECKS` table in `tools/build_lectures.py` and re-run it
rather than hand-editing the week pages or the Lectures nav.

| Piece | State |
| --- | --- |
| MkDocs config, theme, nav | Done — mirrors CCE 114 |
| GitHub Pages workflow (MkDocs + Marp) | Done — untested until first push |
| Marp theme `slides/theme/ce414.css` | Done — BYU navy, adapted from `cce114.css` |
| `tools/docx2md.py` | Done and tested against Lab 1 |
| `tools/pptx_extract.py` | Copied from CCE 114, unchanged |
| `tools/slide-conversion-guide.md` | Adapted for ArcGIS Pro and CE 414's rhythm |
| Lab pages 1–10 | **Migrated Sept 3, 2026** from the Word handouts — text and images complete, every page carries `TODO(instructor)` / `VERIFY` comments and a migration-notes block; nothing yet verified in ArcGIS Pro |
| Labs 1 and 2, revised | **Done, assigned versions** (September 6, 2026). Each was rewritten after a full run in ArcGIS Pro 3.7.1 with every figure re-shot, drafted as `draft.md` beside the migrated page, piloted, and then promoted to `docs/assignments/lab-0N/README.md`. Both have a sensitivity-analysis step in place of the old second study area, a five-part rubric of ten points each, and a self-assessment/peer-review requirement. The comparison that drove Lab 2's revision is `tools/lab02/PARITY_PLAN.md`; the revision notes sit in an HTML comment at the top of each page. `docs/arcgis-tips.md`, which both labs reference, is in the nav. Lab 2's figures were re-shot a second time on the evening of September 6, 2026, in a from-scratch GUI pass at 175 % display scaling (the GUI pilot the round-3 notes said was owed); that pass corrected four things in the text and the example maps are now in the extract's native WGS 1984 UTM Zone 12N. Lab 1's figures are still the 100 %-scaling captures and would benefit from the same treatment. |
| Lecture pages and decks | **All 15 PowerPoints converted to Marp on Sept 3, 2026**, plus a new Final Project deck built from the Learning Suite page; one page per week under `docs/lectures/`, generated by `tools/build_lectures.py` |
| Policies, schedule, course overview | Stubs with TODOs |
| Week 2 decks (ModelBuilder A and B), revision | **Planned** (September 7, 2026): `slides/week-02/LECTURE_PLAN.md` is a slide-by-slide handoff plan for the Sept 8 and 10 sessions: two parts only, no data-models wrap-up, Lab 1 clinic folded into Part B, asset list with new ArcGIS Pro captures and infographics, Lab 1 and 2 figures to reuse. Executed September 7, 2026: both decks revised and live, with fresh ArcGIS Pro captures from C:\Ames\Week02\CitiesRivers.aprx, the hosted cities-and-rivers data, and the Lab 1 clinic in Part B. The closing slides carry the confirmed Fall 2026 dates (Quiz 2 and Lab 1, Saturday 11:59 pm). Learning Suite Week 2 was aligned on September 7, 2026: data-models wrap-up removed, Part 3 renamed to the Walmart lab discussion, cookie activity due Thursday 9:30 am. Open: the anonymized prior-year report page for Part B; until one exists the instructor shows the named prior-year PDFs from Learning Suite. |

## If you are picking this up cold, do this first

A single, self-contained first task that exercises the whole pipeline:

**Migrate Lab 1 to `docs/assignments/lab-01/`.**

1. Read `CLAUDE.md`, then the "Known problems" section below.
2. Run the converter (command in step 1 of the migration order).
3. Rename `images/fig-NN.png` to descriptive names and fix the references.
4. Read the rendered page end to end (`mkdocs serve`) against the Word original side by side.
5. Do **not** re-shoot the screenshots — Lab 1's are gated, see the warning below.
6. Report: what converted cleanly, what needed hand-fixing, and every item you flagged.

It is small enough to finish, and it tells you whether `docx2md.py` needs work before the other
nine labs go through it.

## Migration order

Work in this order. It front-loads the things students hit first and the things already repaired.

### 1. Lab 1 — Walmart Site Selection

Best first candidate: the Word version was corrected on Sept 3, 2026 (census vintage, density
units, projected CRS, Intersect-vs-Clip, rubric total), so the text is in good shape.

```bash
python3 tools/docx2md.py \
  "/Users/danames/ames-sync/Work/Teaching/CE 414 Engineering Applications of GIS/Labs/Lab 1 - Walmart Site Selection.docx" \
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
  *Resolved September 9, 2026:* its NDVI content was folded into `slides/week-03/raster-analysis-map-algebra.md`
  (Tuesday: map algebra, then NDVI as the first raster model) and the Thursday session became a new
  hands-on deck, `slides/week-03/raster-hands-on.md`. The Part C deck is gone.
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

## Syllabus decisions and open items (September 7, 2026)

The Fall 2026 Learning Suite syllabus was transcribed into `tools/build_lectures.py` (the `DUE`
table), `docs/schedule.md`, `docs/policies/grading.md`, and `docs/course.md`. Reviewing it with the
instructor produced these decisions; the open ones need to be settled on Learning Suite and then
mirrored here.

Settled:

- **Class is 8:00 to 9:15 am Tuesday and Thursday** (75 minutes). The 2:00 to 2:50 pm slot in the
  Learning Suite section header is an **open lab period** with the computer lab reserved for this
  class, for individual work on the lab assignment. The site says so on the course and schedule pages.
- **In-class activities are due at 9:30 am** the day they happen, fifteen minutes after class. The
  Learning Suite due times were already 9:30 am; the site now explains why.
- **Chapter 10** of *GIS Fundamentals* is about half terrain analysis and half watersheds, which is
  why Quiz 6 (Watershed Delineation) points back to it.
- **Presentation day 3** (the Friday exam-preparation day of Week 15) is removed. The site no longer
  mentions it; remove it from the Learning Suite schedule too.

Open, in priority order:

1. **Exam schedule: settled September 8, 2026.** Testing Center requests (pending approval) put
   Midterm 1 at Tuesday October 20, 8:00 am, to Thursday October 22, 9:00 pm (Week 8) and Midterm 2
   at Tuesday December 1 to Thursday December 3, same hours (Week 14); the late fee starts 2:00 pm
   Thursday. The site reflects this (`DUE[8]`, `DUE[14]`, schedule and grading pages, Week 8 and
   12 closing slides). Still to do: mirror it on Learning Suite (both exam assignments and the
   schedule text entries), and decide what Thursday of Week 7 becomes now that it is not exam day.
2. **The pre-Thanksgiving pile-up.** Moving Midterm 2 to Week 14 takes it out of Week 12, which
   still has Quiz 11, Lab 11, and the final-project kickoff. Week 14 now carries Midterm 2 and the
   first presentation day; judge after this offering whether that is too much.
3. **Final project proposal date.** The proposal meeting is due Friday December 4, after
   presentations begin on Thursday December 3. Move it earlier (Week 13 is the natural slot), then
   update `DUE[14]`, the schedule page's milestone table, and `docs/assignments/final-project.md`.
4. **Lab 6 — Lake Depth Explorer (renumbering done September 8, 2026).** The new bathymetry lab
   is Lab 6, introduced Thursday of Week 7 and due that Saturday; the Word-era Labs 6 to 10 became
   Labs 7 to 11 (folders, image prefixes, nav, index, overview, DUE table, schedule, and every
   deck closing slide were renumbered) and "Choose Your Own Adventure" is gone. Learning Suite
   matches except Lab 6's due date, which still reads October 10 and should be October 17.
   `docs/assignments/lab-06/README.md` is a **placeholder** written to the anatomy in
   `tools/lab-conversion-guide.md`: the analytical question, the parameters the student varies,
   the tool list, the step titles, the deliverables, and the rubric are in place; every check
   value, figure, and data file is a `TODO(instructor)`. The design still to be settled: which
   lake, the elevation surface and its vertical datum, the water-surface elevation range and step,
   and how the model loops (the ModelBuilder **For** iterator with inline `%Value%` substitution,
   to be verified in ArcGIS Pro 3.7). Then build it per section 9 of the guide: model, data
   package, check values, figures, example maps, pilot.
5. **Rethink the reading quizzes.** Open question: what is a "reading quiz" worth in the AI era? One
   option under consideration is a short **pre-class quiz and a post-class quiz** per topic, with
   AI and web search allowed instead of the book. Nothing is decided; until it is, the site describes
   the quizzes as the syllabus does (open book, independent, Saturday 11:59 pm).
6. **Grading points: settled September 8, 2026** from the instructor assignments view: 1,270 points
   (labs 550, quizzes 220, exams 300, final project 100, attendance and participation 100). The
   student view shows only 1,030 because Quizzes 5 to 11 and the Final Exam are not yet visible to
   students; publish them or the percentages students see stay off.
7. **Quiz 1 timing** (due two days after the first class, covering two chapters) is still as
   Learning Suite has it. The cookie activity due date was fixed on Learning Suite September 8.

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

**Lab screenshot verification pass (Sept 3, 2026):** the per-lab image plan, the reasons the
first attempt stalled at the Citrix door, and the Mac-side capture helper are in
[`tools/screenshot-verification-handoff.md`](tools/screenshot-verification-handoff.md) and
`tools/capture_citrix.py`. Read the handoff before starting any screenshot session.

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

The full standard, section by section, is `tools/lab-conversion-guide.md`; Labs 1 and 2 are the
reference pages. The short list:

- [ ] Text converted, headings correct, tables render
- [ ] Images renamed descriptively and displaying
- [ ] Every field name, SQL expression, unit, CRS, and coded value verified in ArcGIS Pro
- [ ] All data links tested; provenance, vintage, and license recorded
- [ ] Rubric matches the stated deliverables and the points total is correct
- [ ] ArcGIS Pro version the lab was tested against is recorded
- [ ] Page rendered and read end to end before it is linked for students

## Definition of done, per lecture deck

- [ ] Converted per `tools/slide-conversion-guide.md`, which is the authority on structure and tone
- [ ] Title slide, a **Today's Goals** slide, and a **Before Next Class** slide
- [ ] Every speaker note from the source carried across as an HTML comment
- [ ] All ArcGIS 9 / ArcMap / ArcCatalog / ArcToolbox wording updated to ArcGIS Pro equivalents
- [ ] Any remaining ArcMap-era screenshot explicitly flagged, not silently kept
- [ ] Images in the deck's own `images/` folder, nothing wider than 2000 px, folder under ~15 MB
- [ ] Deck rendered to PNGs and **every slide looked at** — no overflow, no unreadable image
- [ ] A conversion-notes HTML comment at the end of the deck: source, slides dropped, TODOs
- [ ] A matching page under `docs/lectures/` linking to the published deck URL

## Reporting back

Whatever you finish, say plainly: what you changed, what you verified versus what you assumed,
what you flagged and why, and what you deliberately did not do. Anything you could not verify
should be named, not smoothed over — the whole point of this migration is that the site is more
trustworthy than the Word documents it replaces.
