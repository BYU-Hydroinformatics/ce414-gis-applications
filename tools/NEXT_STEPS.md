# Next steps: hand-off prompts (written October 9, 2026)

Each section below is a self-contained prompt for a fresh Claude Code session opened in this
repository. Paste the block under **Prompt** as the first message. They are ordered by difficulty
and by dependency: 1 before 2; 3, 4 and 5 are independent.

State of the course on October 9, 2026: Labs 1–11 are rebuilt, GUI-built, promoted and pushed, each
with a report template; Learning Suite due dates are set through Lab 11. Weeks 1–13 have decks.
What remains is Lab 12, Week 14, Midterm 2, the final-project rubric, and a capture backlog.

Every prompt assumes the agent reads `CLAUDE.md` first (it is loaded automatically) and follows
its hard rules: ArcGIS Pro not QGIS, never fabricate a screenshot, never invent a field name or
number, verify in ArcGIS Pro, American English, "ArcGIS Pro" in full, check every link, do not push
without being asked.

---

## 1. Lab 12: Network Analysis (largest; needs decisions from Dan)

**Why it is hard:** a new lab from nothing, in a topic (Network Analyst) the course has not used yet,
with a network dataset to build or source, a GUI build at 175 %, and a one-week schedule (introduced
Tuesday of Week 14, due Saturday of Week 14, the same week as Midterm 2).

**Prompt**

> Build Lab 12: Network Analysis for CE 414. The page `docs/assignments/lab-12/README.md` is a stub.
> Follow `tools/lab-conversion-guide.md` section 9 ("Building a new lab from nothing") and the
> pipeline in `tools/labs-09-11-plan.md` section 3. Use Lab 11 (`docs/assignments/lab-11/README.md`,
> `tools/lab11/`) as the closest model: it is the most recent lab and shows the whole pattern (hosted
> package built by a script, `run_model.py` reference run with `check_values.json`, a personal number
> from the last two BYU ID digits with a lookup CSV, no-GUI pilot, GUI build with captures, example
> maps with `arcpy.mp`, report template via `tools/templates/make_lab_report_template.js`).
>
> Step 1 is a plan, not a page: write `tools/lab12/PLAN.md` proposing the analytical question, the
> data, the one or two numbers students vary, and the personal number, then **stop and ask me to
> decide** before building. Constraints and facts to start from:
> - Network Analyst is licensed on this machine (`arcpy.CheckExtension("Network")` returns Available).
> - The course is set in Utah County. UGRC's `UtahRoads` feature service (services1.arcgis.com/
>   99lidPhWCzftIe9K, layer `UtahRoads`) has ONEWAY, SPEED_LMT, DOT_FCLASS and address fields;
>   check whether UGRC publishes a prebuilt network dataset before planning to build one, and say
>   which is simpler for students in a one-week lab.
> - Candidate questions (pick or improve): fire-station or hospital service areas in Utah County and
>   the population or buildings outside a response time; closest facility; a site-selection
>   location-allocation that echoes Lab 1. The deck and lab should contrast network distance with
>   Lab 11's cost distance and with straight-line distance.
> - One ModelBuilder model with parameters, a sensitivity step that varies a number the answer
>   actually depends on (Lab 11 learned this the hard way: measure that the parameter moves the
>   result across the whole personal range before publishing it), two maps, rubric five rows of ten.
> - Week 14 is also Midterm 2 week; keep the lab to about nine steps and host everything prepared.
>
> After my decisions: build the package, the reference run, the draft (`draft.md`, search-excluded),
> pilot it with a subagent, GUI-build it at 175 % (see the memory note on ArcGIS Pro desktop control
> and `tools/screenshots/README.md`; computer use is granted for ArcGIS Pro only), make the example
> maps and template, promote, and commit. Also: `docs/policies/grading.md` still says "Labs 1 to 11,
> 550"; ask me the points for Lab 12 and update it, `tools/build_schedule.py` (LABS/DUE already list
> Lab 12 in Week 14), and the Learning Suite assignment (due Saturday of Week 14, 11:59 pm; link the
> page and template; allow multiple uploads for the `.atbx`). Report what you measured and what is
> still owed. Do not push until I say so.

---

## 2. Week 14 decks: Network Analyst, two lectures (after task 1)

**Why it is hard:** two decks with real figures and ArcGIS Pro captures, aligned with a lab that does
not exist yet; there is no source PowerPoint for this topic.

**Prompt**

> Write the two Week 14 lectures on network analysis for CE 414: `slides/week-14/network-analysis-a.md`
> (Tuesday: what a network dataset is — edges, junctions, connectivity, turns, one-way and impedance
> attributes; shortest path versus least-cost path versus straight line; travel-time cost) and
> `slides/week-14/network-analysis-b.md` (Thursday: service areas, closest facility and
> location-allocation in ArcGIS Pro, then Lab 12). Read `tools/slide-conversion-guide.md`; use
> `slides/week-12/least-cost-path-b.md` as the model for structure, figures, speaker notes and the
> closing QR quiz (`docs/quizzes/<slug>/index.html`, `tools/make_quiz_qr.py`, `tools/check_quizzes.py`;
> watch for the longest-option-is-the-answer tell). Every map and number comes from Lab 12's data and
> reference run (`tools/lab12/`), drawn by a `tools/week14_*.py` script; tool captures come from a real
> ArcGIS Pro session, never fabricated. Register both decks and quizzes in `tools/build_schedule.py`
> (DECKS, PRACTICE; remove the Week 14 NO_DECK text), re-run it, render both decks to PNG with marp
> (`--allow-local-files --images png`) and look at every slide, and run `mkdocs build --strict`.
> Commit; do not push. Midterm 2 is open in the Testing Center that week: say so on Before Next Class.

---

## 3. Midterm 2 (keep out of the public repo)

**Why it is hard:** it must cover only what was taught, in the format the students were promised, with
real ArcGIS Pro screen grabs, and none of it can land in the public repository.

**Prompt**

> Draft Concepts Midterm 2 for CE 414 (Fall 2026), in the format of Midterm 1:
> `C:\Users\dpame\Downloads\Midterm1-2026\` holds `2026 Midterm 1 DRAFT.md`, `KEY.md`, `NOTES.md` and
> `images/`. Read all three first and match them. Write the new files to
> `C:\Users\dpame\Downloads\Midterm2-2026\` — **never inside the course repository**, which is public.
> Format promised to students: paper and pencil in the Testing Center, closed book and notes, no
> computer; multiple choice, fill in the blank, short answer, draw a sketch, and questions on a figure
> or an ArcGIS Pro screen grab ("what does this tool do", "which tool would you use for X"). 100 points.
> Coverage: from Week 8 (flood mapping, HAND) through Week 13 — interpolation and RMSE (Week 9), cut
> and fill and raster volumes (Week 10), coordinate systems and GPS (Week 11), least cost paths
> (Week 12), the final-project lecture (Week 13) — drawn from those weeks' decks
> (`slides/week-08` … `week-13`), their QR quizzes (`docs/quizzes/`) and the Learning Suite reading
> quizzes (generators in the private repo, `ce414-private/quizzes/learning-suite/`). Ask me whether Week 14's network analysis is
> in scope (it is taught the same week the exam is open). Use only numbers that appear in class
> material, keep any number that exists only in class out of public files, and use real captures from
> the repo's images or a fresh ArcGIS Pro session. Include a coverage matrix, a key with worked answers
> and partial credit, and a "could not confirm" list. Report the file paths; commit nothing.

---

## 4. Final project: peer scoresheet and instructor rubric

**Why it is hard:** it needs Dan's grading intent, and the rubric has to match the lab rubrics' style
while covering a team project, a video presentation and a write-up.

**Prompt**

> The final-project page `docs/assignments/final-project.md` has a TODO: the peer scoresheet and the
> instructor rubric are missing. Read the page, `docs/policies/grading.md` (proposal meeting 10,
> presentation 40, write-up 50; presentations are video only; notes on at least ten classmates'
> presentations, 10 points), the Week 13 deck `slides/week-13/final-project-introduction.md`, and two
> lab rubrics (`docs/assignments/lab-11/README.md` and `lab-07`) for the itemized-bullet style. Draft
> (a) an instructor rubric for the presentation (40) and the lab-style write-up (50), itemized so the
> bullets sum to each row's points, and (b) a one-page peer scoresheet students fill in while watching
> classmates' videos. Show me both before editing the page; then add them, consider a Word template for
> the write-up with `tools/templates/make_lab_report_template.js` (it reads the rubric from the page),
> run `mkdocs build --strict`, and commit. Do not push.

---

## 5. ArcGIS Pro capture backlog (desktop control)

**Why it is hard:** it needs computer use on ArcGIS Pro at 175 % scaling with the capture tooling, and
several items need finding first.

**Prompt**

> Clear the remaining ArcGIS Pro capture TODOs in the CE 414 site. Read the memory note on ArcGIS Pro
> desktop control and `tools/screenshots/README.md` first (175 % scaling with
> `tools/screenshots/setdpi.py`, `park.py` for the Claude window, `grabdlg.py`/`cap.py`/`stitchat.py`;
> set scaling back to 100 % and `park.py Claude 966` at the end). Computer use is granted for ArcGIS Pro
> only. Find the work with `grep -rn "TODO(capture)\|TODO(graphic)" docs slides`: Lab 5 has three
> capture TODOs (`docs/assignments/lab-05/README.md`; the project is `C:\Ames\Lab05GUI\Lab05.aprx`);
> several Week 1, 3 and 6 slides want ArcGIS Pro screenshots; and earlier notes list six captures that
> still show an old geodatabase name — find them by comparing the geodatabase names in images' visible
> text with the names the pages now use. Never fabricate or edit a capture's content; crop and stitch
> only. Replace each TODO with the figure, real alt text and a caption, render each page or deck and
> look at it, run `mkdocs build --strict`, and commit. Do not push.

---

## Not for an agent

These need Dan, a student, or a lab machine:

- **Student GUI pilots** of the rebuilt labs on a lab machine (Labs 7–11 were GUI-built on the
  instructor laptop only).
- **Instructor decisions** left as `TODO(instructor)` comments in the Week 4 and Week 5 decks
  (guest-speaker slide, image rights for the Daily Mail and NOAA images, the scale-and-uncertainty
  additions in Terrain Analysis) — `grep -rn "TODO(instructor)" slides`.
- **Midterm 1 logistics** (calculators, time limit) recorded in `Downloads\Midterm1-2026\NOTES.md`.
- **Lab 7:** the Jordanelle Dam completion date is still marked VERIFY (Reclamation's pages timed out).
