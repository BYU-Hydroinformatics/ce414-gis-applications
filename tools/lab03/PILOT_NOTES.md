# Lab 3 — no-GUI pilot

Run 2026-09-18 against `docs/assignments/lab-03/draft.md` (the version committed as "Lab 3 draft:
the model version, expanded", 7f9809f). Per section 6 of `tools/lab-conversion-guide.md`: one agent
reads the page as a first-time student, and reproduces the tool chain with the ArcGIS Pro Python.

Tool chain reproduced independently in a **new** scratch geodatabase, `C:\Ames\Pilot03\Pilot03.gdb`,
on stand-in geometry (two UTM 12N polygons of 528 and 64 km², three two-point lines of 522, 175 and
1,361 m). `C:\Ames\Lab03\` was not touched. Script:
`<scratchpad>/pilot03_chain.py` — reproduce with
`"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" pilot03_chain.py`.

**Headline: the five-tool chain in Step 9 is correct and runs. The instructions for *building* it in
ModelBuilder are not — two of the six numbered sub-steps cannot be performed as written.** Findings
1 and 2 are blocking; a student following Step 9 stops at item 1.

Rubric sums are clean (`tools/lab03/check_rubric.py`: 10/10/10/10/10, total 50, extra credit 5).
All 15 referenced images exist. No bare "Pro". All nine external links resolve.

---

## Ranked findings

### Blocking — a student cannot complete the step as written

**1. Step 9 item 4 (line 601) — the Buffer distance cannot be exposed as a parameter the way the
step says, and it is the one parameter Step 10 depends on.**
The step says "Right-click each of these and choose **Parameter** … the **Buffer distance** on tool
5." There is no Buffer-distance oval on the canvas to right-click; the distance lives inside the
tool. Lab 1 already records the verified two-step procedure (`docs/assignments/lab-01/README.md`
lines 489–490, confirmed in its GUI pilot): right-click the **Buffer** tool ▸ **Create Variable ▸
From Parameter ▸ Distance [value or field]**, which creates a blue oval, *then* right-click that
oval ▸ **Parameter** (or `Ctrl+P`). The draft skips the Create Variable half.
*Fix:* copy Lab 1's wording for the Buffer distance. The other two inputs (`ErrorLines`, the
measurable polygon) are dragged-in datasets and do already appear as ovals, so those are fine, and
`Ctrl+P` itself is correct — Lab 1 and Lab 2 both verify it.

**2. Step 9 item 1 (line 583) — "Press **Ctrl+R** to rename it `Measure Digitized Features`" is
wrong on three counts, and it is the first instruction in the step.**
Lab 2's revision notes record the GUI fact verified on 2026-09-06
(`docs/assignments/lab-02/README.md` lines 72–73 and step text at line 287): *a model cannot be
renamed while it is open in ModelBuilder, and `F2` silently does nothing*; the Catalog rename sets
the model's **Label**, not its **Name**, which is set in **Properties ▸ General**. `Ctrl+R` is not a
documented ModelBuilder shortcut at all. On top of that the proposed name contains spaces, which the
Name field will not take, and the page's own workspace box tells students never to use a space in a
name.
*Fix:* copy Lab 2's Step-0 paragraph verbatim, adapted to `Lab03.atbx`: close the ModelBuilder view
first, rename from the Catalog pane, and note the Label-vs-Name split. Pick a space-free name
(`MeasureDigitized`) and let the Label carry the readable one.

**3. Step 9 item 6 (lines 617–620) and all of Step 10 — re-running the model to the same outputs
fails, and nothing on the page prevents it.**
Item 6 explicitly tells students to run the model **twice** ("run it once with any value, read
`Error_Summary`, then run it again with the real number"), and Step 10 runs it three to five more
times. **Measured:** with `overwriteOutput` off — the default for a new ArcGIS Pro project — the
second Buffer to the same output fails with *"Failed to execute. Parameters are not valid."* Step 0
sets no geoprocessing environments at all and neither step says to rename outputs per run. Lab 2
handles exactly this case (its line 551: give each output a new name carrying the scenario in it,
`NDVI_class_06`, and note that the dialog warns when a name already exists).
*Fix:* either add the per-run output-naming instruction to Step 9 item 6 and Step 10, or have Step 0
set **Project Options ▸ Geoprocessing ▸ Allow geoprocessing tools to overwrite existing datasets**
and say what that costs. Lab 2's naming approach is better teaching — the student keeps all five
runs' numbers.

**4. Step 10 line 650 — "re-draw your three error lines" silently corrupts the model's own check
value.** **Measured:** re-drawing three lines into the same `ErrorLines` feature class gave
`FREQUENCY` = 6 and `MEAN_Error_m` = 2,137 m instead of 686 m; the mean is an average across every
run so far. That directly contradicts the Step 9 TIP (line 626), which tells students `FREQUENCY`
should be 3. Across five runs the student ends with 15 lines and a meaningless mean. The measurable
polygon gets an explicit "into a **new** feature class" at line 661; the error lines get nothing.
*Fix:* "into a new line feature class named for the run — `ErrorLines_A`, `ErrorLines_C` …" This is
also the reason the `ErrorLines` input is a parameter, which is worth saying.

**5. Rubric — Map 2 is required and carries no points.**
Deliverables (lines 719–720), Step 10 (line 681) and the Example Maps section all require Map 2. The
rubric's five rows are Write-up / Georeferencing / Digitizing+model / Map 1 / Sensitivity. Line 806
asserts "Map 2 is graded inside the sensitivity row" — but that row's five bullets (3+2+1+2+2 = 10)
never mention Map 2, so the claim is unbacked and Map 2 is worth zero. The guide's rubric template
and Lab 2's decided rubric (10 write-up / 10 model / 10 map 1 / **10 map 2** / 10 sensitivity) both
carry a Map 2 row.
*Fix:* add bullets inside Sensitivity that actually carry Map 2's points and re-sum to 10, or
restore a Map 2 row and rebalance. Either way this is a Deliverables-vs-Rubric gap of the kind
section 10 of the guide lists as definition-of-done.

**6. Step 10 — no way to get the control points back once they are deleted.**
Line 642: "To drop points from the solve, delete rows in the **Control Point Table**." Runs A (3
clustered) and B (4 corners) are subsets of run C's twelve. Deleting rows destroys them, so a
student who works the table top-to-bottom (A, B, C, D, E) loses the points C, D and E need and has
to re-collect the whole sheet. Step 4's NOTE (lines 416–418) warns only about the opposite
direction. The Georeference tab's save/load links file is the only way through this, and the page
never mentions it.
*Fix:* tell students to save their links to a file before deleting anything, and state the run
order — C, D, E first (all points), then B, then A. Needs GUI confirmation of the exact button name
and file extension.

### High — factual errors and house-rule violations

**7. Step 4 NOTE, line 416 — "Twelve is more than **the old minimum of eight**".** Direct violation
of CLAUDE.md's rule and section 3 of the lab guide: never refer to an earlier version of the handout
in student-facing text. Students have never seen "eight" and it only confuses. The migration notes
already carry the history (line 848). *Fix:* delete the clause; keep the reasons that stand on their
own — Step 10 re-solves with subsets, and 3rd Order Polynomial and Spline each need ten.

**8. Step 0 WARNING, line 317 — "Lab 1 made this mistake deliberately so you would recognize it."**
False. Lab 1 (README lines 224–227, and its pilot-3 note at line 634) says the UGRC shapefile
downloads *arrive* in Web Mercator, which makes the wrong answer the default outcome rather than a
hypothetical, and Lab 1's Step 0 sets the Output Coordinate System to stop it. Nothing was staged.
*Fix:* "Lab 1's data arrived in Web Mercator, which made the wrong answer the default; that is why
Lab 1 set the Output Coordinate System before measuring anything."

**9. Data TIP, line 205 — wrong step number.** "Step 7 asks you to measure that shape, and Step 10
asks you to measure it again." Step 7 digitizes; **Step 9** measures. This is in the one paragraph a
student uses to decide whether a sheet is usable before committing to it.

**10. Data TIP, line 202 — the pre-flight test is half the size of the actual requirement.** "Can
you name at least **six** features on it that you could also point to on a modern basemap?" Step 4
requires **at least twelve** control points (line 406) and Step 6 requires **three more** check
features that were explicitly *not* control points (line 474) — fifteen identifiable features. A
student who passes the six test, does the work, and then cannot find twelve has to abandon the sheet.
*Fix:* raise it to fifteen and say what the fifteen are for.

**11. Example Model, line 269 — parameter count disagrees with Step 9.** "The finished model has
five tools and **three parameters**." Step 9 item 4 (lines 599–602) exposes **six**: two inputs, the
Buffer distance, two output tables and the envelope. Item 6 then says "fill in the **three**
inputs" — which is a third number describing the same dialog. Related: line 270 says the model
"returns **four** things" and the rubric (line 800) grades "the four outputs", but the model writes
**three** datasets (`Area_Summary`, `Error_Summary`, `Uncertainty_Envelope`) carrying four-plus
numbers. *Fix:* settle on one count in all four places — "three outputs, six exposed parameters" is
what the model as described actually is.

**12. ModelBuilder Tools table — two rows are for tools Lab 1 already taught.** **Buffer** (line
258) has a row in Lab 1's own tool table (lab-01 line 172) and is used through that lab; the
attribute-table **Add** row (line 254) overlaps Lab 1's **Add Field** row (lab-01 line 174). Guide
section 2: "Every tool the steps use for the first time *in this lab* gets a row; tools from earlier
labs do not." *Fix:* drop the Buffer row. Either drop the Add row or say plainly it is the
attribute-table button rather than the geoprocessing tool used in Lab 1.

**13. Figure provenance, review box line 44 — Figure 2 is in the wrong group.** The box says
"Figures 2, 4 and 12 are 2026-09-09 captures." `images/lab03-georeference-button.png` (Figure 2)
carries a 2026-09-04 file date, the same vintage as Figures 1, 3 and 5, which the box dates to
2026-09-03. Figures 4 and 12 do carry 09-09 dates. *Fix:* move Figure 2 to the earlier group, or
re-shoot it.

**14. Important Note #2, line 297 — tells students something the page knows is false.** "The figures
were captured in **ArcGIS Pro 3.7.1**." The review box (line 45) and the migration notes both state
that Figures 7 to 11 are older captures from an earlier ArcGIS Pro. *Fix:* until 7–11 are re-shot,
say which figures come from which version, or drop the version claim and keep "the ribbon, the panes
and the button names are what to follow".

### Medium

**15. Figures 6a/6b are attached to the wrong step.** They sit in Step 7 (lines 508–515), but the
operation they illustrate — Catalog pane ▸ right-click the geodatabase ▸ **New ▸ Feature Class** —
is first performed in **Step 6** (lines 478–479), which has no figure at all. The first time a
student does it they get nothing; the second time they get two figures. *Fix:* move them into
Step 6, renumber, and have Step 7 refer back ("as in Step 6").

**16. Line 143 — `{ target="_blank" }` dropped from the ArcGIS Tips link.** The assigned Lab 3 page
(README.md line 142) and both reference labs carry it.
`docs/javascripts/external-links.js` retargets only cross-origin links and file downloads, so a
same-origin `.md` link is not covered by the site-wide script. A regression against the page being
replaced. (External links on this page need no annotation — the script handles them.)

**17. "Going further: the graticule" is in the wrong place and is not universally attemptable.**
Line 688 makes it an `###` inside **Step-by-Step Solution**, so it renders as a sixth step after
Step 10; the guide's anatomy puts `### Going further: …` under **## Data**. It also has no hosted
data and no check values, and a student whose chosen sheet has no printed graticule simply cannot
attempt the five points. *Fix:* move the section, and state up front that it needs a sheet with a
graticule — or resolve TODO(instructor) #1 and host the Stansbury sheet, which would also give this
lab its first published check values.

**18. Step 10's two tables use different baselines.** The measurement table (line 665) is headed
"Difference from run **C**"; the rubric (line 802) says "difference from **baseline**"; Deliverables
(line 716) lets the student nominate any run as their baseline and Step 10 line 681 says "pick one
run other than your baseline". If a student defends run D, the table's reference column is measuring
against something they did not choose. Pick one word and use it in all four places.

**19. Step 10 question 1 has a pre-announced tie.** "Which run gave the lowest total RMS error?"
Run A is three points on a 1st Order Polynomial, which the page itself already tells students
(Step 4 TIP, line 441) gives exactly `0.000000`; Spline (run E) forces an exact fit through every
point and should report the same. So the answer is a tie at zero, announced 200 lines earlier, and
the Step 10 TIP ("watch what the spline does, and watch what run A does") gives it away twice more.
*Fix:* ask instead why **two** runs tie at zero and what a shared zero tells you — that is the
lesson, and the tie makes it sharper. Needs GUI confirmation of what the Control Point Table reports
for a Spline.

**20. Step 9 tool 5 — the envelope carries misleading inherited fields, and has no Dissolve.**
**Measured:** Buffer wrote one polygon per input polygon (2 in, 2 out) and carried `Area_km2` and
`Perim_km` forward unchanged from the input, so the envelope's attribute table shows the *original*
polygon's area under a field named `Area_km2`. A student who opens the envelope to check its size
reads the wrong number. Harmless if Step 7's "its own polygon feature class" is followed literally
and holds one polygon; worth a sentence either way, plus a Dissolve decision if more than one
polygon is allowed.

**21. Step 9 TIP, line 625 — the check value does not say what it applies to.** "`Area_Summary`
should have exactly **one row**, with `FREQUENCY` equal to the number of polygons you digitized."
Step 7 says to put the measurable polygon in **its own** feature class, so the number is 1 for
almost every student — but "the number of polygons you digitized" reads as though it counts the six
features of Step 7. Guide section 3: say what a check value applies to. *Fix:* "…equal to the number
of polygons in the feature class you pointed the model at — one, if you followed Step 7."

**22. Three Deliverables items have no rubric bullet, and one rubric bullet has no Deliverable.**
No bullet grades: "a description of your **other** digitized features: what they are, what they were
called, and what is there now" (lines 739–740); "which transformation you chose" (line 729 — the
Georeferencing row grades the point count and distribution but not the transformation choice); and
"what it is and what is there now" for the measurable polygon (lines 736–737). Conversely, the
Digitizing row's first bullet grades features being "in the project geodatabase and in the map's
coordinate system", but Deliverables never asks the student to hand in the project or geodatabase.

**23. The two example maps fail the rubric they illustrate, and one contradicts the page's own
warning.** Both Figure 13 and Figure 14 have text boxes reading literally "Date" and "Projection"
with no author name — they fail the Map 1 bullet "Text box with author, date, map projection, and
the sheet's title and date", and neither title states a transformation or a control-point count
(Map 1's first bullet). The Example Maps NOTE (lines 786–789) calls out only the missing uncertainty
envelope. Separately, Figure 14's alt text describes "a georeferenced historic **pictorial** map of
Luxembourg" while the Data WARNING (lines 173–177) tells students a pictorial view is not a map and
will waste their afternoon. Looking at the image, it is a plan view drawn in a decorative style, so
the alt text is the defect — but as written the page's worked example contradicts its own rule.
Figure 13's caption asserts "an 1876 sheet"; nothing on the map carries a date and the migration
note says neither example has a usable source citation, so that is an unverifiable assertion.

### Low

**24. Line 361 — "a hundred **metres** from the origin".** British spelling; CLAUDE.md rule 8. (The
*number* is right — `GEOREF_FINDINGS.md` records exactly this for the Stansbury sheet, a raster
whose coordinates run −113 to −111 drawn ~113 m west of the origin. Only the spelling is wrong.)

**25. Two step headings run to four words** — Step 1 "Find a Historic Map" and Step 9 "Build the
Measurement Model" — against the guide's "two- or three-word title". Step 0's "Set Up the Project"
is sanctioned by the guide's own example. Very low priority.

**26. topoView row, line 186 overstates the collection.** "Every USGS topographic sheet ever
published, back to 1884." The USGS page (checked in a browser, see below) says the HTMC holds "more
than 178,000 maps" printed between 1884 and **2006** and "continues to grow", with the separate US
Topo series covering 2009 onward. *Fix:* "USGS topographic sheets from 1884 to 2006, plus the
current US Topo series."

**27. References omit Buffer**, the third geoprocessing tool new to Step 9; Calculate Geometry
Attributes and Summary Statistics both have entries. Add it or drop the other two.

**28. The geodesic WARNING over-claims at student scale.** Lines 611–615 use a `> [!WARNING]`, which
the guide reserves for a silent failure that gives a wrong answer. **Measured** on a 528 km² polygon
in NAD 1983 UTM Zone 12N: geodesic 528.292 km² against planar 528.000 km² — **0.055 %**. The text's
own claim ("on a sheet the size of a county the difference is small") is correct, which is the
argument for demoting the box to a `> [!NOTE]`, or for keeping the WARNING and quoting the measured
size of the effect so the student can see when it starts to matter.

---

## Stated / measured / match

Everything the draft asserts about the Step 9 chain that can be checked without the GUI, measured in
`C:\Ames\Pilot03\Pilot03.gdb` with ArcGIS Pro 3.7.1 `arcgispro-py3`, licence ArcInfo (Advanced),
stand-in geometry in NAD 1983 UTM Zone 12N (EPSG 26912).

| # | Draft says | Measured | Match |
| --- | --- | --- | :-: |
| 1 | Tool 1 **Calculate Geometry Attributes**, `Area_km2` = *Area (geodesic)*, unit Square kilometers | `arcpy.management.CalculateGeometryAttributes`, `AREA_GEODESIC` + `SQUARE_KILOMETERS`; field created automatically as **Double** | yes |
| 2 | Tool 1 also `Perim_km` = *Perimeter length (geodesic)*, unit Kilometers | `PERIMETER_LENGTH_GEODESIC` + `KILOMETERS`, both properties accepted in one call | yes |
| 3 | The named fields do not have to be created first | Neither field existed; the tool added both | yes |
| 4 | Tool 2 **Summary Statistics**, input = output of tool 1 | `arcpy.analysis.Statistics` accepts tool 1's derived output (the same feature class), which is what the ModelBuilder green oval carries | yes |
| 5 | Tool 2 writes `Area_Summary` with `Area_km2` SUM and `Perim_km` SUM | Fields written: `OBJECTID`, `FREQUENCY`, `SUM_Area_km2`, `SUM_Perim_km` | yes |
| 6 | `Area_Summary` has **exactly one row** | 1 row | yes |
| 7 | `Area_Summary.FREQUENCY` = number of polygons | 2 polygons in → `FREQUENCY` = 2 | yes (but see finding 21) |
| 8 | Tool 3 on `ErrorLines`, `Error_m` = *Length (geodesic)*, unit Meters | `LENGTH_GEODESIC` + `METERS`; 522.15 / 174.98 / 1360.59 m | yes |
| 9 | Tool 4 **Summary Statistics** MEAN, MAX, MIN on `Error_m` | `MEAN_Error_m` 685.91, `MAX_Error_m` 1360.59, `MIN_Error_m` 174.98 | yes |
| 10 | `Error_Summary` has one row with `FREQUENCY` = 3 | 1 row, `FREQUENCY` = 3 | yes |
| 11 | Field name `SUM_Area_km2` (Step 9 TIP) | `SUM_Area_km2` | yes |
| 12 | "If `SUM_Area_km2` is a number in the millions, your area unit is square meters" | 592.3 in km²; the same polygons in SQUARE_METERS are 5.92 × 10⁸ | yes |
| 13 | Tool 5 **Buffer**, input = output of tool 1, distance a linear unit in meters | `arcpy.analysis.Buffer` with `"685.91 Meters"` ran on the derived output | yes |
| 14 | The five tools run "in the order given, with the parameters as the step describes them" | All five ran, in order, first try, no warnings | yes |
| 15 | MIN is collected in tool 4 | Runs — but `MIN_Error_m` appears nowhere in Step 10's tables, Deliverables or the rubric. Harmless, unused | n/a |
| 16 | Model "returns four things" / rubric "the four outputs" | Three output **datasets** (`Area_Summary`, `Error_Summary`, `Uncertainty_Envelope`) carrying five numbers | **no** — finding 11 |
| 17 | Example Model: "three parameters"; Step 9 item 4: six things exposed; item 6: "the three inputs" | Three different counts of the same dialog | **no** — finding 11 |
| 18 | Step 9 item 6: run the model twice, second time with the real mean error | Second run to the same output with `overwriteOutput` off: *"Failed to execute. Parameters are not valid."* | **no** — finding 3 |
| 19 | Step 9 TIP: `Error_Summary.FREQUENCY` = 3, after Step 10's "re-draw your three error lines" | Re-drawing into the same feature class → `FREQUENCY` 6, `MEAN_Error_m` 2,137 m (was 686 m) | **no** — finding 4 |
| 20 | Buffer produces "an uncertainty envelope" (singular) | One polygon **per input polygon** (2 in → 2 out), inheriting `Area_km2` / `Perim_km` from the input | partial — finding 20 |
| 21 | Geodesic vs planar: "on a sheet the size of a county the difference is small" | 528.292 km² geodesic vs 528.000 km² planar = **0.055 %** on a 528 km² polygon in UTM 12N | yes, and see finding 28 |
| 22 | Envelope is "dramatically bigger than the feature itself" (Step 9 NOTE) | 592.3 km² → 680.6 km², **1.15×**, at a 686 m mean error. The migration note's 1460.6 → 2954.0 km² (2.02×) came from an 8,290 m error. Both are stand-ins; the claim's size depends entirely on the student's error, so "dramatically" is not guaranteed | soften |
| 23 | Rubric rows sum to ten, total fifty | `check_rubric.py`: 10 / 10 / 10 / 10 / 10 = 50, extra credit 5 | yes |
| 24 | Ctrl+P exposes a parameter (Step 9 item 4) | Verified in Lab 1's GUI pilot (lab-01 lines 490, 498) and Lab 2 | yes |
| 25 | Ctrl+R renames the model (Step 9 item 1) | Contradicted by Lab 2's verified GUI fact: a model cannot be renamed while open in ModelBuilder, F2 does nothing, and the Catalog rename sets Label not Name | **no** — finding 2 |
| 26 | Right-click ▸ Parameter exposes the Buffer distance (Step 9 item 4) | Lab 1's verified procedure needs **Create Variable ▸ From Parameter ▸ Distance** first | **no** — finding 1 |
| 27 | All 15 figures referenced exist in `images/` | 15 referenced, 15 present, no orphans | yes |
| 28 | Figures 2, 4, 12 are 2026-09-09 captures | Fig 4 and Fig 12 files dated 09-09; **Fig 2 dated 09-04** | **no** — finding 13 |
| 29 | Internal links `../../arcgis-tips.md`, `../../policies/ai-policy.md`, `README.md` | All three files exist | yes |
| 30 | Nine external links | `topoview` 200, `davidrumsey.com` 200, `commons.wikimedia.org` 200, four `pro.arcgis.com` 200. `usgs.gov` and `loc.gov` return 403 to curl; both opened correctly in a browser (loc.gov behind a Cloudflare bot check, exactly as the draft's own table says) | yes |
| 31 | Default project toolbox is `Lab03.atbx` (Step 9 item 6) | Consistent with Lab 2's verified `Lab02.atbx` for a project named `Lab02` | yes |

---

## What I could not check without the GUI

Everything below is asserted by the draft and is **unverified**. It needs a person or an agent with
desktop control driving ArcGIS Pro 3.7.1; the GUI pilot is still owed for this lab either way.

1. **The whole of Steps 3, 4, 5 and 10's georeferencing half.** The Georeference tab, **Fit to
   Display**, **Add Control Points**, the **Control Point Table**, the **Transformation** menu, and
   the residual/RMS readouts are interactive by nature. I confirmed none of it.
2. **Findings 1, 2 and 6 in the GUI.** I established them from Lab 1's and Lab 2's *recorded* GUI
   facts, not by driving ModelBuilder myself. Confirm before rewriting: (a) that the Buffer distance
   needs Create Variable; (b) the exact rename sequence and whether a model Label may hold spaces;
   (c) the name and behaviour of the Georeference tab's save/load control-point-links control.
3. **The Step 4 minimum-control-points table (lines 423–432).** I could not read ArcGIS Pro 3.7.1's
   own Transformation menu. Figure 12 is said to show it — check the table against the figure.
4. **What the Control Point Table reports for a Spline** (finding 19), and whether run A's affine
   3-point RMS really displays as `0.000000`.
5. **Whether topoView still offers a JPEG download alongside the GeoTIFF** (the Data WARNING at
   lines 192–198 rests entirely on this). topoView is a JavaScript map app; the format list only
   appears after selecting a sheet.
6. **Whether a model output exposed as a parameter is added to the Contents pane as a Standalone
   Table** when run from its dialog (Step 9 TIP, line 623).
7. **Anything in Steps 2, 7 and 8 involving the editing panes** — Create Features, Save in Manage
   Edits, the Fields view, the Labeling tab — and whether Figures 7 to 11 still match ArcGIS Pro
   3.7.1's layout at all, which the migration notes already flag as owed.
8. **Real check values.** This lab still publishes none, because every student uses a different
   sheet. Nothing in the stated/measured table above is a number a student will see; the stand-in
   geometry only proves the chain and the field names. If the Stansbury sheet is hosted
   (TODO(instructor) #1), real check values become possible for the first time and this table should
   be rebuilt against them.
