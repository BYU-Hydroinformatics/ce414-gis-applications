# Lab 5 pipeline

Scripts that verify Lab 5 (Watershed Delineation) and regenerate its data package and figures.
`fetch_dem.py` and `make_extract.py` run with the standalone Python 3.14 (rasterio); the rest run
with the ArcGIS Pro Python, `"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"`,
in this order:

| Script | What it does |
| --- | --- |
| `fetch_dem.py` | Reads the Rock Canyon window out of the USGS 1/3 arc-second tile `n41w112` over HTTP and writes `C:\Ames\Lab05\Data\RockCanyon_DEM.tif` unchanged. |
| `make_extract.py` | Zips it with `READ-ME-FIRST.txt` into `docs/data/lab05-rock-canyon-dem.zip`. |
| `run_model.py [thresholds]` | Runs the lab's model step for step in `C:\Ames\Lab05\Check.gdb` (project, outlet, Fill, Flow Direction, Flow Accumulation, Snap Pour Point, Watershed, the Step 8 expression, Stream Link, Stream to Feature, Watershed on the links, Raster to Polygon), clips the NHD (needs `Data\nhd_bbox.json`, a REST query of the UGRC service for the DEM box in UTM), and writes `check_values.json` with the threshold sweep. About 1 minute plus 15 s per threshold. |
| `extra_checks.py` | The failure-mode numbers the TIPs quote (unfilled DEM, snap distance 0, Web Mercator NHD length, where the accumulation maximum is); writes `extra_checks.json`. |
| `make_svgs.py` | The eight tool icons, Figure A (DEM metadata), Figure B (a real 5 x 5 D8 patch, recorded in `d8_patch.json`) and Figure C (a diagram of the model). |
| `build_figures.py [checks\|layouts]` | The five step check maps and the two example layouts, rendered by ArcGIS Pro through arcpy.mp. Needs ArcGIS Pro signed in for the basemaps, and Lab 4's `Utah_County` for the locator. |

`explore.py`, `peek.py` and `basin_check.py` are the first-look scripts that found the outlet.

Lessons (2026-09-29):

- The outlet coordinate 40.26525 N, 111.63 W sits on the DEM's channel; a point 40 m north of it
  with Snap distance 0 delineates one cell. Snap Pour Point moves it 45 m downstream.
- `Con(test, 1)` without a false value is what makes non-stream cells NoData; Stream Link treats
  every valued cell, including 0, as stream.
- Raster to Polygon without *Create multipart features* turns 29 subwatersheds into 61 polygons
  (diagonal-only connections).
- The UGRC NHD service is Web Mercator; a Clip left in it reports 49.1 km instead of 37.4 km.
- StreamStats' ss-delineate API: `https://streamstats.usgs.gov/ss-delineate/v1/delineate/sshydro/UT?lat=..&lon=..`
  (the old `streamstatsservices` endpoint returns 404).
- A 29-class unique-value layer overflows an arcpy.mp legend; draw the colors from one layer kept out
  of the legend and the outlines from a single-symbol copy that is in it.
