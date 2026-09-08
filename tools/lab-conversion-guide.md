# Lab conversion and authoring guide

How a CE 414 lab page is built, whether you are bringing one of the migrated Word-era labs
(Labs 3 to 10) up to the standard of Labs 1 and 2, or writing a new lab from nothing. This is the
lab counterpart of `tools/slide-conversion-guide.md`, and it is the authority when the two
disagree with an older page. Read `CLAUDE.md` and `ROADMAP.md` first; the hard rules there
(ArcGIS Pro not QGIS, no fabricated screenshots, no invented field names or figures, verify in
ArcGIS Pro before asserting, American English) are assumed throughout and not repeated.

**The reference pages are `docs/assignments/lab-01/README.md` and `docs/assignments/lab-02/README.md`.**
Read both end to end before touching a lab. Each has an HTML comment at the top (revision notes)
and one at the bottom (migration notes) that show what was checked, what was changed, and why.
`tools/lab02/PARITY_PLAN.md` is the worked example of comparing a weaker lab against a stronger one
and closing the gap; its first table is the template for the comparison you should write first.

## 1. What a lab is for

Every lab in this course has the same spine, and a revision that loses it has failed:

1. **One model, built once, built to be changed.** The student assembles a ModelBuilder model from
   named tools, gives its intermediate data readable names, and exposes the numbers they chose as
   model parameters so the model can be re-run from a tool dialog.
2. **Check values at every step.** Every step that produces something publishes the number a
   correct result has (a feature count, a cell count, an area, a value range) and the number a
   common mistake gives, in the form "if you got X you did Y wrong."
3. **A sensitivity step instead of "now do it again somewhere else."** The default result is *an*
   answer, not *the* answer. The student re-runs the model with the parameters changed, tabulates
   what moves, answers three fixed questions, and picks one scenario for a second map. In Lab 1 the
   lesson is that small changes narrow a recommendation; in Lab 2 it is that they reveal what a
   class actually contains. Repeating the analysis in another county or scene is not required and
   should not be; it repeats the data wrangling, not the analysis.
4. **Where the method breaks.** The student must say in the report where the result is wrong and
   why, and what data would fix it. Two students with different defensible answers can both be right.
5. **Deliverables the rubric grades, and nothing else.** Two maps (baseline and one scenario), a
   report of stated contents, a self-assessment against the pasted rubric, and a named peer reviewer.

Do not add a second study area, a second county, a second scene, or an ungraded "for extra
practice" section. An optional extra with hosted data and its own rubric row, worth at most five
points, is the only sanctioned extension (Lab 2's Magic Valley extract is the model).

## 2. Page anatomy

Headings, in this order, with these exact forms. Section names in Labs 1 and 2 differ where the
subject demands it (Lab 1 has *Spatial Considerations*, Lab 2 *Analysis Considerations*); keep
the role, adapt the noun.

```
# Lab N: Short Title
**Civil Engineering 414 — Engineering Applications of GIS**
Fall 2026 · Dr. Dan Ames
*Optional italic subtitle from the original handout*
<!-- Revision notes ... -->                      instructor-facing, see section 8
## Background
## Problem Statement
## Spatial Considerations  |  Analysis Considerations
## Data
### The <area> extract (prepared for you)       one subsection per data source that needs one
### Going further: ... (optional)                only if there is a sanctioned optional extra
## Analysis Tools  |  ModelBuilder Tools
## Example Model
## Complete the Lab
## Step-by-Step Solution
### Step 0 — Set Up the Project
### Step 1 — Two or Three Word Title
...
### Step N — Test the Assumptions | Test the Threshold      the sensitivity step, always last
## Deliverables
## References
## Example Maps
## Rubric for <Lab Title>
<!-- Migration notes ... -->                     instructor-facing, see section 8
```

### Background and Problem Statement

Keep the original handout's voice and domain content; correct what is wrong (Lab 2's Landsat
history stopped at Landsat 7 and cited a defunct archive) and drop what is dead. Add one paragraph
that names the analytical question the lab is really about: what the method measures and does not
measure, and that the student's job includes finding out how much the answer depends on their
choices. Both reference labs end the Background with a sentence of the form "In Step N you will
vary it, see how far the answer moves, and use what moves to ..." — write that sentence.

End the section with the `> [!IMPORTANT]` box headed **Your job — see the deliverables below**,
one or two sentences: build one model, run it on the study area, test the parameters, make the
two maps.

### Spatial / Analysis Considerations

A bulleted list of every choice that shapes the answer, each stated as a decision somebody made:
the thresholds and distances with their default values and where those defaults came from, the
data vintage or scene date, the coordinate system and cell size, anything that a default in
ArcGIS Pro will silently decide. Every item here should reappear as a check value in a step or as
a row in the sensitivity table.

### Data

Open with the workspace box (`> [!IMPORTANT]`, **Set up your folder before you download anything**):
D: drive, one folder per student and per lab, no spaces in names, why C: and network drives are out,
USB 3.0 as the alternative, and a link to `docs/arcgis-tips.md`. Copy it from Lab 1 and shorten
it as Lab 2 did; do not rewrite it.

Then, in this order:

- **Why sources must be judged.** The six metadata questions (what, where, when, why, how, who),
  tied to the CCE 114 metadata lecture, applied to this lab's data. Lab 1 does it for vector
  downloads with two infographics; Lab 2 does it for imagery through the scene's MTL file with one.
  Have the student copy two or three metadata values into their report and grade them.
- **A source table**: one row per layer, saying whether it is a prepared extract we host, an
  official agency download, a live web service, or something the student creates. Vary the ways
  deliberately and say so.
- **One subsection per prepared extract.** Host it in `docs/data/` as a zip under about 30 MB, with
  a `READ-ME-FIRST.txt` inside that gives provenance, processing, vintage, license and a credit
  line. The page lists the files in the zip in a table, states what was done to them, and gives
  the check values a student sees on loading (value ranges, feature counts, coordinate system).
  Anything the processing did that will show up in results (Lab 2's water at exactly −1.0, the
  clipped boundary cells) is stated here so nobody reports it as a finding.
- **A layer the student must create and justify**, where the subject allows one (Lab 1's Walmart
  points, with an inclusion rule they defend). Where it does not, the parameter they choose plays
  that role; say so.
- **Going further (optional)** only for the sanctioned extra. It says plainly that nothing in the
  lab requires it, gives the hosted data and its check values, and points at the rubric's
  extra-credit row.

Every external link on the page is checked when the page is touched (curl the status; open in a
browser any site that blocks scripts, such as usgs.gov). Dead links are replaced or removed, never
left. UGRC links point at the `/explore` pages, where the Download button works.

### Analysis Tools / ModelBuilder Tools

A two-column table: an SVG icon plus the tool name in bold, and one or two sentences on what the
tool does to the data (with a textbook page reference where the original had one). Icons are
hand-authored SVG generated by the lab's `make_svgs.py` (`tools/lab01/make_svgs.py` has six,
`tools/lab02/make_svgs.py` three, same palette); add new icons there, never as loose files. Every
tool the steps use for the first time in this lab gets a row; tools from earlier labs do not.

### Example Model

The finished model exported from ModelBuilder as **SVG** (Export ▸ Export To Graphic, with nothing
selected so there are no selection strokes), captioned **Figure C** with "click it to open it full
size." Every intermediate dataset in it has been renamed to something a reader can follow. Say
that everything marked `P` appears in the tool dialog the student builds later.

### Complete the Lab

The unchanged paragraph inviting advanced students to attempt the lab from the information above,
and a `> [!TIP]` asking them to say so in the report. No extra credit is promised here; the rubric
has no row for it.

### Step-by-Step Solution

Two `> [!NOTE]` boxes first. **Important Note #1** says the steps walk through the study area at
the default parameters and that Step N re-runs the same model, so build it once and build it to be
changed. **Important Note #2** says the screenshots were captured in a stated ArcGIS Pro version
against the data students download, may not match exactly, and (if true) that paths in the
figures start with `C:\` because they were captured on an instructor machine.

Then the steps. Every step heading is `### Step N — Two or Three Word Title`. Step 0 is always
project set-up: create the project (the *Location* box does not take a typed path), add the data,
the prompts ArcGIS Pro shows on the way (the statistics prompt for rasters), the license check if
an extension is needed, create and rename the model, and **the environments that decide what the
outputs come out as**, with a check value that proves they are right (Lab 1: the county's area in
the output coordinate system; Lab 2: the cell count).

Within a step, the pattern is: what to do, in the imperative, naming ribbon tabs, panes and
buttons in bold as ArcGIS Pro labels them; the tool dialog figure and the ModelBuilder snippet
figure; then the boxes:

- `> [!WARNING]` for a silent failure: a default that gives a wrong answer without an error
  (buffer units in meters, a field typed Long instead of Double, a dialog left open when Run is
  clicked, running from the tool dialog deleting intermediate data).
- `> [!TIP]` **Check the result** with the expected number, and what the common wrong numbers mean.
- `> [!NOTE]` for the pedagogy: why Float first, why two classification branches, why the
  Intersect returns more features than the input.

Text comparisons, SQL, field names and coded values are given exactly as the data has them, in
code spans, and only after they have been verified against the downloaded data. If the original
handout asserts a value you cannot verify, rewrite the step so the student derives it from the
data and flag it in the migration notes.

The **parameters step** exposes the numbers the student will vary, not the inputs and outputs for
their own sake. The reason to bother with parameters is that they make the run the student is
about to repeat cheap; say that. Where the number lives inside a tool table that cannot be a
parameter (Lab 2's Reclassify), add a branch that can (a Raster Calculator with an inline
variable) and keep both, explaining why.

The **sensitivity step** is last and has a fixed shape: an opening paragraph on why the default
map is an answer and not the answer; "run the model at least three more times" from the tool
dialog, with suggested values and an instruction to choose deliberately; what to record for each
run (parameter values, count, area) in a required table; three numbered questions in bold; the
instruction to pick one run for the second map and to say on that map what changed and why; and a
`> [!TIP]` that hints at the finding without giving it away ("one of these criteria does almost
nothing at its default", "the forest never drops out before the fields do"). Make sure the
suggested values let the student actually observe what the TIP describes: the Lab 2 pilot found
the one-third crossing sat above every suggested threshold. Where two outputs exist and only one
responds to the parameter, say which one to count.

### Deliverables

"Make **two** professional map layouts:" numbered 1 (baseline, with what must be on it) and 2 (one
scenario, "whichever of your runs most changes the picture", stating on the map what changed and
why). Then "Write a brief report (2–3 pages of text, plus your figures and maps) covering:" as a
bulleted list that names **every item the rubric grades**: title block and peer reviewer,
requirements and approach, the model description a reader could repeat from, one full-page model
figure exported from ModelBuilder and one capture of the toolbox interface, the metadata values,
the sensitivity table and its three answers, where the result is wrong and why, the pasted rubric
with a self-assessment, and the optional extra if there is one. End with the `> [!IMPORTANT]`
peer-review box copied from the reference labs.

### References, Example Maps, Rubric

References as in the original, corrected where checkable and flagged with `<!-- VERIFY -->` where
not. Example Maps: two layouts built as real ArcGIS Pro layouts against this run's results (Lab 1's
`tools/lab01/build_layouts.py` and Lab 2's `tools/lab02/build_layout.py` do it with `arcpy.mp`),
one at the defaults and one scenario, each captioned with what a student should do better than
the example. Say explicitly that they are examples, not templates, and that the student's name
must be on their maps.

The rubric is **five parts of ten**, in this order, each row itemized with the value of every
bullet in parentheses so that the bullets sum to ten:

| Row | What it grades |
| --- | --- |
| Write-up | title block and peer reviewer (1); requirements and approach (2); the lab's judgment items — recommendation and justification, metadata values, where the method is wrong (5 to 6 in total); organized writing with figures numbered, sources credited, rubric pasted with self-assessment (1 to 2) |
| ModelBuilder model — correct and working | runs end to end from its dialog and matches the check values **at the default parameters** (4); full-page model figure (2); toolbox interface capture with the parameters exposed (2); description a reader could repeat from (2) |
| Map 1 — your baseline | title with the parameter values (1); neat line, north arrow, scale bar (1); text box with author, date, projection and data (1); the result layer clearly symbolized with a legend (2); boundary and labeled places (1); inset or close-ups (2); basemap, scale and legibility (2) |
| Map 2 — one scenario | the same, minus the inset, plus: title and text box say what changed and why this run was chosen (2) |
| Sensitivity | the table (4); each of the three questions (2) |

Then `| **Total** | **/50** |`, and after it the optional `| **Extra credit — ...** | up to +5 |`
row, itemized the same way. Open the section with the sentence "Fifty points in five parts of ten
... The bullets say what each part is worth, so you know exactly what to submit." A script
should confirm the sums before the page is promoted (see section 7).

## 3. Writing rules

These are the ones this course has needed; the general rules are in `CLAUDE.md`.

- **"ArcGIS Pro" in full**, every time, in anything a student reads. Grep for a bare "Pro" before
  promoting.
- **Never refer to earlier versions of the handout** in student text: not "the old lab said", not
  "unlike previous years", not "this step replaced". Students cannot see the old files. That
  history goes in the HTML comments.
- **Step headings carry a two- or three-word title.** Figures within a step are numbered by the
  step (`Figure 6a`, `Figure 6b`) only when a step has more than one figure at the same point;
  otherwise `Figure 6`. Do not cite a lettered figure that has no lettered caption.
- **Infographics and the model diagram are lettered** (Figure A, B, C) and lettered in the order
  they appear on the page; step figures are numbered from Figure 0a.
- **Every figure has real alt text** describing what is in it (the dialog title, the field values,
  what the map shows), and a bold caption `**Figure N.**` on its own line. Alt text and caption
  must agree with the figure, including the parts that are inconvenient (the Lab 2 environments
  dialog shows a setting the text says to leave empty; the caption now says so).
- **Numbers are consistent everywhere they appear**: header notes, considerations, data section,
  step TIPs, deliverables, rubric, references, example-map text boxes, migration notes. When a
  number is a mean over an area and another is a cell value, say which is which.
- **Say what a check value applies to.** "Every classified raster has 6,040,284 cells" is true;
  "every raster" was not.
- **Admonitions are GitHub-style** (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`) and
  used for what they are named; a TIP with an expected number, a WARNING for a silent failure.
- **External links open in a new tab**: `{ target="_blank" }` after the link.
- **Images live in the lab's own `images/` folder** with descriptive names prefixed by the lab
  (`lab02-reclassify-tool-dialog.png`); PNG for anything with text, JPEG for map captures, SVG for
  diagrams and icons. Nothing on a page references an image outside its folder.
- **Units and spelling**: miles and square miles for the results students report (with the
  conversion given once), meters where ArcGIS Pro shows meters; American English.

## 4. Data and verification

A lab is only as good as the numbers it publishes. Before the page asserts anything:

1. **Run the whole lab in ArcGIS Pro** (currently 3.7.1) on the data students will download, in a
   project named for the lab under `C:\Ames\LabNN\` on the instructor machine, and record the Pro
   version in the migration notes. Every tool name, pane, button and dialog in the steps comes from
   that run. Where you have not seen it, write "verify this" rather than a fact.
2. **Measure every check value** from that run and from arcpy where a number needs a script (the
   sensitivity table, means over sample areas). Keep the measurement script or snippet in
   `tools/labNN/` (Lab 2's `samples.json` and the sampling snippet recorded in its plan).
3. **Publish the baseline numbers to students; keep the sensitivity table in the migration notes.**
   Students find the sensitivity result themselves; the TIP hints at it.
4. **Prepared extracts** are built by a script in `tools/labNN/` (Lab 2's
   `fetch_second_scene.py` and `make_second_extract.py`) so they can be rebuilt, documented in the
   zip's `READ-ME-FIRST.txt`, and their size stated on the page as measured, not remembered.
5. **Every link checked** (section 2, Data).

## 5. Figures

- **Every capture comes from a real ArcGIS Pro session** against the lab's data. The capture
  tooling and its gotchas are in `tools/screenshots/README.md`; read it, it changes.
- **The model diagram is an SVG export**, and the per-step ModelBuilder snippets are **cut from that
  same export**, not screen-captured, so dialogs, snippets and overview come from one run.
  `tools/lab02/cut_model_snippets.py` renders the SVG at 3x with headless Chrome and crops by
  label position; copy it for a new lab. Snippets for early steps must not show things that do
  not exist yet at that step (parameter `P` markers, variables added later); strip or mask them,
  as the script does, and say so in the migration notes.
- **Icons and infographics are hand-authored SVG with real text**, generated by the lab's
  `make_svgs.py`. Image models do not render labels; do not use them for anything with words.
  Infographic numbers are measured (Lab 2's Figure A reads `samples.json`), never illustrative.
- **Example maps are real layouts** built with `arcpy.mp` and exported by ArcGIS Pro at 150 dpi.
  `tools/lab01/README.md` records the legend and frame settings that work.
- **Look at every figure you produce** at the size it renders. Most defects are visual.

## 6. Piloting

No lab is promoted without a pilot, and the pilot tests the page as it will be assigned, so it
runs after the sensitivity step and the rubric are in place.

**The no-GUI pilot** is always possible: one fresh agent reads the page start to finish as a
first-time student and logs every confusion, forward reference, figure/caption mismatch,
number that disagrees between sections, deliverables-versus-rubric gap and leftover mention of
things the page no longer asks for; and it reproduces every published check value with the
ArcGIS Pro Python (`arcgispro-py3`; Spatial Analyst checks out headless) against the hosted data,
working in `C:\Ames\PilotNN\`. Give it the brief in `tools/lab02/PARITY_PLAN.md`'s pilot item and
have it write `PILOT_NOTES.md` with a ranked findings list and a stated/measured/match table. The
Lab 2 pilot took twelve minutes and found ten real defects.

**The GUI pilot** — a person, or an agent with desktop control, driving Steps 0 to N on a lab
machine — is still owed for each lab and is recorded as owed in the migration notes until done.
Subagents do not get desktop control; only the main session can, and only if the user grants it.

Fix what the pilot finds in the draft, record the findings and fixes in the migration notes, and
then promote.

## 7. Workflow: revise, review, promote

1. **Compare first.** For an existing lab, write `tools/labNN/PARITY_PLAN.md`: a table of every
   element of the reference labs against what this lab has, the gap, and the plan in the order you
   would do it, with the instructor's decisions marked. Measure the check values in the same
   document. Wait for the decisions before building the parts that depend on them.
2. **Draft beside the assigned page.** Write `docs/assignments/lab-NN/draft.md` with front matter
   `search: exclude: true`, the title prefixed `DRAFT — `, and a `> [!WARNING]` box after the byline
   headed **This is a draft for review** that lists *changes to what the lab asks students to do*,
   *corrections to things that were wrong*, the figure provenance, and site behavior. The draft
   is not in the nav; `mkdocs build --strict` reports it as unlinked, which is expected. Commit the
   draft in rounds with messages that say what changed and why.
3. **Pilot** (section 6) and fix.
4. **Promote.** Strip the front matter and the `DRAFT — ` prefix; turn the review box into the
   `<!-- Revision notes -->` comment (it is the changelog; students do not need it); replace
   `README.md` with the draft and `git rm` the draft; delete the images only the old page used and
   note the deletions in the migration notes; make sure nothing student-visible references a
   deleted image or the draft; add any new site page to `mkdocs.yml`; update `ROADMAP.md`.
   Then confirm: rubric rows sum to ten and the total to fifty; no bare "Pro"; no "old version"
   language; every link live; `mkdocs build --strict` passes with no unlinked-page notice for the
   lab; and the rendered page read in a browser (`preview_start` with the `mkdocs-pro` launch
   configuration; the site is served under `/ce414-gis-applications/`).
5. **Commit; do not push.** The push publishes to students and is the maintainer's call. A
   subagent leaves its work in the tree and reports.

## 8. The two comments

**Revision notes** (top of the page, after the byline): what changed for students, what was
corrected, figure provenance, site behavior. Written for the next person who revises the lab.

**Migration notes** (bottom of the page, after the rubric), one paragraph per topic on single
lines so they diff cleanly: the source file and date; the ArcGIS Pro version verified against and
how (GUI, arcpy); DATA PACKAGES with build scripts, sizes and processing; VERIFIED NUMBERS;
SENSITIVITY numbers measured "for setting expectations; do NOT publish"; CORRECTIONS carried
from earlier rounds; GUI FACTS learned; PILOT results; and a numbered `TODO(instructor)` list of
everything that needs the instructor's decision or a person at a lab machine. Inline
`<!-- VERIFY -->` and `<!-- TODO(instructor) -->` comments stay next to the sentence they concern.

## 9. Building a new lab from nothing

Same anatomy, same spine, and the order of work is:

1. Decide the analytical question and the one number (or two) the student will choose. If there
   is no such number, the lab has no sensitivity step and needs redesigning until it does.
2. Build the model in ArcGIS Pro on the real data; name every dataset; expose the parameters;
   export the SVG; measure the check values and the sensitivity table.
3. Prepare and host the data extract with its READ-ME; write the source table and the metadata
   questions for this data type.
4. Write the page top to bottom in the section order of section 2, boxes and check values in
   every step, capturing figures as you go.
5. Build the two example maps with `arcpy.mp`; write the rubric and make the Deliverables list
   match it item for item.
6. Pilot, promote, commit, report.

A skeleton with every heading and box in place is the quickest start: copy
`docs/assignments/lab-02/README.md`, delete the content under each heading, and keep the boxes.

## 10. Definition of done

The per-lab list in `ROADMAP.md`, plus what Labs 1 and 2 added:

- [ ] Headings in the section 2 order; every step titled; Step 0 sets up project and environments with a check value
- [ ] One model, parameters exposed, sensitivity step last with table, three questions and a scenario map
- [ ] No required second study area; any optional extra has hosted data, check values and a rubric row of at most five points
- [ ] Check value with a failure interpretation in every step that produces something
- [ ] Data section: workspace box, metadata questions, source table, prepared extract with READ-ME and stated processing effects
- [ ] Tool table with generated SVG icons; model as SVG; snippets cut from it; example maps built as real layouts
- [ ] Deliverables list and rubric name the same items; rubric five rows of ten with per-bullet values, total fifty
- [ ] No bare "Pro", no reference to earlier handout versions, every link checked, figures lettered and numbered in page order with agreeing alt text and captions
- [ ] Every number verified in ArcGIS Pro or arcpy, recorded in the migration notes with the version
- [ ] Piloted (no-GUI at minimum), findings fixed and recorded; GUI pilot recorded as done or owed
- [ ] Strict build passes; rendered page read end to end in a browser before promotion
