# Lab 4 pipeline

Scripts that verify Lab 4 (Cell Phone Tower Placement) and regenerate its data package and
figures. Run with the ArcGIS Pro Python,
`"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"`, in this order:

| Script | What it does |
| --- | --- |
| `fetch_towers.py` | Queries the HIFLD *Cellular Towers in the United States (Archive)* feature service for `LocState = 'UT'` and saves `C:\Ames\Lab04\Data\hifld_towers_UT.geojson`. |
| `make_extract.py` | Turns that GeoJSON into `UtahCellTowers.shp` plus `READ-ME-FIRST.txt` and zips them to `docs/data/lab04-utah-cell-towers.zip`. |
| `run_model.py [--sens]` | Runs the lab's model step for step in `C:\Ames\Lab04\Check.gdb` and writes `check_values.json` (baseline, and with `--sens` twelve one-at-a-time scenarios). About 50 s for the shared steps and 45 s per run. |
| `describe_zones.py` | Where the baseline's larger candidate zones are, the density range in the county, and what de-duplicating the towers changes; writes `zones.json`. |
| `scenario.py` | Re-runs every scenario, records whether the example recommended site survives (`site_survival.json`), and keeps the density-40 run for the example scenario map. |
| `make_svgs.py` | The six tool icons, Figure A (metadata) and Figure B (one tower's density, computed from the documented kernel). Figure C is a ModelBuilder SVG export, not generated. |
| `build_figures.py [checks\|layouts]` | The step check maps and the two example layouts, rendered by ArcGIS Pro through arcpy.mp into the lab's images folder. Needs ArcGIS Pro signed in for the basemaps. |

Inputs, as the page tells students to get them: the four USGS 1 arc-second tiles in
`C:\Ames\Lab04\Data\DEM\`, the UGRC `Counties` and UDOT `UDOT_Routes` shapefiles in
`C:\Ames\Lab04\Data\Counties\` and `...\UDOT_Routes\`, and the unzipped tower extract.

Lessons from building it (2026-09-24):

- **Mosaic To New Raster must not be given a cell size while it reprojects.** With a UTM spatial
  reference (from the tool or the environment) and `cellsize=30` it produced 117,789 × 128,657
  cells over a 3,500 km extent and took 38 minutes. With the cell size blank it takes 20 s but
  makes non-square 24.05 × 30.96 m cells, and it ignores `arcpy.env.cellSize`. Project Raster to
  30 m (bilinear) afterwards is the clean route.
- Kernel Density's output extent is the extent of the input points. The 50 km county buffer puts
  towers on every side of Utah County, so the density raster covers the county; a much smaller
  buffer might not.
- `BuildRasterAttributeTable` + a SearchCursor on `Value, Count` is the quickest way to get the
  "cells equal to 1" check values; the cursor needs a path, not a `Raster` object.
- Don't run a second arcpy script against `Check.gdb` while a scenario run is writing to it:
  it produced "ERROR 000871: Unable to delete the output".
- Raster layers symbolized through a CIM unique-value colorizer show in an arcpy.mp legend, but
  the legend overflows silently; check `legend.isOverflowing` and set `minFontSize` in the CIM.
