# Labs 9–11: plan to bring them to the Lab 4–8 standard

**Status (October 6, 2026):** the instructor accepted every recommendation below. The MkDocs
comment-stripping hook (section 7, quick fix) is in `hooks/strip_comments.py`. Lab 9 follows the
instructor's original intent, recorded in section 4.

Written October 5, 2026. The authority for what "done" means is `tools/lab-conversion-guide.md`
(section 10) and `tools/lab-report-template-guide.md`; this file is the order of work, the design
decisions each lab needs from the instructor, and a strategy for making sure students learn the
material rather than outsource it.

## 1. Where things stand

| Lab | Topic | State | Gap to the standard |
| --- | --- | --- | --- |
| 1–8 | — | Promoted, arcpy-verified, piloted, report templates | Lab 1 captures are still 100 % scaling; Lab 5 Step 14 pop-up capture owed; Labs 6–8 Learning Suite due dates |
| 9 | Interpolation (Y Mountain) | Sept 3 Word migration, 178 lines, 7 TODO/VERIFY | Everything: no data source, no check values, 7 surfaces + 7 difference rasters, second DEM instead of a sensitivity step, RMSE sentence wrong, stale Figure 2, rubric not 5×10, no icons/Figure C/example maps/template. **Overlaps Lab 8**, which already uses IDW and compares it with Spline |
| 10 | Wind farm suitability (South Dakota) | Sept 3 migration, 537 lines, 20 TODOs | Study area contradicts itself (SE counties vs "western SD"); river buffer 1 mi vs 2 mi in four places; exclusions mixed with preferences; 0/1 factors with raw weights 7/6/4/3/2; no CRS or raster environments; "do it again for your own counties"; a dead wind data link; old captures |
| 11 | Least-cost power line (Utah County) | Sept 3 migration, 362 lines, 14 TODOs | Uses deprecated **Cost Distance / Cost Path** (ROADMAP "Known problems"); barriers vs costs undefined; "lower elevation is cheaper" is not defensible; no CRS/environments; gis.utah.gov links redirect; a reference 404s; sensitivity only asked as prose |

## 2. Calendar

Lab N is introduced the week it is assigned and due Saturday of Week N+1.

| Lab | Introduced | Due | Ready (promoted, GUI-built, template) by |
| --- | --- | --- | --- |
| 9 | Tue Oct 27 (Week 9) | Sat Nov 7 | **Tue Oct 20** |
| 10 | Tue Nov 3 (Week 10) | Sat Nov 14 | **Tue Oct 27** |
| 11 | Tue Nov 10 (Week 11) | Sat Nov 21 | **Tue Nov 3** |

Week 8 is Midterm 1 (Oct 20–22), so Lab 9 should be finished **before** it. Each of Labs 4–8 took
about two working sessions: one for the parity plan, arcpy run, data, draft and pilot, and one for
the GUI build, captures, template and deck alignment.

Proposed order: Lab 9 parity plan this week (Oct 6–7), draft and pilot Oct 8–9, GUI build Oct 12–13;
Lab 10 Oct 13–17; Lab 11 Oct 20–24 (alongside the Week 11 deck fix-up).

## 3. The pipeline every lab goes through

This is the sequence Labs 4–8 proved. Nothing here is new; it is listed so each lab has a checklist.

1. **`tools/labNN/PARITY_PLAN.md`**: compare against the reference labs, record the gaps, and list
   decisions for the instructor. **Stop and wait for the decisions.**
2. **arcpy reference run** (`tools/labNN/run_model.py`, `C:\Ames\LabNN\`): the default run, then every
   sensitivity run, and `check_values.json` and `step_checks.json` measured, never estimated.
3. **Data package** (`tools/labNN/fetch_*.py`, `make_extract.py`): a hosted zip under about 30 MB in
   `docs/data/` with `READ-ME-FIRST.txt`; at least one live source (service or agency download)
   so the metadata questions have something to bite on.
4. **Draft** `docs/assignments/lab-NN/draft.md` in the section-2 anatomy: Step 0 with environments and
   a check value, a check value with a failure explanation in every step, the sensitivity step last,
   and a rubric of five rows worth ten points each.
5. **Icons** (`make_svgs.py`), Figure A/B infographics with measured numbers.
6. **No-GUI pilot** by a subagent in `C:\Ames\PilotNN\`: read the page as a student and reproduce every
   check value; it writes `PILOT_NOTES.md`. Fix what it finds.
7. **Decisions accepted → promote** (old page to `lab-NN-backup/`, strict build, browser read).
8. **GUI build** with desktop control at 175 % scaling (`C:\Ames\LabNNGUI\LabNN.aprx`): drive every
   step, capture every dialog, export the model SVG as Figure C, cut the snippets
   (`cut_model_snippets.py`), correct the page wherever the GUI disagrees with arcpy (it has every
   time: Bilinear default, Reclassify dropping −1 rows, dialog runs deleting outputs, ERROR 002869).
9. **Example maps** built with `arcpy.mp` (`build_figures.py`), one baseline and one scenario.
10. **Report template**: add a `LABS['NN']` entry to `tools/templates/make_lab_report_template.js` and
    build `labNN-report-template.docx`.
11. **Align the week's deck** with the lab (tool names, data, check values that may be shown in class).
12. **Learning Suite**: due date, and a link to the page and the template. Then commit, and push on approval.

## 4. Lab 9: Interpolation Explorer

**Intent (instructor, Oct 6).** Lab 8 uses interpolation only as a means to an end: rebuilding the
plain beneath Big Southern Butte. Lab 9 is where students *explore* interpolation. They sample a known
surface, rebuild it with several methods and parameter settings, compare each rebuild to the truth, and
learn how each method behaves. The source is `Lab 8 - Practicing with Interpolation.docx` (copy in
Downloads, Oct 6), and the current page is a faithful migration of it. The revision keeps that design
and gives it the course spine.

- **Data.** A Y Mountain 1/3 arc-second DEM. Step 0 brings it in from the USGS 3DEP image service and
  asks "what came back?" (the Week 9 tie-in). A hosted extract is the fallback, and it is what the check
  values are measured against. The project is NAD 1983 UTM Zone 12N at 30 m, as in the original.
- **Baseline model.** Random sample points with a fixed seed (Random Number Generator environment),
  then Extract Values to Points, then three methods at their defaults: **Thiessen**, **IDW** and
  **Ordinary Kriging**. Each surface gets a difference raster against the truth (Raster Calculator) and
  an RMSE (square, Zonal Statistics mean, square root). This is the original's chain, with the RMSE
  sentence fixed so it says *mean* of the squares.
- **How they behave.** One step per method, each with check values and a `NOTE` that names what to
  look for in that surface, the thing the original lab let students discover:
  - Thiessen: terraces and cliffs at the polygon edges.
  - IDW: bull's-eyes, and a surface that never exceeds the highest sample or drops below the lowest.
  - Kriging: smoothing that shaves peaks and fills valleys.

  Students record each surface's minimum and maximum against the true DEM and where its largest errors
  sit.
- **Sensitivity step.** This replaces the original's "three IDW and three Kriging variants" and the
  second DEM. Students re-run from the tool dialog with each method's own parameter changed (IDW power;
  the Kriging semivariogram model or search radius) and the sample count changed (for example 250 /
  2,500 / 10,000). They record one table of method, parameters, N, RMSE, minimum and maximum, then
  answer three questions:
  1. Which method wins, and does the winner change with N?
  2. Which parameter mattered and which barely did?
  3. *In practice you have no true DEM.* Withhold 200 checkpoints in one run and compare the RMSE they
     give with the full-grid RMSE. How far off is the estimate a practitioner would actually report?

  Seven or more surfaces still get built, so the exploration the original was after survives. They are
  organized as runs of one model rather than seven copies of the tools.
- **Maps.** Map 1 is the comparison sheet: the true DEM, the three surfaces, and the three error rasters
  on one shared diverging ramp, each labeled with method, parameters and RMSE. Map 2 is the run that
  most changes the ranking.
- **Personal run** (section 8). The graded table uses a seed taken from the student's BYU ID digits. The
  published check values use the fixed course seed.
- **Individual work**, like Labs 4–8. The partner note goes.

## 5. Lab 10: wind farm suitability

**Proposed design: keep the subject and fix the method.** This is the course's weighted-overlay lab,
and the Week 10 deck ("Criteria to Surface") sets it up.

- **One study area.** The six southeastern counties (Minnehaha, Moody, Lake, McCook, Turner, Lincoln),
  which the example map already shows. Delete "western South Dakota". CRS NAD 1983 UTM Zone 14N. Set
  cell size, snap raster, extent and mask in Step 0, with a cell-count check value.
- **Split the criteria into two kinds.** *Exclusions* (wind speed < 7 m/s; within 20 mi of an existing
  wind farm; within 1 mi of a river) become a 0/1 mask applied once. *Preferences* (distance to town,
  distance to road, wind speed above 7) are scored on a common 1–10 scale and combined with weights
  that sum to 1. The weights are the student's choice, and they must justify them. That justification
  is the Lab 1-style "layer you create and defend".
- **Fewer tool chains.** Replace the four Buffer → Polygon to Raster → Reclassify chains with distance
  rasters (Distance Accumulation or Euclidean Distance; check which one 3.7.1 recommends) followed by
  Reclassify. This cuts the tool count and gives graded scores instead of a single cliff at the buffer
  edge.
- **Data, varied deliberately.**
  - Wind speed at 80 or 100 m: replace the dead link. Candidates are NREL (WIND Toolkit / WindExchange
    maps) and the Global Wind Atlas; check license and vintage, then host a clipped extract.
  - Existing turbines: the **USGS/LBNL U.S. Wind Turbine Database**. It is live, versioned quarterly,
    and has rich attributes, which makes it the right layer for the metadata questions.
  - Roads (TIGER primary/secondary), places (Census), and rivers (NHD), as agency downloads.
- **Sensitivity.** Three weight sets (the student's own, plus "wind-first" and "infrastructure-first")
  and one exclusion distance (wind-farm spacing at 10 vs 20 mi). Record suitable area, the top-scoring
  site's location, and whether it moves. Three questions: what moves the answer most, is the top site
  robust, and what the score does *not* measure (land ownership, transmission capacity, wildlife).
- **Removed.** "Repeat for counties you select."

**Decisions for the instructor (Lab 10)**

1. Southeastern counties, with "western SD" deleted? (Recommend: yes.)
2. Exclusion mask + normalized weighted preferences, instead of all-0/1 weighted? (Recommend: yes. It is
   the main concept error in the current lab.)
3. **Weighted Sum** with weights summing to 1, or **Weighted Overlay** (percent influence, integer
   scale), or the ArcGIS Pro **Suitability Modeler**? (Recommend: Weighted Sum inside ModelBuilder,
   because the model is the spine of every lab. Mention Suitability Modeler in the deck as the
   interactive alternative.)
4. River exclusion is 1 mi (as the criteria list and the Figure 11 dialog say), not 2 mi? (Recommend: 1 mi.)

## 6. Lab 11: least-cost power line

**Proposed design: same corridor, current tools.**

- **Tools.** **Distance Accumulation** (with its barrier input) → **Optimal Path As Line**, replacing
  Cost Distance / Cost Path / backlink. Verify every parameter name in 3.7.1. Align the Week 11
  `least-cost-path.md` deck in the same pass; it still mentions the old tools 16 times.
- **Cost surface, defined once and stated.**
  - *Hard barriers* go in Distance Accumulation's barrier input: open water, and a city core if chosen.
  - *Costs* on a 1–10 scale: distance from road corridor, river crossing, city proximity (multiple-ring
    scale), and co-location with existing transmission lines (cheaper).
  - **Slope instead of raw elevation.** "Lower is cheaper" is not a defensible engineering cost;
    steepness is.
  - UTM 12N, a stated cell size (30 m recommended for run time) and snap raster.
- **Endpoints.** Hosted as a two-point feature class. Coordinates come from real features (the
  Spanish Fork wind park, the Bluffdale data center) as read from imagery or data; they are not typed
  from memory. Update the scenario sentence so it names what exists today.
- **Data.**
  - Hosted 30 m Utah County DEM extract.
  - UGRC layers linked at their `/explore` pages: UDOT routes, NHD lakes and streams, municipal
    boundaries.
  - Transmission lines from HIFLD, matching Lab 4's precedent; check the license.
  - Replace the 404 RFF reference, and settle Meehan 2003 vs 2007.
- **Check values.** Path length (km), total accumulated cost, the share of the path inside the road
  corridor, and the number of river crossings.
- **Sensitivity.** River-crossing cost ×2 and ×½; barrier vs high-cost for water; slope weight on/off.
  Map 2 overlays the baseline and one alternative path. Three questions: which assumption moves the
  line most, how much longer is the least-cost path than the straight line and why, and what the cost
  surface leaves out (right-of-way, the public opinion the Background already raises).
- **Scope.** Lab 11 is due in Week 12 with the final-project kickoff, so keep it to about ten steps.

**Decisions for the instructor (Lab 11)**

1. Distance Accumulation + Optimal Path As Line? (Recommend: yes; ROADMAP already says so.)
2. Slope rather than elevation as the terrain cost? (Recommend: yes.)
3. Which constraints are hard barriers: water only, or water and city cores?
4. Scenario wording: keep the NSA data center / Spanish Fork wind farm, or reframe it?

## 7. Fix now, before any of the above: instructor notes are public

The migration-notes HTML comments, including the sensitivity tables marked "do NOT publish", are in
the **rendered page source** on the live site. Checked October 5: the Lab 8 page source contains
`SENSITIVITY (do NOT publish): IDW 5.…`. The Markdown is also readable on the public GitHub repo, and
`tools/labNN/run_model.py` is a complete arcpy solution to every lab.

- **Quick fix (minutes).** An MkDocs hook (`on_page_markdown`) that strips `<!-- … -->` from lab pages
  before rendering. This removes the numbers from the site that students and crawlers actually read.
- **Real fix.** Keep sensitivity tables, measured scenario results and any answer key out of the
  public repo, as was already done for the quiz keys (Drive, `CE 414 …/Quizzes`): a private
  `instructor/` repo or a Drive folder, with only a pointer left in the migration notes. Treat the
  `run_model.py` scripts as public, so the published check values must be ones a student is *meant* to
  match, and the graded numbers must be ones they cannot simply copy (section 8).

## 8. Making sure students learn it rather than outsource it

**Starting point.** The AI policy already allows AI with disclosure and draws two bright lines: no
field names, expressions or numbers from AI, and no generated output presented as ArcGIS Pro work.
Midterms ban AI; the final exam is an open-computer modeling problem in ArcGIS Pro.

**Assumption.** A determined student with a chatbot can now write the whole report, and a computer-use
agent can drive ArcGIS Pro (this course's own figures were captured that way). AI detectors are not
reliable enough to grade on.

**Goal.** Make doing the lab the cheapest path to the points, and verify understanding where it counts.
Six measures follow, roughly in order of payoff per hour of instructor time.

1. **Personal numbers that the instructor can reproduce.** Keep the published check values at a fixed
   seed so students can confirm their model works. Then make the *graded* run personal: the random
   seed (Labs 8 and 9), the student's own weight set (Lab 10), or one personal endpoint shift (Lab 11)
   comes from the last four digits of their BYU ID. Nobody can copy a classmate's table or an AI's
   guess, and `run_model.py --seed NNNN` reproduces any student's numbers in a minute. The arcpy
   reference scripts already exist for every rebuilt lab, so they become **grading oracles**: a report
   whose numbers do not reproduce gets a conversation, not an accusation.
2. **Submit the toolbox.** Add the `.atbx` (a few KB) to every submission alongside the PDF. The grader
   can open it, see the model, and run it at the student's parameters. A model the student never
   built cannot be faked convincingly, and it is far stronger evidence than a screenshot. One template
   checklist line, no rubric change.
3. **Spot-check vivas in the open lab period.** For each lab, pick about five students at random (a
   different five each time) for a three-minute check at their machine during the 2:00 lab period or
   the week after submission: "Open your model. Change N to 300 and run it. What do you expect to
   happen to the RMSE, and why?" Announce it in the syllabus and on every lab page. The deterrence comes
   from the possibility, not the count, so it costs about 15 minutes a week. A student who cannot run
   their own model gets the write-up graded as unverified.
4. **Judgment tied to their own map.** The "where the method breaks" item must cite a specific place
   on *their* result, with coordinates and a cropped figure: "the largest Kriging error is at
   <lat, lon>, on <the landform there>, because…". Generic prose about interpolation
   (what AI produces) earns nothing; a specific claim about their raster is checkable and is what an
   engineer actually does. This is a wording change to the existing rubric bullet in each lab.
5. **The labs are the exam prep, and the exams say so.** Write two or three Midterm 2 items per lab
   that can only be answered quickly by someone who ran it: a check-value interpretation ("your
   Thiessen surface has terraces; which parameter would change them?") or a sensitivity prediction. The
   final exam's modeling question is the real summative test that a student can build a model
   unaided. Tell students in Week 9 that Labs 8–11 feed Midterm 2 directly, so outsourcing a lab is
   visibly borrowing against the exam.
6. **One assignment designed *around* AI** (AI policy TODO 2). In Lab 10, the student asks an AI for a
   weight set and its justification *before* doing the sensitivity runs, and then tests the AI's
   weights as one of their scenarios and reports what the data says about them. This is one bullet
   inside the existing sensitivity row, and it puts the course's bright line (AI is confident about
   things only the data can answer) into practice instead of just stating it.

**What I would not do.** AI detectors, lockdown browsers for labs, or banning AI on labs. All three
punish honest students and are unenforceable in a computer lab.

**Decisions for the instructor (integrity)**

1. Personal seeds and weights from BYU ID digits, starting with Lab 9? (Recommend: yes. Lab 8 could
   also take it, but it is already assigned.)
2. `.atbx` with every submission from Lab 9 on? (Recommend: yes.)
3. Random spot-check vivas, announced on Learning Suite and on each lab page? (Recommend: yes, five per
   lab.)
4. The Lab 10 AI-weights bullet? (Recommend: yes, as a pilot of an AI-designed item.)
5. The MkDocs comment-stripping hook now, and move the instructor notes to a private home? (Recommend:
   the hook today.)

## 9. Odds and ends to sweep while doing this

- Lab 1 captures to 175 % (the only lab whose figures predate the GUI-capture standard).
- Lab 5 Step 14 completed-run capture.
- Learning Suite due dates for Labs 6–8, then 9–11 as each is promoted.
- Final project: peer scoresheet and instructor rubric still TODO on `final-project.md`. The template
  generator could build a final-project template from the same machinery.
- Week 9 deck: the Connections menu paths are still marked VERIFY. Check them during the Lab 9 GUI
  build if Step 0 uses the image service.
