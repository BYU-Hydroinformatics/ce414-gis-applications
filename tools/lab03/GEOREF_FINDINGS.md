# Georeferencing the 1852 Stansbury sheet — measurements and the unresolved question

Working notes, 2026-09-18. Instructor-facing. The point of this file is the *last* section: the
sheet turned out to demonstrate the lab's own lesson better than anything we could have staged.

## The sheet

*Map of the Great Salt Lake and adjacent country in the Territory of Utah*, surveyed 1849–50 under
Col. J. J. Abert by Capt. Howard Stansbury, drawn by Gunnison, Carrington and Preuss, published
1852. Library of Congress item 2018588045, via Wikimedia Commons. Public domain.
9447 x 13337 px, 19.3 MB JPEG. Local copy: `C:\Ames\Lab03\Data\stansbury_gsl_1852.jpg`.

Chosen over the alternatives because it is a real survey with a printed graticule, it is visibly
folded (the crease lines are genuine distortion, not scanner error), and it covers both Great Salt
Lake and Utah Lake, so it is local to the students.

## The graticule, measured

Graticule lines were found by intensity profile across blank bands of the sheet, then fitted as
arithmetic ladders. Content and fold lines were rejected by the fit.

| | Spacing | Fit quality |
| --- | ---: | --- |
| Latitude, 10' interval | 916.0 px | 12 lines, max residual 17 px |
| Longitude, 10' interval | 686.5 px | 10 of 14 candidates on the ladder |

The ratio of the two, **0.7495**, against **cos(41.1 deg) = 0.7536** — agreement to half a percent.
Nobody put that there; it is the signature of a real geographic graticule at this latitude, and it
is the strongest evidence that the ladders are the graticule and not map furniture.

Anchors read from the printed border labels: the latitude ladder line at y = 478 is labeled 42 deg,
and the longitude ladder lines at x = 2474 / 3161 / 3847 / 4534 are labeled 113 deg 10', 113 deg 0',
112 deg 50', 112 deg 40'. A world file was written from those anchors:
`stansbury_gsl_1852.jgw` + `.prj` (WGS 1984 geographic).

## Checking it against ground truth

Reference coordinates from Wikipedia's coordinate data. Scan positions read off ruled crops, so they
carry perhaps +/- 50 px (about 1 km) of my own estimation error.

Reproduce with `georef_from_graticule.py`, which prints this table.

| Feature | Truth | Latitude error | Longitude error |
| --- | --- | ---: | ---: |
| Utah Lake | 40.2200 N, 111.8000 W | 2.24 km (see note) | 9.7 km west (6.8') |
| Antelope Island | 40.9583 N, 112.2139 W | **60 m** | 15.2 km west (10.8') |
| Promontory Point | 41.2222 N, 112.4114 W | 1.24 km | 18.9 km west (13.5') |
| Salt Lake City plat | 40.7706 N, 111.8925 W | small | same direction |

Note on Utah Lake: only its *x* was measured off a ruled crop; its *y* was left at the first
estimate, so the 2.24 km is my sloppiness and not a property of the sheet. The two features whose
positions were measured properly, Antelope Island and Promontory Point, bracket the latitude error
at 60 m and 1.24 km. Re-measure Utah Lake's y before quoting that row anywhere.

**Latitude is superb and longitude is not.** That asymmetry is not noise: it is what you expect from
a survey that fixed latitude by celestial altitude, which is easy, and longitude by chronometer
carried overland from Fort Leavenworth, which is hard. Worth stating in class as the likely
explanation and worth a student checking rather than taking from us.

## What the longitude error actually is

Two explanations were in play. The first was that I had anchored to the wrong degree line, off by
exactly one 10' tick. The second was that Stansbury's longitudes are genuinely wrong.

**A third measurement settled it.** The offset is not constant — it grows steadily westward:

| Feature | True longitude | Westward offset |
| --- | ---: | ---: |
| Utah Lake | 111.80 W | 6.8' |
| Antelope Island | 112.21 W | 10.8' |
| Promontory Point | 112.41 W | 13.5' |

A wrong anchor would put a **constant** 10.0' on every feature. This is a gradient, so it is not my
anchor. Fitting longitude against scan position across the three features gives about
2.05e-4 deg/px, where the printed graticule gives 2.428e-4 deg/px — the map's east-west spacing
between real features is roughly 18% wider than its own graticule says it should be. Over the 3,000
px separating these features that is some 540 px of accumulated disagreement, against a per-feature
estimation error of about 60 px, so the trend is well clear of my measurement noise.

So the sheet carries **both** a westward longitude shift and a longitude scale error, while its
latitudes are correct to within a kilometer and its internal geometry is sound (Antelope Island
measures 24.7 km long on the sheet against about 24 km in fact).

That asymmetry is what you expect from the period: latitude comes from celestial altitude, which is
straightforward, and longitude from a chronometer carried overland from Fort Leavenworth, which is
not. Stated as the likely explanation, and worth a student checking rather than taking from us.

Still to do: put the sheet on a basemap in ArcGIS Pro and look at it, which is the check no amount
of arithmetic substitutes for, and which also produces the georeferenced sheet needed to re-shoot
the lab's Figures 6 to 11.

### Why this matters more than getting the answer

Every number the software would report about this georeference is excellent. A least-squares fit to
the graticule intersections would return an RMS error near zero, because the graticule is drawn
almost perfectly regularly — the ladders fit to 17 px out of 916. **The RMS would be near zero and
the map would still be fifteen kilometers out of place**, because RMS cannot see a systematic error
in the thing you anchored to.

That is Lab 3's Step 5 warning, occurring by accident, on a real sheet, at a scale a student can
measure. It is a better illustration of the point than the sentence currently in the lab, and it is
the argument for the expansion proposed in `EXPANSION_PROPOSAL.md`.

## Confirmed in ArcGIS Pro, 2026-09-18

The arithmetic above was checked the only way that counts: the sheet was loaded over a basemap in
ArcGIS Pro 3.7.1, in a project at `C:\Ames\Lab03`, and looked at.

Two things had to be fixed before it would draw in place. The world file was read correctly on the
first try — the extent came in at exactly the computed corners — but the raster had **no coordinate
system**, so ArcGIS Pro drew it in the map's Web Mercator units and put a sheet whose coordinates run
about -113 to -111 at roughly 113 metres west of the origin, in the Gulf of Guinea. That is the exact
phenomenon the lab's Figure 1 illustrates, arrived at accidentally. `DefineProjection` to WGS 1984
fixed it, and the sheet then landed over Utah.

Measuring the sheet's own Promontory Point against the real one, in the map, in NAD 1983 UTM Zone
12N:

| | Latitude | Longitude |
| --- | --- | --- |
| Sheet's Promontory Point | 41.21143 N | 112.63130 W |
| Actual Promontory Point | 41.22222 N | 112.41139 W |
| **Offset** | **1.2 km** | **13.2' = 18.4 km west** |

Against the headless estimate of 13.5' and 18.9 km. The two methods agree to within half a
kilometre, which is inside the error of reading a feature's position off a ruled crop by eye.

`slides/week-04/images/geo-stansbury-1852-over-basemap.png` is a capture of the sheet at 62%
transparency over the modern lake: the 1852 islands sit visibly west of where the modern basemap puts
them, and the 1852 shoreline runs out into what is now the Great Salt Lake Desert.

## What is still owed

This georeference was derived analytically — graticule detection plus arithmetic — not by driving
the Georeference tab the way the lab tells students to. Both routes are legitimate and the analytic
one is reproducible, but the lab's own instructions have not been walked. Owed:

1. **Georeference it a second time from ground features**, through the Georeference tab, collecting
   control points as a student would. The difference between that answer and the graticule answer is
   the sheet's survey error, separated out — the optional extra proposed in `EXPANSION_PROPOSAL.md`.
2. **Re-shoot Lab 3's Figures 7 to 11.** Figure 6 was done on 2026-09-18 and is no longer a problem.
   The rest need digitized features in the project, which means walking Steps 6 and 7 for real.
3. **Build the two example layouts** as a baseline/scenario pair with `arcpy.mp`, the way
   `tools/lab01/build_layouts.py` does.
4. **Georeference the 1847 plat**, which has no graticule and so must be done from ground features —
   the Salt Lake City street grid, anchored on Temple Square.
5. **Re-measure Utah Lake's scan y**, per the note above.

Items 1 to 4 need the ArcGIS Pro GUI. The 2026-09-18 pass got as far as loading and verifying the
sheet and re-shooting Figure 6; the project it left behind is `C:\Ames\Lab03\Lab03.aprx`, with the
sheet loaded, defined as WGS 1984, over a NAD 1983 UTM Zone 12N map.
