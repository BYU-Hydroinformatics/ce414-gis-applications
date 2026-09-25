"""Build docs/data/lab04-utah-cell-towers.zip from the GeoJSON that fetch_towers.py saved.

The extract is every Utah record of the FCC-derived "Cellular Towers in the United States
(Archive)" layer, as a shapefile in geographic coordinates (GCS WGS 1984), with nothing filtered
and nothing de-duplicated, plus READ-ME-FIRST.txt. Students project and clip it themselves.

    "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" tools/lab04/make_extract.py
"""
import arcpy, json, pathlib, shutil, zipfile, collections

SRC = pathlib.Path(r"C:\Ames\Lab04\Data\hifld_towers_UT.geojson")
STAGE = pathlib.Path(r"C:\Ames\Lab04\Data\lab04-utah-cell-towers")
REPO = pathlib.Path(__file__).resolve().parents[2]
ZIP = REPO / "docs" / "data" / "lab04-utah-cell-towers.zip"

README = """UTAH CELL TOWERS - prepared extract for CE 414 Lab 4 (Cell Phone Tower Placement)
=====================================================================================

WHAT
  UtahCellTowers.shp - {n} point records: every Utah record of the federal layer named below.
  One record is one FCC cellular license LOCATION (a licensee's antenna site), not one
  physical structure. {d} of the records share their exact coordinates with another record,
  because two licensees - or one licensee twice - registered the same site. Nothing was
  removed or merged; deciding what that does to a density analysis is part of the lab.

WHERE
  All of Utah. Coordinate system: GCS WGS 1984 (latitude/longitude, decimal degrees),
  as the source service delivers it. Project it before measuring any distance or area.

WHEN
  Source layer "Last Data Update: 07/06/2024". The layer is ARCHIVED: its publisher says it
  "will no longer be updated or maintained". Retrieved for this course on {retrieved}.

WHY / HOW
  Compiled by the Homeland Infrastructure Foundation-Level Data (HIFLD) program from the
  Federal Communications Commission's Universal Licensing System, for the Cellular
  Radiotelephone Service (the original 800 MHz cellular band). It therefore does NOT include
  sites licensed only under PCS, AWS or later spectrum, and it is far from a complete census
  of towers: the real number of cell sites in Utah County is many times larger.

WHO
  Source: "Cellular Towers in the United States (Archive)", Federal_User_Community on
  ArcGIS Online, item 15dabb4108254481b591018be2598f3c,
  https://www.arcgis.com/home/item.html?id=15dabb4108254481b591018be2598f3c
  Original data: U.S. Federal Communications Commission.

PROCESSING
  1. Queried the feature service with LocState = 'UT' (all fields, output WGS 1984).
  2. Converted the GeoJSON to a shapefile with arcpy JSONToFeatures. No other change.
  Scripts: tools/lab04/fetch_towers.py and tools/lab04/make_extract.py in the course repo.

FIELDS (selected)
  Licensee    company holding the license
  LocCity, LocCounty, LocState   location as the licensee reported it
  StrucType   structure type (LTOWER lattice tower, MTOWER monopole, TANK, POLE, ...)
  AllStruc    overall structure height in meters (0 where not reported)
  LicStatus   license status (A = active)

LICENSE
  U.S. federal government data; no use restrictions stated. Credit line:
  "Cell tower locations: FCC Cellular Radiotelephone Service sites via HIFLD (archive, data
  updated July 2024)."
"""


def main():
    fc = json.loads(SRC.read_text())
    feats = fc["features"]
    xy = collections.Counter(tuple(round(c, 5) for c in f["geometry"]["coordinates"]) for f in feats)
    dup_records = sum(v for v in xy.values() if v > 1)
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    tmp = STAGE / "_in.geojson"
    tmp.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    arcpy.env.overwriteOutput = True
    arcpy.conversion.JSONToFeatures(str(tmp), str(STAGE / "UtahCellTowers.shp"), "POINT")
    tmp.unlink()
    n = int(arcpy.management.GetCount(str(STAGE / "UtahCellTowers.shp"))[0])
    (STAGE / "READ-ME-FIRST.txt").write_text(
        README.format(n=n, d=dup_records, retrieved=fc.get("retrieved", "unknown")), encoding="utf-8")
    ZIP.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STAGE.iterdir()):
            if p.suffix.lower() in (".lock",) or p.name.endswith(".sr.lock"):
                continue
            z.write(p, f"lab04-utah-cell-towers/{p.name}")
    print(n, "records;", dup_records, "records share a location;", ZIP, round(ZIP.stat().st_size / 1e3), "kB")


if __name__ == "__main__":
    main()
