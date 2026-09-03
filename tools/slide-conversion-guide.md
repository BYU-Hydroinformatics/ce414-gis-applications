# Converting a CE 414 PowerPoint into a Marp web slide deck

This is the recipe inherited from the CCE 114 course site. Follow it exactly so every deck looks
and behaves the same. Once the first CE 414 deck is converted, read it first as the reference for
structure, tone, and formatting; until then use CCE 114's `slides/day-02/gis-data-models.md`.

## Where things go

- Deck: `slides/week-NN/<slug>.md` (Marp markdown). One deck per file; a day may have two.
- Images: `slides/day-NN/images/<prefix>-<descriptive-name>.<ext>`, where `<prefix>` is a short
  tag for the deck (Day 1 used `ci-` and `gis-`, Day 2 used `dm-`). Every image the deck uses
  lives here; nothing is referenced from outside the folder.
- The site builds each `slides/*/*.md` with marp-cli on every push and publishes it at
  `https://byu-hydroinformatics.github.io/ce414-geomatics/slides/day-NN/<slug>.html`.
- Do **not** commit the local `.html` build, and do not edit anything outside your
  `slides/day-NN/` folder. The lecture-day pages under `docs/lectures/` are generated from
  `tools/build_schedule.py`; report your deck title and URL and the maintainer adds it there.
- Do **not** run `git commit` or `git push`. Leave the work in the working tree.

## Step 1: extract the source deck

```bash
python3 tools/pptx_extract.py "/path/to/deck.pptx" /path/to/scratch/dayNN
```

That writes `text.md` (all slide text, speaker notes, media names, hidden flags), `media/`
(every image), `deck.pdf`, low-res page renders, and labeled contact sheets `sheet-N.jpg`.
Read `text.md` in full, then look at every contact sheet with the Read tool so you know what each
slide looks like. Hidden slides are omitted from the PDF, so page numbers skip them; `text.md`
gives both the slide number and the PDF page.

If a slide is built from PowerPoint shapes (a diagram, a table drawn over an image, annotated
callouts), do not rebuild it: render that PDF page at 200 dpi (written as `hires-NN-N.png`) and use the render as the slide's
image:

```bash
python3 tools/pptx_extract.py "/path/to/deck.pptx" /path/to/scratch/dayNN --hires 12 15 16
```

## Step 2: plan the deck

Write the deck as a **Tuesday concepts lecture** (or, when told, a Thursday hands-on session)
for the CE 414 rhythm: Dr. Ames teaches all sessions, and most weeks pair a concepts lecture with
the lab that applies it. Keep the source deck's content, order, and voice; tighten wording where
the original was rough.

Three standing rules (set 2026-09-03) apply to every deck:

1. **Never name a professor when pointing to the other class day.** Instructors change between
   semesters. Write "Thursday, we will do exactly this with the points you collect" or "on Tuesday
   we saw...", never "Thursday with Dr. X." The title-slide byline is the one place names belong.
2. **American English**: meters, kilometers, center, color, catalog, gray. Not metres, centre,
   colour. Journal and product names keep their own spelling.
3. **Nearly every slide carries a graphic.** Section-divider (`lead`) slides are the exception. If
   a slide has none, generate one with the OpenAI image skill (gpt-image-1, a shared style suffix
   across the deck, no text in the image) and save it in the deck's `images/` folder. Quiz and
   table slides get a supporting illustration; do not add decoration for its own sake.

Specifically:

- Start with a title slide (class `lead`, background image on the right) and a **Today's Goals**
  slide: "By the end of class you should be able to:" plus 3 to 5 outcomes.
- End with a **Before Next Class** slide: the textbook reading, the open-book quiz on Learning
  Suite, the current lab (link to the assignments page), and office hours
  (`https://calendly.com/dan-ames/office-hours`). Where a concept deck leads into a Thursday
  session, add a short preview slide naming the lab and what the deck gives them for it.
- Keep every speaker note from the source as an HTML comment at the bottom of its slide
  (`<!-- ... -->`). Marp shows these in presenter view. Add a note where a slide would otherwise
  be a bare image so the presenter knows what to say.
- Mark question slides with `<!-- _class: quiz -->` and in-class activities with
  `<!-- _class: activity -->`. Multiple-choice options use `<ol type="A">`.
- Section-break slides use `<!-- _class: lead -->`.
- **Software wording:** CE 414 uses **ArcGIS Pro**, not QGIS — the opposite of CCE 114, so do not
  copy that course's software substitutions. What must change here is *version* language: replace
  ArcGIS 9 / ArcMap / ArcCatalog / ArcToolbox wording with current ArcGIS Pro equivalents (Catalog
  pane, Geoprocessing pane, `.atbx` toolboxes, the contextual ModelBuilder ribbon tab). Leave
  concepts alone. If a slide shows an ArcMap-era screenshot, keep it for now and flag it (see
  Step 5); **never fabricate an ArcGIS Pro screenshot**.
- Drop hidden slides unless they are obviously useful backups (Day 2 kept demo backups).
- Video slides become a thumbnail image wrapped in `<a href="..." target="_blank">` plus the URL
  underneath in small text.
- **Never reproduce song lyrics** or long copyrighted passages, even if the source slide has
  them. Keep the image and link, describe in one line.
- Don't invent facts. If the source has a placeholder or an unreadable slide, leave a
  `<!-- TODO: ... -->` comment and mention it in your report.

## Step 3: images

- Copy images from `media/` into `slides/day-NN/images/` with descriptive names and the deck
  prefix. Skip images only used by dropped slides.
- Downscale anything wider than 2000 px (Pillow is available). Keep the folder under about
  15 MB. Convert huge PNG photos to JPEG.
- Image directives that work with the theme (see the Day 1 and Day 2 decks):
  - `![h:470 center](images/x.png)` for a single large figure under a title
  - `![bg right:40% w:90%](images/x.png)` for a side image next to bullets
  - `![bg contain](images/x.png)` for a full-slide figure (no title needed)
  - `<div class="columns">…</div>` for two columns; `<div class="imggrid">` for a photo grid
- Alt text in the markdown is not shown; put meaning in speaker notes instead.

## Step 4: front matter and theme

```markdown
---
marp: true
theme: ce414
paginate: true
footer: "CE 414 · Day NN — <Deck Title>"
---
```

The theme is `slides/theme/ce414.css` (BYU navy, `lead`/`quiz`/`activity` classes, `columns`,
`imggrid`). Do not edit the theme. Inline `style` attributes are fine for one-off layout.

## Step 5: build and check (required)

```bash
npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html \
  slides/day-NN/<slug>.md -o /path/to/scratch/dayNN/check.html

npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html \
  --allow-local-files --images png --image-scale 0.5 \
  slides/day-NN/<slug>.md -o /path/to/scratch/dayNN/qa/s.png
```

`--no-stdin` matters: without it marp hangs waiting on stdin. `--allow-local-files` matters:
without it every image renders as a broken icon. In zsh, an `rm` on a glob that matches nothing
aborts the whole `&&` chain, so don't chain `rm` before the build.

Then build contact sheets of the PNGs (same Pillow loop as `tools/pptx_extract.py`) and **look
at every one**. Fix anything that overflows the slide, any image that is too small to read, any
duplicated visual, any missing image. Re-render and re-check until clean. Delete the check
`.html` if you built it inside the repo.

Finally, add one HTML comment at the very end of the deck:

```markdown
<!-- Conversion notes (YYYY-MM-DD): source deck; slides dropped; ArcGIS screenshots that need a
QGIS re-shoot: ...; anything else the instructor should look at. -->
```

## Report back

Your final message should give: the deck path and title, the published URL, slide count, which
source slides were dropped and why, every ArcGIS screenshot or TODO flagged, and the folder size.
