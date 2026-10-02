"""Ramp-toe check values for Lab 6 (the Step 1 shore-feature table), measured on wahweap_ft.

Ramp locations are from OpenStreetMap (Overpass, queried 2026-10-02):
  Wahweap Main                 node 914051609  "Wahweap Marina Main boat launch" (leisure=slipway)
  Wahweap Stateline Auxiliary  node 11882429534 (leisure=slipway, unnamed, check_date 2025-04-18);
                               NPS places it "between Stateline and Wahweap boat ramps"
                               (news release 2021-07-15). Not OSM way 109046268 "Stateline Launch
                               Ramp", which is the other (Stateline) ramp.
  Antelope Point (public)      way 109032037  "Antelope Point boat launch"
Each ramp's centerline below was drawn on Esri World Imagery chips (the parking-lot end to past the
waterline); the toe was read where the ramp's steady grade ends.

    python ramp_toes.py <Lab06.gdb>

Prints the 10 m and 30 m profiles. Run with the ArcGIS Pro Python. Result on 2026-10-02:
  Wahweap Main     grade break ~3,548 ft on wahweap_ft (3,542.4 on powell_ft); NPS cutoff 3,545
  Stateline Aux.   grade levels onto a bench ~3,529-3,531 ft;                  NPS cutoff 3,515
                   (ramp rehabilitated 2021 and extended later, after the 2017-18 survey)
  Antelope Point   concrete ends on imagery ~385 m down the line, where the surface falls from
                   ~3,590 to ~3,577 ft in 10 m;                                NPS cutoff 3,588
"""
import os
import sys

import arcpy
import numpy as np

GDB = sys.argv[1]
LINES = {  # (start x, start y, end x, end y) in NAD83(2011) UTM 12N, parking-lot end first
    "wahweap_main": (456670, 4094213, 457200, 4094490),
    "stateline_auxiliary": (456306, 4095260, 456700, 4095300),
    "antelope_point": (460699, 4090917, 460588, 4091380),
}


def grid(name):
    r = arcpy.Raster(os.path.join(GDB, name))
    return r.extent.XMin, r.extent.YMax, r.meanCellWidth, arcpy.RasterToNumPyArray(r, nodata_to_value=np.nan)


g10, g30 = grid("wahweap_ft"), grid("powell_ft")


def at(g, x, y):
    x0, y0, cs, a = g
    return a[int((y0 - y) // cs), int((x - x0) // cs)]


for name, (ax, ay, bx, by) in LINES.items():
    print(name)
    length = np.hypot(bx - ax, by - ay)
    for d in np.arange(0, length + 1, 10):
        x, y = ax + (bx - ax) * d / length, ay + (by - ay) * d / length
        print(f"  {d:4.0f} m  {x:9.1f} {y:10.1f}  10 m {at(g10, x, y):7.1f}  30 m {at(g30, x, y):7.1f}")
