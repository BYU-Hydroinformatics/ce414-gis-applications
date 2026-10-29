# Projecting a DEM

Most DEMs you download, including the USGS 3D Elevation Program's, come in geographic coordinates:
latitude and longitude. Project them before you compute slope, area, distance or volume.

## Geographic cells are not square

A one-arc-second cell is shorter east–west than north–south at Utah's latitude. In Lab 4 the
county mosaic's cells are about **24 m wide and 31 m tall**. Terrain tools that assume square cells
still run on such a raster, and give wrong answers quietly.

**Slope** is the example the labs measure. On the unprojected Little Cottonwood DEM in Lab 12, it
reports a mean slope of 24.3°, about 2.6° too gentle. Two or three degrees move a lot of terrain
across a classification break.

## Project Raster: three settings to check

Use **Project Raster** (Data Management Tools), and set these yourself rather than accepting what
the dialog proposes:

1. **Output Coordinate System**: NAD 1983 UTM zone 12N for anywhere in Utah.
2. **Resampling Technique**: **Bilinear interpolation** for elevation. The dialog can open at
   Nearest neighbor. Nearest copies the single nearest value and leaves small steps in the
   surface, which Slope reads as slope and which can become false pits. Use Nearest only for
   categories, such as land cover or a 1/0 result.
3. **Output Cell Size**: type a round number in **both X and Y**, such as `30` or `10`. The tool
   proposes the input's own non-square cell size (about 24.05 × 30.96 in Lab 4, about 9.04 in
   Lab 12).

*Figure placeholder: the Project Raster dialog with Bilinear interpolation and a round cell size typed
in both X and Y. Lab 4's `lab04-project-raster-dialog.png` and
`lab04-project-raster-default-cellsize.png` are real captures that could be copied into this page's
`images/` folder.*

**Check the result:** open the output's **Properties** ▸ **Source** ▸ *Raster Information*. The
cell size should be the one you typed. A cell size of about 0.0001 means you are looking at the
unprojected DEM, in degrees.

## Then check Slope's units

**Slope**'s **Output measurement** can be *Degree* or *Percent rise*, and the two are far apart: a
5 percent slope is only 2.9 degrees. Use the unit your criteria are written in. A maximum above 90
means the output is in percent rise.

## Mosaic first, without a cell size

If you mosaic several tiles before projecting, leave **Cellsize** empty in **Mosaic To New
Raster** and set the cell size in Project Raster. See
[Defaults that give a confidently wrong answer](wrong-answer-defaults.md#mosaic-pixel-type).
