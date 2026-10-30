# ArcGIS Tips — screen-capture plan

Shot list for the **ArcGIS Tips** menu (`docs/arcgis-tips/`, added Oct 29, 2026 in 1c3e039 and
68d6f9c). Those pages are almost all text and carry 8 "Figure placeholder:" notes and 6
"[To do: confirm …]" notes. The menu is there to walk students through the tricky parts of
ArcGIS Pro step by step, so this plan goes well past the placeholders: every trap gets a picture of the
trap itself (the default state), and most get a second picture of the fixed state.

Method: `tools/screenshots/README.md` and the Lessons sections in it. 175 % scaling (`setdpi.py 175`
before launching ArcGIS Pro), `grabwin.py` / `grabdlg.py` for dialogs, `cap.py` + `crop.py` with a
background sleep for menus and tooltips, park the Claude window, stop Grammarly, PNG for dialogs and
JPEG for map views.

## Conventions for these figures

- **Folder:** `docs/arcgis-tips/images/` (new). Nothing references an image outside its own folder,
  so the lab captures listed under *Reuse* are **copied** there, not linked.
- **Names:** `<page>-<what>.png`, e.g. `wrong-defaults-buffer-meters.png`.
- **Trap / fix pairs:** where a tip says "it opens at X, set it to Y", capture the dialog as it
  opens (X, *wrong*) and as fixed (Y, *right*). On the page, put them side by side or one after the
  other, with captions that start "As it opens:" and "Fixed:".
- **Callouts:** a red rounded rectangle around the one control that matters, sometimes with a
  short label ("Delete Intermediate Data — do not click"). There is no helper for this yet, so the
  first job is a small `tools/screenshots/callout.py IN OUT x0 y0 x1 y1 [label]` (Pillow, 4 px
  #D62728 stroke at 175 %, label in a white box). Use at most one or two callouts per image.
- **Paths read `D:\Smith\…`.** This Dell has no D: drive. For the session, map one:
  `subst D: C:\Ames\TipsD` (undo with `subst D: /d`). The captures then match the workspace page
  instead of needing a "this was captured on C:" caption.
- **Projects:** a fresh `D:\Smith\Lab01` project made on camera (workspace shots), and copies of
  the existing GUI projects for everything else, so the originals stay clean:
  Lab01 (Buffer, Add Field, Select, SQL), Lab02 (rasters, Reclassify, NDVI model, Intermediate),
  Lab04GUI (Mosaic, Project Raster, Kernel Density), Lab05GUI (Snap Pour Point, Raster to Polygon),
  Lab06GUI (Con / SQL Editor, `%name%` outputs), Lab08GUI (Thiessen, Polygon to Raster, Zonal
  Statistics, the multi-frame comparison layout for the credits page), Lab12GUI (Snowbird
  `Shape__Area`).
- **Alt text** describes every visible value, as the labs do. Captions say what to look at.

Counts: **★ = fills an existing placeholder** (8), **new** = added for hand-holding, **reuse** = copy
an existing lab capture (still check it against ArcGIS Pro 3.7.1, and re-take it if the lab state shows through
in a confusing way).

---

## 1. Set up your workspace and project — `workspace.md`

| # | File | State to capture | Callout |
|---|---|---|---|
| 1.1 | `workspace-folders.png` | File Explorer at `D:\Smith\` showing `Lab01 … Lab03` folders, the address bar reading `D:\Smith` | none |
| 1.2 | `workspace-space-in-name-error.png` | A raster tool failing on a path with a space (e.g. Slope writing to `D:\John Smith\Lab 01\`), with the red error message. **Only if it reproduces in 3.7.1**; if the tool succeeds, drop this shot and soften the page's wording (to-do below) | error text |
| 1.3 | `workspace-new-project-dialog.png` | New Project ▸ Map dialog as it opens: default Location (`C:\Users\…\Documents\ArcGIS\Projects`) and *Create a folder* **checked** | Location box + check box |
| 1.4 | `workspace-browse-name-box.png` | The browse dialog with `D:\Smith\Lab01` typed in the **Name** box at the bottom | Name box |
| 1.5 | `workspace-new-project-fixed.png` | New Project dialog fixed: Name `Lab01`, Location `D:\Smith\Lab01`, *Create a folder* **unchecked** | check box |
| 1.6 | `workspace-nested-folder.png` | The result of leaving the box checked: Catalog pane (or Explorer) showing `D:\Smith\Lab01\Lab01\Lab01.aprx` | the doubled folder |

## 2. Set the coordinate system before you measure — `coordinate-system.md`

| # | File | State | Callout |
|---|---|---|---|
| 2.1 | `crs-modelbuilder-environments-button.png` | ModelBuilder ribbon tab, **Model** group, Environments button | button |
| 2.2 | `crs-environments-empty.png` | Environments dialog, Output Coordinate System empty (as it opens) | the box |
| 2.3 | `crs-picker-search.png` | Coordinate system picker with `utm zone 12n` searched and **NAD 1983 UTM zone 12N** highlighted | the result row |
| 2.4 | `crs-environments-set.png` | Environments dialog with NAD_1983_UTM_Zone_12N set | the box |
| 2.5 | `crs-area-three-ways.png` | Attribute table of Utah County showing a `Shape_Area` (or calculated area) of ≈ 0.59 (degrees), ≈ 3,668 (Web Mercator), ≈ 2,141 sq mi (UTM): three small table crops stacked, labeled. Compute geometry with Calculate Geometry so the numbers come from ArcGIS Pro itself, not from me | the value cell |
| 2.6 | `crs-map-properties-web-mercator.png` | Map ▸ Properties ▸ Coordinate Systems showing WGS 1984 Web Mercator (auxiliary sphere): what "my data came in Web Mercator" looks like | the current CRS line |
| 2.7 | `crs-snowbird-shape-area.png` | Lab 12: the attribute table of the service layer showing `Shape__Area` ≈ 18.7 million beside the exported UTM copy's `Shape_Area` ≈ 10.78 million | both fields |
| 2.8 | `crs-export-environments.png` | Export Features ▸ Environments tab with Output Coordinate System set | the box |
| 2.9 | **reuse** `lab02-environments-dialog.png` | can stand in for 2.4 if it shows Output Coordinate System clearly | — |

## 3. Housekeeping — `housekeeping.md`

| # | File | State | Callout |
|---|---|---|---|
| 3.1 | `housekeeping-shapefile-parts.png` | File Explorer showing one shapefile's `.shp .shx .dbf .prj .cpg` side by side, next to the Catalog pane showing it as one item | none |
| 3.2 | `housekeeping-catalog-rename.png` | Catalog pane right-click on a feature class with **Rename** highlighted | Rename |
| 3.3 | `housekeeping-model-labels.png` | Two crops of the same model: default labels (`Output Feature Class`, `Select_Output_3`) vs descriptive (`HighDensity_Tracts`) | none |

## 4. Defaults that give a confidently wrong answer — `wrong-answer-defaults.md`

Ten items, each a trap/fix pair. This page gains the most from pictures.

| # | File | State | Callout |
|---|---|---|---|
| 4.1a | `wrong-defaults-buffer-meters.png` | Buffer, Distance `2`, unit box reading **Meters** (set itself) | unit box |
| 4.1b | `wrong-defaults-buffer-unit-list.png` | the unit list open with **Statute Miles** highlighted (no plain "Miles") | Statute Miles |
| 4.1c | `wrong-defaults-buffer-two-meters-map.jpg` | map: a 2 m buffer (invisible ring) next to the 2-mile buffer; zoomed so the size difference is plain | none |
| 4.2a | `wrong-defaults-add-field-long.png` | Add Field with Field Type **Long** (default) | Field Type |
| 4.2b | `wrong-defaults-add-field-double.png` | Field Type list open at **Double (64-bit floating point)** | the item |
| 4.2c | `wrong-defaults-long-vs-double-table.png` | a table with the same calculated density in a Long field and a Double field (resolves the rounds/truncates to-do; see below) | the two cells |
| 4.2d | `wrong-defaults-calcfield-text.png` | Calculate Field with a new field name typed and the Field Type box at **Text** | Field Type |
| 4.3a | `wrong-defaults-run-dialog-open.png` | ModelBuilder: a Select dialog open with an expression typed, the ribbon **Run** button in view | Run + OK |
| 4.3b | `wrong-defaults-ok-moves.png` | the same Select dialog before and after switching on the SQL Editor, showing OK lower down (two crops side by side) | OK in both |
| 4.4a | `wrong-defaults-dissolve-none.png` | Buffer, Dissolve Type **No Dissolve** | box |
| 4.4b | `wrong-defaults-dissolve-map.jpg` | map pair: overlapping road buffers (outlines on) vs one dissolved zone | none |
| 4.5 | `wrong-defaults-mosaic-pixel-type.png` | Mosaic To New Raster, Pixel Type **8 bit unsigned** and Cellsize empty | Pixel Type |
| 4.5r | **reuse** `lab04-mosaic-dialog.png` | fixed state (32 bit float) | — |
| 4.6a | `wrong-defaults-snap-zero.png` | Snap Pour Point, Snap distance **0** | box |
| 4.6b | `wrong-defaults-snap-tiny-basin.jpg` | map: a few-cell "watershed" from an unsnapped click beside the real basin | the speck |
| 4.6r | **reuse** `lab05-snap-pour-point-dialog.png` | fixed (50 m) | — |
| 4.7a | `wrong-defaults-multipart-off.png` | Raster to Polygon with *Create multipart features* unchecked | check box |
| 4.7b | `wrong-defaults-multipart-count.png` | attribute tables: 61 rows vs 29 rows (Lab 5 subwatersheds) | record count |
| 4.8a | `wrong-defaults-thiessen-fid.png` | Create Thiessen Polygons at **Only feature ID** | Output Fields |
| 4.8b | `wrong-defaults-polygon-to-raster-objectid.png` | Polygon to Raster with Value field **OBJECTID** | Value field |
| 4.8r | **reuse** `lab08-thiessen-polygons.png` | fixed (All fields) | — |
| 4.9a | `wrong-defaults-zonal-mean.png` | Zonal Statistics at **Mean**, Zone field `OBJECTID` | both boxes |
| 4.9b | `wrong-defaults-zonal-sum-list.png` | the statistic list scrolled to **Sum** | Sum |
| 4.10a | `wrong-defaults-kd-proposed.png` | Kernel Density right after the input is set: cell size ≈ 1,772, radius empty | both |
| 4.10r | **reuse** `lab04-kernel-density-settings.png` | fixed | — |

## 5. Check what a tool actually produced — `check-your-output.md`

| # | File | State | Callout |
|---|---|---|---|
| 5.1 | `check-output-record-count.png` | attribute table footer showing **"0 of 29 selected"** / record count, with the counter called out | footer |
| 5.2 | `check-output-gp-success.png` | Geoprocessing pane green "completed" banner for a Select that returned 0 features, beside its empty table: success ≠ right | banner + count |
| 5.3 | `check-output-intersect-count.png` | before/after counts across an Intersect with the county line (more features than you started with) | counts |
| 5.4 | `check-output-view-messages.png` | the **View Details** link and the messages window with the feature count line | link |

## 6. Writing attribute expressions — `attribute-expressions.md`

| # | File | State | Callout |
|---|---|---|---|
| 6.1 | `expressions-clause-mode.png` | Select ▸ expression builder in clause mode: `Where NAME is equal to UTAH` | the clause row |
| 6.2 | `expressions-sql-toggle.png` | the same with **SQL Editor** on: `NAME = 'UTAH'` | the toggle |
| 6.3 | `expressions-case-zero.png` | `NAME = 'Utah'` with the green check **and** a 0-record result | both |
| 6.4 | `expressions-field-type-text.png` | Fields view of the UGRC roads layer showing `CARTOCODE` as **Text** | Data Type |
| 6.5 | `expressions-in-list.png` | `CARTOCODE IN ('1','2','3')` in the SQL Editor (the values here must come from the real field; read them off 6.4's layer before typing) | none |
| 6.6 | `expressions-pick-list-standalone.png` | standalone Select: the value dropdown listing unique values | the list |
| 6.7 | `expressions-no-pick-list-model.png` | the same tool inside ModelBuilder on a model variable: empty value box | the box |

## 7. Tool dialogs that change what you typed — `dialog-surprises.md`

| # | File | State | Callout |
|---|---|---|---|
| ★7.1 | `dialog-raster-calc-reset.png` | Raster Calculator with an expression typed and Output raster reset to `RasterC_1` (placeholder) | output box |
| 7.2 | `dialog-extract-mask-reset.png` | Extract by Mask after changing the input: the typed name replaced | output box |
| 7.3 | `dialog-sql-cleared.png` | Lab 6 Con: expression present (left), then SQL Editor toggled off and on and the box empty (right) | the box |
| 7.4 | `dialog-green-check.png` | "The SQL expression is valid" message close-up | message |

## 8. Running a model from its tool dialog — `running-models.md`

| # | File | State | Callout |
|---|---|---|---|
| 8.1 | `models-before-dialog-run.png` | Contents pane after a ModelBuilder run: all the intermediate layers present | the layers |
| 8.2 | `models-after-dialog-run.png` | the same after a dialog run: only parameter outputs remain (and a red "!" broken-link layer if that is what ArcGIS Pro shows; capture whatever happens) | the gap |
| 8.3 | `models-parameter-menu.png` | right-click an oval ▸ **Parameter** highlighted, and the P badge on the oval afterwards | menu item + badge |
| ★8.4 | `models-delete-intermediate.png` | canvas toolbar with **✗ Intermediate** called out, labeled "Delete Intermediate Data — do not click" (placeholder) | button + label |
| 8.5 | `models-ctrl-i-command.png` | Command Search finding **Intermediate Data (Ctrl+I)**; take it only if the Ctrl+I to-do comes out in favor of keeping it on the page | command |
| 8.6 | `models-close-tab.png` | the ModelBuilder view tab's ✕ close button | ✕ |
| ★8.7 | `models-catalog-edit-open.png` | Catalog pane, `Lab02.atbx` expanded, model right-click menu with Edit and Open (placeholder) | Edit, Open |
| 8.8 | `models-tool-dialog.png` | the model open as a tool in the Geoprocessing pane, parameters filled | none |
| 8.9 | `models-empty-parameters.png` | the same tool with the model tab still open: empty parameter list (only if it reproduces) | — |
| 8.10 | `models-output-exists-warning.png` | an output box with the yellow "already exists" warning icon and its tooltip | icon |
| 8.11 | `models-close-on-completion.png` | the run's progress/messages with **Close on completion** unchecked | check box |
| 8.12 | **reuse** `lab02-catalog-model.png` | if it shows the toolbox tree clearly | — |

## 9. Creating a point feature class — `point-feature-class.md`

Already step-numbered, so one picture per step.

| # | File | State | Callout |
|---|---|---|---|
| 9.1 | `points-new-feature-class-menu.png` | Catalog ▸ Databases ▸ `Lab01.gdb` right-click ▸ New ▸ Feature Class | menu path |
| 9.2 | `points-wizard-name-type.png` | wizard page 1: name `Candidate_Sites`, Type **Point** | Type |
| 9.3 | `points-wizard-fields.png` | Fields page with a `NAME` text field added | new row |
| 9.4 | `points-wizard-crs.png` | Spatial Reference page with NAD 1983 UTM zone 12N | CRS |
| 9.5 | `points-create-features-pane.png` | Edit ▸ Create and the Create Features pane with the new layer's template | template |
| 9.6 | `points-placed-on-imagery.jpg` | three points placed on imagery at a sensible zoom | none |
| 9.7 | `points-save-edits.png` | Edit tab **Save** button (and the Save Edits prompt) | Save |
| 9.r | **reuse** `lab03-new-feature-class.png`, `lab03-edit-ribbon-create.png`, `lab03-edit-create-features.png` | for 9.2 and 9.5 if they read as generic (they are polygon, so likely re-take as point) | — |

## 10. Working with rasters — `rasters.md`

| # | File | State | Callout |
|---|---|---|---|
| 10.1 | **reuse** `lab02-pyramids-statistics-prompt.png` | Build Pyramids and Calculate Statistics prompt | — |
| 10.2 | `rasters-flat-gray.jpg` | a raster with no statistics drawing as a flat gray block | none |
| 10.3 | `rasters-integer-ndvi.png` | Symbology/histogram of an integer NDVI with only 0 and 1 values, beside the Float version's spread | value range |
| 10.4 | `rasters-float-tool.png` | the Float tool placed before Minus in a model (canvas crop) | Float |
| 10.5 | `rasters-nodata-vs-zero.jpg` | identify pop-up on a NoData cell ("NoData") vs a 0 cell | the values |
| 10.6 | `rasters-reclass-table.png` | Reclassify table: the empty last row being typed into, a selected row ready for Delete | last row |
| 10.7 | `rasters-reclass-classify.png` | the Classify dialog with method and count | class count box |
| 10.8 | `rasters-percent-variable.png` | Raster Calculator with `Con("%NDVI%" >= %Threshold%, 1, 0)` and the connectors drawn on the canvas behind it | the `%…%` text |
| 10.9 | **reuse** `lab02-raster-calculator-dialog.png`, `lab02-reclassify-tool-dialog.png` | where they already show the point | — |

## 11. Projecting a DEM — `projecting-dems.md`

| # | File | State | Callout |
|---|---|---|---|
| 11.1 | `dem-raster-info-degrees.png` | unprojected mosaic Properties ▸ Source ▸ Raster Information: cell size ≈ 0.000278 (or whatever ArcGIS Pro shows), GCS | cell size |
| ★11.2 | **reuse** `lab04-project-raster-default-cellsize.png` | as it opens (24.05 × 30.96 proposed) | add callout |
| ★11.3 | **reuse** `lab04-project-raster-dialog.png` | fixed (Bilinear, 30 × 30), per the placeholder | add callout |
| 11.4 | `dem-resampling-list.png` | Resampling Technique list open, Bilinear highlighted | item |
| 11.5 | `dem-raster-info-projected.png` | Raster Information after projecting: 30 × 30, UTM | cell size |
| 11.6 | `dem-slope-units.png` | Slope dialog, Output measurement list (Degree / Percent rise) | list |
| 11.7 | `dem-nearest-steps.jpg` | hillshade of a Nearest-resampled DEM next to Bilinear: the stair-step artifacts (good visual, optional) | none |

## 12. Basemap credits cover a small map frame — `map-frame-credits.md`

Every shot here is also one of the to-dos, so this page is a **verify-and-capture** block.

| # | File | State | Callout |
|---|---|---|---|
| ★12.1 | `credits-before.png` | Lab 8 comparison layout, credits drawn across each small frame (placeholder) | one frame's credits |
| ★12.2 | `credits-dynamic-text-menu.png` | Insert ▸ New Dynamic Text, scrolled to Layout ▸ **Service Layer Credits** (placeholder) | the item |
| ★12.3 | `credits-after.png` | same layout after the fix: frames clear, one small element in the margin (placeholder) | the element |
| 12.4 | `credits-element-pane.png` | Element pane with the text at 6–7 pt | font size |
| ★12.5 | `credits-contents-unchecked.png` | layout Contents pane with Service Layer Credits unchecked (placeholder) | check box |
| 12.6 | `credits-pdf-check.png` | the exported PDF opened in a reader, showing whether the hidden element stayed hidden | none |

## 13. Exporting maps and models — `exporting-deliverables.md`

| # | File | State | Callout |
|---|---|---|---|
| 13.1 | `export-share-export-layout.png` | Share tab, **Export Layout** button (and the Print button it is not) | both |
| ★13.2 | `export-layout-pdf.png` | Export Layout pane, File Type PDF, default vector settings (placeholder) | File Type |
| 13.3 | `export-pdf-selectable.png` | the exported PDF in a reader with the title text selected (highlighted), proving it is vector | selection |
| ★13.4 | `export-modelbuilder-menu.png` | ModelBuilder Export menu open, **Export To Graphic** highlighted, the main button face (Send To Python Window) also marked (placeholder) | arrow vs face |
| 13.5 | `export-graphic-svg.png` | the Export To Graphic save dialog with SVG chosen | type |
| 13.6 | `export-analysis-history.png` | Analysis tab **History** button | button |
| 13.7 | **reuse** `lab07-history.png` | History pane with a card open | — |

## 14. Index page — `index.md`

| # | File | State |
|---|---|---|
| 14.1 | `index-hero.png` | optional: one ArcGIS Pro window with the Geoprocessing pane and a model open, as a page header. Skip if it looks like decoration (rule 9 is for decks; these are pages) |

---

## Verify while ArcGIS Pro is open (the [To do: confirm] notes)

Do these first in their sections, because the answers decide what some shots show.

| Page | To-do | Test | Shot |
|---|---|---|---|
| wrong-answer-defaults §2 | Long field: rounds or truncates? | Add a Long and a Double field; Calculate Field `8539.51` into both; read the table | 4.2c |
| running-models | Does `Ctrl+I` + save + close + reopen tool keep the dataset through a dialog run? | Lab02 copy: flag one oval, Ctrl+S, close tab, open from Catalog, run, check the gdb | 8.5 (or drop) |
| map-frame-credits (×3) | Placing the element clears *every* frame; deleting it restores them; unchecking hides it without restoring, and it stays hidden in PDF | Lab 8 layout copy, step by step, export a PDF after each | 12.1–12.6 |
| workspace (no to-do yet) | Do raster tools really fail on a path with a space in 3.7.1? | Slope to `D:\John Smith\Lab 01\x.tif` and to a gdb under it | 1.2, or soften the text |
| dialog-surprises | Raster Calculator replaced a name typed *after* the expression too | repeat 3× | 7.1 |
| Lab 4 Step (`lab-04/README.md:195`) | Catalog right-click on a model: is there **Rename**? | right-click a model in an .atbx | crop for Lab 4 if useful |
| Lab 7 Fig 5e (`lab-07/README.md:475, 499`) | How many times does Merge run after Collect Values? | Lab07HAND, run, read messages | none (text fix) |
| Lab 11 Step (`lab-11/README.md:353`) | Where is **Select Data**: ribbon Insert ▸ Utilities, or Geoprocessing search? | try both | crop for Lab 11 if useful |

## Rough size

About **95 shots**: 8 placeholders, about 75 new, and about 12 reused captures to check and copy. Two
sessions of a few hours each:

1. **Session A, dialogs (§4, §7, §8, §10, §11, §6):** mostly `grabdlg.py`, fast, and no layout work.
   Includes the Long/Double, Ctrl+I and Raster Calculator checks.
2. **Session B, panes, menus, layouts, and the D: workspace (§1, §2, §3, §5, §9, §12, §13):** more
   menus (background `cap.py`), the File Explorer shots, the credits experiment, PDF exports.

After each session: callouts, copy into `docs/arcgis-tips/images/`, replace each placeholder with
`![alt](images/…)` + **Figure N.** caption, delete each resolved to-do (or rewrite the sentence),
`mkdocs build --strict`, then look at every page in `mkdocs serve`.

---

## Session A results (October 30, 2026, ArcGIS Pro 3.7.0 at 175 %)

51 figures are in `docs/arcgis-tips/images/`, built from raw grabs in `C:\Ames\TipsD\caps` by
`tips_figures.py` (crops, callouts, patches). The project is `D:\Smith\Tips\Tips.aprx`
(`subst D: C:\Ames\TipsD`), made by `tips_setup.py`; `tips_watershed.py` rebuilds the Rock Canyon
subwatersheds. Pages updated: wrong-answer-defaults (24 figures), projecting-dems (6),
coordinate-system (4), running-models (5), rasters (5), attribute-expressions (3),
dialog-surprises (2), exporting-deliverables (2).

Checks settled:

- Long field **rounds** (8539.51 → 8540; exact halves to even). To-do removed.
- Intermediate Data flag: the oval's right-click ▸ **Intermediate Data** (checked by default; menu
  shows Ctrl+Shift+I when checked, Ctrl+I when not). Cleared + saved + tab closed + reopened from
  Catalog: the dataset survived a dialog run; flagged neighbors were deleted. To-do removed, page
  rewritten.
- Model right-click menu in Catalog has **no Rename** (Open, Edit, Batch, …, Properties). Bears on
  the Lab 4 to-do at `lab-04/README.md:195`; Lab 4 not edited.
- Raster to Polygon on Rock Canyon: 61 single-part vs 29 multipart. Confirmed.
- Snap Pour Point at 0: clicks 30–40 m N/S of the channel give 1–10-cell basins; 50 m recovers
  25.2 km². Confirmed (E–W offsets stay on the channel).
- Kernel Density proposes 1,772.48 m with UTM set (confirmed), 0.0198° without.
- Project Raster: Resampling switches to Bilinear by itself for a float DEM; proposed cell size for
  the geographic mosaic is 27.465 m square. Unprojected cell size 0.000278 (page said 0.0001; fixed).
- **Not reproduced:** Raster Calculator / Extract by Mask overwriting a typed output name (5 tries);
  Con clearing a SQL expression on toggle (3.7 refuses with "The expression can't be edited in
  Clause mode"). Page text softened, reasons in an HTML comment; no staged figure.
- Inside ModelBuilder, Select's value box **does** list values when the input is existing data;
  page corrected.

Moved to Session B: 1.x workspace, 2.5–2.8, 3.x, 4.1c/4.4b/4.6b map shots, 5.x, 6.3–6.5 and 6.7,
8.1/8.2 Contents before/after, 8.9, 9.x, 10.2/10.3/10.5, 11.7, 12.x credits, 13.1–13.3, 13.6.

## Session B results (October 30, 2026, afternoon)

34 more figures (85 in `docs/arcgis-tips/images/`). Dialog and pane grabs are cut by
`tips_figures.py`; the three map figures come from `tips_maps.py` (arcpy layout exports of real
data, on a copy `TipsMaps.aprx`); the credits layouts from `tips_export_layout.py`. Pages updated:
workspace (6), point-feature-class (8, one per step), map-frame-credits (4), exporting-deliverables
(6, Lab 7's History capture reused), check-your-output (3), wrong-answer-defaults (+3 maps:
2a, 8a, 12a), attribute-expressions (+1), housekeeping (1). Every "Figure placeholder:" and
"[To do: confirm ...]" on the tips pages is gone.

Checks settled:

- **Map-frame credits, all three to-dos:** a Service Layer Credits element clears the credits from
  all six frames; deleting it brings them back in all six; unchecking it in Contents hides it and
  the frames stay clear in PNG and PDF (pdftotext finds no credit text). Notes in an HTML comment.
- **Spaces in paths:** Slope and Buffer wrote to `D:\John Smith\Lab 01\...` without error in
  ArcGIS Pro 3.7.0. The rule stays; the "raster tools fail" claim was softened.
- **New Project:** the Location box offers recent folders and ignores typing (page was right).
- **Create Feature Class:** type opens at Polygon, Z Values checked, new field Data Type Long.
- **Select with `NAME = 'Utah'`:** validation says "valid, but no records were returned"; the run
  "completed with warnings" (WARNING 000117, empty output).
- **Export Layout** is an unlabeled icon on the Share tab at 175 %; "Output as image" is the
  setting that rasterizes a PDF.
- **Snap Pour Point:** an outlet 30 m north of the channel gives a 1-cell basin at 0 m, 25.2 km² at 50 m.

Not done: a capture of a PDF reader with text selected (13.3) — no reader app under desktop
control; the page states the check in words instead. 8.1/8.2 (Contents before/after a dialog run)
were dropped: the gdb listing is in `caps\gdb-after-mb-run-raw.png` if wanted.
