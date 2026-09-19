# Lab 3 — no-GUI pilot, round 3

Run 2026-09-18 against `docs/assignments/lab-03/draft.md` at 77b5223 ("round 3"). Section 6 of
`tools/lab-conversion-guide.md`, with the instructor's overrides: manual, one-week lab, no model;
control points not required on Map 1. The GUI facts listed in the draft's closing comment (verified
2026-09-18) are taken as true. No ArcGIS Pro GUI, no computer use. No arcpy run was needed: every
number this round was checkable by arithmetic against the walk numbers and Figure 9c (below).
`C:\Ames\Pilot03c\` was not created.

**Headline.** The reorder works: the georeferencing session now ends at Step 7, Map 2 has its
Save-as-New copy, and every step cross-reference was updated correctly (every "Step N" reference
checked). What the reorder left behind is that **Step 6 is now the first time students use Create
Features, the Fields view and Calculate Geometry, but the figures and the Long-type warning for
those tools sit in Steps 8–10**. Four small round-2 items were not touched (Figure 7 crop, Figure 6b
alt text, Figure 5 caption, Step 7 TIP). Step 0's WARNING now contradicts Step 10's NOTE. The lab is
still about 11 hours median — over one week unless class time or a named sheet is given.

Clean: rubric 10/10/10/10/10 = 50, extra credit 2+2+1 = 5; all 28 referenced images exist; no bare
"Pro"; no British spelling; no student-facing reference to earlier handouts (history only in the
draft box and HTML comments); every step heading two or three words (Step 0's four sanctioned);
counts agree everywhere (8 + 3 = 11 features, three clustered, six features, three geometry types,
four fields, three runs, two layouts); `Length_km` fully gone. Walk arithmetic in the comment checks:
means 2,384 / 7,881 / 8,917 m; 395 × 2.384 = 942 km² = 18.0 % of 5,224; RMS cut 1,688 → 623 m is
63 % ("almost two-thirds"). Figure 9c's planar `Shape_Area` 5,221.74 km² vs geodesic 5,223.78 is
0.04 %, which is what the new Step 10 NOTE says. Links: topoView, David Rumsey, both Wikimedia,
three pro.arcgis.com = 200; loc.gov (item, collections) and usgs.gov = 403 to curl (bot block, still
not opened in a browser — the loc.gov item page has never been browser-checked).

---

## Round-2 findings: status

| # | Round-2 finding | Status | Why |
| --- | --- | --- | --- |
| 1 | Map 2 run thrown away | **FIXED** | Step 7 L521–524 Save as New → `sheet_run3.tif`; Map 2 deliverable L719–721 and rubric use it |
| 2 | Session open Steps 4–10 | **FIXED** (residual risk, new #5) | Session now Steps 3–7; Step 5 exports links. Still a 2.5–4 h sitting, and Step 6 edits with the Georeference tab open (unverified) |
| 3 | Control points on Map 1 | **NO LONGER APPLIES** | Instructor decision; removed from deliverable and rubric; Example Maps NOTE L790 says so |
| 4 | Figures 10/11 modeled the wrong thing | **FIXED** | Replaced by 8b (Stansbury polygon) and 9c (four fields, historic name) |
| 5 | Web Mercator interpretation | **PARTLY FIXED** | Step 10 TIP fixed. Step 0 WARNING L297 unchanged and now contradicts Step 10 NOTE L663–664 (new #3) |
| 6 | Geodesic/planar WARNING overstated | **FIXED** | Now a NOTE, "a fraction of a percent" — matches Figure 9c (0.04 %) |
| 7 | P·d is a worst case | **FIXED** | "at most", half-area rule. The optional "a pure shift keeps its area" sentence was not added — fine |
| 8 | Step 6 TIP diagnosis backwards | **FIXED** | L479–484 now says the fit absorbed the whole-sheet shift. Could still add "or your checks are bunched together" (Low, new #16) |
| 9 | Gulf of Guinea | **FIXED** | L324–332 "origin of whatever coordinate system"; caption explains the capture |
| 10 | Run 3 needs middle points | **FIXED** | Step 4 L390–391 asks for three close together near the middle |
| 11 | Unverified check boxes / restore | **FIXED** | Check boxes and Import/Export verified; Step 5 exports |
| 12 | Deliverables vs rubric | **PARTLY FIXED** | Map 1 title/text box/symbolized added; Catalog capture, AI line added; `Length_km` dropped. Still missing from the Map 1 deliverable: legend, neat line, north arrow, scale bar (new #9) |
| 13 | Worked example unproven | **FIXED** | Walk georeferenced it from eight ground points and three checks (comment L872–888) |
| 14 | Figure/alt/caption mismatches | **NOT FIXED** | Figure 7 still crops Spline's "Requires at least 10"; Figure 6b alt still lists "Raster Dataset" (not in the crop); Figure 5 caption still "plainly still in the wrong place" though the image sits over Escondido. The draft box L44 says Figure 5's caption was corrected; it was not (new #7) |
| 15 | TIP may name two runs | **NOT FIXED** | L540 "One of these runs" — run 2 as Spline and run 3 both report ~0 |
| 16 | "first time in this course" vs Add row | **NOT FIXED** | L239 unchanged |
| 17 | Map Properties route | **FIXED** | Double-click Map in Contents (L291–292) |
| 18 | "Square kilometers" | **FIXED** | L656 "Square Kilometers" |
| 19 | "before 1930" | **NOT FIXED** | L165–166; as of 2026 it is "1930 or earlier". Low |
| 20 | Drift from original | **NO LONGER APPLIES** | Instructor accepted; recorded in the comment L890–895 |

---

## New findings, worst first

### High

**1. Step 6 is now the first use of four tools whose figures and warning come later.** After the
reorder, Step 6 (L462–474) is where a student first opens Create Features, saves edits, opens the
Fields view, and runs Calculate Geometry — inside the one-sitting georeferencing session. The help
for those is in Figure 8a (Edit tab, Step 8), Figures 9a/9b (Add, Fields view, Step 9), the
`Long` WARNING (Step 9, L612–616, which even lists `Error_m` from Step 6), and Figure 10 (Calculate
Geometry dialog, Step 10). A first-time student meets every hard part without a picture.
*Fix:* move Figure 8a after Step 6 item 2, Figures 9a and 9b after item 4, and the `Long` WARNING
into Step 6 (renumber to 6c–6f); in Steps 8–9 say "as in Step 6 (Figure 6d)". Figure 10 can stay
(it shows the area/perimeter case) but cite it forward from Step 6: "the dialog looks like
Figure 10, with one row".

**2. Map 2 cannot be built without a second map, and the page never says so.** A layout's map frame
shows the map's live layer visibility. If both layouts point at the one map, turning off the run-1
scan and turning on `sheet_run3.tif` for Map 2 changes Map 1 too. Nothing tells students to add the
copy to a map at all (does Save as New add its output? not in the verified list). New to this lab:
in Labs 1 and 2 the Map 2 difference is a different output layer; here it is the same features over
a different raster.
*Fix:* one paragraph at the end of Step 7 or under Deliverables: "In the Catalog pane, copy your map
and paste it to make a second map for Map 2. In that map, turn off your original scan and add the
`.tif` you kept with Save as New. Point Map 2's layout at that map." (Verify copy/paste of a map in
the Catalog pane on the next GUI walk.)

**3. Step 0 WARNING contradicts Step 10 NOTE.** L297–298: in Web Mercator "every distance and area
you measure later is wrong". L663–664: geodesic numbers "give the right answer whatever coordinate
system". Both cannot be true for a student; the second is (round 2 measured it). What *is* affected
in this lab: Step 7's **Measure Distance, which defaults to Planar** (verified) — about 1.3× too long
at 41° N in Web Mercator — and the scale bar.
*Fix:* "If you leave the map in Web Mercator, every *planar* distance — including the Measure
Distance checks in Step 7, which are planar by default — is too large by a factor that grows with
latitude, about a third at Utah's latitude. The geodesic numbers in Steps 6 and 10 are not affected,
but your feature classes inherit the map's system, so set it here." Keep the Lab 1 sentence.

### Medium

**4. Step 7's run order breaks two ways.** (a) Going from run 2 (2nd Order, needs 6) to run 3 by
unchecking down to three links leaves a 2nd-order solve with too few points; the page never says to
set 1st Order back first. (b) The Save-as-New paragraph (L521) comes after the runs and says "whichever
moves the sheet more", which is only known after run 3 — so a student who picks run 2 must rebuild it
(re-check all links, 2nd Order) and is not told to.
*Fix:* in the run instructions: "For run 3, set the transformation back to 1st Order first, then
uncheck." In the keep paragraph: "If you choose run 2, check every link again and set 2nd Order
before you click Save as New."

**5. The one-sitting session is still 2.5–4 hours, and Step 6 edits inside it unverified.** Note #1
(L271–274) says plan Steps 3–7 in one sitting; the time table below puts that at 2.5–4 h. The export
in Step 5 makes a break safe, but the page does not say where or how to resume. Separately, Step 6
creates a feature class, edits on the Edit tab and saves edits while the Georeference tab is open,
and Step 7 uses the Map tab's Measure Distance during it; the verified list does not record either
being done mid-session (Figure 4 shows Map and Edit tabs available, which is encouraging).
*Fix:* Note #1: "The natural break is the end of Step 5, after you export your control points. If you
stop there, click Save and Close Georeference; to resume, select the scan, click Georeference, and
Import Control Points." Verify on the next walk: (i) editing and Save Edits with the Georeference tab
open do not disturb the solve; (ii) reopening Georeference on a saved scan and importing restores
the table.

**6. Step 7's Measure Distance has no zoom instruction.** Step 6 insists on 1:50,000 because the walk's
hand-drawn lines at 1:500,000 were off by 25–40 % (comment L883–884). Step 7 asks for nine more
measurements with no scale given, and they fill the "Mean check error" column the three questions
turn on.
*Fix:* L508: "…with **Measure Distance** (Map tab, Inquiry group), zoomed to about 1:50,000 as in Step 6.
Record meters; the tool may switch to kilometers for long distances."

**7. Round-2 finding 14 items still open, and the draft box claims one was fixed.** Figure 7
(`lab03-transformation-list.png`) ends at "Spline" with its requirement cut off, yet the caption says
"with the minimum control points each one needs". Figure 6b's alt text lists "Raster Dataset"; the crop
ends at Relationship Class. Figure 5's caption says "plainly still in the wrong place"; the image
shows the sheet over Escondido with I-15 running through it. Draft box L44 lists "Figure 5's caption"
among carried-forward corrections.
*Fix:* re-crop or re-capture Figure 7 to include Spline's line; drop "and Raster Dataset" from 6b's alt;
Figure 5: "one point cannot fix the sheet's scale or rotation, so that zero is telling you nothing".

**8. Figure numbering does not follow the guide's step numbering for Steps 2–4.** Guide section 3:
figures are numbered by the step. Steps 6–10 comply (6a/6b, 7, 8a/8b, 9a–9d, 10); Step 2 has
Figure 1, Step 3 has Figures 2, 3, 4, Step 4 has Figure 5. A student reading "Figure 4" looks for
Step 4.
*Fix:* Figure 1 → 2, Figures 2/3/4 → 3a/3b/3c, Figure 5 → 4; update the Figure 4 reference in the
Step 3 text if any (none now). Example maps 11/12 can stay.

**9. Deliverables ↔ rubric gaps.**
- Rubric → no deliverable: Map 1 "neat line, north arrow and scale bar (1)" and "with a legend"
  (in the 2-point bullet) — the Map 1 deliverable (L715–718) names neither; "professional" is not a
  specification. Rubric Write-up bullet 1 "Assignment title" is not in the report list.
- Rubric Georeferencing bullet 3 grades checks "drawn as error lines", but no deliverable asks for
  evidence of the lines. Add "a capture of your `ErrorLines` attribute table, or of the three lines on
  the map" to the check-features bullet (L734).
- Deliverable → no rubric: Spatial Considerations L111–112 says to report every choice "and why",
  including "what counts as gone" (L127–128); no deliverable or rubric bullet asks for it. Either add
  "what you counted as gone, and why" to the Digitizing deliverable, or cut "Say in your report what
  you chose and why" to the choices that are graded.
- Tension: rubric Georeferencing bullet 1 "distributed … rather than clustered" vs Step 4's required
  three clustered points. Reword the bullet to "reaching all four corners of the sheet".

### Low

**10. Step 7 TIP (L540)** — "One of these runs": round-2 #15, still open. "One or two of these runs…".

**11. Analysis Tools intro (L239)** — "for the first time in this course" vs the Add row's "the Add
Field geoprocessing tool you used in Lab 1". Round-2 #16, still open. "the tools and buttons this lab
relies on".

**12. "Everything in Steps 3 to 7" is on the Georeference tab** (L245, Figure 4 caption L361). Step 6
is on the Catalog pane, Edit tab and attribute table; Step 7's Measure Distance is on the Map tab.
Say "The georeferencing in Steps 3 to 7".

**13. Figure 4's Save group is four unlabeled icons.** The caption names Save and Save as New in it, but
a student cannot tell which icon is which. Add: "The Save group's buttons are icons only; hover for
their names." Same for Export Control Points, which Step 5 sends students to on the table toolbar.

**14. State Plane in feet.** Step 0 allows "a State Plane zone"; Utah's common State Plane systems are in
US feet, so Step 5 residuals and the Step 7 "Total RMS error (m)" column would be in feet. Add "(choose
the meters version if you use State Plane)" or recommend UTM outright.

**15. Step 0 item 1** does not mention the "Create a folder for this local project" check box; left on,
the project and `Lab03.gdb` land in `D:\Smith\Lab03\Lab03\`, and item 2's "in your lab folder" fails.
`arcgis-tips.md` covers it. Add "uncheck *Create a folder for this local project*" or link the tips
section there.

**16. Step 6 TIP (L481)** — add the bunched-checks case: "…or your three check features sit close
together in one part of the sheet."

**17. "older than 1900"** is a requirement in Complete the Lab (L260) and "if you can" in Where to find
(L176). Make them agree ("older than 1900 if you can").

**18. "Before 1930"** (L165) → "in 1930 or earlier" (round-2 #19).

**19. "Do NOT publish" walk numbers are published.** The HTML comment at L872–888 is labeled instructor
only, but Python-Markdown passes comments through to the built page (tested: `markdown.markdown()`
keeps `<!-- … -->` verbatim), so any student who views source sees the Stansbury control points, all
three runs' errors, and the lake area. Lab 1's L625 has the same pattern, so this is a course-wide
decision, not a Lab 3 defect: either accept it and drop "do NOT publish", or move such tables to
`tools/lab03/`.

---

## Time estimate (revised)

First-time student, alone, outside the 75-minute sessions. Week 4 also carries the Chapter 6 reading,
Quiz 4, and the Tuesday "Georeference Your Home" activity (which rehearses Steps 2–5).

| Step | What | Estimate |
| --- | --- | --- |
| 0 | Project, basemap, coordinate system | 10–15 min |
| 1 | Find a sheet, eleven-feature test, six facts, maybe a PDF | 45–120 min (15 with Stansbury) |
| 2 | Add scan, find it | 5–10 min |
| 3 | Georeference tab, Fit to Display, transparency | 10 min |
| 4 | Eight points incl. three clustered, three reserved | 30–60 min |
| 5 | Residuals, fix an outlier, capture, export | 20–35 min |
| 6 | ErrorLines class, three lines at 1:50,000, field, Calculate Geometry (first use of all four) | 30–45 min |
| 7 | Three runs, nine Measure checks, table, Save as New, Save, close; questions drafted | 45–75 min |
| 8 | Three feature classes, six+ features | 45–90 min |
| 9 | Four fields × three classes, fill with F2, label × 3 | 30–45 min |
| 10 | Two fields, Calculate Geometry, P × d | 10–20 min |
| Maps | Two layouts, incl. second map for Map 2 | 90–150 min |
| Report | 2–3 pages, metadata answers, tables, captures, questions | 120–180 min |
| Peer review | Read one, act on yours | 30–60 min |
| **Total** | | **≈ 8.7–15 h, median about 11 h** |

Steps 3–7 (the one sitting): **2.5–4 h**.

**Verdict: unchanged from round 2 — over one week for most students** against the roughly 6–7 h of
outside work a 3-credit week supports, now with the reading and quiz on top. The reorder fixed
correctness, not length (it removed `Length_km`, about 10 min, and added the export and Save as New,
about 10 min). Cheapest cuts, in order: (1) host the Stansbury sheet or name one topoView sheet as
the default and make "your own sheet" the stretch option — saves up to 1.5 h and removes the most
variable step; (2) make Map 2 a half-page figure in the report rather than a second full layout —
saves 45–60 min and removes finding 2's second-map setup; (3) require the four attributes on the
polygon and point classes only, or cut `Present_Day` — saves 15 min; (4) give Thursday of Week 4 as a
work session for Steps 6–7.
