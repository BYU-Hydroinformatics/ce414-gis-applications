"""Keep the example-map scenario and test whether the example recommended site survives every
scenario. Run after run_model.py.

    python scenario.py            -> Suitable_D40 / Suitable_Polys_D40 in Check.gdb, site_survival.json
"""
import arcpy, json, pathlib
from arcpy.sa import *
import run_model as rm

SITE = (418391, 4425403)     # label point of the largest baseline zone (Goshen Valley, SR 68)


def value_at(ras, xy):
    v = arcpy.management.GetCellValue(ras, f"{xy[0]} {xy[1]}").getOutput(0)
    return None if v in ("NoData", "") else float(v)


def main():
    rm.setup()
    log = {"county_km2": rm.area("Utah_County") / rm.KM2}
    arcpy.env.cellSize = rm.CELL
    out = {"site_utm": SITE, "runs": []}
    for p in [rm.DEFAULT] + list(rm.SCENARIOS):
        r = rm.run(p, log)
        v = value_at(rm.GDB + r"\Suitable_Sites_s", SITE)
        r["site_suitable"] = v == 1
        out["runs"].append({k: r[k] for k in ("max_slope", "road_km", "radius_m", "max_density",
                                               "suitable_km2", "pct_county", "site_suitable")})
        print(out["runs"][-1])
        if p["max_density"] == 40 and p == dict(rm.DEFAULT, max_density=40):
            arcpy.management.CopyRaster("Suitable_Sites_s", "Suitable_D40")
            arcpy.management.CopyFeatures("Suitable_Polys_s", "Suitable_Polys_D40")
            arcpy.management.CopyRaster("Low_Tower_Density_s", "Low_Tower_Density_D40")
    pathlib.Path(__file__).with_name("site_survival.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
