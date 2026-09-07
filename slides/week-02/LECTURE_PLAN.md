# Week 2 lecture plan: ModelBuilder Part A (Tuesday) and Part B (Thursday)

Written September 7, 2026 for whoever revises the two Week 2 decks before class on Tuesday,
September 8 and Thursday, September 10. It is a handoff document: everything an agent needs to do
the work is here or linked from here. Read `CLAUDE.md` and `tools/slide-conversion-guide.md` first;
they carry the hard rules (ArcGIS Pro wording, no fabricated screenshots, every slide a graphic,
American English, no instructor names outside the title slide).

## 1. Decisions already made

These are the instructor's calls. Do not re-litigate them; build to them.

1. **Two ModelBuilder sessions, not three.** Tuesday is Part A, Thursday is Part B. Learning Suite
   currently lists a "Part 3" on Thursday (Walmart lab discussion, prior-year submissions, validation,
   publication-quality maps). That material moves *into Part B*. The Week 3 deck called
   "ModelBuilder Part C" is not about ModelBuilder at all (it is an NDVI preview, see
   `slides/week-03/modelbuilder-c.md`); leave it for the Week 3 revision and do not point to it as
   a third part.
2. **Drop the "Data Models, continued" wrap-up** from Tuesday. Students got it last Thursday. Part A
   opens with "what is a model" and goes straight to ModelBuilder. If any data-models idea is needed
   later in the deck (a DEM is both a raster data model and a terrain model), say it in one line on
   the slide where it comes up.
3. **Tuesday teaches concepts and mechanics and prepares students for Lab 1.** Thursday locks the
   concepts in, gives practice (the cookie model), and coaches the lab: parameters, documentation,
   the rubric, peer review, and what a good submission looks like.
4. **The "good example" on Thursday is built from the revised Lab 1**, not from prior-year student
   reports. The lab changed on September 6 (two maps, sensitivity analysis, five-part rubric, peer
   review, self-assessment), so the Cooper and Cordner PDFs on Learning Suite no longer match the
   assignment. Use the example maps and rubric from `docs/assignments/lab-01/README.md` instead; the
   old PDFs may be shown for one slide as "what the map looked like in past years," nothing more.
5. **Magic Valley stays optional in Lab 2.** Not relevant to this week; noted so nobody "fixes" it.

## 2. What exists today

| Deck | Slides | State |
| --- | --- | --- |
| `slides/week-02/modelbuilder-a.md` | 28 | Converted Sept 3. Text is sound. Four ArcMap-era or drawn figures, one unverified number, three text-only slides, one dead data reference, three `VERIFY` notes. |
| `slides/week-02/modelbuilder-b.md` | 20 | Converted Sept 3. All 19 screenshots are current ArcGIS Pro captures from a "RiversDemo" project and are the quality bar. Two `TODO(graphic)`, one wording `VERIFY`. Contains nothing yet on the Walmart lab, the rubric, or peer review. |

Images live in `slides/week-02/images/`, prefixed `mba-` and `mbb-`. Contact sheets of all 41 were
reviewed on Sept 7; the verdicts are in section 5.

Assets produced for the labs on Sept 5 and 6 that this week can reuse (copy into
`slides/week-02/images/` with an `mba-`/`mbb-` prefix; a deck must not reference an image outside
its own folder):

- Lab 1 (`docs/assignments/lab-01/images/`): `lab01-full-model-overview.svg` (the whole Walmart
  model), six tool icons `icon-*.svg`, `lab01-metadata-questions.svg`, `lab01-data-sources.svg`,
  `lab01-example-map-baseline.png` and `-scenario.png` (the two example layouts),
  `lab01-create-variable-parameter-menu.png`, `lab01-parameter-add-to-display-menu.png`, every tool
  dialog and per-step model snippet.
- Lab 2 (`docs/assignments/lab-02/images/`), all captured Sept 6 at 175 % scaling and sharp:
  `lab02-model-overview.svg`, `lab02-float-connect-menu.png` (the drag-to-connect menu),
  `lab02-parameter-menu-output.png` (right-click menu with Add To Display and Parameter),
  `lab02-model-properties-general.png` and `-parameters.png`, `lab02-model-tool-interface.png` and
  `-threshold.png`, `lab02-model-run-progress.png`, `lab02-environments-dialog.png`,
  `lab02-catalog-model.png`, `lab02-add-tools-to-model.png`, `lab02-threshold-run-messages.png`.

## 3. Tuesday, September 8: ModelBuilder Part A

**Purpose.** By the end, a student can explain what a model is and why ModelBuilder is the way we
build analyses in this course, can create a toolbox and model in ArcGIS Pro, read the state of a
canvas, and has watched one complete model built and run. They leave able to start Lab 1 Steps 0
to 4 that evening.

**Time budget** (sessions are 75 minutes; the instructor prefers more slides than the hour needs, used or skipped as the class flows, so treat these as a ceiling, not a script):

| Minutes | Block | Slides (new numbering) |
| --- | --- | --- |
| 0 to 3 | Title, goals | 1, 2 |
| 3 to 15 | What is a model | 3 to 10 |
| 15 to 22 | What ModelBuilder is, why we use it | 11 to 13 |
| 22 to 38 | Building a model in ArcGIS Pro (live demo alongside the slides) | 14 to 20 |
| 38 to 55 | Cities Near Rivers, problem to result, then "You try it" | 21 to 26 |
| 55 to 68 | Read Lab 1's model: the same ideas at lab scale | 27 to 29 |
| 68 to 75 | Things to remember, preview of Part B, before next class | 30 to 32 |

**Slide-by-slide.** "Keep" means text stands; "Revise" means edit text or swap the figure; "New"
means a slide that does not exist yet. Asset codes (A1, A2, ...) are defined in section 5.

| # | Slide | Action | Notes |
| --- | --- | --- | --- |
| 1 | Title | Keep | Background is the cities/rivers map; fine. |
| 2 | Today's Goals | Revise | Add a fifth goal: "Recognize the Lab 1 model as the same pattern." Swap the background to Lab 1's model overview (A9) so the goals slide shows where the day ends up. |
| 3 | Review: What is a Model | Keep | |
| 4 to 8 | Globe, map, photo, weather, DEM | Keep | Five example slides; keep them fast. On the DEM slide add the one-line data-models bridge ("a raster data model and a terrain model at once"), which replaces the dropped wrap-up. |
| 9 | Many types of models | Revise | Text only today. Add infographic A1 (five kinds of model, each with an engineering example). |
| 10 | A recipe is a model | Keep | The HTML recipe diagram already reads as data, tool, derived data. Say so on the slide: add a one-line legend "ovals are data, boxes are tools" that matches ModelBuilder's colors. This slide seeds Thursday's cookie exercise. |
| 11 | What is ModelBuilder | Revise | Text only today. Put the Lab 2 model overview (A10) on it, because it is the cleanest small real model we have, and caption it "one analysis, written down." |
| 12 | Example geoprocessing tasks | Keep | The 2005 Esri composite is dated in style but not wrong. Acceptable for one more semester; note as low-priority replacement (A11). |
| 13 | Geoprocessing options in ArcGIS | Revise | The figure is ArcGIS 9 / Windows XP. Replace with a new four-panel capture from ArcGIS Pro 3.7 (A2): the Geoprocessing pane tool dialog, the Python window, a model on the canvas, and an arcpy line in a notebook or script. Keep the sentence "the same tool, four ways to run it." |
| 14 | Lead: Building a model | Keep | |
| 15 | Start a new model (toolbox) | Keep | Screenshot is current. Add the keyboard shortcut Ctrl+Shift+B to the slide, it is already in the notes. |
| 16 | Add a model to your toolbox | Revise | Correct the rename guidance from the Sept 6 Lab 2 run: renaming in the Catalog pane changes the model's **Label** only; the **Name** stays "Model" until you set it in Properties, General; and a model cannot be renamed at all while it is open in ModelBuilder. Replace the Tool Properties screenshot with the sharper `lab02-model-properties-general.png` (A12), which shows exactly that Name/Label mismatch. |
| 17 | Set the model's environments | Revise | Keep the text. Replace the screenshot with `lab02-environments-dialog.png` (A13), which shows the Environments dialog students actually meet from the ModelBuilder ribbon. Add one bullet: "Output Coordinate System empty means Same as Input; set it on purpose or leave it empty on purpose." |
| 18 | The ModelBuilder ribbon | Keep | Verified capture. |
| 19 | Elements have three states | Revise | The drawn diagrams use ArcMap's drop-shadow convention. In ArcGIS Pro 3.x a run element carries a **green check badge**, and a not-ready element is **gray**. Replace the three drawings with three real Pro canvas crops (A3): not ready (gray, use or re-crop `mbb-gray-node-missing-parameters.png`), ready (colored, no badge), run (green checks; crop from `lab02-float-tool-modelbuilder.png` or a fresh capture). Rewrite bullet 3 from "colored and shaded" to "colored with a green check." |
| 20 | Start building your model | Revise | The connect step is now verified: drag from an element onto a tool and a "Select input..." menu asks which parameter it feeds. Put `lab02-float-connect-menu.png` (A14) on the slide and close the `TODO(instructor)`. |
| 21 | Lead: Cities Near Rivers | Keep | |
| 22 | The problem | Keep | |
| 23 | The model | Revise | The figure is the classic ArcMap window. Re-capture the same Project, Buffer, Intersect model on an ArcGIS Pro canvas (A4) in the RiversDemo project that produced the Part B screenshots, or export it as SVG from ModelBuilder as the labs do. |
| 24 | The result | Revise | The "898 of 3,128 cities" number is unverified. Run the model on the dataset the course will distribute (see section 6) and quote that number, or say "about 29 percent" with the dataset named. Re-capture the result map from Pro (A5). |
| 25 | You try it | Revise | Point students at the hosted cities and rivers download (section 6) instead of a MapWindow CD. Replace the monitor clip art with a real Pro screenshot of the two layers loaded (A6). Give the exact projection to use and the number to compare against. |
| 26 | New: Read a model out loud | New | One slide, the Cities Near Rivers Pro canvas (A4) with numbered callouts 1 to 5 in reading order. The skill being taught is reading a canvas as a sentence, which is what the Lab 1 rubric's "description a reader could repeat from" asks for. |
| 27 | New: Lab 1 is the same pattern | New | `lab01-full-model-overview.svg` (A9) full width. Talk through it as Select, Intersect, Add Field and Calculate Field, Select, Select, Buffer, Intersect, Buffer, Erase. Do not teach the steps; show that it is one chain of the tools they just saw. |
| 28 | New: The tools you will use | New | A grid of the six Lab 1 tool icons (A15) with the one-line meaning of each, lifted from the lab's tool table. |
| 29 | New: Two traps before you start the lab | New | Two real dialog captures from Lab 1: Add Field with the type set to Double (`lab01-add-field-density-dialog.png`) and Buffer with the unit set to Statute Miles (`lab01-buffer-roads-dialog.png`). The lab's two most expensive mistakes, shown once in class. |
| 30 | Things to remember | Revise | Resolve the two `VERIFY` notes: "Add To Display" is the exact menu label (confirmed Sept 6, `lab02-parameter-menu-output.png` shows it checked); the intermediate-data controls in Pro 3.7 are the **Intermediate Data** check on an output's right-click menu and **Intermediate** in the ribbon's Run group. Confirm in a live session where "Delete Intermediate Data" lives in 3.7 before asserting it; if unsure, drop that bullet. Use the right-click menu capture as the figure. |
| 31 | Coming up: Part B | Revise | Text only today. Use `lab02-model-tool-interface-threshold.png` (A16): a finished tool dialog with a threshold parameter, which is exactly what Part B builds. |
| 32 | Before Next Class | Revise | Fill in the reading chapter and the quiz. Add "sketch a model of baking a cookie on paper and bring it" as the Thursday prep, since the cookie exercise depends on it. Keep the Lab 1 link. |

**Correctness items to close on Tuesday's deck** (each is already flagged in the deck as a comment):

- Slide 13 ArcGIS 9 composite: replace (A2).
- Slide 19 element states: Pro uses check badges, not shading (A3).
- Slide 20 connect-by-drag wording: verified; add the capture (A14).
- Slide 23 ArcMap model window: replace (A4).
- Slide 24 "898 of 3,128": verify or restate.
- Slide 25 MapWindow CD data reference: replace with the hosted download.
- Slide 30 the two `VERIFY` notes.
- Slide 16 rename behavior: correct as described (from the Lab 2 GUI run notes in
  `docs/assignments/lab-02/README.md`, revision notes at the top).

## 4. Thursday, September 10: ModelBuilder Part B

**Purpose.** Lock in the concepts with a hands-on exercise, turn a model into a reusable tool,
show how to document it, and then coach the lab: what the rubric rewards, what a complete
submission looks like, how peer review works, and how to judge whether a model's answer is right.

**Time budget:**

| Minutes | Block | Slides |
| --- | --- | --- |
| 0 to 3 | Title, goals | 1, 2 |
| 3 to 18 | Cookie model: sketch, compare, rebuild in ArcGIS Pro live | 3 to 5 |
| 18 to 26 | Three things that save an hour (Add To Display, gray nodes, run one node) | 6 to 9 |
| 26 to 30 | Rename elements | 10 |
| 30 to 45 | Parameters: variable, P marker, tool dialog, Create Variable From Parameter | 11 to 16 |
| 45 to 52 | Documenting a model | 17 to 20 |
| 52 to 70 | Lab 1 clinic: rubric, the good example, validation, publication-quality maps, peer review | 21 to 27 |
| 70 to 75 | Going forward, before next class | 28, 29 |

**Slide-by-slide.**

| # | Slide | Action | Notes |
| --- | --- | --- | --- |
| 1 | Title | Keep | |
| 2 | Today's Goals | Revise | Add two goals: "Read the Lab 1 rubric and know what each part rewards" and "Give and act on a peer review." |
| 3 | Cookie model review | Revise | Keep the student sketch and the Cookie Monster image. Add a second, tidier sketch (B1, a clean diagram in ModelBuilder colors) so the class sees the "smaller model" answer drawn, not only described. |
| 4 | New: Build the cookie model live | New | A ModelBuilder canvas with three data ovals feeding a Mix tool, a Bake tool and a Cookies output, made with real Pro elements (B2: use three small tables as inputs and Merge or Copy Rows as stand-in tools, then rename every element). The point is the vocabulary: data, tool, derived data, connector, parameter. Keep the demo under eight minutes. |
| 5 | Cities Near Rivers: how many ways? | Revise | Text-only discussion slide. Add capture B3: the same answer produced two ways, Buffer + Intersect beside Select Layer By Location, as two small canvases. If time is short, a single canvas with both branches is enough. |
| 6 | Lead: three things | Keep | |
| 7 | Get the output onto the map | Keep | Current capture. Optionally swap to the sharper Lab 2 menu capture (A14 family); not required. |
| 8 | Gray node | Keep | |
| 9 | Test one piece at a time | Keep | |
| 10 | Rename your elements | Keep | Add the Sept 6 finding to the notes: Rename here changes the element label; the model's own Name is set in Properties. |
| 11 | Lead: parameters | Keep | |
| 12 | Mark a variable as a parameter | Keep | |
| 13 | Now the model opens ready to run | Keep | Note in the notes that current projects create `.atbx` toolboxes; the screenshot shows `.tbx`. Already there. |
| 14 | Two parameters, two inputs | Keep | |
| 15 | Create a variable from a tool parameter | Revise | Add the Lab 1 counterpart beside the RiversDemo capture: `lab01-create-variable-parameter-menu.png`, which is the exact move Lab 1 Step 10 asks for (Buffer, Create Variable, From Parameter, Distance). Title the pair "the same move in your lab." |
| 16 | Then make that variable a parameter | Keep | Add a line: Lab 2 will do the same with a Double variable and a Raster Calculator expression; no figure needed. |
| 17 | Lead: documenting | Keep | |
| 18 | Metadata documentation | Revise | Wording is verified: the Catalog right-click menu in Pro 3.7.1 reads **Edit Metadata** (seen Sept 6 with the shortcut Ctrl+Shift+M). Capture that menu (B4) and close both TODOs. |
| 19 | Edit metadata | Keep | |
| 20 | View metadata | Keep | |
| 21 | New lead: Lab 1 clinic | New | Section divider. |
| 22 | New: What the rubric rewards | New | The five-part rubric from the lab as a one-slide table: Write-up 10, Model 10, Map 1 10, Map 2 10, Sensitivity 10, with the two or three highest-value bullets under each. Build it from `docs/assignments/lab-01/README.md`, "Rubric" section; do not paraphrase point values. Graphic: infographic B5, a five-box rubric strip. |
| 23 | New: A complete submission looks like this | New | The "good example." Left: `lab01-example-map-baseline.png`. Right: a checklist of what the lab's Deliverables section asks for (report sections, model figure exported from ModelBuilder, tool-dialog capture, sensitivity table, rubric with self-assessment, peer reviewer named). One sentence at the bottom: "the example map is not a template; yours will differ because your threshold and stores differ." |
| 24 | New: What a publication-quality map has | New | `lab01-example-map-baseline.png` with numbered callouts (B6): title with the threshold in it, legend, north arrow, scale bar in miles, inset with extent box, text box (result, author, date, projection, sources, method), county outline, labeled cities. This is the Learning Suite "what goes into a publication quality map" item. |
| 25 | New: Is the answer right? | New | The Learning Suite "how accurate are the results, how can we validate the model" item. Three prompts on the slide: (1) the check values in the lab (1,532 roads, 47 tracts, about 12.9 square miles) and what a mismatch means; (2) the Step 7 finding that one criterion changed nothing; (3) Step 12, vary the three numbers and see what survives. Graphic: `lab01-example-map-scenario.png` beside the baseline, the same map at a 3-mile exclusion. |
| 26 | New: Peer review, how to do it | New | The lab requires a named peer reviewer and a sentence on what changed. Give the protocol: swap reports, read against the rubric, write three things to fix, the author acts on them and names the reviewer. Ten minutes of class time can be used to pair people up. Graphic: infographic B7, a three-panel "read, mark, fix" strip. |
| 27 | New: Prior years, for one slide | New | Optional. One page from a prior-year report as "the map looked like this before; the analysis is the same, the deliverables are different." Only if the instructor supplies a page that is anonymized; otherwise drop this slide. |
| 28 | Going forward | Keep | |
| 29 | Before Next Class | Revise | Add the graphic (B8, a small "what's due" visual or the Lab 1 example map at thumbnail). Fill in reading and quiz. Add "Lab 1 due" with the date the instructor sets. |

**Correctness items to close on Thursday's deck:**

- Slide 18 menu wording: verified as "Edit Metadata"; add capture B4.
- Slide 10 and 13 notes: add the Name versus Label finding.
- Everything in slides 22 to 26 must be copied from the current Lab 1 page, not remembered.
  Point values, check values and deliverable wording change; the page is the source of truth.

## 5. Asset list

Every new screenshot comes from a real ArcGIS Pro 3.7.1 session (rule 2 in `CLAUDE.md`). Capture
at 175 % display scaling with the workflow in `tools/screenshots/README.md` (setdpi.py, grabwin.py;
PrintWindow does not work under scaling). Infographics are generated with the OpenAI image skill
(`anthropic-skills:openai-images`) and saved as PNG in the deck's `images/` folder; they must show
nothing that pretends to be an ArcGIS Pro screen.

**Tuesday (A):**

| Code | Asset | Kind | Source or prompt |
| --- | --- | --- | --- |
| A1 | Five kinds of model | Infographic | Five tiles: theory, law, hypothesis, equation, structured idea; an engineering example under each (Manning's equation, rational method, free-body diagram, and so on). Flat, BYU navy and gray, no screenshots. |
| A2 | Four ways to run a tool | Screenshot composite | Four Pro captures tiled: Geoprocessing pane with the Buffer tool open; Python window with one arcpy line; a two-tool model on the canvas; an arcpy script in a notebook. Label each panel. |
| A3 | Three element states | Screenshot crops | Real canvas crops: gray not-ready element, colored ready element, run element with the green check. |
| A4 | Cities Near Rivers model in Pro | Screenshot or SVG export | RiversDemo project: Project, Buffer, Project, Intersect, elements renamed as in Part B. Export To Graphic, SVG, like the labs do. |
| A5 | Cities Near Rivers result map | Screenshot | Same project, result layer symbolized, count visible in the attribute table. |
| A6 | You try it starting point | Screenshot | The two input layers loaded in a fresh project. Replaces the clip art. |
| A9 | Lab 1 model overview | Copy | `lab01-full-model-overview.svg` |
| A10 | Lab 2 model overview | Copy | `lab02-model-overview.svg` |
| A11 | Example geoprocessing tasks | Infographic, low priority | Four tiles: site selection, least-cost route, nearest facility, population in a zone. Only if time remains. |
| A12 | Tool Properties, General | Copy | `lab02-model-properties-general.png` |
| A13 | Environments dialog | Copy | `lab02-environments-dialog.png` |
| A14 | Connect menu | Copy | `lab02-float-connect-menu.png` |
| A15 | Six tool icons | Copy | `docs/assignments/lab-01/images/icon-*.svg` |
| A16 | Finished tool dialog | Copy | `lab02-model-tool-interface-threshold.png` |

**Thursday (B):**

| Code | Asset | Kind | Source or prompt |
| --- | --- | --- | --- |
| B1 | Tidy cookie model | Diagram | Draw in the deck's HTML (as the recipe slide does) or as a small SVG: flour, sugar, eggs, butter into Mix, then Bake, then Cookies; ModelBuilder colors. |
| B2 | Cookie model on a Pro canvas | Screenshot | Three tiny tables as inputs, two stand-in tools, every element renamed. Honest caption: the tools are stand-ins. |
| B3 | Two ways to the same answer | Screenshot | Buffer + Intersect beside Select Layer By Location, same inputs. |
| B4 | Edit Metadata on the Catalog menu | Screenshot | Right-click a model in the Catalog pane; the menu shows Edit Metadata with Ctrl+Shift+M. |
| B5 | Rubric strip | Infographic | Five boxes, ten points each, the top bullets of each part. Values copied from the lab page. |
| B6 | Anatomy of the example map | Annotated figure | `lab01-example-map-baseline.png` with numbered callouts. Callouts added in the deck's HTML or in an image editor; do not regenerate the map. |
| B7 | Peer review in three steps | Infographic | Read against the rubric, mark three things, author fixes and names the reviewer. |
| B8 | Before Next Class visual | Infographic or thumbnail | Small "what's due" card; or reuse the example map at thumbnail size. |

## 6. Data for the Cities Near Rivers exercise

Learning Suite distributes "United States.zip" for Part A. The deck still refers to a MapWindow
installer CD. To do:

1. Find the cities and rivers layers the instructor actually uses (ask; the RiversDemo project
   used for the Part B captures has them at `D:\Ames\RiversDemo\RiversDemo.gdb`).
2. Confirm the license allows redistribution (the MapWindow sample data was public domain U.S.
   Census and USGS data; check before hosting).
3. Host as `docs/data/week02-cities-rivers.zip`, link it from the "You try it" slide and from
   `docs/lectures/week-02.md`, and verify the count the slide quotes against that exact file.

## 7. Learning Suite text to post

Replace the two day entries with this (adjust dates and the quiz name):

**Tue, Sep 8. Graphical Modeling and ModelBuilder, Part A.**
Discussion: what a model is, and automating GIS analysis with models. Slides: ModelBuilder, Part A
(link to the week page). Data: cities and rivers (link to the hosted zip). Lab: Lab 1, Walmart Site
Selection (link). Before Thursday: sketch a model of baking a cookie on paper and bring it.

**Thu, Sep 10. Graphical Modeling and ModelBuilder, Part B.**
In-class activity: the cookie model, on paper and in ArcGIS Pro. Discussion: parameters, tool
dialogs, documenting a model. Lab clinic: the Lab 1 rubric, what a complete submission looks like,
validating your result, publication-quality maps, and peer review. Slides: ModelBuilder, Part B.

## 8. Quality bar and definition of done

- Every slide has a graphic except lead dividers. No slide keeps an ArcMap or ArcGIS 9 capture.
- Every number on a slide (898 cities, 1,532 roads, 47 tracts, 12.9 square miles, rubric points)
  is either verified in this pass or copied from the current lab page, and the deck says which
  dataset it came from.
- "ArcGIS Pro" is written in full in student-facing text. Links are checked (curl, and a browser
  for sites that block scripts).
- Speaker notes survive on every slide; the conversion-notes comment at the end of each deck is
  updated with what changed on Sept 7 to 8 and what is still open.
- `tools/build_lectures.py` DECKS descriptions updated if a deck's one-line summary changes, then
  the script re-run (it regenerates `docs/lectures/week-02.md`).
- Both decks render with the command in `CLAUDE.md` and are looked at as images
  (`--allow-local-files --images png`): no overflowing image, no orphaned caption, no text under
  a background image.
- `mkdocs build --strict` passes.
- Work is left in the working tree with a report of what was done, what was captured, and what
  remains; the maintainer commits and pushes.

## 9. Order of work if time runs short

1. Tuesday's correctness fixes (section 3 list) and the four Lab-asset copies (A9, A12, A13, A14).
2. Tuesday's three new lab-bridge slides (27 to 29).
3. Thursday's lab clinic slides (22 to 26), because nothing else on Thursday covers the material
   Learning Suite promised.
4. New Pro captures A2 to A6 and B2 to B4.
5. Infographics A1, B5, B7, then B1, B6, B8.
6. A11, slide 27 on Thursday, and anything marked optional.
