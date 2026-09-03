# Working in this repository

Read [`ROADMAP.md`](ROADMAP.md) before doing anything substantial. It has the migration order, the
known content problems, and the per-item definition of done. This file is the short version:
what we are doing, and the rules that are easy to get wrong.

## What we are trying to accomplish

CE 414's lab handouts are Word documents and its lectures are PowerPoints, distributed as
attachments through Learning Suite. That means students download files, versions drift, links rot
quietly, and nothing is reviewable or linkable.

We are moving all of it to a public course site:

- **Labs** → Markdown in `docs/assignments/lab-NN/`, rendered by MkDocs Material.
- **Lectures** → [Marp](https://marp.app/) web decks in `slides/week-NN/`.

Both rebuild and redeploy on every push to `main`. The goal is that a student gets a **URL**, the
material is diffable and reviewable, and a correction ships in one commit instead of by re-uploading
a file. This repository is the sibling of
[cce114-geomatics](https://github.com/BYU-Hydroinformatics/cce114-geomatics), which did the same
thing for the introductory course. Copy its patterns.

Migration is not transcription. Each converted lab is also *corrected*: field names, SQL
expressions, units, coordinate systems, data links and rubric totals get verified as they move.
A lab that was wrong in Word should not be wrong in Markdown.

## Hard rules

1. **CE 414 uses ArcGIS Pro. CCE 114 uses QGIS.** When you borrow anything from the sibling repo —
   especially `tools/slide-conversion-guide.md` — do not carry its ArcGIS→QGIS substitutions
   across. Here the direction is the opposite: replace *ArcGIS 9 / ArcMap / ArcCatalog / ArcToolbox*
   wording with current ArcGIS Pro equivalents (Catalog pane, Geoprocessing pane, `.atbx`
   toolboxes, the contextual ModelBuilder ribbon tab).
2. **Never fabricate a screenshot.** Captures come from a real ArcGIS Pro session. If a deck needs
   an image that does not exist yet, leave a `<!-- TODO -->` and say so in your report.
3. **Never invent a field name, coded value, SQL expression, or data figure.** If the source
   handout asserts something you cannot verify — the classic example is the UDOT `Carto` = 1,2,3,6
   expression in Lab 1 — do not "fix" it with a guess. Rewrite the step so the student derives it
   from the actual data, and flag it.
4. **Verify in ArcGIS Pro before asserting.** Tool names, parameters, and pane locations have moved
   between versions. If you have not seen it, write it as "verify this" rather than as fact.
5. **Do not reproduce copyrighted material** — song lyrics, long textbook passages — even when a
   source slide contains them. Keep the reference, describe it in a line.
6. **Preserve originals.** The Word and PowerPoint sources live outside this repo. If you edit them,
   archive the original first (see the `Old/` folders in the course directory).
6a. **`docs/lectures/` is generated.** `tools/build_lectures.py` rewrites every `docs/lectures/week-NN.md`,
   `docs/lectures/README.md`, and the Lectures section of `mkdocs.yml` from its `DECKS` table. Edit the
   table and re-run the script; hand edits to those files are overwritten (notes survive only below a
   `<!-- notes -->` marker in a week page).
7. **Never name an instructor when referring to another class session.** Instructors change between
   semesters. The title-slide byline is the one place names belong.
8. **American English throughout** — meters, kilometers, center, color, catalog, gray. Journal and
   product names keep their own spelling.
9. **Nearly every slide carries a graphic**, section-divider (`lead`) slides excepted. If a slide
   has none, generate one with the OpenAI image skill and save it in the deck's `images/` folder.
   Do not add decoration for its own sake.

Rules 7 to 9 are shared with the sibling repo and are recorded in
`tools/slide-conversion-guide.md`, which is the authority when writing or converting a deck.

## Where the source material lives

Not in this repo:

```
/Users/danames/ames-sync/Work/Teaching/CE 414 Engineering Applications of GIS/
├── Labs/                        Lab 1–10 .docx
├── Lectures/2026/               the 15 current .pptx decks
├── _screenshots_2026/           new ArcGIS Pro captures + README
├── recommended_plan.md          living course-improvement plan
└── SCREENSHOT_SHOT_LIST.md      image-by-image audit of every deck and lab
```

Those last two are worth reading in full before a large piece of work.

## How to build and check

```bash
pip install mkdocs-material mkdocs-github-admonitions-plugin
mkdocs build --strict          # must pass; --strict catches broken nav and links
mkdocs serve                   # local preview at :8000
```

A deck:

```bash
npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html \
  slides/week-NN/<slug>.md -o /tmp/check.html
```

`--no-stdin` matters — without it marp hangs. To render slides as images for visual QA, add
`--allow-local-files --images png`; without `--allow-local-files` every image is a broken icon.

**Always look at what you produced.** Render the page or the deck and read it before calling it
done. Most defects in this material are visual: an image that overflows, a caption orphaned from
its figure, a table that lost a column.

## Conventions

- One folder per lab: `docs/assignments/lab-NN/README.md` + `images/`. Nothing references an image
  outside its own folder.
- One folder per lecture week: `slides/week-NN/<slug>.md` + `images/`.
- GitHub-style admonitions (`> [!NOTE]`, `> [!WARNING]`) — the `gh-admonitions` plugin renders them.
- Schedule in **week numbers, not calendar dates**, so the site survives re-offering.
- Do not commit built output: `site/`, `_site/`, or deck `.html`.

## Git

Commit logically-grouped work with a message that says what changed and why. Do not push to `main`
without being asked — the push is what publishes to students. If you are a subagent converting a
single deck or lab, leave the work in the working tree and report; the maintainer commits.
