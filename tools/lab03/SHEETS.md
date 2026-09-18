# Candidate historic sheets, with provenance

Downloaded 2026-09-18 to `C:\Ames\Lab03\Data\` (outside this repository — these are working copies,
not hosted course data). All three are public domain, all three came from Wikimedia Commons, and all
three trace to a Library of Congress item. Re-download commands are in the table so the set can be
rebuilt.

If any of these is later hosted in `docs/data/` for students, it needs a `READ-ME-FIRST.txt` giving
provenance, processing, vintage, license and a credit line, per section 2 of the lab guide.

| File | Sheet | Date | Source | Size |
| --- | --- | --- | --- | --- |
| `stansbury_gsl_1852.jpg` | Map of the Great Salt Lake and adjacent country in the Territory of Utah | surveyed 1849–50, published 1852 | LOC 2018588045 | 9447 x 13337, 19.3 MB |
| `slc_plat_1847.jpg` | Plat of the Great City of the Valley of the Great Salt Lake | 1847 | LOC 2017587026 | 4328 x 6503, 3.0 MB |
| `slc_birdseye_1891.jpg` | Salt Lake City, Utah 1891 | 1891 | LOC 75696616 | 13970 x 8370, 15.1 MB |

Credits as Commons gives them: Stansbury sheet — Stansbury, Howard; Gunnison, J. W.; Carrington,
Albert; Preuss, Charles. Plat — Pratt, Orson; Sherwood, Henry Garlick. Bird's-eye — Wellge, H.,
American Publishing Co., Milwaukee.

## What each one is for

**Stansbury 1852 — the working example.** A real survey with a printed graticule, so it can be
georeferenced from its own coordinates as well as from ground features, and the difference between
those two answers is the sheet's survey error. It is visibly folded, so the crease lines are genuine
distortion of exactly the kind the lab's Data section warns about. It covers both Great Salt Lake and
Utah Lake, so it is local. Georeferenced; see `GEOREF_FINDINGS.md`.

**1847 plat — the idealized case.** The founding Salt Lake City plat, 135 blocks drawn as a perfect
grid on a leather scroll. Matchable to the downtown street grid that still exists, with Temple Square
as the anchor. Because the plat is an *intention* rather than a survey, its residuals measure the gap
between the plan and what was actually laid out on the ground — a different and more interesting
error than scanner distortion. The scroll's curl at the edges is real distortion too.

**1891 bird's-eye — the counter-example.** A panoramic view, drawn in perspective from an imagined
viewpoint northwest of the city. The street grid visibly converges toward a vanishing point, so scale
varies continuously across the image and no transformation in the ArcGIS Pro menu can fit it. This is
the sheet the lab's Data section tells students not to use, and five minutes of watching it fail in
class is worth more than the warning. Not to be georeferenced for real — the point is that it cannot
be.

## Note on the download format

All three arrived as plain JPEG, which is what the lab now tells students to take. Had the Stansbury
sheet been taken as a USGS-style GeoTIFF it would have arrived already georeferenced and none of the
above would have been possible — which is the reason for the warning added to the Data section on
2026-09-17.
