# Lab 3 — no-GUI pilot, round 2

Run 2026-09-18 against `docs/assignments/lab-03/draft.md` at 0c868b2 ("round 2: back to a manual
one-week lab"). Per section 6 of `tools/lab-conversion-guide.md`, with the instructor's override:
Lab 3 is deliberately manual (no model) and must fit in one week. Absence of a model is not
reported.

Headless work only, in a new folder `C:\Ames\Pilot03b\` (`Pilot03b.gdb`), ArcGIS Pro 3.7.1
`arcgispro-py3`, stand-in geometry in NAD 1983 UTM Zone 12N. `C:\Ames\Lab03\`, `Lab03Walk\` and
`Pilot03\` were not touched. Scripts, re-runnable:

- `C:\Ames\Pilot03b\pilot03b.py` — Calculate Geometry Attributes into pre-existing Double fields; the
  buffer test of "area uncertainty ≈ perimeter × mean check error"; shift, jitter and scale cases.
  Results also in `pilot03b_results.json`.
- `C:\Ames\Pilot03b\pilot03b_crs.py` — geodesic vs planar area, UTM 12N vs Web Mercator.
- `C:\Ames\Pilot03b\origin.py` — where (0, 0) falls in UTM 12N and two State Plane zones.

**Headline.** The measurement tooling is right: every Calculate Geometry property/unit the page names
exists and writes into pre-existing Double fields. The draft is clean on the house rules. But the
**order of the steps does not work**: the Georeference tab must stay open and unsaved from Step 4 to
the end of Step 10 (a multi-sitting span on lab machines), and Step 10 then discards the run that
Map 2 has to show. Three of the page's check-value interpretations are also wrong in ways the
measurements show (Step 9 TIP, Step 9 WARNING, Step 6 TIP), and the Step 9 uncertainty formula is a
worst case, not a typical error.

Clean: rubric rows 10/10/10/10/10 = 50, extra credit 5 (`check_rubric.py`); all 26 referenced images
exist; no bare "Pro"; no British spelling; every step heading titled (two or three words, Step 0's
four sanctioned by the guide); no ModelBuilder, Summary Statistics, Buffer, envelope, Figure C or
five-run leftovers in student text (they appear only in the migration comment, which is correct);
control-point, check-feature, run and field counts agree everywhere (8 + 3 = 11, six features,
three runs, four fields).

---

## Ranked findings

### Blocking — a student cannot finish the lab as written

**1. Map 2 cannot be made: Step 10 throws away the run it must show.** Line 636: "When you are done,
switch back to run 1, click **Save** on the Georeference tab, and close it." Deliverables Map 2
(line 668) and rubric Sensitivity bullet 3 (3 points) require the sheet "as re-solved in run 2 or
run 3". After line 636 that solution no longer exists anywhere, and one raster cannot sit in two
positions for two layouts. Nothing on the page says to keep a copy.
*Fix:* in Step 10, after the run chosen for Map 2, write it to a new raster with the Save group's
save-as-new control (see Figure 4: the Save group has four unlabeled icons — **verify the name**),
e.g. `Sheet_run3.tif`; then return to run 1 and **Save**. Map 2 uses the copy. Say so in Step 10
and in the Map 2 deliverable.

**2. The Georeference session must stay open, unsaved, from Step 4 to the end of Step 10.** Step 4
WARNING (lines 394–398): do not Save and close until Step 10; "if you must stop, either leave ArcGIS
Pro open, or save and be prepared to re-collect your points." Steps 6–9 (error lines, all
digitizing, attributes, measurement) sit inside that window: roughly 3–5 hours of work (time table
below), which is at least two sittings for most students, on lab machines that log off. It also
assumes, unverified, that Create Features editing works while the Georeference tab is active.
*Fix (reorder, no new work):* Step 6 Check Your Error → **Step 7 Test the Transformation** (today's
Step 10, saving the Map-2 copy per finding 1, then Save run 1 and close) → Step 8 Digitize → Step 9
Attributes → Step 10 Measure. The digitized features do not move with the transformation (the page
says so, line 616), so nothing is lost by digitizing after the save. Move question 3's "and your
measured area" clause into the measurement step. Also tell students to export their control points
at the end of Step 5 as insurance (verify the button). This removes the "leave ArcGIS Pro open"
instruction entirely.

**3. "Control points shown" on Map 1 has no instruction.** Deliverables line 667 and rubric Map 1
bullet 6 (1 point) require them; Figures 13 and 14 show them as pins. Control points draw only while
the Georeference tab is open; after the Save-and-close in Step 10 they are gone, and the page never
says how to put them on a layout. Carried unchanged from the assigned page.
*Fix:* verify in the GUI walk what works in ArcGIS Pro 3.7.1 (exporting the links and adding them
as a point layer, or a control-point display option), and write it as a numbered sub-step. If there
is no clean route, drop the bullet and move its point.

### High — wrong statements a careful student will act on

**4. Figures 10 and 11 model the opposite of what the step asks.** Figure 10's four features are
*Childhood Home, Westfield North County Mall, Del Dios Middle School, Grandma's Farm* in a layer
named `Locations`, with **one** field (`Location_Name`). Figure 11 labels the same four and shows
"Roads" traced along modern I-15 and CA-78. Step 7 says to digitize what is **gone** (line 466),
Step 8 says the name comes from the historic sheet "exactly as printed" (line 505) and that there
are **four** fields. The alt text is accurate to the images, so the defect is the images.
*Fix:* re-shoot on the Stansbury walk with four filled fields and historic names (these are already
owed as Figures 7–11). Until then, add a caption line: "This capture predates the four-field
attribute set and shows modern places; yours should show historic ones."

**5. Step 9 TIP's failure interpretation cannot happen** (lines 573–574: "a number that disagrees
wildly with the feature's size … means the map's coordinate system is still Web Mercator").
**Measured:** a 1,497 km² polygon near the Great Salt Lake has geodesic area **1497.193 km² in both
UTM 12N and Web Mercator**. Geodesic measurement is independent of the coordinate system, and
Calculate Geometry Attributes **refuses** planar `AREA` on a Web Mercator feature class (ERROR 000800,
only geodesic properties offered). The Step 0 WARNING (line 286, "every distance and area you
measure later is wrong") is likewise not true of anything this lab measures with Calculate Geometry.
*Fix:* Step 9 TIP: a wildly wrong area means the wrong unit, the wrong polygon, or a sheet whose
scale is badly off — go back to Step 6's error lines. Step 0 WARNING: keep "set a projected system",
but give the real reasons (feature classes inherit it; the Measure tool and the map's scale bar
use it; planar numbers in Web Mercator are 1.7× too big at this latitude — measured 1.75× for the
lake, 1.68× for a Utah-sized box).

**6. Step 9 WARNING overstates the geodesic/planar difference** (line 558: "on a sheet the size of a
state it is not" small). **Measured** in UTM 12N: 0.05 % on the 1,497 km² polygon, **0.04 % on a
Utah-sized 238,632 km² box**, 0.06 % on a 50 km² rectangle. The guide reserves WARNING for silent
wrong answers; this is neither. Same as round-1 finding 28, now with a stronger false claim.
*Fix:* demote to a NOTE: "In a UTM or State Plane zone the geodesic and planar numbers differ by
well under a tenth of a percent; use geodesic anyway, it is the one that does not depend on your
projection."

**7. Step 9's uncertainty rule is a worst case, and says nothing about when it fails.** See the
measurement section below. In short: `perimeter × d` is the area change if **every point of the
outline moves outward (or inward) by d**. It is accurate to 2–5 % for d up to about 5 % of the
feature's size; it is asymmetric (+P·d+πd² out, −(P·d−πd²) in); it overstates the change for a
hand-traced wiggly outline (0.76–0.83 × P·d at d = 250–500 m); and it is meaningless once d
approaches half the feature's narrowest width (the inward buffer vanishes). Most important for the
lab's own logic: a **pure shift changes the area by exactly zero**, and random per-vertex error of
size d changes it by about **4–5 % of P·d**. Only a scale-type error (the outline growing or
shrinking) realizes the full P·d.
*Fix:* reword lines 561–568 as "at most about", and add two sentences: "This is the worst case — an
outline that grew or shrank by your error all the way round. A sheet that is merely shifted keeps
its area; it is the location that is wrong. If perimeter × error comes out larger than half your
area, say that this area cannot be measured from this sheet at this accuracy." Then question 3 has
something real to argue about.

**8. Step 6 TIP's diagnosis is backwards for a least-squares fit** (lines 460–462: "If all three
point the same way, the whole sheet is shifted, which is usually the old survey's error"). A 1st
Order Polynomial fitted by least squares has a translation term, so the control-point residuals sum
to zero in x and in y: any whole-sheet shift is absorbed by the fit. Three independent check errors
that point the same way mean **that part of the sheet** is displaced relative to where the control
points pinned it — local distortion (a fold, a survey error in that region), or checks bunched in one
area — not a shifted sheet. Rubric Georeferencing bullet 4 (1 point) grades this conclusion.
(Established from the mathematics of the fit, not measured in the GUI; confirm that ArcGIS Pro's
polynomial solve is least squares, which Esri's georeferencing overview states.)
*Fix:* "If all three point the same way, the part of the sheet they sit in is displaced relative to
the parts your control points pinned — check whether they are bunched together. If they point in
different ways, the sheet is bent in ways an affine transformation cannot follow." Also relevant to
finding 7: a local shift barely changes a polygon's area.

**9. Step 2's "Gulf of Guinea" is wrong for this page's own order of work.** Step 0 sets a UTM or
State Plane system *before* Step 2 adds the scan. An image with no spatial reference is drawn in the
map's coordinates, so the speck lands at that system's origin. **Computed:** UTM 12N (0, 0) is
**0.0° N, 115.49° W**, the eastern Pacific; Utah Central State Plane (feet) is 20.5° N, 116.0° W.
Figure 1 was captured in a map whose origin is 0°, 0°. A student who finds the speck in the Pacific
will think something is wrong.
*Fix:* "at the origin of your map's coordinate system — for UTM Zone 12N that is on the equator in
the Pacific, west of Ecuador; in a map left in Web Mercator it is off West Africa (Figure 1)."
Verify in the GUI walk.

### Medium

**10. Run 3 needs points Step 4 told students not to collect.** Step 10 run 3 is "only three, all near
the middle of the sheet" (line 590); Step 4 says put points near all four corners and "avoid
clusters" (lines 371–376). A student with eight well-spread points may have none near the middle.
*Fix:* Step 4: "include two or three near the middle as well — Step 10 uses them"; or define run 3
as "the three of your points that are closest together".

**11. Step 10 depends on two unverified GUI behaviors, and the second one decides whether run 1 can
be restored.** Lines 592–597: switching links off with a check box in the Control Point Table (the
VERIFY comment says the wording assumes it), and line 398's VERIFY on whether reopening restores
links. If links can only be deleted, "switch back to run 1" (line 636) is impossible without a saved
links file. Fold into finding 2's fix: export links first, whatever the answer.

**12. Deliverables vs rubric, both directions.**
- Rubric → no deliverable: Map 1's "title stating the transformation used", "text box with author,
  date, map projection, and the sheet's title and date", and "symbolized by type … with a legend"
  (line 747) are not in the Map 1 description (line 666–667). Copy them across.
- Rubric Digitizing bullet 1 (3 points: "each geometry type in its own feature class in the map's
  coordinate system") has no deliverable that evidences it; nothing asks for the geodatabase or the
  feature-class names. The Data table (line 138) says to *record* them. *Fix:* add "your feature
  class names, geometry types and coordinate system" to the report list.
- Step 9 item 4 computes `Length_km` for the line feature class; it appears in no deliverable and no
  rubric bullet. Drop it (saves time) or add it to the feature table.
- The AI-use NOTE requires "one line at the end of your report"; the Deliverables list omits it.

**13. The worked example is offered for student use before anyone has georeferenced it from ground
features.** Line 209: "You may use it for your own lab." `tools/lab03/GEOREF_FINDINGS.md` records a
graticule-based fit and three ground checks; its own "next steps" item 1 (georeference from ground
features, as a student would) is still owed. The page requires eleven stable features and forbids
shorelines and river banks (line 374–375); on an 1850 sheet of the Great Salt Lake country it is not
yet shown that eleven exist. Resolve in the GUI walk before promotion, or soften to "worth looking
at".

**14. Figure/alt/caption mismatches (small).** Figure 12's caption says the menu shows "the minimum
control points each one needs", but the capture cuts off Spline's line (the table's "10" for Spline
is not visible in the figure). Figure 6b's alt text lists "Raster Dataset", which is below the crop.
Figure 5's caption says the sheet "is plainly still in the wrong place"; in the image, after Fit to
Display, it sits roughly over Escondido — "not yet fitted" is safer.

**15. Step 10 TIP may name two runs.** "One of these runs will give you the best RMS number" (line
633) — if the student picks **Spline** for run 2 (allowed with ten or more points), run 2 and run 3
both report an exact fit. Question 1 already handles "very close to zero"; change the TIP to "One or
two of these runs …".

**16. Analysis Tools intro contradicts its own Add row.** "These are the tools you will use for the
first time in this course" (line 229–230), then the Add row says it "does the same job" as Lab 1's
Add Field. Change the intro to "the tools and buttons this lab relies on".

**17. Step 0 item 4, "On the View tab, open Map Properties ▸ Coordinate Systems"** — carried from
the assigned page and not verified here; the documented route I know is right-click the map in the
Contents pane ▸ Properties. Verify in the GUI walk.

### Low

**18.** The tool's unit label is "Square Kilometers" (from `CalculateGeometryAttributes.tool` resources
in the install); the page writes "Square kilometers" (line 550). Cosmetic.

**19.** Line 155–156, "Anything published in the United States before 1930 is in the public domain":
as of 2026 it is 1930 or earlier. True as written, just conservative.

**20. Drift from the original handout.** The original required a U.S. state sheet **before 1900**
*and* a European city **before 1800**. The draft keeps the assigned page's single sheet (the second
sheet's role is now Map 2's re-solve) and softens the date to "older than 1900 if you can" (line 166).
The additions (polygons, four attributes, error lines, one measurement) extend the original rather
than replacing it, and the 50-point total is kept. I judge this acceptable, with one thing lost that
is worth a sentence in class: the contrast between georeferencing a small-scale state sheet and a
large-scale city plan.

### Round-1 findings: status

Gone with the model (no longer apply): 1, 2, 3, 4, 11, 12 (Buffer row), 20, 21, 22, 27.
Fixed: 5 (Map 2 now carries 3 points in Sensitivity), 7 (no "old minimum"), 8 (Lab 1 Web Mercator
reworded), 9 (Step 9 cited), 10 (eleven features), 13 (Figure 2 provenance), 14 (version claim),
15 (Figures 6a/6b in Step 6), 16 (`target="_blank"` restored), 18 (one baseline, "run 1"),
23 (Example Maps NOTE and Figure 14 alt text), 24 (meters), 25 (headings), 26 (topoView wording).
Partly fixed: 6 (run order now removes points last, but see findings 2 and 11), 17 (graticule is
now its own `##` section and states that it needs a graticule; still no hosted data or check
values), 19 (question 1 reworded; see finding 15). **Still open and worse:** 28 (see finding 6).

---

## Stated / measured / match

ArcGIS Pro 3.7.1 `arcgispro-py3`, `C:\Ames\Pilot03b\Pilot03b.gdb`, NAD 1983 UTM Zone 12N
(EPSG 26912) unless stated.

| # | Draft says | Measured | Match |
| --- | --- | --- | :-: |
| 1 | Step 9: Calculate Geometry, **Area (geodesic)**, **Square kilometers** into a pre-added Double `Area_km2` | `AREA_GEODESIC` + `SQUARE_KILOMETERS` wrote 50.0311 km² (50 km² planar rectangle) and 28.2910 km² (r = 3 km circle); field stayed **Double**, no duplicate field (6 fields total) | yes |
| 2 | **Perimeter length (geodesic)** in **Kilometers** into pre-added Double `Perim_km` | `PERIMETER_LENGTH_GEODESIC` + `KILOMETERS`: 30.0093 km, 18.8552 km; Double | yes |
| 3 | **Length (geodesic)** in **Kilometers** into `Length_km` | `LENGTH_GEODESIC`: 15.0047 km for a 15.000 km planar line; Double | yes |
| 4 | Step 6: **Length (geodesic)** in **Meters** into Double `Error_m` | 500.150 / 200.062 / 400.116 m for 500 / 200 / 400 m planar lines; Double | yes |
| 5 | Dialog labels "Area (geodesic)", "Perimeter length (geodesic)", "Length (geodesic)", "Kilometers", "Meters" | All present verbatim in the tool's resource file in the install; area unit label is "Square **K**ilometers" | yes (case) |
| 6 | Step 9 TIP: millions ⇒ unit is square meters | 50 km² = 5.0 × 10⁷ m² (round 1 measured the same) | yes |
| 7 | Step 9 TIP: wildly wrong area ⇒ map still in Web Mercator | Geodesic area 1497.193 km² in UTM 12N **and** in Web Mercator; planar `AREA` refused on a Web Mercator feature class (ERROR 000800) | **no** — finding 5 |
| 8 | Step 9 WARNING: geodesic vs planar small for a county, not small for a state | UTM 12N planar/geodesic = 0.9995 (1,497 km²), **0.9996 (Utah-sized, 238,632 km²)** | **no** — finding 6 |
| 9 | Step 0 WARNING: Web Mercator makes areas wrong "by a factor that grows with latitude" | Planar Web Mercator / geodesic = 1.752 (lake, ~41° N), 1.684 (Utah box) — true of **planar** numbers only | partly — finding 5 |
| 10 | Step 9: area uncertainty ≈ perimeter × mean check error | True for a uniform outward/inward displacement with d small: within 2 % at d/r ≤ 0.03, within 5 % at d/r ≤ 0.1 (circle, square, strip, star). See table below | yes, within limits — finding 7 |
| 11 | Same formula, as a ± | Outward and inward differ by 2πd²: circle r = 3 km, d = 500 m → +10.21 / −8.64 km² against ±9.42 | asymmetric |
| 12 | Same formula, hand-traced outline | Wiggly "lake" (A 28.4 km², P 39.9 km, 2.1× a circle's perimeter): out/in = 0.83/0.77 × P·d at d = 250 m, 0.76/0.64 at 500 m | overstates |
| 13 | Same formula, small feature | Pond r = 250 m: d = 100 m → P·d = 0.157 km² on a 0.196 km² pond (80 %); d = 250 m → P·d = 0.39 km², **2× the area**, inner buffer empty | breaks down |
| 14 | Same formula, if the sheet is shifted (Step 6 TIP's "all three point the same way") | Rigid shift of 100 / 500 / 1,000 m → area change **0.000** | formula does not apply |
| 15 | Same formula, random per-vertex error | 100-vertex outline, RMS vertex error d, 200 trials: SD of area = 0.175 / 0.912 / 2.216 km² against P·d = 3.99 / 19.9 / 39.9 → **4.4–5.6 % of P·d** | formula ~20× too big |
| 16 | Same formula, scale-type error (outline grows by d) | Traced lake scaled so its equivalent radius grows by d: 1.92 / 10.24 / 22.04 km² against P·d 3.99 / 19.9 / 39.9 → ~0.5 × (because the traced perimeter is wiggle-inflated) | overstates ~2× |
| 17 | Step 2: unreferenced scan lands in the Gulf of Guinea | After Step 0 sets UTM 12N the origin is 0.0° N, 115.49° W (Pacific); Utah Central SP feet 20.52° N, 116.05° W | **no** — finding 9 (predicted; verify in GUI) |
| 18 | Rubric rows ten each, total fifty, extra credit five | 10/10/10/10/10 = 50; +5 | yes |
| 19 | All figures and icons exist | 26 referenced, 26 present | yes |
| 20 | Figure 12 shows every transformation's minimum | Spline's requirement is cropped off | partial — finding 14 |
| 21 | Step 4 minimum-points table | Matches Figure 12 for the seven visible rows (1, 3, 3, 6, 10, 3, 4) | yes |
| 22 | Internal links (`../../arcgis-tips.md`, `../../policies/ai-policy.md`, `README.md`) | All exist | yes |
| 23 | External links | topoView, David Rumsey, both Wikimedia, three pro.arcgis.com: 200. loc.gov (item and collections) and usgs.gov: 403 to curl (bot block) — not opened in a browser this round | partly unchecked |

**Buffer test in full** (planar, UTM 12N; `dA_out` = area gained by buffering outward d, `dA_in` =
area lost buffering inward d; ratios to P·d):

| Shape | A km² | P km | d = 10 m | 100 m | 500 m | 1,000 m |
| --- | ---: | ---: | --- | --- | --- | --- |
| Circle r 3 km | 28.27 | 18.85 | 1.002 / 0.998 | 1.017 / 0.983 | 1.083 / 0.917 | 1.167 / 0.833 |
| Square 4 km | 16.00 | 16.00 | 1.002 / 0.997 | 1.020 / 0.975 | 1.098 / 0.875 | 1.196 / 0.750 |
| Strip 20 × 0.5 km | 10.00 | 41.00 | 1.001 / 0.999 | 1.008 / 0.990 | 1.038 / 0.488 ∅ | 1.077 / 0.244 ∅ |
| 8-point star | 11.02 | 31.14 | 1.000 / 0.992 | 0.999 / 0.918 | 0.995 / 0.592 | 0.991 / 0.350 |
| Traced lake | 28.42 | 39.86 | 1.001 / 0.999 | 0.952 / 0.944 | 0.761 / 0.643 | 0.731 / 0.498 |
| Pond r 250 m | 0.196 | 1.571 | 1.020 / 0.980 | 1.200 / 0.800 | 2.000 / 0.250 ∅ | 3.000 / 0.125 ∅ |

∅ = inward buffer empty (the polygon vanished). Rule of thumb from these numbers: P·d is good to
about 5 % when d is under a tenth of the feature's narrowest half-width and the outline is smooth;
it is useless when d is more than about half that width, which is where P·d exceeds half the area.

---

## One-week time estimate

First-time student, working alone, outside the 75-minute class sessions.

| Step | What | Estimate |
| --- | --- | --- |
| 0 | Project, basemap, coordinate system | 10–15 min |
| 1 | Find a sheet, apply the eleven-feature test, record six facts, maybe convert a PDF | 45–120 min |
| 2–3 | Add scan, Fit to Display, transparency | 15 min |
| 4 | Eight or more spread control points, three reserved | 30–60 min |
| 5 | Read residuals, fix an outlier | 15–30 min |
| 6 | ErrorLines class, three lines, field, Calculate Geometry | 20–30 min |
| 7 | Six or more features in three feature classes | 45–90 min |
| 8 | Four fields × three classes, fill, label × 3 | 30–45 min |
| 9 | Two/three fields, Calculate Geometry, uncertainty arithmetic | 15–25 min |
| 10 | Three runs, nine Measure checks, table, three questions (+ saving the Map-2 copy) | 45–75 min |
| Maps | Two full-page layouts | 90–150 min |
| Report | 2–3 pages, metadata answers, feature table, three questions | 120–180 min |
| Peer review | Read someone else's, act on yours | 30–60 min |
| **Total** | | **≈ 8.5–15 h, median about 11 h** |

Steps 4–10 alone are about 3.5–6 hours, which is why finding 2 matters: that span will not happen in
one sitting.

**Verdict: borderline, over one week for most students unless class time is given to it.** A 3-credit
course with two 75-minute sessions supports roughly six to seven hours of outside work a week; the
median here is about eleven. It fits if the Thursday session is a working lab session (as Week 3's
was) and Step 1 is shortened. Compared with the assigned page, this draft adds about 1.5–2.5 hours
(error lines, polygon class, three extra fields, the measurement, the extra run). The cheapest cuts,
in order: let students use the Stansbury sheet or a named topoView sheet so Step 1 is 15 minutes
(saves up to 1.5 h, once finding 13 is resolved); drop `Length_km` (finding 12); make the attribute
fields required only on one feature class or cut to three fields; make Map 2 a half-page inset or a
screenshot figure in the report rather than a second full layout (saves 45–60 min). The optional
graticule adds another 1.5–2 hours and is correctly optional.

---

## What I could not check without the GUI

1. Everything on the Georeference tab: Fit to Display, Add Control Points, whether the scan moves
   with one or two points (Step 4, line 359), the Control Point Table's contents and whether links
   can be switched off with a check box (VERIFY at line 595), the names of the four unlabeled Save
   group icons (Figure 4), and whether reopening Georeference on a saved image restores its links
   (VERIFY at line 398).
2. Whether Create Features editing works while the Georeference tab is still active (finding 2).
3. How to show control points on a layout after the Georeference tab is closed (finding 3).
4. Where an unreferenced scan actually lands in a map already set to UTM (finding 9 — computed, not
   seen).
5. The Measure tool's default mode (planar or geodesic) and units in a UTM map; Step 10's check
   distances depend on it. In UTM 12N the difference is ~0.03 %, so it only matters in Web Mercator.
6. The right-click **Calculate Geometry** dialog from an attribute-table header: that it opens with
   the field preset and uses the same labels as the tool (I checked the tool's resource strings, not
   the dialog).
7. Step 0's "View tab ▸ Map Properties" route, and whether the new-project Location box refuses a
   typed path (line 275).
8. Whether new feature classes made from the Catalog pane are added to the map automatically
   (Step 7 item 2 assumes it).
9. Whether eleven stable, identifiable features exist on the Stansbury sheet (finding 13).
10. Whether topoView still offers a JPEG alongside the GeoTIFF (round 1's item 5, still open).
11. The loc.gov and usgs.gov links in a browser (403 to curl; round 1 opened the usgs.gov and
    loc.gov collections pages in a browser, but the loc.gov **item** page was not checked either
    time).
12. Real check values: still none, because every student's sheet differs. The numbers above prove
    the tooling and the arithmetic on stand-in geometry, not anything a student will see.
