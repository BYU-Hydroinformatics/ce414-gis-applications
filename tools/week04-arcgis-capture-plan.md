# Week 4 remote-sensing deck: ArcGIS Pro captures to make

**For:** the machine with ArcGIS Pro. **Deck:** `slides/week-04/remote-sensing.md`.
**Written:** 2026-09-23, the day before the lecture. **Status:** items 1–3 done 2026-09-23 on the
Windows machine (ArcGIS Pro 3.7.1); what was done and how is recorded under each item.

A Claude session on the ArcGIS Pro machine should start with
`tools/week04-windows-agent-handoff.md`, which says how to run this plan there.

Project: `C:\Ames\Week04\RemoteSensing.aprx`, built by `tools/week04_arcgis_project.py` (maps
Eiffel, Snow, Smoke, Night, Landsat; symbology set through the CIM) and rendered by
`tools/week04_arcgis_render.py` (a layout map frame sized to each raster, exported by ArcGIS Pro).
The Eiffel map was saved with the three band layers on and blended with Screen, ready for a live demo.

## 1. ~~Re-create the three MODIS band slides~~ Done: Landsat band slides

- ~~Legacy Multi-Channel Viewer screenshots with identical annotations~~ replaced by four slides,
  "Band 4 — red", "Band 3 — green", "Band 2 — blue", "Band 5 — near-infrared".
- Data: the Lab 2 scene, Landsat 8 OLI `LC08_L2SP_038032_20250712_02_T1` (path 38, row 32,
  12 July 2025), Collection 2 Level-2 surface reflectance. B4 and B5 came from the Lab 2 download;
  B2 and B3 were fetched by `tools/week04_fetch_bands.py` from the Microsoft Planetary Computer
  mirror of the USGS archive (no login). Living Atlas was not tried: the Lab 2 scene ties straight
  to the NDVI students computed. Clipped to Utah Lake / Provo / Orem, UTM 12N
  415000–460000 E, 4430000–4470000 N, in `C:\Ames\Week04\RemoteSensing.gdb`.
- Symbology: grayscale Stretch, Minimum Maximum with custom min/max DN 7,700–18,800 (0.5th–99.5th
  percentile of the three visible bands together; reflectance about 0.01–0.32) on B2, B3, B4. B5
  has its own stretch, DN 7,000–26,300, because every field saturates on the shared one; the slide
  note says so.
- Files: `rs-arcgis-band-red.jpg`, `-green.jpg`, `-blue.jpg`, `-nir.jpg` (1000 px wide).
- Labels are inline SVG over the image, different on each slide, with reflectance sampled from the
  band rasters (7×7 means): center-pivot field B2 0.046, B3 0.076, B4 0.062, B5 0.484; Utah Lake
  0.101 / 0.156 / 0.100 / 0.011; Provo Bay 0.027 / 0.076 / 0.043 / 0.024; bare ground west of the
  lake 0.099 / 0.146 / 0.173 / 0.248.

## 2. ~~Split the four example images into bands~~ Done

- Each JPEG is in its map as a full-color layer plus three single-band layers (`Band_1/2/3`),
  Stretch, Minimum Maximum, **Edit min/max values** 0 and 255, black-to-red / -green / -blue.
- Files: `rs-arcgis-<eiffel|snow|smoke|night>-<red|green|blue>.jpg`. Checked against the source
  photos: the band channel matches the photo's channel to a mean of 1–4 DN (JPEG noise) and the
  other two channels are about 0, so the pixel claims on the slides (smoke over water about
  R 88, G 112, B 123, and so on) hold in ArcGIS Pro.
- New slide after the Eiffel Tower slide, "The same split in ArcGIS Pro", with two live screen grabs
  at 175 % scaling: `rs-arcgis-eiffel-symbology.png` (the Symbology pane) and
  `rs-arcgis-eiffel-screen-blend.jpg` (all three layers on, Layer Blend = Screen, the photo
  reassembled).
- VERIFIED in ArcGIS Pro 3.7.1:
  - There is no "Format color ramp…". The Color scheme dropdown ends with **More color schemes…**
    and **Color scheme properties…**; the latter opens the **Color Scheme Editor** (Continuous
    Color Scheme, color stops, Algorithm Linear).
  - **Raster Layer** tab → Effects group → **Layer Blend** offers Normal; lightening modes Screen,
    Color Dodge, Lighten, Linear Dodge; darkening modes Multiply, Color Burn, Darken, Linear Burn;
    comparison modes Difference, Exclusion; divergent modes Overlay, Hard Light, Soft Light, Linear
    Light, Pin Light, Vivid Light, and more below.
- The twelve script-made `rs-band-*.jpg` files and `band_splits()` in
  `tools/week04_remote_sensing_figures.py` were deleted.

## 3. ~~While ArcGIS Pro is open~~ Done

- Hyperspectral: ArcGIS Pro's supported raster formats page (checked 2026-09-23) lists ENVI header
  (.hdr with .dat/.img/.raw/.bsq), AVIRIS, HDF4, HDF5, netCDF, EMIT (.nc), and Hyperion (.tif).
  PRISMA, EnMAP, and DESIS are not listed. Speaker note updated.
- MODIS: still delivering, but NASA Earthdata says Terra and Aqua begin shutting down in late
  2026 / early 2027, and Suomi NPP data delivery ends 1 November 2026. VIIRS (NOAA-20, NOAA-21) added
  to the trade-off table.

## Still open

- The `satjournal.tcom.ohiou.edu/pdf/shippert.pdf` source on "Many narrow, contiguous bands" timed
  out on 2026-09-23; it is still marked VERIFY in the note.
- No Landsat capture of the ArcGIS Pro UI itself (the band slides are map renders only).
