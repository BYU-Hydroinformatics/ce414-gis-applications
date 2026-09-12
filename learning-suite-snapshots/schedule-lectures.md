# Schedule cell edits — lecture decks

Applied September 3, 2026 to the Fall 2026 Schedule (`cid-ahk3xMzyr311`). In each cell the
`.pptx` attachment's `ck_embededFile` span was replaced with a link to the published deck.
Everything else in the cell — data `.zip` and `.xlsx` downloads, external links, prose — was
left untouched.

| Schedule item | Attachment removed | Now links to |
| --- | --- | --- |
| Thu Sep 3 · Spatial Data Models - Refresher | `414 - Data Models.pptx` | `/slides/week-01/data-models-refresher.html` |
| Tue Sep 8 · Model Builder Part 1 | `414 - ModelBuilder A.pptx` | `/slides/week-02/modelbuilder-a.html` |
| Thu Sep 10 · Model Builder Part 2 | `414 - ModelBuilder B.pptx` | `/slides/week-02/modelbuilder-b.html` |
| Tue Sep 15 · NDVI Model | `414 - ModelBuilder C.pptx` | `/slides/week-03/modelbuilder-c.html` |
| Tue Sep 15 · Raster Analysis Part 1 | `414 - Raster Analysis and Map Algebra.pptx` | `/slides/week-03/raster-analysis-map-algebra.html` |
| Tue Sep 22 · Image Georeferencing | `414 - Georectifying Images.pptx` | `/slides/week-04/georectifying-images.html` |
| Thu Sep 24 · Satellite and Imagery Data | `414 - Remote Sensing and 3D Imaging.pptx` | `/slides/week-04/remote-sensing-3d-imaging.html` |
| Tue Sep 29 · Terrain Analysis Part 1 | `Terrain Analysis.pptx` | `/slides/week-05/terrain-analysis.html` |
| Tue Oct 6 · Hydrologic Analysis Part 1 | `414 - Watershed Delineation.pptx` | `/slides/week-06/watershed-delineation.html` |
| Tue Oct 20 · Sampling and Interpolation Part 1 | `414 - Interpolation.pptx` | `/slides/week-08/interpolation.html` |
| Thu Oct 29 · Data Services and Data Quality | `Overview_of_OGC_Web_Services.pptx` | `/slides/week-09/ogc-web-services.html` |
| Tue Nov 3 · Raster-Based Site Suitability Part 1 | `414 - Raster Based Spatial Analysis.pptx` | `/slides/week-10/raster-spatial-analysis.html` |
| Tue Nov 10 · Least Cost Path Part 1 | `414 - Least Cost Path Analysis.pptx` | `/slides/week-11/least-cost-path.html` |
| Thu Nov 12 · Projections & Coordinate Systems | `Coordinate Systems and Projections.pptx` | `/slides/week-11/coordinate-systems-projections.html` |
| Thu Nov 19 · Differential GPS | `8 - GPS and Triangulation.pptx` | `/slides/week-12/gps-triangulation.html` |

Two lab names that had been plain text were also linked:

| Schedule item | Now links to |
| --- | --- |
| Tue Sep 8 · "Lab: Walmart Site Selection Model" | `/assignments/lab-01/` |
| Tue Sep 22 · "Lab: Georectifying and Digitizing Images" | `/assignments/lab-03/` |

## Rollback

> [!WARNING]
> Unlike the lab snapshots, the removed `fileId` GUIDs were **not** captured for most of these
> cells. Only two were recorded before the edit:
>
> - `414 - Data Models.pptx` → `fileId=4555c794-Gf2A-2Nfn-CMwU-nxa94be74f63`
> - `414 - ModelBuilder A.pptx` → `fileId=d0c504a5-DwuP-rQih-CUdX-Qie897b38949`

This is recoverable but more manual than the lab rollback. The `.pptx` files were not deleted —
they are still in the Learning Suite file store and in the course folder under `Lectures/2026/`.
To restore one, re-embed the file through the CKEditor file picker in the schedule cell rather
than pasting a recorded `fileId`.

## Deliberately left as downloads

- `engineering stamps.pptx` (Thu Sep 3) — example stamps for an in-class activity, not a lecture deck.
- The sixteen `Example Final Project - *.docx` / `.pdf` files (Tue Nov 17) — see open question 2
  in [`../LEARNING_SUITE_MIGRATION_PLAN.md`](../LEARNING_SUITE_MIGRATION_PLAN.md); undecided.
- All data `.zip`, `.xlsx` and `.txt` files, and the two prior-year student PDFs (Thu Sep 10).

## Pending after the 2026-09-10 LiDAR split — Weeks 4 and 5 deck links

The Week 4 Thursday deck was split and LiDAR moved to Week 5. Three schedule cells need attention;
none has been edited yet.

| Cell | Now points at | Should point at |
| --- | --- | --- |
| Thu Sep 24 · Satellite and Imagery Data | `/slides/week-04/remote-sensing-3d-imaging.html` — **404** | `/slides/week-04/remote-sensing.html`, titled "Remote Sensing" |
| Tue Sep 29 · Terrain Analysis Part 1 | `/slides/week-05/terrain-analysis.html` — resolves, but that is now the **Thursday** deck | `/slides/week-05/elevation-data-lidar.html`, titled "Elevation Data and LiDAR" |
| Thu Oct 1 · Week 5 Thursday | no entry recorded in this snapshot | `/slides/week-05/terrain-analysis.html`, titled "Terrain Analysis" |

**Applied 2026-09-11.** All three cells were edited and the hrefs verified after a reload. The
Thursday Week 5 cell existed after all, as "Terrain Analysis Part 2"; it simply had no slides link.

| Cell | Heading | Slides link |
| --- | --- | --- |
| Thu Sep 24 | Satellite and Imagery Data (unchanged) | "Remote Sensing" -> `/slides/week-04/remote-sensing.html` |
| Tue Sep 29 | "Terrain Analysis Part 1" -> "Elevation Data and LiDAR" | "Elevation Data and LiDAR (slides)" -> `/slides/week-05/elevation-data-lidar.html` |
| Thu Oct 1 | "Terrain Analysis Part 2" -> "Terrain Analysis" | "Slides: Terrain Analysis" -> `/slides/week-05/terrain-analysis.html`, **added**; the cell had none |

Discussion lines were rewritten on all three to describe what each deck now covers. Two other edits
followed from the split:

- The Thu Sep 24 bullet "3D models from LiDAR and Structure from Motion" (the BYU PRISM gallery)
  **moved** to Tue Sep 29, since Thursday no longer teaches LiDAR.
- Thu Sep 24's discussion no longer says "LiDAR and aerial/satellite imagery".

Every attachment, fileId and in-class activity line was left alone.

**TODO(instructor):** the graded assignment item **"In Class Activity - Terrain Analysis - Slope"**
still sits on **Tue Sep 29**, and the "Compute terrain variables" line with
`terrain analysis - in class activity.xlsx` is on that cell too. Slope is now **Thursday's**
material. Moving a graded item changes its due date, so nothing was touched — but the activity and
the lecture that teaches it are currently a day apart. The same xlsx is attached to the Thursday
cell as well, so the simplest fix may be to move the assignment item's date rather than any text.

