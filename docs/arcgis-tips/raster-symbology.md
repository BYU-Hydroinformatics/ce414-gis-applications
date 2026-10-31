# Make your raster symbology look good

ArcGIS Pro draws a new raster in gray, stretched between its own lowest and highest values. That is
fine for a first look and never right for a map you hand in. This page shows how to turn the gray
into something a reader understands at a glance: a terrain map, a set of maps that can be compared,
an error map, flow accumulation and flow direction. Every map below was made in ArcGIS Pro 3.7 from
the course's own data, and every setting is one you can make in the Symbology pane.

![Two maps of the Rock Canyon basin. Left, titled As it arrives: gray, Percent Clip: a smooth gray gradient from black in the west to white in the east, with the canyons barely visible. Right, titled Elevation #1 ramp, hillshade on top in Multiply: the same DEM colored from pale blue-green at the canyon mouth through green, yellow, orange and brown to gray and white on the peaks, with every ridge and gully shaded.](images/raster-terrain.jpg)

**Figure 1.** The Rock Canyon DEM (Lab 5) as ArcGIS Pro first draws it, and after the three steps
on this page: a color ramp, a hillshade, and a blend mode.

The recipe for a terrain map, in short:

1. Make a **hillshade** of the DEM.
2. Give the DEM a **stretched color ramp** made for elevation.
3. Put the hillshade **on top** and set its **Layer Blend** to **Multiply**, with some
   **Transparency**.

The sections below explain each step and what to change when the result looks wrong.

## Open the Symbology pane

Select the raster layer in the **Contents** pane, then either right-click it ▸ **Symbology**, or on
the **Raster Layer** ribbon tab click **Symbology**. The pane follows whichever layer is selected, so
check its title — *Symbology - DEM* — before you change anything.

**Primary symbology**, at the top, decides everything else:

| Primary symbology | Use it for | On this page |
| --- | --- | --- |
| **Stretch** | Continuous values you want as a smooth ramp: elevation, a surface, a hillshade | Terrain, Lab 8 surfaces |
| **Classify** | Continuous values you want in a few labeled bands: error, depth, slope classes, accumulation | Error maps, flow accumulation |
| **Unique Values** | Codes, where each value is a category: land cover, flow direction, a 1/0 result | Flow direction |
| **Discrete** | Many integer codes with no legend needed | — |

## Step 1 — Make a hillshade

A hillshade lights the DEM from one direction and records how bright each cell would be. It is
what makes terrain look like terrain.

Run **Hillshade** (Spatial Analyst Tools) on your DEM. The defaults — light from the northwest
(**Azimuth** 315) at 45° above the horizon (**Altitude** 45), **Z factor** 1 — are what readers
expect, because shadows that fall toward you make valleys look like ridges. Keep them.

![The Hillshade tool in the Geoprocessing pane: Input raster DEM_UTM, Output raster Hillshade_RockCanyon, Azimuth 315 and Altitude 45 (outlined in red), Model shadows unchecked, Z factor 1.](images/symbology-hillshade-tool.png)

**Figure 2.** Hillshade with its defaults. The DEM must be projected first (see
[Projecting a DEM](projecting-dems.md)); on a DEM in degrees the hillshade comes out flat or
streaked.

> [!TIP]
> **Make a hillshade of each surface you map, not of the true DEM.** In Lab 8, a hillshade made from
> `True_DEM` puts the real mountain's ridges on top of every interpolated surface, so Thiessen, IDW
> and Kriging all look as detailed as the truth (Figure 11). A hillshade of each surface shows what
> that surface actually is.

## Step 2 — A stretched color ramp

Select the DEM and set **Primary symbology** to **Stretch**. Then:

- **Color scheme.** Click the ramp to open the list. Tick **Show names** at the bottom of the list,
  then choose one made for elevation: **Elevation #1** is the one used on this page. Avoid
  rainbow ramps (**Spectrum**) for anything continuous: their bright yellow and cyan bands make
  false edges.
- **Stretch type.** Leave it at **Percent Clip** for a DEM (see the next section for when not to).
- **Labels.** The two **Label** boxes are what the legend prints. Round them: `1,377 m` and
  `3,371 m`, not `1376.67` and `3370.6`.

![The Symbology pane for the DEM layer: Primary symbology Stretch, Band_1, Color scheme Elevation #1 (a ramp from pale blue-green through green, yellow, orange and brown to white, outlined in red), Invert unchecked, Value 1376.669434 and 3370.603027, Label 1376.67 and 3370.6, Stretch type Percent Clip (outlined in red), Min 0.500 and Max 0.500, Gamma 1.0, Sharpening 0, and below on the Statistics tab, Statistics Dataset with Min 1376.66943359 and Max 3370.60302734.](images/symbology-stretch-pane.png)

**Figure 3.** The Symbology pane behind Figure 1's finished map.

## Step 3 — Put the hillshade on top, and blend it

There are two ways to combine a color ramp with a hillshade, and the second looks better:

- **Ramp over hillshade, partly transparent.** Hillshade at the bottom of the Contents pane, DEM
  above it with **Transparency** around 40–50 %. Easy, but the colors wash out to pastel.
- **Hillshade over ramp, blended.** DEM at the bottom, hillshade **above** it. Select the hillshade
  and, on the **Raster Layer** tab in the **Effects** group, set **Layer Blend** to **Multiply** and
  **Transparency** to about **35 %**. Multiply darkens the colors underneath where the hillshade is
  dark and leaves them alone where it is white, so the colors stay strong and the relief stays
  crisp. Use 0 % and the shadows go black; use 60 % and the relief fades.

![Three panels of the same part of Rock Canyon. Left, No hillshade: smooth bands of color with no relief. Middle, DEM 45% transparent over hillshade: relief visible but the colors pale and grayish. Right, Hillshade on top, Multiply, 35%: strong colors with every ridge and gully shaded.](images/raster-hillshade-ways.jpg)

**Figure 4.** No hillshade; the ramp 45 % transparent over the hillshade; the hillshade on top in
Multiply at 35 %.

![The Raster Layer tab of the ribbon with the hillshade layer selected: in the Effects group, Transparency 35.0% and Layer Blend Multiply, outlined in red.](images/symbology-effects-group.png)

**Figure 5.** **Raster Layer** tab ▸ **Effects**: Transparency and Layer Blend, set on the
hillshade layer.

![The Layer Blend list open: Lighten, Linear Dodge, then under Darkening modes Multiply (highlighted and outlined in red), Color Burn, Darken, Linear Burn, then Comparison modes, Divergent modes and Color combination modes.](images/symbology-layer-blend.png)

**Figure 6.** **Multiply** is under *Darkening modes*. **Overlay** and **Soft Light** also work on
a hillshade; try them if Multiply looks too dark on your data.

## Stretch types and statistics

The **Stretch type** decides how the values are spread along the color ramp.

![The Stretch type list open: Minimum Maximum (Display values between the actual minimum and maximum), Percent Clip (Cut off percentages of highest and lowest values, highlighted and outlined in red), Standard Deviation (Display values between a specified number of standard deviations), Histogram Equalize, and Custom.](images/symbology-stretch-types.png)

**Figure 7.** The stretch types in ArcGIS Pro 3.7, each with its own one-line explanation.

On a smooth DEM the choice barely matters. On **skewed** data, where most cells are small and a few
are huge, it decides whether you see anything at all. Flow accumulation is the extreme case: half
of Rock Canyon's cells have 5 or fewer cells upstream, and the outlet has 430,024.

![Three panels of flow accumulation in Rock Canyon on a white-to-blue ramp. Minimum Maximum: almost all white, with only the main channel faintly blue. Percent Clip, 0.5 %: the main channel dark blue, nothing else. Standard Deviation, n = 2.5: the main channel dark and several tributaries visible in light blue.](images/raster-stretch-types.jpg)

**Figure 8.** One flow accumulation raster, three stretch types. For data like this, use
**Classify** instead (see [Flow accumulation](#flow-accumulation) below).

- **Minimum Maximum** spreads the ramp evenly from the lowest to the highest value. Good when you set
  the ends yourself (see below); poor when a few extreme cells set them.
- **Percent Clip** (the default) ignores the lowest and highest 0.5 % of cells. Good for most DEMs.
- **Standard Deviation** spreads the ramp across a few standard deviations either side of the mean.
  Good for skewed data.
- **Histogram Equalize** gives each color the same number of cells. Dramatic, but the colors no
  longer mean even steps of elevation, so avoid it on any map with a legend.

The **Statistics** tab, below, decides which cells those statistics come from:

![The Statistics tab with its list open: DRA, Dynamic range adjustment uses statistics from the current display extent (outlined in red), and Dataset, Uses the statistics from the raster dataset (highlighted).](images/symbology-statistics-list.png)

**Figure 9a.** **Dataset** uses the whole raster; **DRA** uses only what is on screen.

![Two panels zoomed in on a small valley floor in Rock Canyon. Left, Statistics: Dataset: one flat blue-green color with faint relief. Right, Statistics: DRA (current display extent): the same view in the full ramp, green, yellow, brown and white, every small rise visible.](images/raster-stats-view.jpg)

**Figure 9b.** Zoomed in on one valley floor. With **Dataset**, the whole view falls in one color of
a ramp that runs to the peaks. **DRA** stretches the ramp across just the view. Use DRA for a close-up
map; never use it for maps that must be compared, because each view gets its own colors.

## Maps that must be compared: one scale for all

Whenever two or more rasters sit side by side — Lab 8's three surfaces, its three error maps, a
before-and-after, a sensitivity run — they need **the same colors for the same values**. ArcGIS
Pro stretches each layer to its own range, so by default they do not.

**For a stretch,** set the same ends on every layer:

1. Set **Stretch type** to **Minimum Maximum**.
2. Tick **Edit min/max values** (it appears only with Minimum Maximum).
3. Type the same **Value** at each end on every layer, rounded to cover all of them: Lab 8's
   surfaces run from 1,368 to 2,887 m, so `1350` and `2900`.
4. Retype the **Label** boxes too. They do not follow the values, so the legend still shows each
   layer's own range until you change them (Figure 10 still reads 1368.74 and 2885.54).

![The Symbology pane for the IDW surface: Stretch, Color scheme Elevation #1, Edit min/max values checked (outlined in red), Value 1350 and 2900, Label 1368.74 and 2885.54 (both rows outlined in red), Stretch type Minimum Maximum.](images/symbology-edit-min-max.png)

**Figure 10.** Fixed ends of 1,350 and 2,900 m. The labels still show this layer's own range;
retype them.

**For classes,** use **Classify** with **Manual Interval** and type the same breaks on every layer
(next section). Once one layer is right, copy its symbology to the others. Either select a layer
that still needs it and, in the Symbology pane's menu (☰), choose **Import from layer** and pick
the finished one; or right-click the finished layer ▸ **Copy**, then right-click each other layer ▸
**Paste Properties** (Ctrl+Shift+V).

![The Symbology pane menu (☰) open over a Classify layer: Import from layer file, Import from layer (outlined in red), Export as raster function template, Manage Symbology.](images/symbology-import-from-layer.png)

**Figure 10b.** **Import from layer** copies another layer's symbology onto the selected one.

![Two rows of three maps of the Y Mountain study area. Top row, titled Thiessen over the true hillshade, IDW over the true hillshade and Kriging over the true hillshade: all three look alike, with sharp ridges and gullies. Bottom row, each over its own hillshade: Thiessen shows hard-edged polygon facets and steps, IDW shows rounded bumps and small pits around the sample points, Kriging is smooth and soft-edged.](images/raster-lab8-surfaces.jpg)

**Figure 11.** Lab 8's three surfaces on the same 1,350–2,900 m stretch. Over the true DEM's
hillshade (top) they look alike, because the hillshade supplies detail none of them has. Over their
own hillshades (bottom) each method's character shows: Thiessen's facets, IDW's pits around the
points, Kriging's smoothness.

## Error maps: a diverging classification

An error map (surface minus truth, model minus observation, one run minus another) has a meaningful
**zero**, and the sign matters. That calls for:

- **Classify**, **Method: Manual Interval**, so you choose the breaks.
- **Symmetric breaks** around zero: −100, −50, −20, −5, 5, 20, 50, 100 m in Lab 8. The same breaks
  on every error map.
- A **diverging** pair of colors: one hue for too high, another for too low, darker for bigger.
- The middle class, within 5 m, as **no color** (or white), so the hillshade or the background shows
  through where the method got it right.

To set the classes: choose **Classify**, set **Method** to **Manual Interval** and **Classes** to the
number you need, then on the **Classes** tab type each **Upper value** and **Label**. Click a class's
color patch to select the row, click it again to open the color palette, and pick a color, or
**No color** at the top.

![The Symbology pane for the IDW error layer: Primary symbology Classify, Method Manual Interval (outlined in red), Classes 9, and the Classes tab with Upper value and Label columns (outlined in red): ≤ -100.0 over 100 m high (dark red), ≤ -50.0 50 - 100 m high, ≤ -20.0 20 - 50 m high, ≤ -5.0 5 - 20 m high (light orange), ≤ 5.0 within 5 m (no color), ≤ 20.0 5 - 20 m low (light blue).](images/symbology-classify-pane.png)

**Figure 12.** Lab 8's error classes. Red means the surface is too high, blue too low.

![The color palette open over the Classes tab, with No color at the top outlined in red, then ArcGIS Colors, Eyedropper, More colors and Color properties; the within 5 m row is selected below.](images/symbology-no-color.png)

**Figure 13.** Click a class's color patch twice for the palette. **No color** is at the top.

![Two rows of three error maps of the Y Mountain study area. Top row, each on its own red-to-blue stretch: Thiessen mostly pale, IDW mostly pink, Kriging mostly salmon, so the same color means a different error in each and Kriging looks as bad as the others. Bottom row, on the shared diverging classes over a light hillshade: Thiessen dense with dark red and blue, IDW less so, Kriging mostly pale with fewer dark patches, titled with RMSEs of 28.29, 20.71 and 14.46 m.](images/raster-lab8-errors.jpg)

**Figure 14.** Lab 8's three error maps (2,500 points). Top: each on its own stretch, as ArcGIS Pro
draws them; zero is a different color in each and the maps cannot be compared. Bottom: one set of
classes with the 5 m band left clear, so the order Thiessen, IDW, Kriging is plain at a glance.

## Flow accumulation

Flow accumulation counts the cells that drain through each cell. A few cells along the main channel
carry hundreds of thousands; most carry a handful. Any stretch is dominated by the channel and the
map comes out almost black (Figure 15, left). Classify it instead, with classes that grow by
**powers of 10**:

| Upper value | Label | Color |
| --- | --- | --- |
| 1,000 | fewer than 1,000 cells | **No color** |
| 10,000 | 1,000 – 10,000 | light blue |
| 100,000 | 10,000 – 100,000 | mid blue |
| the maximum | over 100,000 | dark blue |

Hiding the smallest class leaves only the drainage network, and a light hillshade underneath (the
hillshade alone, 45 % transparent) puts it in its landscape. With 10 m cells, 1,000 cells is
0.1 km²; pick the lowest break to match the stream threshold you use in the lab.

![Two maps of the Rock Canyon basin. Left, As it arrives: almost all black, with the main channel a thin white line and a few faint gray tributaries. Right, Classes by powers of 10, small ones hidden: a branching blue drainage network, dark blue in the main canyon and light blue in the side gullies, over a pale gray hillshade.](images/raster-flow-accumulation.jpg)

**Figure 15.** Flow accumulation as it arrives, and in four classes over a hillshade.

## Flow direction

Flow direction stores one of eight codes per cell — 1, 2, 4, 8, 16, 32, 64, 128 for E, SE, S, SW,
W, NW, N, NE — and ArcGIS Pro gives each a random **Unique Values** color. Recolor them so that the
colors run once around a color wheel in the same order as the directions: neighboring directions
then get neighboring colors, and a hillside that drains one way reads as one block.

1. **Primary symbology: Unique Values**, Field `Value`.
2. Double-click each **Label** and type the direction: `E`, `SE`, … `NE`.
3. Click each color patch and pick colors that run around the wheel: red, orange, yellow, green,
   teal, blue, purple, magenta.
4. Put a hillshade on top in **Multiply** (about 50 % transparent).

![The Symbology pane for Flow direction: Unique Values, Field 1 Value, and the Values list (outlined in red): 1 E red, 2 SE orange, 4 S yellow, 8 SW green, 16 W teal.](images/symbology-unique-values.png)

**Figure 16.** The eight codes labeled with their directions and colored around the wheel.

![Two maps of the same Rock Canyon hillside. Left, As it arrives: unique values, random colors: speckled bright green, cyan, yellow, red, violet and gray with no pattern. Right, A hue wheel, E round to NE, hillshade on top: the north side of the canyon in greens and teals (draining southwest and west), the south side in purples and magentas (draining north and northeast), the valley floor in yellow, with the relief shaded.](images/raster-flow-direction.jpg)

**Figure 17.** The same flow direction raster with random colors and with a color wheel. The two
sides of the canyon now read as two blocks draining toward the channel.

## Small things that make a big difference

- **Pixelated close-ups.** At large scales each cell draws as a square. For continuous data (a DEM,
  a surface, a hillshade) set **Resampling Type** to **Bilinear**: on the **Raster Layer** tab, it
  is the top icon in the right-hand column of the **Rendering** group (or type *Resampling* in the
  Command Search box). Keep **Nearest Neighbor** for codes and classes — flow direction, land
  cover, error classes — where blending neighbors would invent values that do not exist.

    ![The Resampling Type gallery: Nearest Neighbor (Assign value from closest cell), Bilinear (Interpolate value from surrounding 4 cells, outlined in red), Cubic (Interpolate value from surrounding 16 cells) and Majority.](images/symbology-resampling-type.png)

    **Figure 18.** Resampling Type changes only how the layer is drawn, never its values.

- **NoData.** Cells with no value draw as nothing by default, which is usually right. If the area
  outside your study area shows a color, those cells are zeros, not NoData (see
  [Working with rasters](rasters.md)).
- **Background value.** A clipped raster sometimes draws a black or white frame around the data:
  cells holding 0 (or some other fill value) rather than NoData. For a **Stretch** layer, on the
  Symbology pane's **Mask** tab, tick **Display background value**, type the fill value, and set its
  color to no color. Classify layers have only the **Nodata** color on that tab.

    ![The Mask tab of a Stretch layer's Symbology pane: Display background value (check box, outlined in red), a value box reading 0 and a color box with a transparent swatch (outlined in red), and Nodata with its own transparent swatch.](images/symbology-mask-tab.png)

    **Figure 19.** The Mask tab of a Stretch layer.
- **Basemaps.** Turn the basemap off under a full-coverage raster: it is hidden anyway and still
  adds its credits. Over a partly transparent layer, a light basemap such as **Light Gray Canvas**
  competes least with the colors.
- **Legends.** Round the labels, add the units, and take the hillshade out of the legend: in the
  **layout's** Contents pane, expand **Legend** and uncheck **Hillshade**. The hillshade stays on the
  map; only its legend entry goes.

    ![The layout's Contents pane: Legend Test, then Legend expanded with Hillshade unchecked (outlined in red) and DEM checked, then Frame.](images/symbology-legend-items.png)

    **Figure 20.** Each layer in a legend has its own check box in the layout's Contents pane.
- **Same ramp, same meaning.** Use one ramp for one kind of quantity throughout a report: one
  elevation ramp, one diverging error ramp. A reader learns it once.

## See also

- [Working with rasters](rasters.md) — statistics, NoData, Reclassify.
- [Projecting a DEM](projecting-dems.md) — project before you make a hillshade.
- [Exporting maps and models for your report](exporting-deliverables.md) — export the layout as a
  PDF once the map looks right.
