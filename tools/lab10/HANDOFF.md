# Lab 10 test on the home Dell: handoff

For a new Claude Code session on Dan's home Dell (Windows, ArcGIS Pro). The aim is to show, on a
second machine, that Lab 10 (Least Cost Path Power Lines, due Saturday of Week 11) works as
published. This covers the scripted reference run, the grading lookup, and the build from the student
page that is still owed (the hidden `TODO(instructor)` at the end of
`docs/assignments/lab-10/README.md`). Until now, everything was built on the instructor laptop
(ArcGIS Pro 3.7.1).

Read `CLAUDE.md` first. Its rules apply here too: never invent a value, write "verify this" for anything
not seen in ArcGIS Pro, and do not push to `main`.

## 0. Setup

1. Clone both repositories **side by side** in the same parent folder. The scripts find the
   private one at `..\ce414-private` relative to the public checkout:

   ```
   <parent>\ce414-gis-applications   https://github.com/BYU-Hydroinformatics/ce414-gis-applications
   <parent>\ce414-private            https://github.com/danames/ce414-private  (private)
   ```

   If they are already cloned, `git pull` both. You need public commit `9aa66a8` or later and private
   `c68cb78` or later. Those commits renumbered the Lab 10–12 sensitivity files and grading lookups.
   Older checkouts write Lab 10's results to `lab11_sensitivity.json`.
2. Use ArcGIS Pro's Python, not a system Python:

   ```
   "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts\propy.bat"
   ```

   Below, `propy` means that full path.
3. Record the ArcGIS Pro version (**Project** ▸ **About**) and confirm that **Spatial Analyst** is
   licensed (**Project** ▸ **Licensing**). Every check value was measured in 3.7.1. If the Dell runs a
   different version, a difference in the last digit is a finding to report, not a failure to fix.
4. The scripts write to `C:\Ames\...`. Make sure `C:\Ames` can be created and written to.
5. Confirm that the package the students download is the same file as the one in the repository:

   ```
   certutil -hashfile docs\data\lab10-power-line.zip SHA256
   ```

   Expected: `d9eca5207b812b1d3ac78b27e188236783d04888a2a55513ad1701a093223236`, 17,984,171 bytes.
   Also download it from
   `https://byu-hydroinformatics.github.io/ce414-gis-applications/data/lab10-power-line.zip` and check
   that the hash matches.

## A. Scripted reference run (no GUI, about 10–20 minutes)

From `tools\lab10`:

```
propy run_model.py
```

This unzips the package to `C:\Ames\Lab10\ref` and builds `Ref.gdb`. It runs the baseline and six
sensitivity runs, then rewrites two files:

- `tools\lab10\check_values.json` (public)
- `..\ce414-private\sensitivity\lab10_sensitivity.json` (private)

**Pass:** `git diff --stat tools/lab10/check_values.json` in the public repository and
`git diff --stat sensitivity/lab10_sensitivity.json` in the private one both show **no change**. If
either changed, show the differing keys. **Do not commit the new values.** Report them and restore
the file with `git checkout -- <file>`.

Record how long the run took.

## B. Grading lookup

The lookup is `..\ce414-private\grading-oracles\lab10_personal_lookup.csv`: one row for every
BYU ID ending from 00 to 99, giving the length, cost and crossings for that student's Line_Weight.
Graders check reports against it.

- **Spot check (minutes; run A first, since it builds the score rasters):**

  ```
  propy -c "import run_model as rm; rm.setup(); [print(d, rm.route(f'chk{d:02d}', 1, round(0.005*d, 3))) for d in (0, 2, 50, 89, 99)]"
  ```

  Compare `length_km`, `total_cost` and `river_crossings` with those rows of the CSV. The page itself
  gives two of them: ending **02** is 53.70 km, 652,118, 4 crossings; ending **89** is 54.95 km,
  707,263, 4 crossings.
- **Full sweep (optional, probably 1–2 hours; run it in the background):** `propy run_model.py personal`
  rewrites the CSV. **Pass:** `git diff` on the CSV in the private repository is empty.

## C. Build from the student page (the owed pilot)

This needs ArcGIS Pro's GUI. Dan can do it at the keyboard, or the session can do it with computer
use if it has that. Work from the **live page**, as a student would, not from the repository source:
`https://byu-hydroinformatics.github.io/ce414-gis-applications/assignments/lab-10/`.

1. Make the project folder `C:\Ames\Lab10Dell\` (the page says `D:\Smith\Lab10\`, which is the lab
   machines' D: drive). Download the zip from the page and follow Steps 0–7 exactly as written. Build
   the model by hand in ModelBuilder. Don't use `gui_project.py`: it needs a template project that
   exists only on the laptop, and setting up the project by hand is part of the test.
2. After the run inside ModelBuilder (Step 7), **before any run from the tool dialog**, check every
   intermediate dataset:

   ```
   propy tools\lab10\check_gui.py C:\Ames\Lab10Dell\Lab10.gdb
   ```

   Every count, range and class table should match the page's **Check the result** tips and
   `check_values.json`.
3. Do Step 8: one run from the tool dialog at the defaults, with the `_Base` names. Run
   `check_gui.py C:\Ames\Lab10Dell\Lab10.gdb Route_Base` again. The route should be **56.09 km**, with
   **744,018** at the destination (read with **Explore**, as the page says) and **4** crossings
   (Pairwise Intersect). Confirm that the dialog run deleted the non-parameter datasets, as the page's
   warning says.
4. Do Step 9's runs (L0, L2, S5, and a personal weight: use 0.445 for the example ID ending 89). Record
   each run's length and cost, and try the **Measure** tool for the "largest distance from the baseline"
   column. Report how easy that measurement is to make consistently.
5. Make a rough version of each map. They don't need to be finished, only far enough to show that
   the definition-query approach in the page's warning works.

While you work, record:

- **Timings:** the run inside ModelBuilder, each run from the dialog, and the total time from an empty
  folder to a finished Step 9 table. The page says "about a minute and a half on a laptop".
- **Every mismatch between the page and the screen:** a label, a default, a pane location, a step that
  needed a click the page does not mention, or a dialog behavior (for example, output names resetting
  after validation). Quote the page's sentence and say what ArcGIS Pro actually showed.
- **Every place a student could go wrong** that the page does not warn about.

## Report

Write the results to `..\ce414-private\plans\lab10-dell-test-2026-11.md`. It goes in the private
repository because it may quote sensitivity and lookup values. Include:

- the machine, the ArcGIS Pro version, and the pass/fail for setup step 5 and for parts A, B and C
- the timings
- the page/screen mismatches, each with a proposed rewrite of the sentence
- any check value that did not reproduce, with the value you got

Commit the report in the private repository. Don't push either repository and don't edit the lab page.
Dan will decide which page changes to make and will publish them from the laptop.
