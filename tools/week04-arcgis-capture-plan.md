# Week 4 remote-sensing deck: ArcGIS Pro captures to make

**For:** the machine with ArcGIS Pro. **Deck:** `slides/week-04/remote-sensing.md`.
**Written:** 2026-09-23, the day before the lecture.

The deck can be taught as it stands. Every item below replaces a stand-in with a real ArcGIS Pro
capture. Each slide it touches carries a `TODO(instructor)` note that points back to this file.
Save captures into `slides/week-04/images/` under the names given, then swap the references in the
deck. Crop to the map view, plus the Symbology pane where the step says so. Leave out the ribbon and
any account or tab strip.

## 1. Re-create the three MODIS band slides ("Band 1 — red", "Band 4 — green", "Band 3 — blue")

The current slides are legacy Multi-Channel Viewer screenshots. All three carry the same annotations
and the wavelength labels have not been checked.

1. Download one scene that shows vegetation, bare ground, cloud, and water together. Use Landsat 8/9
   Collection 2 Level-2 from EarthExplorer; a Utah scene with Utah Lake, farmland, and some cloud
   works well. A Sentinel-2 L2A scene also works. Note the scene ID for the speaker notes.
2. Add the red, green, and blue band files to a new map one at a time (Landsat 8/9: B4 = red,
   B3 = green, B2 = blue).
3. Symbolize each band as **Stretch** with the same stretch type (Percent Clip or Min-Max) and
   **grayscale**. Capture the map and the Symbology pane for each band:
   `rs-arcgis-band-red.png`, `rs-arcgis-band-green.png`, `rs-arcgis-band-blue.png`.
4. Label each capture differently. That fixes the old slides' problem of identical annotations.
   Mark the features whose brightness actually changes from band to band: vegetation (dark in red),
   water, cloud, and bare ground.
5. Optional, to set up NDVI: capture B5 (near-infrared) the same way, as `rs-arcgis-band-nir.png`.
   Vegetation turns bright in that band.
6. Check the band wavelengths in the speaker notes against the scene's metadata.

## 2. Split the four example images into bands (section 5, "Pulling Real Images Apart")

These slides now show band splits made by a Python script
(`tools/week04_remote_sensing_figures.py`), computed from the images' own pixels. The values are
correct. What the slides lack is the ArcGIS Pro context.

Images: `rs-eiffel-tower-aerial.jpg`, `rs-maryland-snow.jpg`, `rs-california-wildfires.jpg`,
`rs-europe-at-night.jpg`. They are all in `slides/week-04/images/`.

For each one:

1. Add the JPEG to a map. ArcGIS Pro reads it as a three-band raster. It has no spatial reference,
   which is fine for this purpose; dismiss the warning.
2. Expand the layer, or add the bands individually (`image.jpg/Band_1` and so on). Band_1 = red,
   Band_2 = green, Band_3 = blue.
3. Symbolize each band as **Stretch**, type **None** or **Min-Max** with min 0 and max 255, so the
   ramp spans the full 0–255 range and is not auto-stretched.
4. Choose a color ramp for each band:
   - **Black → red** for Band_1, **black → green** for Band_2, **black → blue** for Band_3. This is
     what the slides use now. It is the physically correct version, because 0 means no light, and
     the three tinted bands add back up to the original. You can demonstrate that live: set the
     layers to the **Screen** blend mode and stack them. VERIFY which layer blend modes
     ArcGIS Pro offers.
   - Or **white → red** and so on, if you prefer that look. It reads well, but the bands no longer
     add up to the original image.
   - If ArcGIS Pro has no black-to-red ramp, make one: in the color-ramp dropdown, open
     **Format color ramp…** and create a two-color **Algorithmic** ramp. VERIFY the menu name.
5. Capture the map with the Symbology pane showing the 0–255 range. Name each capture
   `rs-arcgis-<key>-<band>.png`, where key is `eiffel`, `snow`, `smoke`, or `night`.
6. In the deck, replace the `rs-band-<key>-<band>.jpg` references with the new captures. The
   four-across layout on each slide can stay as it is.

Worth doing live in class, if there is time: do the Eiffel Tower split in front of the students.
It takes about two minutes and makes the grid-paper slide ("A color image is three bands, stacked") concrete.

## 3. While ArcGIS Pro is open

- "Many narrow, contiguous bands": check which hyperspectral formats ArcGIS Pro opens natively, for example ENVI `.hdr`
  or HDF, and whether multidimensional raster tools apply. Update the speaker note either way.
- "Every satellite is a trade-off": check whether MODIS (Terra/Aqua) is still delivering data. If it is not, add VIIRS as
  its successor in the table.
