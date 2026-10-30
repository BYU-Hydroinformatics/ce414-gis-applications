"""Build the ArcGIS Tips figures (docs/arcgis-tips/images/) from the raw captures.

The raw captures are screen grabs at 175 % display scaling from the 2026-10-30 session
(ArcGIS Pro 3.7, project D:\\Smith\\Tips, see tips_setup.py). They live outside the repository in
C:\\Ames\\TipsD\\caps; this script records how each figure was cut from them, so a figure can be
re-made after a re-capture:

    python tools/screenshots/tips_figures.py [RAW_DIR]

Each entry: source file, crop box (source pixels), callout boxes (source pixels), optional label,
optional patches (a rectangle filled with the color sampled at a point, used to remove a tooltip
or a personal folder name). Callouts follow callout.py's style.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

RAW = sys.argv[1] if len(sys.argv) > 1 else r"C:\Ames\TipsD\caps"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "arcgis-tips", "images")
RED = (214, 39, 40)
PANE = (0, 0, 820, 990)

FIGS = {
    # wrong-answer-defaults.md
    "wrong-defaults-buffer-meters.png": dict(
        src="buffer-meters-raw.png", crop=(0, 0, 812, 845), boxes=[(419, 443, 802, 481)],
        patches=[((419, 482, 512, 530), (300, 500))]),
    "wrong-defaults-buffer-unit-list.png": dict(
        src="buffer-unit-list-full.png", crop=(1100, 0, 1912, 845),
        boxes=[(1521, 677, 1871, 713)]),
    "wrong-defaults-buffer-fixed.png": dict(
        src="buffer-fixed-raw.png", crop=(0, 0, 812, 845),
        boxes=[(419, 443, 802, 481), (35, 786, 802, 826)]),
    "wrong-defaults-add-field-long.png": dict(
        src="addfield-long-raw.png", crop=(0, 0, 812, 800), boxes=[(34, 431, 801, 466)]),
    "wrong-defaults-add-field-double.png": dict(
        src="addfield-type-list-full.png", crop=(1100, 0, 1912, 845),
        boxes=[(1136, 596, 1901, 631)]),
    "wrong-defaults-long-vs-double.png": dict(
        src="long-vs-double-raw.png", crop=(15, 158, 812, 415),
        boxes=[(672, 166, 804, 410)]),
    "wrong-defaults-calcfield-text.png": dict(
        src="calcfield-text-raw.png", crop=(0, 0, 812, 560), boxes=[(34, 433, 773, 468)]),
    "wrong-defaults-mosaic-8bit.png": dict(
        src="mosaic-8bit-raw.png", crop=(0, 0, 812, 905),
        boxes=[(35, 655, 772, 692), (405, 710, 772, 750)]),
    "wrong-defaults-mosaic-pixel-list.png": dict(
        src="mosaic-pixel-list-full.png", crop=(1100, 0, 1912, 1000),
        boxes=[(1136, 938, 1880, 974)]),
    "wrong-defaults-snap-zero.png": dict(
        src="snap-zero-raw.png", crop=(0, 0, 812, 600), boxes=[(419, 521, 801, 558)]),
    "wrong-defaults-snap-50.png": dict(
        src="snap-50-raw.png", crop=(0, 0, 812, 600), boxes=[(419, 521, 801, 558)]),
    "wrong-defaults-multipart-off.png": dict(
        src="multipart-off-raw.png", crop=(0, 0, 812, 580), boxes=[(34, 482, 312, 516)]),
    "wrong-defaults-multipart-on.png": dict(
        src="multipart-on-raw.png", crop=(0, 0, 812, 580), boxes=[(34, 482, 312, 516)]),
    "wrong-defaults-singlepart-count.png": dict(
        src="singlepart-count-raw.png", crop=(12, 62, 990, 505),
        boxes=[(222, 460, 380, 492), (515, 205, 662, 287)]),
    "wrong-defaults-multipart-count.png": dict(
        src="multipart-count-raw.png", crop=(12, 62, 990, 505), boxes=[(222, 460, 380, 492)]),
    "wrong-defaults-thiessen-fid.png": dict(
        src="thiessen-fid-raw.png", crop=(0, 0, 812, 470), boxes=[(34, 382, 801, 418)]),
    "wrong-defaults-thiessen-all.png": dict(
        src="thiessen-all-raw.png", crop=(0, 0, 812, 470), boxes=[(34, 382, 801, 418)]),
    "wrong-defaults-polygon-to-raster-objectid.png": dict(
        src="poly2raster-objectid-raw.png", crop=(0, 0, 812, 740), boxes=[(34, 297, 761, 332)]),
    "wrong-defaults-polygon-to-raster-rastervalu.png": dict(
        src="poly2raster-rastervalu-raw.png", crop=(0, 0, 812, 740), boxes=[(34, 297, 761, 332)]),
    "wrong-defaults-zonal-mean.png": dict(
        src="zonal-mean-raw.png", crop=(0, 0, 812, 740),
        boxes=[(34, 297, 761, 332), (34, 554, 801, 589)]),
    "wrong-defaults-zonal-sum-list.png": dict(
        src="zonal-sum-list-full.png", crop=(1100, 0, 1912, 930), boxes=[(1136, 881, 1901, 915)]),
    "wrong-defaults-kd-degrees.png": dict(
        src="kd-degrees-raw.png", crop=(0, 0, 812, 830), boxes=[(34, 466, 761, 501)]),
    "wrong-defaults-kd-proposed.png": dict(
        src="kd-proposed-raw.png", crop=(0, 0, 812, 830),
        boxes=[(34, 466, 761, 501), (419, 521, 801, 558)]),
    # projecting-dems.md
    "dem-raster-info-degrees.png": dict(
        src="raster-info-degrees-raw.png", crop=(0, 0, 1300, 920), boxes=[(366, 476, 1186, 560)]),
    "dem-project-raster-proposed.png": dict(
        src="project-raster-proposed-raw.png", crop=(0, 0, 812, 870),
        boxes=[(54, 701, 801, 738)]),
    "dem-resampling-list.png": dict(
        src="resampling-list-full.png", crop=(1100, 0, 1912, 870), boxes=[(1136, 642, 1901, 677)]),
    "dem-project-raster-fixed.png": dict(
        src="project-raster-fixed-raw.png", crop=(0, 0, 812, 870),
        boxes=[(34, 560, 801, 596), (54, 701, 801, 738)]),
    "dem-raster-info-projected.png": dict(
        src="raster-info-projected-raw.png", crop=(0, 0, 1300, 920), boxes=[(366, 518, 1186, 600)]),
    "dem-slope-units.png": dict(
        src="slope-units-full.png", crop=(1100, 0, 1912, 720), boxes=[(1136, 503, 1901, 580)]),
    # coordinate-system.md
    "crs-modelbuilder-environments.png": dict(
        src="model-canvas-full.png", crop=(20, 125, 870, 305), boxes=[(412, 232, 582, 270)]),
    "crs-environments-empty.png": dict(
        src="mb-env-empty-raw.png", crop=(0, 0, 1300, 535), boxes=[(565, 331, 1207, 368)]),
    "crs-picker-search.png": dict(
        src="crs-picker-raw.png", crop=(0, 0, 919, 788),
        boxes=[(30, 334, 333, 374), (100, 640, 862, 675)]),
    "crs-environments-set.png": dict(
        src="mb-env-set-raw.png", crop=(0, 0, 1300, 535), boxes=[(565, 331, 1207, 368)]),
    # running-models.md
    "models-delete-intermediate.png": dict(
        src="model-canvas-full.png", crop=(20, 368, 1000, 490), boxes=[(503, 383, 655, 416)],
        label="Delete Intermediate Data — do not click", at="below"),
    "models-oval-menu.png": dict(
        src="mb-oval-menu-full.png", crop=(840, 40, 1400, 650),
        boxes=[(930, 154, 1380, 193), (930, 199, 1380, 244)]),
    "models-catalog-edit-open.png": dict(
        src="catalog-model-menu-full.png", crop=(950, 0, 1880, 860),
        patches=[((1492, 0, 1880, 66), (1870, 110))],  # the signed-in user's avatar
        boxes=[(967, 5, 1488, 103), (1446, 811, 1864, 848)]),
    "models-tool-dialog.png": dict(
        src="model-tool-dialog-raw.png", crop=(0, 0, 812, 580),
        boxes=[(6, 405, 32, 433), (6, 490, 32, 518)]),
    "models-run-dialog.png": dict(
        src="mb-run-dialog-raw.png", crop=(0, 0, 840, 697), boxes=[(14, 650, 245, 685)]),
    # rasters.md
    "rasters-float-before-minus.png": dict(
        src="model-canvas-full.png", crop=(40, 545, 1060, 765), boxes=[(262, 568, 434, 642)]),
    "rasters-percent-variable.png": dict(
        src="mb-rastercalc-percent-raw.png", crop=(0, 0, 665, 734), boxes=[(37, 408, 640, 444)]),
    "rasters-reclass-table.png": dict(
        src="mb-reclass-table-raw.png", crop=(0, 0, 665, 804),
        boxes=[(40, 498, 640, 529), (40, 533, 163, 582)]),
    "rasters-reclass-row-selected.png": dict(
        src="mb-reclass-row-selected-raw.png", crop=(0, 0, 665, 804), boxes=[(40, 437, 640, 465)]),
    "rasters-reclass-classify.png": dict(
        src="mb-classify-raw.png", crop=(0, 0, 900, 760), boxes=[(152, 167, 334, 205)]),
    # attribute-expressions.md and dialog-surprises.md
    "expressions-clause-mode.png": dict(
        src="mb-select-clause-raw.png", crop=(0, 0, 1000, 662), boxes=[(30, 450, 975, 490)]),
    "expressions-sql-mode.png": dict(
        src="mb-select-sql-raw.png", crop=(0, 0, 1000, 727), boxes=[(775, 387, 931, 416)]),
    "expressions-pick-list.png": dict(
        src="mb-select-value-list-full.png", crop=(300, 180, 1300, 842),
        boxes=[(930, 662, 1218, 782)]),
    "dialog-sql-valid.png": dict(
        src="mb-select-valid-raw.png", crop=(0, 0, 1000, 787), boxes=[(52, 630, 348, 668)]),
    "dialog-con-clause-refused.png": dict(
        src="mb-con-clause-refused-raw.png", crop=(0, 0, 1000, 944),
        boxes=[(52, 548, 640, 585)]),
    # exporting-deliverables.md
    "export-modelbuilder-menu.png": dict(
        src="mb-export-menu-full.png", crop=(340, 100, 1100, 330),
        boxes=[(580, 270, 1062, 314)]),
    "export-graphic-svg.png": dict(
        src="mb-export-svg-raw.png", crop=(0, 465, 893, 613), boxes=[(521, 478, 870, 520)]),

    # Session B (2026-10-30, afternoon). workspace.md
    "workspace-folders.png": dict(
        src="explorer-smith-full.png", crop=(300, 115, 1600, 760), boxes=[(690, 205, 1200, 255)]),
    "workspace-new-backstage.png": dict(
        src="new-project-backstage-full.png", crop=(0, 0, 1900, 920),
        boxes=[(395, 300, 525, 480)]),
    "workspace-new-project-default.png": dict(
        src="new-project-default-raw.png", crop=(0, 0, 910, 478),
        boxes=[(40, 200, 830, 282), (40, 300, 425, 332)]),
    "workspace-browse-name.png": dict(
        src="new-project-browse-full.png", crop=(200, 115, 1090, 710),
        boxes=[(530, 595, 715, 690)]),
    "workspace-new-project-checked.png": dict(
        src="new-project-checked-raw.png", crop=(0, 0, 910, 478),
        boxes=[(40, 200, 830, 282), (40, 300, 425, 332)]),
    "workspace-new-project-fixed.png": dict(
        src="new-project-fixed-raw.png", crop=(0, 0, 910, 478), boxes=[(40, 300, 425, 332)]),
    # housekeeping.md
    "housekeeping-shapefile-parts.png": dict(
        src="explorer-shapefile-full.png", crop=(590, 295, 1590, 960), boxes=[]),
    # point-feature-class.md
    "points-new-fc-menu.png": dict(
        src="points-new-fc-menu-full.png", crop=(930, 0, 1840, 980),
        boxes=[(950, 10, 1470, 50), (1478, 64, 1832, 100)]),
    "points-define.png": dict(
        src="points-page1-raw.png", crop=(0, 0, 812, 800), boxes=[(54, 400, 757, 440)]),
    "points-fields-long.png": dict(
        src="points-fields-long-raw.png", crop=(0, 0, 812, 560), boxes=[(416, 293, 806, 326)]),
    "points-fields-type-list.png": dict(
        src="points-fields-type-list-full.png", crop=(1100, 0, 1912, 720),
        boxes=[(1525, 490, 1855, 522)]),
    "points-fields-text.png": dict(
        src="points-fields-text-raw.png", crop=(0, 0, 812, 560), boxes=[(416, 293, 806, 326)]),
    "points-crs.png": dict(
        src="points-crs-raw.png", crop=(0, 0, 812, 640), boxes=[(30, 215, 700, 255)]),
    "points-edit-ribbon.png": dict(
        src="points-edit-ribbon-full.png", crop=(0, 85, 1000, 300),
        boxes=[(845, 135, 960, 180), (200, 140, 275, 240)]),
    "points-placed.png": dict(
        src="points-placed-full.png", crop=(0, 0, 1944, 980),
        boxes=[(1382, 640, 1641, 680), (200, 145, 275, 240)]),
    # check-your-output.md
    "check-output-select-warning.png": dict(
        src="select-zero-completed-full.png", crop=(1100, 0, 1912, 1000),
        boxes=[(1135, 700, 1880, 735), (1105, 895, 1905, 960)]),
    "check-output-warning-details.png": dict(
        src="select-zero-details-full.png", crop=(575, 239, 1343, 757),
        boxes=[(597, 433, 1194, 458)]),
    "check-output-empty-table.png": dict(
        src="select-zero-table-full.png", crop=(590, 660, 1925, 1000),
        boxes=[(799, 948, 950, 976)]),
    # attribute-expressions.md
    "expressions-field-type-text.png": dict(
        src="fields-cartocode-full.png", crop=(590, 320, 1925, 990),
        boxes=[(905, 668, 1300, 700)]),
    # map-frame-credits.md
    "credits-dynamic-text-menu.png": dict(
        src="credits-dynamic-text-menu-full.png", crop=(975, 100, 1900, 600),
        boxes=[(1275, 362, 1569, 454)]),
    "credits-contents-unchecked.png": dict(
        src="credits-contents-unchecked-full.png", crop=(15, 320, 585, 700),
        boxes=[(76, 607, 551, 637)]),
    # exporting-deliverables.md
    "export-layout-button.png": dict(
        src="share-export-layout-tip-full.png", crop=(0, 100, 1330, 385),
        boxes=[(921, 170, 994, 213)]),
    "export-layout-pane.png": dict(
        src="export-layout-pane-raw.png", crop=(0, 0, 812, 940),
        boxes=[(545, 252, 755, 306), (28, 608, 225, 640)]),
    "export-history-button.png": dict(
        src="analysis-history-tip-full.png", crop=(0, 0, 800, 620), boxes=[(18, 100, 122, 235)]),
}

# Layout exports and arcpy map renders (tips_maps.py, tips_export_layout.py): copied with a
# downsample only, no callouts. Source paths are relative to RAW.
COPIES = {
    "credits-before.jpg": ("credits-before-export.png", 1200),
    "credits-after.jpg": ("credits-after-export.png", 1200),
    "wrong-defaults-buffer-2m-vs-2mi.jpg": ("maps/buffer-2m-vs-2mi.jpg", 1500),
    "wrong-defaults-buffer-dissolve.jpg": ("maps/buffer-dissolve.jpg", 1500),
    "wrong-defaults-snap-tiny-basin.jpg": ("maps/snap-tiny-basin.jpg", 1500),
}

# Side by side: the same Select dialog before and after the SQL Editor is switched on.
PAIRS = {
    "wrong-defaults-ok-moves.png": [
        ("mb-select-clause-raw.png", (0, 0, 1000, 662), (849, 600, 979, 642)),
        ("mb-select-sql-raw.png", (0, 0, 1000, 727), (849, 664, 979, 706)),
    ],
}


def font(size):
    for name in ("segoeuib.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_boxes(im, boxes, origin):
    d = ImageDraw.Draw(im)
    ox, oy = origin
    for x0, y0, x1, y1 in boxes:
        d.rounded_rectangle([x0 - ox - 6, y0 - oy - 6, x1 - ox + 6, y1 - oy + 6], radius=8,
                            outline=RED, width=4)


def draw_label(im, box, origin, text, at):
    f = font(26)
    d = ImageDraw.Draw(im)
    tw, th = d.textbbox((0, 0), text, font=f)[2:]
    w, h = tw + 16, th + 14
    x0, y0, x1, y1 = (box[0] - origin[0], box[1] - origin[1], box[2] - origin[0],
                      box[3] - origin[1])
    if at == "right":
        lx, ly = x1 + 14, (y0 + y1) // 2 - h // 2
        if lx + w > im.width:  # no room: put it inside the box's left edge instead
            lx = x0 - w - 14
    elif at == "above":
        lx, ly = x0 - 6, y0 - 6 - h - 6
    else:
        lx, ly = x0 - 6, y1 + 12
    lx = max(2, min(lx, im.width - w - 2))
    ly = max(2, min(ly, im.height - h - 2))
    d.rounded_rectangle([lx, ly, lx + w, ly + h], radius=6, fill=RED)
    d.text((lx + 8, ly + 5), text, font=f, fill=(255, 255, 255))


def build(name, spec):
    im = Image.open(os.path.join(RAW, spec["src"])).convert("RGB")
    for (x0, y0, x1, y1), (sx, sy) in spec.get("patches", []):
        color = im.getpixel((sx, sy))
        ImageDraw.Draw(im).rectangle([x0, y0, x1, y1], fill=color)
    crop = spec["crop"]
    out = im.crop(crop)
    draw_boxes(out, spec["boxes"], crop[:2])
    if spec.get("label"):
        draw_label(out, spec["boxes"][0], crop[:2], spec["label"], spec.get("at", "below"))
    out.save(os.path.join(OUT, name), optimize=True)
    return out.size


def build_pair(name, parts, gap=40):
    tiles = []
    for src, crop, box in parts:
        im = Image.open(os.path.join(RAW, src)).convert("RGB").crop(crop)
        draw_boxes(im, [box], crop[:2])
        tiles.append(im)
    w = sum(t.width for t in tiles) + gap * (len(tiles) - 1)
    h = max(t.height for t in tiles)
    out = Image.new("RGB", (w, h), (255, 255, 255))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + gap
    out.save(os.path.join(OUT, name), optimize=True)
    return out.size


def main():
    os.makedirs(OUT, exist_ok=True)
    only = set(sys.argv[2:])
    for name, spec in FIGS.items():
        if not only or name in only:
            print(name, build(name, spec))
    for name, parts in PAIRS.items():
        if not only or name in only:
            print(name, build_pair(name, parts))
    for name, (src, width) in COPIES.items():
        if not only or name in only:
            im = Image.open(os.path.join(RAW, src)).convert("RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            im.save(os.path.join(OUT, name), quality=85, optimize=True)
            print(name, im.size)


if __name__ == "__main__":
    main()
