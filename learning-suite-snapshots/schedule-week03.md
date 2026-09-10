# Schedule cell edits — Week 3 (Sep 15 and Sep 17, 2026)

Applied September 9, 2026 to the Fall 2026 Schedule (`cid-ahk3xMzyr311`), to match the Week 3 plan
published the same day (commit `eebba03`: one Tuesday deck, *Raster Analysis and Map Algebra*, with
the retired *ModelBuilder, Part C* NDVI content folded in; a new Thursday deck, *Raster Analysis
Hands-On*; and a Thursday in-class activity). The instructor chose to keep every old data
attachment in the cells as an "Optional extra data" line rather than drop them.

## Tue Sep 15 — "Raster Analysis and Map Algebra - Part 1" → "Raster Analysis and Map Algebra"

Removed text (the deck link, the xlsx attachment and the kernels link were kept):

```html
<p><strong>Raster Analysis and Map Algebra - Part 1</strong></p>
<ul>
    <li><u>Discussion:</u>&nbsp;Introduction to Raster Data analysis including map algebra, moving windows, etc.&nbsp;</li>
    <li><span><u>In Class Activity</u>: Utah Raster Excel Analysis</span></li>
</ul>
```

Kept attachment: `raster analysis in class.xlsx` → `fileId=20d9d5fd-Wuxt-k15p-Bjjz-YT90e5d492cc`.

Added: a new discussion line, "In Class Activity: Simple Map Algebra in Excel (upload the workbook
to Learning Suite by 9:30 am)", "Lab: NDVI" → `/assignments/lab-02/`, and the NAIP attachment
from the deleted "NDVI Model" item as an "Optional extra data" line.

## Tue Sep 15 — "NDVI Model" item deleted

Its deck link pointed at `slides/week-03/modelbuilder-c.html`, which no longer exists (404). Full
removed markup:

```html
<p><strong>NDVI Model</strong></p>
<ul>
    <li>The NDVI Model:&nbsp;<a href="https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-03/modelbuilder-c.html" target="_blank">ModelBuilder &mdash; Part C (slides)</a>&nbsp;</li>
    <li>Explore Lehi NAIP data.&nbsp;Sample Data, NAIP Imagery for Lehi Utah:&nbsp;<span class="ck_embededFile"><span class="embededFile_Name">LehiNAIP2003-2018.zip</span>&nbsp;&nbsp;<span class="embededFile_FileOptions"><a class="embededFile_Download" href="plugins/Upload/fileDownload.php?fileId=c55ae691-5Ir2-3xKP-UeVH-SPfe006b84d3" target="_blank">Download</a></span></span><span>&nbsp;</span></li>
</ul>
```

The NAIP attachment (same `fileId`) now lives in the Tuesday cell above.

## Thu Sep 17 — "Raster Analysis and Map Algebra - Part 2" → "Raster Analysis Hands-On"

Removed text (all four attachments were kept, moved to an "Optional extra data" line):

```html
<p><strong>Raster Analysis and Map Algebra - Part 2</strong></p>
<ul>
    <li><u>Discussion:</u>&nbsp;
    <ul>
        <li>More on Map Algebra from prev. PPT</li>
        <li>Utah precipitation analysis in Excel</li>
        <li>(Convert&nbsp;ASCII to Raster to try it in ArcMap)</li>
    </ul>
    </li>
    <li><u>Data</u>:
    <ul>
        <li>Challenge:&nbsp;[utah map algebra data.xlsx]</li>
        <li><span>Solution: &nbsp;</span>[utah map algebra data - Solution.xlsx]</li>
        <li>[UtahRaster.zip],&nbsp;[UtahAvgAnnPrec.txt]</li>
    </ul>
    </li>
</ul>
```

Kept attachments (each a standard `ck_embededFile` span with `plugins/Upload/fileDownload.php?fileId=…`):

| File | fileId |
| --- | --- |
| `utah map algebra data.xlsx` | `0b714482-VVnO-JtTN-XY7W-qw2029f44eb4` |
| `utah map algebra data - Solution.xlsx` | `c8bf327c-q7ei-RB0a-EaVm-7057aa6167a8` |
| `UtahRaster.zip` | `04569e89-PTL7-fXgw-6dj4-9T5ba644cdd4` |
| `UtahAvgAnnPrec.txt` | `56dba1fb-KeCO-PaeH-IqRQ-Ex5141aabaa0` |

Added: the hands-on discussion line, "Slides: Raster Analysis Hands-On" → `/slides/week-03/raster-hands-on.html`,
"Bring: your Lab 2 project…", the UGRC municipal boundaries link, and "In Class Activity: Raster
Analysis Hands-On (upload the activity sheet to Learning Suite by 9:30 am)".

## New assignment

"In Class Activity - Raster Analysis Hands-On" — Attendance and Participation, 5 points, due Thu Sep 17
at 9:30 am, file upload, copied from "In Class Activity - Simple Map Algebra". This is the Learning
Suite item the deck's authoring notes said was missing.

## Rollback

Every removed span is reproduced or tabulated above with its `fileId`, so a cell can be restored
through the CKEditor **Source** view without re-embedding. The "NDVI Model" item itself must be
re-created as a new text item on Tue Sep 15 (the day's `⋯` menu has no undo).

## Superseded September 9, 2026 — the deck URLs in this snapshot are dead

Later on September 9 the Week 3 pair was resplit into Part A and Part B, and both slugs recorded
above changed:

| In this snapshot | Now |
| --- | --- |
| `/slides/week-03/raster-analysis-map-algebra.html` | `/slides/week-03/raster-analysis-a.html` |
| `/slides/week-03/raster-hands-on.html` | `/slides/week-03/raster-analysis-b.html` |

**TODO(instructor):** the Week 3 Tuesday and Thursday entries on Learning Suite still carry the old
links and will 404. Update both, and the deck titles with them: they are now "Raster Analysis and
Map Algebra, Part A" and "... Part B". The Thursday entry should also say that the hour opens with
the raster-function families and the threshold parameter before the four exercises.
