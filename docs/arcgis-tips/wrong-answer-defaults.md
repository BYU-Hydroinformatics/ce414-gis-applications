# Defaults that give a confidently wrong answer

Every setting on this page produces output, reports success, and shows no error. They are the most
common causes of a lab that "ran fine" and still earns a poor grade. The first four come up in
Lab 1; the rest appear in the raster labs that follow.

When a dialog fills in a box for you, treat it as a guess and check it.

## 1. Buffer distances default to meters

The Buffer tool's Distance row has **two** boxes: a number and a unit. The unit reads *Unknown*
until you type a number, and then it silently sets itself to **Meters**. Type `2`, click OK, and
you have made a **two-meter** buffer instead of a two-mile one. Your radius is **1,609 times too
small** — that is just the number of meters in a mile. For a circular buffer the area comes out
about 2.6 million times too small; for a buffer around a long road it is nearer 1,600 times, since
a thin ribbon's area scales with the radius rather than its square.

Always set the unit box yourself. There is no plain "Miles" option in ArcGIS Pro 3.7; choose
**Statute Miles**.

## 2. Add Field defaults to Long (32-bit integer)

If you are creating a field that will hold a calculated value with a decimal part — a density, a
ratio, an average — set **Field Type** to **Double (64-bit floating point)**. The default is Long,
which silently **rounds every value to a whole number** — a density of 8,539.51 is stored as 8,540.
(It rounds rather than truncating, so the loss is easy to miss when you skim the table.)
**[To do: confirm whether a Long field rounds or truncates a calculated decimal. Lab 1 says it
"discards the decimal part".]**

Calculate Field can also create the field for you, if you type a new name in **Field Name**. Then
set its **Field Type** yourself: it opens at **Text**, and every later comparison or calculation
against a text field breaks.

## 3. Clicking Run with a tool dialog still open

If a tool's dialog is open and you click **Run**, the model runs with whatever was last *committed*
— not what is on screen. A Select tool whose expression has not been committed selects *everything*
and reports success in about a second.

Click **OK** on the tool dialog first, every time. Watch out: the OK button **moves down** when you
switch on the SQL Editor, which is exactly when people miss it.

## 4. Buffer's Dissolve Type defaults to No Dissolve

Buffering 1,500 road segments with "No Dissolve" gives you 1,500 overlapping polygons, and anything
you intersect with them afterwards comes out as a mess of slivers. When you want a single zone,
set **Dissolve Type** to *Dissolve all output features into a single feature*.

## 5. Mosaic To New Raster defaults to 8 bit unsigned {#mosaic-pixel-type}

**Pixel Type** opens at *8 bit unsigned*, which holds only whole numbers from 0 to 255. Every
elevation in Utah is above that. Set it to **32 bit float** for a DEM.

Leave **Cellsize** empty and set the cell size when you project the mosaic (see
[Projecting a DEM](projecting-dems.md)). In Lab 4, typing `30` there produced a raster of 15 billion
cells, almost all of them empty, and the tool ran for 38 minutes. Left empty, the same step takes
about 30 seconds.

## 6. Snap Pour Point's snap distance defaults to 0

At 0 the outlet stays on whatever cell you clicked. A click 30 or 40 m to the side of the channel,
which looks right on the imagery, lands on a hillside cell that drains only a few of its
neighbors. The watershed then comes out as a "basin" of a few cells to a few dozen, with no error.
Set a snap distance large enough to reach the channel (50 m in Lab 5) and check that the basin is
the size you expect.

## 7. Raster to Polygon leaves "Create multipart features" off

In flow-direction rasters, some cells of one zone touch only corner to corner, and Raster to Polygon
treats a corner as a break. Left unchecked, Lab 5's 29 subwatersheds come out as about 61 polygons,
including slivers of one or two cells, and any count you report is wrong. Check **Create multipart
features** whenever one zone should be one feature.

## 8. Thiessen polygons and Polygon to Raster drop your values

Two defaults in a row give a surface of ID numbers instead of measurements:

- **Create Thiessen Polygons** opens at **Output Fields: Only feature ID**, so the polygons carry
  none of the points' attributes. Choose **All fields**.
- **Polygon to Raster** fills **Value field** with `OBJECTID` by itself. Choose the field that holds
  the value you want, such as `RASTERVALU`.

## 9. Zonal Statistics opens at the wrong statistic

**Zonal Statistics** opens with **Statistics Type** at *Mean*, and **Zonal Statistics as Table**
opens at *All*. Pick the statistic the step asks for. A volume, for example, is a *Sum* (near the
bottom of the list). The **Zone field** fills in `OBJECTID` by itself; check that it is the field that
identifies your zones.

## 10. Kernel Density proposes a coarse cell and reads the radius in map units

As soon as the input is set, **Kernel Density** proposes a coarse output cell size (about 1,772 m in
Lab 4), and its **Search radius** is in the linear unit of the output
coordinate system, meters for UTM. Type both yourself. A radius typed as `20` meaning kilometers is
read as 20 meters, and the densities come out in the millions.

