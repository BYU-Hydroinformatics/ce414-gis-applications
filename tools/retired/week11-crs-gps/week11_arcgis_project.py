# Build C:\Ames\Week11\Week11.aprx for the Week 11 captures, and compute the datum-shift numbers the
# two decks quote (slides/week-11/coordinate-systems-projections.md and gps-triangulation.md).
#
#   Campuses_NAD83   BYU and the University of Utah, GCS NAD 1983 (the coordinates on the deck's slide)
#   Campuses_NAD27   the same two places in GCS NAD 1927, projected with NAD_1927_To_NAD_1983_NADCON,
#                    the grid transformation ArcGIS Pro ships (what an old survey or an old map would report)
#   Campuses_DefinedWrong   the NAD 1927 numbers stored in a NAD 1983 feature class: the error a
#                    Define Projection with the wrong datum makes. Drawn over the right layer it shows
#                    the misregistration the "registration" slide talks about.
#   gps_points.csv   the two campuses as a receiver would log them (WGS 1984 lat/long), for the
#                    XY Table To Point capture in the Thursday deck.
#
# Writes tools/week11_arcgis_numbers.json. Run with the ArcGIS Pro Python while ArcGIS Pro does not
# have the project open.
import json, os, sys
import arcpy

ROOT = r"C:\Ames\Week11"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APRX = os.path.join(ROOT, "Week11.aprx")
TEMPLATE = r"C:\Ames\Week02\CitiesRivers.aprx"
GDB = os.path.join(ROOT, "Week11.gdb")
PLACES = [("BYU", -111.6493, 40.2518), ("University of Utah", -111.8421, 40.7649)]
NAD83, NAD27, WGS84 = (arcpy.SpatialReference(c) for c in (4269, 4267, 4326))
UTM83 = arcpy.SpatialReference(26912)
NAD83_2011 = arcpy.SpatialReference(6318)
NUM = {}


def points(name, sr, coords):
    fc = os.path.join(GDB, name)
    if arcpy.Exists(fc): arcpy.management.Delete(fc)
    arcpy.management.CreateFeatureclass(GDB, name, "POINT", spatial_reference=sr)
    arcpy.management.AddField(fc, "Name", "TEXT", field_length=40)
    with arcpy.da.InsertCursor(fc, ["Name", "SHAPE@XY"]) as cur:
        for n, x, y in coords: cur.insertRow([n, (x, y)])
    return fc


def shift(pt_from, sr_from, sr_to, transformation):
    """Ground distance (m, in UTM 12N) between a point taken as-is and the same point transformed."""
    g = arcpy.PointGeometry(arcpy.Point(*pt_from), sr_from)
    moved = g.projectAs(sr_to, transformation)
    a = arcpy.PointGeometry(arcpy.Point(*pt_from), sr_to).projectAs(UTM83)
    b = moved.projectAs(UTM83)
    return moved.firstPoint, a.distanceTo(b), (b.firstPoint.X - a.firstPoint.X, b.firstPoint.Y - a.firstPoint.Y)


def main():
    os.makedirs(ROOT, exist_ok=True)
    if not arcpy.Exists(GDB): arcpy.management.CreateFileGDB(ROOT, "Week11.gdb")
    utah = arcpy.Extent(-114.05, 37.0, -109.04, 42.0)

    t27 = arcpy.ListTransformations(NAD27, NAD83, utah)
    tw = arcpy.ListTransformations(WGS84, NAD83_2011, utah)
    NUM["transformations_nad27_to_nad83_utah"] = t27[:6]
    NUM["transformations_wgs84_to_nad83_2011_utah"] = tw[:6]

    NADCON = "NAD_1927_To_NAD_1983_NADCON"
    assert NADCON in arcpy.ListTransformations(NAD27, NAD83, utah)
    nad27 = []
    for n, x, y in PLACES:
        p, d, (dx, dy) = shift((x, y), NAD83, NAD27, NADCON)
        # How much the choice matters: the first transformation the list offers, against NADCON.
        alt = arcpy.PointGeometry(arcpy.Point(x, y), NAD83).projectAs(NAD27, t27[0])
        gap = alt.projectAs(UTM83).distanceTo(arcpy.PointGeometry(p, NAD27).projectAs(UTM83))
        NUM.setdefault("nad27_choice_gap_m", {})[n] = {"first_listed": t27[0], "vs": NADCON,
                                                       "gap_m": round(gap, 2)}
        nad27.append((n, p.X, p.Y))
        NUM.setdefault("nad83_to_nad27", {})[n] = {
            "transformation": NADCON, "nad27_lon": round(p.X, 6), "nad27_lat": round(p.Y, 6),
            "ground_shift_m": round(d, 1), "dx_m": round(dx, 1), "dy_m": round(dy, 1)}
        _, d2, (dx2, dy2) = shift((x, y), WGS84, NAD83_2011, tw[0])
        NUM.setdefault("wgs84_to_nad83_2011", {})[n] = {
            "transformation": tw[0], "ground_shift_m": round(d2, 2), "dx_m": round(dx2, 2),
            "dy_m": round(dy2, 2)}
    points("Campuses_NAD83", NAD83, PLACES)
    points("Campuses_NAD27", NAD27, nad27)
    points("Campuses_DefinedWrong", NAD83, nad27)
    with open(os.path.join(ROOT, "gps_points.csv"), "w", newline="\n") as f:
        f.write("Name,Latitude,Longitude\n")
        for n, x, y in PLACES: f.write(f"{n},{y},{x}\n")

    if not os.path.exists(APRX):
        arcpy.mp.ArcGISProject(TEMPLATE).saveACopy(APRX)
        aprx = arcpy.mp.ArcGISProject(APRX)
        for m in aprx.listMaps(): aprx.deleteItem(m)
        for l in aprx.listLayouts(): aprx.deleteItem(l)
        aprx.defaultGeodatabase = GDB
        aprx.homeFolder = ROOT
        m = aprx.createMap("Registration")
        m.spatialReference = UTM83
        for name in ("Campuses_DefinedWrong", "Campuses_NAD83"):
            lyr = m.addDataFromPath(os.path.join(GDB, name))
        aprx.save()
        print("saved", APRX)

    with open(os.path.join(REPO, "tools", "week11_arcgis_numbers.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(NUM, f, indent=2)
    print(json.dumps(NUM, indent=2))


if __name__ == "__main__":
    main()
