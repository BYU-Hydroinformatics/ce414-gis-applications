# Handoff to the Claude session on the Windows ArcGIS Pro machine: finish the Week 4 remote-sensing deck

**Written:** 2026-09-23, on the Mac, the evening before the lecture (Thursday of Week 4).
**Deck:** `slides/week-04/remote-sensing.md`, published at
`https://byu-hydroinformatics.github.io/ce414-gis-applications/slides/week-04/remote-sensing.html`.

You are the Claude instance on the Windows PC that has ArcGIS Pro. The Mac session revised this
deck but could not make ArcGIS Pro captures. Your job is to make those captures and put them in the
deck. The deck is already teachable as it is: every stand-in is honest and labeled. So do the items
in order and stop cleanly wherever time runs out.

## Before you start

1. `git pull` on `main`. You should see commits `2ff2d11` and `013fe4e`, or later.
2. Read `CLAUDE.md`, then `tools/week04-arcgis-capture-plan.md`. The capture plan is the
   authoritative checklist, and this file only adds how to run it on this machine. The hard rules
   that matter most here:
   - **Never fabricate a screenshot.** Every image you add must be captured from a live ArcGIS Pro
     session.
   - **Verify in ArcGIS Pro before asserting.** The plan marks menu names it could not check with
     `VERIFY`. Confirm them in ArcGIS Pro and fix the plan's wording if it is wrong.
   - Write "ArcGIS Pro" in full in anything a student reads.
3. Read `tools/screenshots/README.md` for the capture helpers on this machine and the lessons from
   earlier sessions: display scaling, `PrintWindow` versus screen grabs, parking the Claude window,
   and Grammarly. Run the helpers with ArcGIS Pro's Python:
   `"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" tools\screenshots\<script>.py ...`
4. Work in a project such as `C:\Ames\Week04\RemoteSensing.aprx`. Earlier weeks used `C:\Ames\WeekNN`.

## The work, in priority order

### A. Band splits of the four example images (highest priority: four slides use them tomorrow)

Section 5 of the deck ("Pulling Real Images Apart") has four slides: "The Eiffel Tower, band by
band", "Snow or cloud?", "Smoke from the 2007 California wildfires", and "Europe at night". Each
slide shows a full-color image beside its red, green, and blue bands. Those band images
(`slides/week-04/images/rs-band-<key>-<band>.jpg`) were computed with Python by
`tools/week04_remote_sensing_figures.py`. Replace them with ArcGIS Pro captures, following
section 2 of the capture plan:

- The source images are already in the repo: `slides/week-04/images/rs-eiffel-tower-aerial.jpg`,
  `rs-maryland-snow.jpg`, `rs-california-wildfires.jpg`, and `rs-europe-at-night.jpg`. Copy them into
  the project folder and add each one to the map.
- Show one band at a time with a **Stretch** renderer fixed at **0–255**, so it is not
  auto-stretched. Use a **black-to-red**, **black-to-green**, or **black-to-blue** ramp. The
  instructor asked for single-color ramps rather than grayscale. Black-to-color is the current
  choice because the three bands then add back up to the original. If you cannot build a
  black-to-color ramp, stop and ask Dan rather than substituting grayscale.
- Capture the map view with the Symbology pane visible, so students can see the 0–255 range and
  the ramp. Save each capture as `slides/week-04/images/rs-arcgis-<key>-<band>.png`, where key is
  `eiffel`, `snow`, `smoke`, or `night` and band is `red`, `green`, or `blue`. Use JPEG instead if
  the capture is mostly imagery and the PNG is large.
- The layout constraint: each slide shows four images side by side at about 290 px wide each. A
  capture that includes the Symbology pane will be too small to read at that size. Two options, in
  order of preference:
  1. Capture the **map view only** for the three band tiles, so they look like the current tiles.
     Then add **one** capture of the Symbology pane (for the Eiffel red band) to the Eiffel slide's
     speaker note, or as a small inset. Ask Dan which he prefers if he is around.
  2. Or redesign that one slide as full color plus the Symbology pane on top, with the three bands
     below. Render it and check that it reads before committing to it.
- Swap the `<img src="images/rs-band-...">` references in the four slides, and update each
  slide's speaker note: remove the "split by script, not ArcGIS Pro" sentence and the `TODO`, and
  say what was captured.
- Check that the bullet claims still hold in the ArcGIS Pro rendering. The claims were checked
  against pixel values, for example smoke over water at about R 88, G 112, B 123 against desert at
  about R 198, G 171, B 142. If a claim looks wrong in ArcGIS Pro, flag it; do not quietly edit it.
- Once all four slides use ArcGIS Pro captures, delete the twelve unused `rs-band-*.jpg` files and
  the `band_splits()` step in `tools/week04_remote_sensing_figures.py`, or leave the function and
  remove only its call. Say which you did.

### B. Re-create the three MODIS band slides

These are the slides "Band 1 — red", "Band 4 — green", and "Band 3 — blue", in section 3. Follow
section 1 of the capture plan.

- **Data.** EarthExplorer needs Dan's USGS login, and you must not enter credentials. Two routes:
  - **Preferred, if it works:** a Landsat or Sentinel-2 imagery layer from **ArcGIS Living Atlas**
    in the Catalog pane. ArcGIS Pro is already signed in to ArcGIS Online. Pick a single cloud-light
    scene, and use the **Extract Bands** raster function to show one band at a time. VERIFY that
    the layer allows single-scene selection and band extraction on this license. If it does,
    record the layer name and scene date for the speaker notes.
  - **Otherwise:** ask Dan to download one Landsat 8/9 Collection 2 Level-2 scene: a Utah
    scene with water, farmland, desert, and a little cloud, bands B2, B3, B4, and B5.
- **Symbology.** Use grayscale with the same stretch on all three bands, so brightness is
  comparable across bands. Keep the extent identical across the three captures.
- **Annotations.** The old slides had identical annotations on all three bands, which undercut the
  comparison. Annotate only what changes from band to band, and add the annotations as slide
  markup (positioned HTML labels or a small inline SVG over the image), not burned into the PNG.
  Look at `slides/week-04/remote-sensing.md` slide "The spectrum, at a glance" for the pattern: an
  inline `<svg>` with an `<image href="images/...">` and labels on top.
- **Deck text.** Update the slide titles and bullets to the real band numbers and wavelengths of
  the sensor you used. For Landsat 8/9 OLI those are B4 red 0.64–0.67 µm, B3 green 0.53–0.59 µm, and
  B2 blue 0.45–0.51 µm. The current text says MODIS bands 1, 4, and 3. Rewrite the speaker notes to
  match, and remove the `TODO(instructor)` notes on those three slides.
- **Optional:** a near-infrared (B5) capture as a fourth slide, "Band 5 — near-infrared", where
  vegetation flips from dark to bright. That sets up NDVI and ties to the band ruler slide.

### C. Two checks while ArcGIS Pro is open

- "Many narrow, contiguous bands": find out which hyperspectral formats ArcGIS Pro opens natively
  (for example ENVI `.hdr` or HDF) and put the answer in that slide's speaker note, replacing the
  `VERIFY`.
- "Every satellite is a trade-off": check whether MODIS on Terra and Aqua is still delivering. If it
  is not, add VIIRS (Suomi NPP, NOAA-20, NOAA-21) to the table, and resolve the `VERIFY` note.

## Checking your work (required)

Render the deck and look at every slide you touched:

```bash
npx -y @marp-team/marp-cli@latest --no-stdin --theme slides/theme/ce414.css --html --allow-local-files --images png slides/week-04/remote-sensing.md -o %TEMP%\rs\s.png
```

Check that nothing overflows into the footer, that labels sit on the features they name, and that
band tiles are the same size across a row. Then run `mkdocs build --strict`. Do not commit `site/`
or any deck `.html`. The date stamp: run `python tools/stamp_decks.py` after committing, and commit
**only** the `slides/week-04/remote-sensing.md` stamp change. The script also restamps about ten
other decks, which should be left alone.

## Finishing

- Commit with a message that says what was captured and from what data.
- **Pushing publishes to students.** Push only if Dan says to. If the lecture has already started,
  do not push mid-class.
- Report back to Dan with:
  - which slides now use ArcGIS Pro captures
  - the data source and scene ID
  - any `VERIFY` you resolved, and what the answer was
  - anything you could not do, and why
- Update `tools/week04-arcgis-capture-plan.md` by ticking off or striking what is done, so the
  next session knows the state.
