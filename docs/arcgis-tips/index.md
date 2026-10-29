# ArcGIS Tips and Reminders

Read the three under *Before you start* before Lab 1. Come back to the rest whenever a tool "works"
but the answer looks wrong, or when ArcGIS Pro does something you did not expect. Each tip is a
short page of its own, so a lab can link straight to the one you need.

Everything here was checked in **ArcGIS Pro 3.7** during full runs of the labs. Where a setting has
moved or been renamed since older versions of these handouts, the current wording is given.

## Before you start

- [Set up your workspace and project](workspace.md) — work on the D: drive, never put a space in a
  name, and create the project where you meant to.
- [Set the coordinate system before you measure](coordinate-system.md) — the Output Coordinate
  System environment, the two wrong areas that tell you it was not set, and Web Mercator lengths.
- [Housekeeping](housekeeping.md) — renaming and moving data, naming outputs, and large downloads.

## When the answer looks wrong

- [Defaults that give a confidently wrong answer](wrong-answer-defaults.md) — ten tool settings
  that run, report success, and give the wrong result.
- [Tool dialogs that change what you typed](dialog-surprises.md) — output names that reset
  themselves, an SQL Editor that clears, and what the green check means.
- [Check what a tool actually produced](check-your-output.md) — record counts, the map, and
  whether each step changed anything.
- [Writing attribute expressions](attribute-expressions.md) — clause and SQL modes, quotes, case,
  and coded values stored as text.

## ModelBuilder

- [Running a model from its tool dialog](running-models.md) — intermediate data that disappears,
  outputs that overwrite each other, and checking a dialog run against the ModelBuilder run.

## Working with data

- [Creating a point feature class](point-feature-class.md) — placing your own points: candidate
  sites, stores, outlets.
- [Working with rasters](rasters.md) — statistics, integer math, environments, NoData, Reclassify,
  and `%name%` variables.
- [Projecting a DEM](projecting-dems.md) — why geographic cells are not square, the three Project
  Raster settings to check, and Slope's units.

## Layouts and reports

- [Basemap credits cover a small map frame](map-frame-credits.md) — moving the service credits off
  small panels, and when you may hide them.
- [Exporting maps and models for your report](exporting-deliverables.md) — layout PDFs that pass the
  grader's check, model SVGs, and the Geoprocessing History.

If you hit a problem that is not here and find a fix, tell your instructor or TA so it can be added.

<script>
  // Links to the sections of the old single-page version of this page still work.
  (function () {
    var moved = {
      "set-up-your-workspace-before-you-start": "workspace/",
      "creating-the-project-in-the-right-place": "workspace/#creating-the-project-in-the-right-place",
      "set-the-coordinate-system-before-you-measure-anything": "coordinate-system/",
      "four-ways-to-get-a-confidently-wrong-answer": "wrong-answer-defaults/",
      "writing-attribute-expressions": "attribute-expressions/",
      "check-what-a-tool-actually-produced": "check-your-output/",
      "creating-a-point-feature-class": "point-feature-class/",
      "housekeeping": "housekeeping/",
      "working-with-rasters-lab-2-onward": "rasters/"
    };
    var target = moved[location.hash.slice(1)];
    if (target) location.replace(target);
  })();
</script>
