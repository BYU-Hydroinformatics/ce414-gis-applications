# Lab 11 (Network Analysis) — plan for the instructor's decisions

Written October 9, 2026, from `tools/NEXT_STEPS.md` section 1. This is step 1 of
`tools/lab-conversion-guide.md` section 9: the analytical question, the data, the numbers the student
varies, and the personal number, with everything below **measured** in ArcGIS Pro 3.7.1's Python on
October 9 (`feasibility_network.py`, `feasibility_population.py`, working folder `C:\Ames\Lab11\`).
Nothing has been built for students yet. **Stop here and decide the numbered items at the end.**

## 1. The question (proposed)

> **Fire response coverage in Utah County.** Which residents live more than four minutes' drive
> from the nearest fire station, how many are there, and how much does that answer depend on the
> response standard and on measuring distance along the roads instead of in a straight line?

Why this one, of the three candidates in the hand-off:

- It uses the one Network Analyst solver students can learn in a week (**Service Area**), and it
  carries a real engineering standard to vary: NFPA 1710's 240-second travel time for the first
  engine and 480 seconds for the full first alarm (secondary sources only so far; the page will say
  "verify the current edition" until the standard itself is checked).
- It closes the course's distance arc explicitly: Lab 1 buffered roads and stores (**straight-line**
  distance), Lab 10 accumulated cost across terrain (**cost distance**), Lab 11 travels the road
  network (**network distance**). Step 6 puts a Lab 1 style buffer beside the service area on the same
  map, and the numbers are far apart (section 5).
- Closest Facility and Location-Allocation are both one more analysis layer in the same model and
  can be the optional "going further" extra (at most five rubric points), not the spine; Week 12 is
  also Midterm 2 week.

## 2. The network: use UGRC's prebuilt dataset, clipped to Utah County (measured, recommended)

UGRC publishes two prebuilt Network Analyst datasets, both file geodatabases on Google Drive:

| Product | What it is | Verdict |
| --- | --- | --- |
| [Utah Street Network](https://gis.utah.gov/data/transportation/street-network-analysis/) | Statewide `UtahRoadsNetworkAnalysis.gdb` (224 MB zipped, 447 MB unzipped): feature dataset `NetworkDataset` in NAD 1983 UTM 12N with `Roads` (414,082 edges, UGRC roads updated through September 23, 2026), 362,238 junctions, and a **built** network dataset `UtahRoadsNetwork` with two cost attributes, **TravelMinutes** (default) and **Length** (meters). No turns, no elevation model, **no travel modes**, no restriction attributes. | **Use it.** |
| [Multimodal Network](https://gis.utah.gov/products/sgid/transportation/multimodal-network/) | Wasatch Front auto + bike + pedestrian + 2019 transit, from a 2018 pilot; pedestrian data densified only within half a mile of 50 sites. | Not for this lab: the extra modes are noise for a fire-response question and the transit data is 2019. |

How UGRC's network costs travel (from the `Roads` fields the template evaluates): `F_T_IMP_MIN` and
`T_F_IMP_MIN` are minutes in each direction, estimated from `SPEED_LMT` and `CARTOCODE`, with surface
streets multiplied by 1.5 for signals and congestion. **One-way streets are not a restriction but a
penalty:** the wrong direction costs 100 times the right one (590 one-way edges in Utah County, every
one asymmetric). The page and the deck should say so, because it is a good example of "the network is
a model too": an engine can legally drive the wrong way with its lights on, and a 100× penalty is one
defensible way to say "almost never".

**Clip and rebuild, do not ask students to build.** `CreateTemplateFromNetworkDataset` on UGRC's
network, `ExportFeatures` of the 41,460 Utah County edges (`COUNTY_L` or `COUNTY_R` = `'49049'`),
`CreateNetworkDatasetFromTemplate`, `BuildNetwork`: 28 seconds end to end, and the student receives
UGRC's own cost definition unchanged in a county-sized geodatabase (about 15 MB zipped, to be
measured). Building a network dataset from raw `UtahRoads` is a Catalog-pane wizard with a dozen
decisions (sources, connectivity, elevation fields, attributes, evaluators, travel modes, build); it is
the right content for the Tuesday deck, not for a one-week lab in exam week. Service Area from all 42
stations at two cutoffs solves in 10 seconds.

Two things to verify in the GUI build before promotion:

- **Travel modes.** UGRC's network has none, and `arcpy.nax.ReplaceNetworkTravelModes` fails on the
  clipped copy without a message (tried four ways). The geoprocessing tool runs without one (it uses
  the default cost, TravelMinutes), so the lab works either way, but a named **Driving Time** mode in
  the dialog is clearer; add it in **Network Dataset Properties ▸ Travel Modes** during the GUI build
  and check it survives the zip.
- **Lab-machine version.** Everything is built in ArcGIS Pro 3.7.1; a network dataset built in 3.7
  must open on the lab machines' version (confirm it is also 3.7).

## 3. The other data

| Layer | Source (all UGRC feature services, as in Lab 10's `make_package.py`) | In Utah County |
| --- | --- | --- |
| Fire stations | `FireStations` (`NAME`, `ADDRESS`, `CITY`, `EMS` = Y/N/blank; layer dated September 2022) | **42** points, including Camp Williams and the UVU fire academy |
| Census blocks 2020 | `CensusBlocks2020` (`GEOID20`, `PP_TOTAL`, `HU_TOTAL`, `ALAND20`) | **10,092** blocks, **659,399** people |
| Roads network | UGRC Utah Street Network, clipped (section 2) | 41,460 edges |
| County boundary | `UtahCountyBoundaries` | 1 |
| Alternatives considered | Licensed hospitals (`LicensedHealthCareFacilities`, `LICENSE_TYPE = 'Hospital'`, 12 in the county, four of them psychiatric or specialty); EMS agencies (`EmergencyMedicalServices`, 30); building footprints (`Buildings`, 191,855 polygons); address points (`UtahAddressPoints`, 248,791) | Hospitals are a weaker question (patients travel to them; 12 facilities, no standard to vary). Buildings and address points are "every door" demand and would make a fine optional extra but are too heavy for the required path. |

Demand is **people, by block centroid** (Feature To Point, inside): a block is "covered" when its
centroid falls inside the service-area polygon. That is what UGRC's own
[Fire Station Travel Times](https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Fire_Station_Travel_Times/FeatureServer)
layer (2, 4 and 6 minute rings, March 2022, "typical network travel, not expedited emergency travel")
leaves out, and it is the honest unit for "how many residents". Students also download one layer live
(the county boundary or the stations) so the metadata questions have something to bite on, as in
Labs 1 and 10.

## 4. The model and the steps (about nine)

One ModelBuilder model, `Lab11.atbx`, with the cutoff exposed:

```
Fire_Stations ─┐
Network ───────┴─ Make Service Area Analysis Layer (cutoffs = %Cutoff_Minutes%, from facilities,
                   standard detail, dissolve overlaps, rings)
               ─ Add Locations (Facilities) ─ Solve ─ Select Data (Polygons) ─ Copy Features → Served_Area
Block_Points ─── Select Layer By Location (INTERSECT Served_Area, INVERT) ─ Copy Features → Unserved_Blocks
               ─ Summary Statistics (SUM PP_TOTAL) → Unserved_Population
Fire_Stations ── Buffer (%Buffer_Distance%, dissolve) → Crow_Area   (Step 6; same selection → Crow_Unserved)
```

| Step | Title | Check value (measured) |
| --- | --- | --- |
| 0 | Set Up the Project | network dataset opens: 41,460 edges; Network Analyst extension on |
| 1 | Look at the Network | one named road's `F_T_IMP_MIN` versus `T_F_IMP_MIN`; the 100× one-way penalty; 590 one-way edges |
| 2 | Place the Stations | 42 stations located, 0 unlocated (5 km search tolerance) |
| 3 | Make the Service Area Layer | layer in the Contents pane with Facilities, Polygons |
| 4 | Solve and Export | 4-minute area **197.3 km²**, 4–8 ring **373.0 km²** |
| 5 | Count the People Outside | **374,769** of 659,399 outside 4 minutes (56.8 %); 64,015 outside 8 minutes (9.7 %) |
| 6 | Compare the Straight Line | 2.5 km buffer leaves **101,007** outside (15.3 %); 3 km, 50,815 (7.7 %) |
| 7 | Set Model Parameters | Cutoff_Minutes and Buffer_Distance exposed; model SVG |
| 8 | Run the Tool | personal cutoff run (section 5) |
| 9 | Test the Standard | the sensitivity table, three questions, Map 2 |

Rubric: Write-up 10, Model 10, Map 1 (service-area rings, uncovered blocks, stations) 10, Map 2 (the
straight-line buffer beside the network area for the same minutes, with the two populations in the
text box) 10, Sensitivity 10. Deliverables list matches item for item; `.atbx` uploaded.

## 5. The numbers the student varies, and the personal number (measured)

**Cutoff minutes** moves the answer across the whole range, which is what Lab 10 taught us to check
before publishing:

| Cutoff (min) | People outside | % |
| --- | --- | --- |
| 2 | 583,002 | 88.4 |
| 3 | 493,127 | 74.8 |
| 4 | 374,769 | 56.8 |
| 5 | 274,105 | 41.6 |
| 6 | 181,107 | 27.5 |
| 7 | 116,270 | 17.6 |
| 8 | 64,015 | 9.7 |
| 10 | 26,375 | 4.0 |
| 12 | 18,373 | 2.8 |

Straight-line buffers around the same 42 stations, for Step 6's contrast:

| Buffer | People outside | % |
| --- | --- | --- |
| 1.5 km | 330,003 | 50.0 |
| 2 km | 196,111 | 29.7 |
| 2.5 km | 101,007 | 15.3 |
| 3 km | 50,815 | 7.7 |
| 4 km | 18,994 | 2.9 |

The teaching point writes itself: four minutes at a 35 mph limit is 3.75 km as the crow flies, which
"covers" 97 % of the county; along the roads at UGRC's typical speeds it covers 43 %.

**Personal number (proposed):** `Cutoff_Minutes = 4 + 0.04 × (last two digits of the BYU ID)`, 4.00 to
7.96 minutes, which spans 56.8 % down to about 10 % outside: every student gets a different population
and the grader reproduces it with `run_model.py --digits NN` (the lookup CSV comes from the reference
run, one solve per value, about 10 s each). The published check values stay at 4 and 8 minutes.

**Second number:** the buffer distance in Step 6 (default 2.5 km; the student also tries the "4 minutes
at the speed limit" distance). Not personal.

**Not proposed as a parameter, but worth a sentence in the deck:** UGRC's 1.5× surface-street factor.
An engine running code three is faster than UGRC's "typical" driver, so the 56.8 % is an upper bound.
If Dan wants a second *network* sensitivity, the package network can carry a second cost attribute
`ResponseMinutes = TravelMinutes / 1.5` and a second travel mode, and Step 9 adds one run with it
(decision 4).

## 6. Fit with Week 12

Tuesday deck (`network-analysis-a`): what a network dataset is, edges, junctions, connectivity,
one-way and impedance, how UGRC built this one (the wizard the students are spared), and the three
distances side by side. Thursday deck (`network-analysis-b`): Service Area, Closest Facility and
Location-Allocation in ArcGIS Pro, then Lab 11 live on the package. Midterm 2 is open Tuesday to
Thursday; the lab is due Saturday 11:59 pm.

## Decisions for the instructor

1. **The question:** fire-station response coverage with Service Area, as above? (Alternatives:
   hospitals; a Lab 1 style site selection with Location-Allocation, which I would keep as the
   optional extra.)
2. **The network:** UGRC's prebuilt Street Network clipped to Utah County and hosted, students never
   build one? (Recommend yes; the build is deck material.)
3. **Demand unit:** people by 2020 block centroid (recommend), or address points?
4. **Sensitivity:** cutoff minutes only, with the straight-line buffer as the contrast (recommend), or
   also the emergency-speed travel mode?
5. **Personal number:** `4 + 0.04 × digits` minutes (4.00 to 7.96)? Any other range is one line to change.
6. **Which stations:** all 42 as published, or drop Camp Williams and the UVU academy (one Select step,
   check value 40)? Recommend keeping all 42 and letting the metadata question ask whether they belong.
7. **Optional extra (at most five points):** Location-Allocation for one new station that covers the
   most uncovered people, or Closest Facility from a student-chosen address? Or no extra, since it is
   exam week (recommend none).
8. **Lab 11 points** for `docs/policies/grading.md`: 50, making "Labs 1 to 12, 600"?
9. **NFPA 1710** as the stated standard, with the "verify the current edition" caveat, or a plainer
   "the city's own four-minute goal"?

## What happens after the decisions

`make_package.py` (clip and rebuild the network, fetch stations, blocks and boundary, READ-ME, zip to
`docs/data/lab11-fire-response.zip`), `run_model.py` (baseline, step checks, cutoff sweep, personal
lookup), `draft.md`, icons and Figure A/B, no-GUI pilot, GUI build at 175 % in `C:\Ames\Lab11GUI\`,
example maps, template, promote, `build_schedule.py` and `grading.md`, Learning Suite. Commit;
no push until asked.

## Measured (October 9, 2026, ArcGIS Pro 3.7.1)

- UGRC Utah Street Network: 414,082 edges, 362,238 junctions statewide; attributes TravelMinutes
  (minutes, default) and Length (meters); no travel modes, turns, elevation model or restrictions.
- Utah County clip: 41,460 edges; template 27 KB; export 17 s, create and build 9 s.
- 590 one-way edges, all with the reverse direction costed at 100× (`F_T_IMP_MIN` vs `T_F_IMP_MIN`).
- 42 stations, all located at 5 km tolerance; Service Area at 4 and 8 min solved in 10 s;
  4-min area 197.3 km², 4 to 8 min ring 373.0 km².
- Blocks: 10,092; population 659,399; the cutoff and buffer tables above.
