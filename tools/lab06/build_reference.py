"""Instructor-only reference layers for Lab 6, from the HydroMap app's baked data.

  data/instructor/powell_hydromap_shorelines.shp   34 shorelines 3370-3700 ft every 10 ft
  data/instructor/gsl_hydromap_shorelines.shp      45 shorelines 4170-4214 ft every 1 ft
  data/instructor/powell_shore_features_nps.csv    NPS ramp cutoff elevations + HydroMap places

The HydroMap shorelines were cut from the full-resolution USGS DEMs (Powell 1 m resampled to
30 m and simplified 60 m; GSL 0.5 m TBDEM), so they are a comparison, not the answer key: the
students' polygons come from the surface in data/student and will differ slightly.
"""
import json
from pathlib import Path

import fiona
import pandas as pd
from fiona.crs import CRS
from shapely.geometry import MultiPolygon, mapping, shape
from shapely.ops import transform
from pyproj import Transformer

APP = Path("/Users/dan/Code/hydromap-app/hydromap/data")
INSTR = Path(__file__).resolve().parents[1] / "data" / "instructor"


def shorelines(prefix, epsg, out):
    tr = Transformer.from_crs(4326, epsg, always_xy=True).transform
    schema = {"geometry": "MultiPolygon",
              "properties": {"Elevation": "int", "AreaSqMi": "float", "Source": "str:60"}}
    files = sorted((APP / "extent").glob(f"{prefix}-extent-*.geojson"))
    with fiona.open(INSTR / out, "w", driver="ESRI Shapefile", crs=CRS.from_epsg(epsg),
                    schema=schema) as dst:
        for f in files:
            for feat in json.loads(f.read_text())["features"]:
                g = transform(tr, shape(feat["geometry"]))
                if g.geom_type == "Polygon":
                    g = MultiPolygon([g])
                p = feat["properties"]
                dst.write({"geometry": mapping(g),
                           "properties": {"Elevation": int(p["elevation_ft_ngvd29"]),
                                          "AreaSqMi": p["area_sq_mi"], "Source": p["source"]}})
    return len(files)


def powell_features():
    wb = json.loads((APP / "tenants" / "powell.json").read_text())["waterbody"]
    places = {p["name"]: p for p in wb["places"]}
    rows = []
    for p in wb["access"]["points"]:
        rows.append({"name": p["name"], "kind": p["kind"],
                     "nps_cutoff_ft_ngvd29": p.get("min_elevation", ""),
                     "status_2026": p.get("status", ""), "note": p.get("note", "")})
    for p in places.values():
        rows.append({"name": p["name"], "kind": p["type"], "lat_approx": p["lat"],
                     "lon_approx": p["lon"], "note": p["note"]})
    pd.DataFrame(rows).to_csv(INSTR / "powell_shore_features_nps.csv", index=False)


if __name__ == "__main__":
    INSTR.mkdir(parents=True, exist_ok=True)
    print("powell", shorelines("powell", 6341, "powell_hydromap_shorelines.shp"))
    print("gsl", shorelines("gsl", 26912, "gsl_hydromap_shorelines.shp"))
    powell_features()
