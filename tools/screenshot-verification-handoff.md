# CE 414 lab screenshot verification — handoff

**Prepared:** September 3, 2026 (session "CE 414 lab screenshots update")
**Goal of the task:** walk every lab on the published site in ArcGIS Pro (BYU Citrix), check each
screenshot against what Pro actually shows today, and replace the ones that are wrong. Text changes
are out of scope for this pass; only images.

## Status: blocked before the first capture — nothing was verified or replaced

No screenshot was checked against ArcGIS Pro and no image on the site was changed. The session
stopped at the Citrix door, for a reason that will recur unless it is handled up front:

- The live Citrix desktop (ArcGIS Pro open, project "Untitled", a ModelBuilder model called
  **Cities Near Rivers** in `Default.atbx`, Catalog pane showing `chn_adm_ocha_2020_shp` under
  OneDrive) is in a Chrome tab that belongs to **another Claude session's tab group** (the group
  labeled "CE 414 course updates"). Claude in Chrome can only drive tabs in its own group, and it
  has no way to adopt an existing tab.
- Opening `byuapps.cloud.com` in a fresh tab redirects to the Microsoft sign-in with
  `prompt=login`, i.e. the Workspace store session has expired even though the HTML5 desktop
  session is still alive. Claude may not enter credentials, so the store cannot be re-entered
  without Dan.
- Re-opening the session's `SessionWindow.html?launchid=…` URL in a new tab fails with
  *"Session failure — Failed to retrieve ICA"*.
- Mac-side input injection is not available either: `osascript` has no Accessibility permission,
  Chrome's *Allow JavaScript from Apple Events* is off, no `cliclick`, no Quartz bindings, no
  remote-debugging port. Mac-side **capture** (`screencapture`) works fine; it is only **driving**
  the session that fails.

### How to unblock (either one)

1. **Sign in to Citrix Workspace in the tab Claude opened** (it is sitting on the BYU/Microsoft
   sign-in page inside Claude's tab group), then tell Claude to continue. Claude launches
   *2025 BYU Standard Desktop - All Apps* from that tab; Citrix reconnects to the existing Windows
   session, so ArcGIS Pro comes back exactly as it is now.
2. Or **drag the "2025 BYU Standard Desktop" tab into Claude's tab group** in Chrome (the group
   chip reads "CE 414 lab screen…"). Then tell Claude to continue.

Whichever route: start each new session by launching the desktop **from inside the session's own
group tab**, never by reusing a tab another session opened.

## Capture workflow (proven in earlier sessions, scripted here)

Nothing can be saved *out* of Citrix (Snipping Tool drag never releases, PowerPoint Save is inert,
image clipboard does not sync). Capture on the Mac instead:

```bash
# once per session, from Claude in Chrome javascript_tool on the Citrix tab:
#   ({sx: window.screenX, sy: window.screenY, top: window.outerHeight - window.innerHeight})
python3 tools/capture_citrix.py --sx 0 --sy 25 --top 87 \
    --region 330,320,1060,790 \
    --out docs/assignments/lab-05/images/lab05-fill-model.png
```

`tools/capture_citrix.py` activates Chrome, grabs the whole screen at Retina resolution, and crops
the viewport-pixel region you give it. Keep the Chrome window fully on screen or the crop clips.
Use Claude in Chrome's `zoom` action to *inspect* a region at 2x before deciding the crop box;
`zoom` images cannot be filed, the script's output can.

Other Citrix facts that cost time to learn (details in `ROADMAP.md`): the course folder is `F:`;
typed paths are blocked, click through the tree; Windows Search is dead; `PrtScn` opens Snipping
Tool; downloads inside the session land in a blocked folder, so **download data on the Mac and
drop it into the course folder**, then refresh Explorer in the session.

Record the exact ArcGIS Pro version (Project ▸ About) on the first pass and put it in every lab's
migration-notes comment; every page currently says "NOT VERIFIED".

## Data: what is on `F:` today

Only Lab 1 has a prepared package:
`Labs/Lab 1 Data/2026-09-02/` — `CE414_Lab1_BaseData_2026-09-02.gdb`, four GeoJSONs, the student
zip, and `ARCGIS_PRO_VALIDATION_CHECKLIST.md` (items 1–4 done, everything from "add the layers to
the map" onward still unchecked). `In Class Activities/Utah Raster Analysis/UtahRasterExercise.gdb`
may hold a Utah DEM usable for raster-tool dialog shots; check its contents before downloading.

Every other lab's data must be fetched first. Suggested drop folder: a new
`_lab_data_2026/lab-NN/` under the course folder, downloaded on the Mac side.

| Lab | Data needed | Source named in the lab page |
| --- | --- | --- |
| 2 | one Landsat 8/9 scene over Utah County (red + NIR bands) | USGS EarthExplorer (login) — `Landsat Data Instructions/` in the course folder |
| 3 | any scanned historic map image | USGS topoView, LoC — the handout example is the 1893 Escondido sheet |
| 4, 5, 6, 10 | Utah 10 m/30 m DEM tiles (n40w112, n40w113, n41w112, n41w113), counties, UDOT routes, NHD | gis.utah.gov SGID |
| 4 | cell tower points | mapcruzin.com |
| 7 | Big Southern Butte, Idaho: two NED tiles | USGS National Map |
| 8 | Y Mountain / Utah County DEM | (no source given in the lab) |
| 9 | South Dakota counties, roads, rivers, wind farms, 80 m wind speed raster | gis.sd.gov, USWTDB, NREL |

## Per-lab image plan

Every ArcGIS-derived image is listed by the file name in `docs/assignments/lab-NN/images/`.
"Leave" = not an ArcGIS capture (diagram, photo, web page, student map) — outside this task.
"Export" = a zoomed-out full-model canvas grab that is illegible; rebuild the model and export it
from ModelBuilder (ModelBuilder ▸ Export ▸ To Graphic) rather than screen-grabbing.

### Lab 1 — Walmart (20 images) — GATED

Do **not** re-shoot until `ARCGIS_PRO_VALIDATION_CHECKLIST.md` passes; the current images encode
the old `CensusBlocks2010` / `!POP100!/!SqMiles!` / `CARTO = 1,2,3,6` workflow and re-shooting now
would just freeze those errors into new pixels. When unblocked: 19 ArcGIS captures
(`lab01-*-dialog.png`, `lab01-*-model.png`, `lab01-parameter-add-to-display-menu.png`;
`lab01-full-model-overview.png` is an Export). Leave `lab01-example-map-utah-county.jpg`.
Running the checklist is itself most of the lab, so this is a full session on its own.

### Lab 2 — NDVI (9)

Re-shoot 8: `lab02-float-tool-modelbuilder.png`, `lab02-minus-tool-dialog.png`,
`lab02-plus-tool-dialog.png`, `lab02-divide-tool-dialog.png`,
`lab02-minus-plus-divide-modelbuilder.png`, `lab02-reclassify-tool-dialog.png`,
`lab02-reclassify-modelbuilder.png`; `lab02-example-model-full.png` is an Export. Keep the
variable names the captions use (NIRFloat, REDFloat, NDVI NUMERATOR/DENOMINATOR, NDVI Values,
Reclass NDVI). Leave `lab02-example-map-utah-county.jpg`. Note the Plus dialog caption has
RED as input 1 and NIR as input 2 — order does not matter for Plus, match the caption anyway.

### Lab 3 — Georeferencing (13) — best first target, mostly pure UI

Re-shoot 11: `lab03-random-location.png` (raster before georeferencing, lands at 0,0 in the Gulf
of Guinea — add the "My Historic Map" callout back as a Pro graphic or crop so the speck is
visible), `lab03-georeference-button.png` (Imagery tab ▸ Alignment ▸ Georeference),
`lab03-fit-to-display.png` (also show the layer transparency slider the caption promises),
`lab03-georeference-tab.png` (the whole contextual tab), `lab03-control-point-example.png`
(show at least one control point placed), `lab03-new-feature-class.png` (Catalog ▸ gdb ▸ New ▸
Feature Class; rename the gdb so it is not "Lab 2"), `lab03-edit-create-features.png`,
`lab03-add-field-button.png` (button label is "Add" — check), `lab03-fields-view.png`,
`lab03-attribute-table-filled.png`, `lab03-labeling.png`. Leave the two student maps.

### Lab 4 — Cell towers (14)

Export: `lab04-full-model-overview.png` (also names a "Lab 8" geodatabase).
Re-shoot 12: the ModelBuilder chains `lab04-mosaic-to-new-raster.png`,
`lab04-slope-raster-calculator.png`, `lab04-project-buffer-udot-routes.png`,
`lab04-extract-by-mask.png`, `lab04-select-buffer-county.png`, `lab04-project-clip-towers.png`,
`lab04-kernel-density-model.png`, `lab04-density-threshold-raster-calculator.png`,
`lab04-combine-rasters-raster-calculator.png`; the dialogs `lab04-clip-tool-dialog.png`,
`lab04-kernel-density-dialog.png`, `lab04-density-threshold-raster-calculator-dialog.png`.
Leave `lab04-example-result-map.jpg`.

### Lab 5 — Watersheds (19)

Leave Figs 1–3 (`lab05-*-diagram.png`) and `lab05-example-map-rock-canyon.jpg`.
Export: `lab05-example-model-overview.png`.
Re-shoot 14: `lab05-mosaic-to-new-raster-model.png`, `lab05-mosaic-to-new-raster-dialog.png`
(both currently name "Lab 8 - Watershed Delineation.gdb"), `lab05-project-raster-model.png`,
`lab05-fill-model.png`, `lab05-flow-direction-model.png`, `lab05-flow-accumulation-model.png`,
`lab05-flow-accumulation-dialog.png`, `lab05-greater-than-model.png`,
`lab05-raster-to-polyline-model.png` (fix the mislabeled "Calculated Watersheds" input),
`lab05-feature-vertices-to-points-model.png`, `lab05-watershed-model.png`,
`lab05-raster-to-polygon-model.png`, `lab05-export-selected-watersheds.png` (was cropped for
privacy; a clean re-shoot with no sign-in visible is better), `lab05-custom-tool-interface.png`.

### Lab 6 — Avalanche (11)

Leave Figs 1–3 (web captures, danger scale) and `lab06-example-map-snowbird.png`.
Export: `lab06-example-model-overview.png`.
Re-shoot 6: `lab06-model-project-raster.png`, `lab06-model-slope.png`, `lab06-model-aspect.png`
(make the upstream variable read "Projected DEM" to match Fig 4), `lab06-model-reclassify-three.png`,
`lab06-reclassify-aspect-window.png`, `lab06-raster-calculator-con.png`.

### Lab 7 — Big Southern Butte (14)

Leave `lab07-big-southern-butte-photo.jpg` and `lab07-example-results-map.png`.
Export: `lab07-complete-model-overview.png`.
Re-shoot 11: `lab07-butte-raster-elevation.png`, `lab07-butte-boundary-polygon.png`,
`lab07-points-boundary-polygon.png`, `lab07-mosaic-to-new-raster.png` (names a "Lab 8" gdb),
`lab07-project-raster.png`, `lab07-create-random-points.png`, `lab07-extract-values-to-points.png`,
`lab07-erase-and-idw.png`, `lab07-extract-by-mask.png`, `lab07-raster-calculator.png` (the
variable names differ from the text's expression — match the text), `lab07-zonal-statistics.png`.

### Lab 8 — Interpolation (2)

Leave `lab08-fixed-radius-interpolation-concept.png`. Re-shoot/Export
`lab08-example-modelbuilder-model.png` after rebuilding the Thiessen + IDW branches; keep the two
annotation call-outs, they are part of the figure's meaning.

### Lab 9 — Wind farm (28) — the current Pro look; other labs should match it

Leave `lab09-sd-wind-speed-80m-map.png` and `lab09-example-map.png`.
Export: `lab09-model-overview-preprocessing.png`, `lab09-model-overview-weighted-sum.png` — and
fix the stale node labels while rebuilding (cities 30 mi not 20, roads 2 mi not 2 km, rivers 1 mi).
Re-shoot 24: model chains `lab09-select-counties-model.png`, `lab09-intersect-model.png`,
`lab09-buffer-model.png`, `lab09-polygon-to-raster-model.png`, `lab09-clip-raster-model.png`,
`lab09-reclassify-model.png`, `lab09-weighted-sum-model.png` (was painted over for privacy),
`lab09-final-steps-model.png`; dialogs `lab09-select-counties-dialog.png`,
`lab09-intersect-roads-dialog.png`, `lab09-buffer-{cities,roads,rivers,windfarms}-dialog.png`,
`lab09-polygon-to-raster-dialog.png`, `lab09-reclassify-{cities,roads,rivers,windfarms,wind-speed}-dialog.png`,
`lab09-weighted-sum-dialog.png`, `lab09-get-raster-properties-dialog.png`,
`lab09-equal-to-dialog.png`, `lab09-raster-to-point-dialog.png`.

### Lab 10 — Least cost path (22) — decision needed first

Figures 17–20 (`lab10-cost-distance-*.png`, `lab10-cost-path-*.png`) show **Cost Distance /
Cost Path**, which Esri has deprecated in favor of **Distance Accumulation + Optimal Path As Line**.
Re-shooting them as-is would publish the deprecated dialogs at higher resolution. `ROADMAP.md`
says fix the tool choice before touching these. The remaining 17 (Mosaic, Select/Buffer, Clip/
Intersect, Buffer/Multiple Ring Buffer and its two tabs, Polygon to Raster and its two tabs,
the five Reclassify dialogs, Raster Calculator, Raster to Polyline) can be re-shot independently
of that decision. Export: `lab10-full-model-overview.png`. Leave `lab10-example-map.png`.

## Suggested order

1. **Lab 3** — no data dependency beyond one historic map image; eleven pure-UI captures.
2. **Lab 2** — six dialogs, one Landsat scene.
3. **Labs 5, 6, 4, 10 (non-deprecated part)** — one download of the Utah DEM tiles serves all four.
4. **Lab 9** — South Dakota data; the reference look for everything else.
5. **Labs 7 and 8** — Idaho and Y Mountain DEMs.
6. **Lab 1** — after the validation checklist. **Lab 10 Figs 17–20** — after the tool decision.

## Definition of done for this task, per lab

- Every "Re-shoot" image above either replaced by a capture from the live session or explicitly
  recorded as "checked, still correct" in the lab's migration-notes comment.
- Every "Export" image replaced by a ModelBuilder export at a legible scale.
- Migration-notes comment updated with the ArcGIS Pro version and the date.
- Page rendered (`mkdocs serve`) and each new figure looked at in place.
