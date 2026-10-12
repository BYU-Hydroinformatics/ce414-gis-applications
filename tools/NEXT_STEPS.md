# Next steps: the rest of Fall 2026 (written October 11, 2026; updated October 12)

Each numbered section is a self-contained prompt for a fresh Claude Code session opened in this
repository. Paste the block under **Prompt** as the first message. The sections are in the order
the calendar needs them; 1 and 2 are the urgent ones.

**State of the course on October 11, 2026.** All twelve labs are rebuilt, GUI-built in ArcGIS Pro
3.7.1, promoted, and have report templates; Lab 12 was finished October 10 (fire-response service
areas on the UGRC network). Weeks 1 to 14 have decks; Week 15 has no class. No `TODO(capture)` is
left anywhere, and the only `TODO(graphic)` notes left are for generated figures, not screenshots.
Midterm 1 is drafted (Testing Center, October 20 to 22); Midterm 2 is drafted (December 1 to 3)
and waits on one decision. The final project has a rubric draft waiting for review. Everything
on `main` is pushed and live (the eight commits waiting on October 11 went out with it).

**Done October 12, 2026 (pushed; site deploy succeeded).**
- **Lab 5 Step 13** (`a92c5a5`): students hit an error running Clip with the live UGRC NHD
  service as its input (Dan sent a Learning Suite announcement on October 9). The step now adds
  the service, selects the lines touching `Rock_Canyon_Basin` with Select By Location, exports
  them with Data ▸ Export Features to `NHD_Local` (UTM 12N environment moved onto the export),
  and clips the copy. Text only, **not run in the GUI**; see section 5.
- **Sensitivity results moved to the private repo** (`8187ae8`, `dfe5ecb`; private `2d00597`,
  `695bc67`). The `SENSITIVITY (do NOT publish)` lines from the Lab 1, 4, 5, 8, 9, 10, 11 and 12
  migration notes, the sensitivity sections of the Lab 7 plan and the Lab 8, Lab 10 and wind-farm
  parity plans, and the Lab 3 draft's Stansbury walk numbers are now in
  `ce414-private/plans/lab-sensitivity-2026.md`; each public place keeps a one-line pointer. The
  sensitivity runs in the Lab 4, 5, 10, 11 and 12 `check_values.json` files, Lab 4's
  `site_survival.json` and Lab 7's two `sensitivity_*_base.json` files are now in
  `ce414-private/sensitivity/`. The model scripts for Labs 4, 5, 7, 10, 11 and 12 write them there,
  and the figure scripts for Labs 4, 5 and 12 and Weeks 12 and 14 read them from there, falling back
  to a git-ignored file beside the script when the private checkout is absent. These script changes
  were compiled and path-checked on the Mac but **not yet run under ArcGIS Pro**.
  `tools/lab-conversion-guide.md` now says new labs keep only a pointer. The numbers remain in the
  public repository's git history.

**Where things live.**
- Public site: this repository, `docs/` and `slides/`, built by `mkdocs build --strict` and the
  deck workflow on every push to `main`. The push is what publishes.
- Private companion: `C:\Users\dpame\code\ce414-private` on Windows,
  `/Users/danames/Code/ce414-private` on the Mac (remote `danames/ce414-private`; it must sit
  beside this checkout for the model and figure scripts to find it): exam drafts and keys
  (`exams/midterm-1-2026`, `exams/midterm-2-2026`), Learning Suite quiz generators,
  `grading-oracles/` (the per-student lookups for Labs 7, 11 and 12), `sensitivity/` (the labs'
  sensitivity runs), and `plans/` (including `lab-sensitivity-2026.md`).
  Nothing from it goes into this repository, including HTML comments. Finished exams and keys are
  also uploaded to the Google Drive folder *Private - exams, keys and grading*.
- ArcGIS Pro GUI projects: `C:\Ames\LabNNGUI\LabNN.aprx` with the **current** lab numbers (Labs 8,
  9 and 10 were renumbered copies made October 10 by `tools/screenshots/renumber_gui_projects.py`;
  originals are in `C:\Ames\_old`). `C:\Ames\Week06\Week06_Figures.aprx` holds the Emigration
  Creek hand-digitized and StreamStats basins; `C:\Ames\Lab01\Lab01.aprx` the Lab 1 data.
- Capture tooling: `tools/screenshots/` (read its README first). Captures are taken at 175 %
  display scaling (`setdpi.py 175`, launch ArcGIS Pro **after** changing it), the Claude window is
  parked with `park.py`, and the session ends with `setdpi.py 100` and `park.py Claude 966`.
- Learning Suite: course `cid-ahk3xMzyr311`; instructor assignments view `.../home/assignments`.
  It holds only due dates, submission boxes, quizzes and links; content lives on the site.

Every prompt assumes the agent reads `CLAUDE.md` first (it is loaded automatically) and follows
its hard rules: ArcGIS Pro not QGIS, never fabricate a screenshot, never invent a field name or a
number, verify in ArcGIS Pro, American English, "ArcGIS Pro" in full, check every link, nothing
private in the public repository, do not push without being asked.

---

## 0. Needs Dan, not an agent

- **Learning Suite, Lab 12.** Sign in to Learning Suite in Chrome, then an agent can add the
  assignment: due **Saturday, December 5, 2026, 11:59 pm** (Saturday of Week 14); description =
  a link to the page and to `docs/assignments/lab-12/lab12-report-template.docx`; multiple file
  uploads enabled so the `.atbx` can be attached. (The October 11 attempt stopped at the BYU
  sign-in page.)
- **Midterm 2 scope.** Is Week 14 (network analysis) on the exam? It is taught the week the exam
  is open, so students testing Tuesday morning will not have heard it. The draft assumes **out**.
- **Final-project rubric.** Read `tools/final-project/RUBRIC_DRAFT.md` and say yes, or what to
  change; section 3 below then puts it on the page.
- **Student pilots on a lab machine.** Labs 7 to 12 were GUI-built on the instructor laptop only.
  One student walk-through per lab, with the run times, is the check the pages still lack.
- **Reading-quiz redesign.** The two-section (reading / class, AI allowed) idea from September 8 is
  still undecided; the site describes the quizzes as the syllabus does.
- **Learning Suite points visibility.** Quizzes 5 to 11 and the Final Exam are not visible to
  students, so the percentages they see are computed on 1,030 points, not the real total.
- **Grading each week** (see section 4 for the agent half): Lab 6 is due October 17, Lab 7
  October 24, Lab 8 October 31, Lab 9 November 7, Lab 10 November 14, Lab 11 November 21, Lab 12
  December 5.

---

## 1. Midterm 2: finish the draft and write the study guide (before November 24)

**Why it is first:** the exam opens December 1 and the Week 14 decks it could not see now exist.
Students also expect a study guide like Midterm 1's (`docs/study-guides/midterm-1.md`).

**Prompt**

> Finish Concepts Midterm 2 for CE 414 (Fall 2026). The draft, key and notes are in the private
> repository `C:\Users\dpame\code\ce414-private\exams\midterm-2-2026\` (`2026 Midterm 2 DRAFT.md`,
> `2026 Midterm 2 KEY.md`, `NOTES.md`, `images/`); read all three and `NOTES.md`'s coverage matrix
> first. Nothing from that folder may be written into the public course repository. Do this:
> (1) The Week 14 decks now exist (`slides/week-14/network-analysis-a.md`, `-b.md`, with the
> `networks` and `service-areas` quizzes under `docs/quizzes/`); check the three items in the
> draft's "Optional: Week 14 bank" against them and rewrite any that the lectures contradict, so
> the bank is ready if I decide Week 14 is in. Ask me for that decision; the draft stays "out"
> until I answer. (2) Re-read every item against the current decks and lab pages for Weeks 8 to 13
> (Labs 7 to 11 were revised after some items were written; Lab 10's shift parameter and Lab 11's
> Distance Accumulation chain in particular) and fix drift. (3) Re-check every figure in `images/`
> against the current repo image; replace any that changed. (4) Write the public study guide
> `docs/study-guides/midterm-2.md` in the exact shape of `docs/study-guides/midterm-1.md`: topics by
> week, the formats, what to bring, the Testing Center window (December 1 to 3, Tuesday 8 am
> start), and nothing that gives away an item; register it in `tools/build_schedule.py` the way
> the Midterm 1 guide is (the Week 14 page links it), re-run the script, `mkdocs build --strict`,
> commit. (5) Export the finished exam and key to PDF, upload both to the Google Drive folder
> *Private - exams, keys and grading*, and commit the markdown in the private repository. Report the
> coverage matrix and the "could not confirm" list. Do not push either repository.

---

## 2. Final exam: one problem done in ArcGIS Pro (write by November 20)

**Why it is hard:** `docs/policies/grading.md` promises "one question done in ArcGIS Pro in the lab
during finals week; open book and open computer; three-hour block", and no such problem exists.
It must be solvable in three hours from a hosted data package, gradable from a short write-up and a
few numbers, and the numbers must be verified by a reference run.

**Prompt**

> Write the CE 414 final exam problem. The promise is in `docs/policies/grading.md`: one problem
> solved in ArcGIS Pro in the lab during finals week, open book and open computer, three hours,
> 100 points. Read `tools/lab-conversion-guide.md` sections 2 and 9 and two late labs
> (`docs/assignments/lab-11/README.md`, `lab-12/README.md`) for the voice, the check-value
> pattern and the rubric style. Propose three candidate problems first, each a new question on a
> small hosted package that combines two or three techniques from Labs 4 to 12 (a suitability
> model with a parameter, a watershed or HAND question, an interpolation with RMSE, a cost path, a
> service area), with a two-line estimate of the time and the gradable outputs; I pick one. Then:
> build the data package with a `tools/final-exam/make_package.py` and a `run_model.py` reference
> run (`check_values.json`), as Lab 12 did; write the student handout as
> `ce414-private/exams/final-2026/FINAL DRAFT.md` with a key, worked numbers, partial credit and a
> rubric whose bullets sum to 100; put the data package in the private repository too (it must not
> be public before the exam; it can move to `docs/data/` afterward). Use only real tool names and
> parameters you have checked in ArcGIS Pro 3.7.1; mark anything unverified. Commit the private
> repository only; report the file paths. Do not push.

---

## 3. Final project: put the rubric and the peer scoresheet on the page (before Week 13, November 24)

**Why it is hard:** it needs Dan's approval of `tools/final-project/RUBRIC_DRAFT.md` first (section
0). After that it is page work plus a Word template.

**Prompt**

> Dan has reviewed `tools/final-project/RUBRIC_DRAFT.md` (apply any changes he gave you). Put
> section A (the instructor rubric: proposal 10, presentation 40, write-up 50) and section B (the
> peer scoresheet, 10 points of presentation notes) into `docs/assignments/final-project.md`,
> replacing its `TODO(instructor)` comment, in the itemized-bullet style of the lab rubrics; keep
> section C out of the public page. Build a Word template for the write-up with
> `tools/templates/make_lab_report_template.js` (add a `final` entry; it reads a page's rubric
> table) and a one-page scoresheet students can print or fill in. Make sure the Week 13 deck
> (`slides/week-13/final-project-introduction.md`) and the Week 14 and 15 schedule pages
> (`tools/build_schedule.py` DUE table) carry the same dates as the final-project page: proposal meeting by Friday of Week 14,
> the eight-minute presentation video by Wednesday of Week 15, presentation notes by Thursday of Week 15. Check every
> link, `mkdocs build --strict`, render the deck, commit. Do not push.

---

## 4. Grading a lab (repeat each week)

**Why it is an agent task:** every rebuilt lab has a reference run, and Labs 7, 11 and 12 have
per-student lookups, so a grading pass is mostly comparison; the judgment calls go to Dan.

**Prompt** (replace NN)

> Grade Lab NN for CE 414. Submissions are the files Dan put in `C:\Ames\Grading\LabNN\` (student
> work is never copied into either repository). Read `docs/assignments/lab-NN/README.md` for the
> rubric and check values, `tools/labNN/check_values.json` for the reference run, and, for Labs 7,
> 11 and 12, the personal lookup in `C:\Users\dpame\code\ce414-private\grading-oracles\` to check
> each student's own parameter result. Read the memory notes on Learning Suite grading and on
> originality checks first. For each submission produce a row: rubric item scores with a one-line
> reason for every deduction, the check values found versus expected, and a flag for any
> near-duplicate layout, model labels, symbology or wording across submissions (compare, do not
> accuse; Dan decides). Write the summary to `C:\Ames\Grading\LabNN\grades.md`; do not enter
> scores in Learning Suite until Dan says so, then do it one student at a time with a screenshot
> before each entry, checking for pre-existing scores. Commit nothing.

---

## 5. Small page fixes left on the lab pages

Each is a `TODO(instructor)` or `VERIFY` comment; `grep -rn "TODO(instructor)\|VERIFY" docs` lists
them (about 25 lines, most of them historical notes that just need closing).

**Prompt**

> Close the open notes on the CE 414 lab pages. `grep -rn "TODO(instructor)\|VERIFY" docs` lists
> them. The ones that still matter: (1) `docs/assignments/lab-07/README.md`: the Jordanelle Dam
> completion and first-storage dates (Reclamation's pages timed out on October 9; try again, and
> the Utah Division of Water Resources or the Central Utah Project pages as second sources), and
> the lab-machine run time once a student pilot reports it. (2) `lab-12/README.md`: the NFPA 1710
> travel-time figures (240 s and 480 s at 90 %) are from secondary sources; confirm against the
> current edition's text or a primary NFPA page and cite it, or soften the sentence. (3) The
> `TODO(instructor)` lists at the foot of Labs 1 to 4 and 12: items marked DONE can be deleted,
> the rest either done now or moved to this file. (4) `docs/policies/ai-policy.md` and
> `university.md`: confirm the quoted university wording is current (link the source) and drop
> the note. Never mention earlier handout versions in student-facing text; put history in HTML
> comments. (5) `lab-05/README.md` Step 13 (changed October 12, text only): in ArcGIS Pro, confirm
> that Clip with the UGRC service as input fails and record the error; that Select By Location ▸
> Data ▸ Export Features exports only the selection and honors the Output Coordinate System
> environment; and that clipping `NHD_Local` still gives 36 lines and about 37.4 km. Close the
> STEP 13 NHD EXPORT note in the migration notes. Check every link on each page you touch,
> `mkdocs build --strict`, commit. Do not push.

---

## 6. Deck graphics still owed (generated figures, plus two ArcGIS Pro sessions)

`grep -rn "TODO(graphic)" slides --include=*.md | grep -v retired` lists 22 notes: Week 11 has 13
(the coordinate-systems and GPS decks), Week 5 two, Week 13 two, and one each in Weeks 2 (a plan
file, ignore), 4, 6, 9 and 12. These want **generated** figures under CLAUDE.md rule 9, not
screenshots. Separately, ROADMAP still lists ArcGIS Pro captures for the Week 4 remote-sensing
deck (MODIS band slides; `tools/week04-arcgis-capture-plan.md`) and the Georectifying deck
(Georeference tab, control points, residuals table), and an old note about Week 2 ModelBuilder A
slides that the September 7 to 8 revision already resolved; reconcile that row.

**Prompt**

> Clear the `TODO(graphic)` notes in the CE 414 decks: `grep -rn "TODO(graphic)" slides
> --include=*.md | grep -v retired`. Read `tools/slide-conversion-guide.md` (rules 7 to 9) and
> the memory note on the OpenAI key first. For each slide, decide whether the note is right that a
> figure is needed (an "ask" slide deliberately bare before its evidence slide stays bare; delete
> the note and say so); otherwise generate the figure with the OpenAI image skill, save it in the
> deck's `images/` folder with a descriptive name, place it with the deck's existing `bg right`
> or `h:` conventions, and write the alt text from what the image actually shows. Never put a
> generated image where a real ArcGIS Pro capture is implied. Then, in a separate ArcGIS Pro
> session at 175 % (read `tools/screenshots/README.md` and the desktop-control memory note), take
> the Week 4 captures listed in `tools/week04-arcgis-capture-plan.md` and the Georeference tab,
> control-point table and residuals captures the Georectifying deck's conversion notes ask for;
> end with `setdpi.py 100` and `park.py Claude 966`. Render every deck you touch to PNG and look at
> each changed slide for overflow; run `tools/stamp_decks.py`; update ROADMAP's capture rows;
> commit. Do not push.

---

## 7. End of semester: close out and prepare Fall 2027

Not urgent until December. CE 414 moves to Canvas for Fall 2027, which is why the site, not the
LMS, holds the content.

**Prompt**

> Close out Fall 2026 for the CE 414 site. (1) `ROADMAP.md`: every row that says a thing is owed
> or pending is checked against the repository and either marked resolved with the date and
> commit, or kept with what is actually left; the capture and ModelBuilder-A rows are stale.
> (2) Write `tools/CANVAS_MIGRATION.md`: the list of everything Learning Suite holds for this
> course (assignments with due dates, the reading quizzes and where their generators live in the
> private repository, the participation items, the exam entries, the links to site pages), so the
> Canvas course can be built from it without opening Learning Suite; the memory note on Learning
> Suite has the course id and the instructor views. (3) For each lab, record the lab-machine run
> time and any student-pilot finding Dan passes on in the page's revision notes. (4) Collect the
> semester's numbers Dan wants to keep but not publish (quiz and exam statistics, grade
> distribution) in the private repository's `plans/`, never here. (5) Archive the semester:
> tag `main` as `fall-2026` after the final push. Report; do not push or tag without Dan's word.

---

## Housekeeping an agent can do any time

- `C:\Ames\_old\` holds the pre-renumbering copies of three GUI projects and
  `C:\Ames\Lab07HAND\ParamTest.gdb` is a leftover; both can go once Dan agrees (they are not in
  any repository).
- `slides/week-02` still owes an anonymized prior-year report page for Part B (no PDF exists;
  Dan said he would show named prior-year PDFs in class instead, so this may simply be dropped).
- The Week 3 Thursday hands-on activity never got its Learning Suite participation item.
- **First Windows run after the sensitivity move.** Clone `danames/ce414-private` beside this
  repository at `C:\Users\dpame\code\` if it is not there, then run any one of the changed model
  scripts (Lab 5's `run_model.py 5000` is the quickest) and its `build_figures.py` to confirm they
  write to and read from `ce414-private/sensitivity/`.
- The Mac checkout has a leftover `git stash` entry (`autostash`, October 11) holding the Lab 5
  Step 13 edit that is now committed; `git stash drop` once Dan agrees.
- Memory notes under `~/.claude/projects/.../memory/` written before October 8 use the **old**
  lab numbers (7 Avalanche, 8 Butte, 9 Interpolation); `lab-renumber-oct08.md` has the mapping.
