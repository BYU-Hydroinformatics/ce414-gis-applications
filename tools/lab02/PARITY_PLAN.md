# Lab 2 draft: plan for bringing it to the level of the Lab 1 draft

**Written:** September 6, 2026, after reading `docs/assignments/lab-01/draft.md` end to end and
comparing it with `docs/assignments/lab-02/draft.md` as committed today.
**Purpose:** make the labs match in structure, depth of background, expectations of the student,
verification behind every number, and grading. This is a proposal; the items marked *decision*
are the instructor's call.

## Where the two drafts stand

| Element of the Lab 1 draft | Lab 2 draft today | Gap |
| --- | --- | --- |
| Header box: what changed, what was wrong, figure provenance, site behavior | Present | None |
| Background rewritten to set up the *analytical* question (how much does the answer depend on the assumptions) | Rewritten to say what NDVI does and does not measure | Small: the "your job is also to find where the method breaks" idea is there but the sensitivity idea is not |
| Spatial Considerations section: the criteria listed as explicit, questionable choices | No equivalent section | **Add** an *Analysis Considerations* section: threshold, scene date, cloud, water, sensor scaling, cell size |
| Data: workspace rules (D:, no spaces, tips page) | Present, condensed | None |
| Data: *why* sources must be judged, six metadata questions, tied to CCE 114, with two infographics (Figures A and B) | One paragraph, no graphic | **Add** the imagery version of the metadata questions, worked against the MTL file, with one infographic |
| Data: table of where each layer comes from | Package table only | Add a source table (extract we host, USGS download, live basemap, UGRC boundaries for the map) |
| Data: prepared extract with a READ-ME and the reasons it exists | Present | None |
| Data: a layer the student must *create and justify* (Walmart points, inclusion rule) | The second scene is the student's own; the threshold is the judgement | Make the parallel explicit: "your threshold is your inclusion rule" |
| Analysis Tools table with hand-drawn SVG icons | Present (3 icons) | The icon generator is not in `tools/lab02`; add it so they are reproducible |
| Example model as a **vector SVG** export, per-step snippets cut from it | PNG capture, per-step crops of the same capture | Export the model as SVG from ModelBuilder and re-cut the snippets |
| Step 0: project gotchas, add data, create model, **set environment + sanity number** | Project, statistics prompt, licensing, create model | **Add** raster environments (cell size, snap raster, extent, mask, output CRS) with a check value |
| Every step: WARNING for silent failures, TIP with an expected number, NOTE on pedagogy | Some (Float note, one TIP, threshold IMPORTANT) | **Add** expected numbers to Steps 1, 2 and 3 (measured today, below) |
| Step 10: parameters *repurposed* to expose the number the student will vary | Parameters expose inputs and output | **Expose the threshold** as a parameter (decision on how) |
| Step 12: sensitivity analysis replacing the second county, with a required table and three questions | Second scene retained; a threshold check is asked for in prose | **Add** a sensitivity step with a table; decide the fate of the second scene |
| Deliverables: itemized report contents, self-assessment, peer review | Shorter; self-assessment and peer review present | Itemize like Lab 1 |
| Two example maps (baseline + scenario) from the same run | One example map | Second map: a threshold scenario, or a second scene |
| Rubric re-split to fund the sensitivity row, total held at 50 | Unchanged points, one row amended | Re-split proposal below |
| `arcgis-tips.md` page carrying the cross-lab reminders | Linked once | Add a raster section to the tips page |
| Migration notes: verified numbers, alternatives rejected, **three pilot runs**, harness limits | Verified run, GUI facts, corrections | Pilot runs not done |

## Numbers measured today (Pro 3.7.1, the packaged extract)

These are the check values a Lab 2 at Lab 1's standard would publish, in the same "if you got X
you did Y wrong" style. All from the `NDVI` and `NDVI_reclass` rasters in `C:\Ames\Lab02\Lab02.gdb`.

| Quantity | Value |
| --- | --- |
| Cells with data | 6,040,284 (2,099 sq mi; the county polygon is 2,141 sq mi — the 42 sq mi difference is worth explaining, see open questions) |
| NDVI min / max / mean / median | −1.000 / 1.000 / 0.399 / 0.431 |
| Share of county below 0 (water, shadow) | 6.6 % |
| Above 0.2 / 0.3 / **0.4** / 0.5 / 0.6 / 0.7 | 1,651 / 1,327 / **1,111** / 917 / 722 / 496 sq mi (79 / 63 / **53** / 44 / 34 / 24 %) |
| Mean NDVI, 1 km circle: Elberta pivot cluster | 0.31 (fields up to 0.84, bare ground between them 0.09) |
| Mean NDVI, 1 km circle: Utah Lake open water | −0.99 |
| Mean NDVI, 1 km circle: Wasatch forest above Provo | 0.75 |
| Mean NDVI, 1 km circle: Cedar Valley benches | 0.24 (max 0.48) |
| Mean NDVI, 1 km circle: Provo downtown | 0.27 (max 0.83) |
| Whole model / Reclassify alone | 36 s / 5 s |

Two things these numbers say that the lab should say too:

1. **0.4 is the median.** The handout's threshold sits at the 53rd percentile of the county, so it
   splits the county in half rather than isolating cropland. Forest (0.75) is far above it; dry
   benches (0.24) and downtown (0.27) are below it; the pivot cluster straddles it. That is the
   whole sensitivity story in one table, and it is what the new step should make students find.
2. **Water reads −1.0, not −0.3.** The extract floored negative reflectances at zero, so over deep
   water NIR = 0 and the ratio is exactly −1. Real water NDVI is usually −0.1 to −0.5. The Data
   section should say this so nobody reports "NDVI of Utah Lake is −1" as a finding.

## The plan, in the order I would do it

### 1. Add a sensitivity step and expose the threshold (the biggest gap)

This is the change that made the Lab 1 draft a different lab, and Lab 2 has an even cleaner
version of it: there is exactly one number in the whole model that the student chose.

- **Step 6 (new): "How much depends on the threshold?"** Run the classification at least three
  more thresholds (say 0.3, 0.5, 0.6), record irrigated area and percentage in a table, and answer
  three questions in the Lab 1 pattern: which threshold best matches fields you can verify in the
  imagery; at what threshold does the forest drop out and what else drops with it; does any single
  threshold separate irrigated fields from forest at all (it does not — that is the finding).
- **Make it a dialog, not hand-editing.** Two ways, *decision*:
  - (a) Keep Reclassify for teaching and add a second branch: **Raster Calculator** with
    `Con("%NDVI%" >= %Threshold%, 1, 0)` where `Threshold` is a Double model variable marked as a
    parameter. This mirrors Lab 1's "expose the distance" exactly and adds one tool to the list.
  - (b) Replace Reclassify with that Con expression. Simpler model, but loses the Reclassify
    dialog, which is a tool students will need in Labs 5 and 6.
  I recommend (a). Either way the Step 4 tool interface then has a threshold box, which is a far
  better answer to "why bother with parameters" than exposing two rasters.
- **Publish the measured table above in the migration notes only** (as Lab 1 does), and put the
  pedagogy in a TIP that hints without giving it away.

### 2. Decide the fate of the second scene (*decision*)

Lab 1 dropped the second county because it repeated the data wrangling and not the analysis. The
same argument applies to a second Landsat scene, and more strongly: the download, the account, the
scale factor and the clipping are an hour of work that teaches nothing new about NDVI. Three
options:

- **Drop it** and let Step 6 carry the second map (a threshold scenario, as Lab 1's scenario map
  does). Cheapest; loses the "find a scene anywhere in the world" experience, which some students
  like.
- **Keep it but shrink it**: we host a *second* prepared extract (a different region and season, say
  a Snake River Plain or Central Valley scene in the same July) so the second run is a two-minute
  parameter dialog, and the lesson is that the threshold that works in Utah County may not work
  there. Keeps the second map, keeps the interface useful, removes the data wrangling.
- **Keep it as is.** Then the Data section's scale-factor warning has to become a full sub-step
  with a figure, because it is the step most students will get wrong silently.

I recommend the middle option. It also gives the rubric two maps that are genuinely different
analyses rather than the same analysis twice.

### 3. Data section to Lab 1 depth

- **Metadata questions for imagery.** A paragraph and an infographic that walks the six questions
  through the MTL file: *what* (bands, scale factor, units), *where* (path/row, UTM zone),
  *when* (acquisition date and time, why July), *how* (Collection 2 Level-2, atmospheric
  correction, cloud score), *who* (USGS), and the license (public domain, credit line). Have
  students open the MTL file and copy three values into their report — the same "read the
  metadata" move Lab 1 makes with the UGRC pages.
- **Source table** like Lab 1's: prepared extract (this site), USGS download (second scene),
  UGRC boundaries (for the map), Esri basemap (live service). The remote-sensing box in Lab 1's
  Figure B is now the one this lab uses; say so.
- **Explain the water value** (−1.0 is an artifact of flooring) and the 42 sq mi difference
  between the raster and the county polygon once it is understood.
- **Optionally a second infographic**: "what NDVI sees" — a three-panel graphic of the red/NIR
  response of vegetation, soil and water with the resulting NDVI ranges. Hand-authored SVG like
  Lab 1's, with the ranges given as textbook generalizations and labeled as such.

### 4. Step 0 environments, with a check value

Lab 1's Step 0 sets the output coordinate system and gives 2,141 sq mi as the number that proves
it. Lab 2's raster equivalent is the Environments tab: **Output Coordinate System**, **Cell Size**,
**Snap Raster**, **Extent** and **Mask** all matter for raster analysis and all default to
something. The check value is the cell count or the county area: 6,040,284 cells / 2,099 sq mi.
Today's run shows why it matters — the outputs came out in NAD 1983 UTM 12N while the inputs are
WGS 1984 UTM 12N, because the model ran under the map's coordinate system. Harmless here (a 1 m
shift), but it is exactly the kind of thing Lab 1 warns about, and a student who sets a snap
raster would not have had it happen.

### 5. Expected numbers in every step

- Step 1: the Float outputs have the same min/max as the inputs; if the Float output is missing,
  the NDVI layer will have only two or three distinct values.
- Step 2: NDVI −1 to +1, mean about 0.40; Utah Lake −1.0; 6.6 % of the county below zero.
- Step 3: 1,111 sq mi (53 %) above 0.4; the reclassified raster's attribute table gives the cell
  counts directly, which is how students should compute area.
- Step 4/6: the sensitivity table.

### 6. Figures

- Export the finished model from ModelBuilder as **SVG** (Export ▸ Export To Graphic) with nothing
  selected, and re-cut the per-step snippets from it at 3x as Lab 1 did, so Figure A is crisp at
  any zoom and the snippets are consistent. Today's PNG captures are fine for the dialogs; the
  model diagram is the one that benefits.
- A **second example map**: the threshold scenario (or the second prepared scene). Build it with
  `tools/lab02/build_layout.py`, which already takes the reclass raster and the text as inputs.
- Put the icon generator in `tools/lab02/` (Lab 1 has `make_svgs.py`) so the three Lab 2 icons and
  the new infographic(s) are reproducible.

### 7. Deliverables and rubric

Itemize the report as Lab 1 does: requirements and approach; one model capture; the toolbox
interface capture; the threshold table and the three questions; the three MTL values; where the
classification is wrong and why; the self-assessment. *Rubric proposal, holding the total at 50*
(**decision**): title/report 5, model description 5, model figure 5, **two maps 20 (10 each)**,
toolbox interface 5, **threshold sensitivity 10**. That is the same re-split Lab 1 made
(30 → 20 + 10).

### 8. Tips page

Add a raster section to `docs/arcgis-tips.md`: the Calculate Statistics prompt; integer vs.
floating-point rasters; raster environments and what each default silently does; NoData; the
Reclassify grid's editing behavior (typing adds a row, Delete removes one, the Classify button);
and the ModelBuilder tool-dialog OK button that ignores clicks until the dialog is moved, which
happened twice today.

### 9. Pilot runs

Lab 1's draft went through three agent pilots and each one found something. Lab 2 has had none.
Today's session showed that desktop control *is* available to the main session on this machine,
so a pilot can be run as a first-time student through the draft — ideally before item 1 lands, so
the pilot tests the lab as it will be assigned. Budget one pilot per revision.

## Open questions

- 2,099 vs 2,141 sq mi: is the 42 sq mi missing from the raster the lake (no — the lake has
  values), the county polygon's edge cells, or a difference between the UGRC polygon used for the
  clip and the one in `Lab01.gdb`? Answer it before publishing either number as a check.
- The extract floors negative reflectance at zero. Keep that (simple, and the −1 over water is
  visually striking) or leave the small negatives in (physically honest, NDVI over water then
  reads about −0.3)? If kept, say it in the READ-ME and the Data section.
- Whether the second scene is dropped, replaced by a second hosted extract, or kept (item 2).
- Whether the threshold is exposed with Raster Calculator alongside Reclassify or instead of it
  (item 1).

## Status, September 6, 2026 (evening)

Instructor decisions: the 42 sq mi raster/polygon difference is edge precision, not worth chasing;
the reflectance flooring stays. The other decisions were taken on the recommendations above and
are flagged as proposals in the draft.

| Item | State |
| --- | --- |
| 1 Sensitivity step + exposed threshold | **Done.** Raster Calculator `Con()` branch with a Double `Threshold` parameter alongside Reclassify; Steps 5 and 6 written; run at 0.6 from the dialog and captured. |
| 2 Second scene | **Dropped as a requirement** (instructor decision, September 6, evening). Round 2 had built the middle option (`docs/data/lab02-magic-valley-landsat.zip`, Step 7); round 3 removed Step 7 and made the second deliverable map a Step 6 threshold scenario, matching Lab 1. The Magic Valley extract stays as an optional *going further* alongside the own-scene USGS route; delete it if unwanted. |
| 3 Data section | **Done.** Figure A (MTL metadata infographic) and Figure B (measured red/NIR/NDVI at five sites), source table, water and area notes, Analysis Considerations section. |
| 4 Step 0 environments + check value | **Done.** Environments dialog captured; 6,040,284 cells / 2,099 sq mi. |
| 5 Expected numbers per step | **Done** for Steps 0, 1, 2, 3 and 6. |
| 6 Figures | **Mostly.** Model exported as SVG (Figure C); scenario map built; infographics scripted in `make_svgs.py`. Per-step snippets still PNG crops; icon generator not in the repo. (A Magic Valley example map is no longer needed.) |
| 7 Deliverables and rubric | **Done** as a proposal: 20 (two maps) + 10 (sensitivity), total 50. |
| 8 Tips page | **Done.** "Working with rasters" section on `docs/arcgis-tips.md`. |
| 9 Pilot runs | **One no-GUI pilot done** (September 6, evening): desktop control was not available to the session, so a fresh agent read the page as a first-time student and reproduced every published check value with arcpy against the hosted extracts (notes at `C:\Ames\Pilot02\PILOT_NOTES.md`). Every number matched; ten text findings were fixed before the draft was promoted. **Still owed:** a GUI pilot by a person on a lab machine, Steps 0 to 6. |

## Outcome, September 6, 2026 (night)

Both drafts were promoted to the assigned pages (`docs/assignments/lab-0N/README.md`), the tips page went into the nav, and the old Word-era pages and their leftover images were deleted. The instructor's rubric decision (10 write-up / 10 model / 10 map 1 / 10 map 2 / 10 sensitivity, plus up to 5 extra credit for the Magic Valley extract in Lab 2) replaced the 20 + 10 proposal above. The second scene is not required; the Magic Valley extract survives only as the extra-credit dataset.
