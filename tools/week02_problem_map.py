"""Draw the "Cities Near Rivers" problem map for Week 2 Part A slide 21 from the course data
package (docs/data/week02-cities-rivers.zip: Natural Earth 1:10m, public domain, clipped to the
lower 48) in USA Contiguous Equidistant Conic, and print the answer counts for a 10 mile and a
5 mile buffer so the slide's check values come from the same data. Needs the ArcGIS Pro Python
environment (arcpy + matplotlib).
Usage: python tools/week02_problem_map.py"""
import tempfile
import zipfile
from pathlib import Path

import arcpy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon

work = Path(tempfile.mkdtemp(prefix='cr_'))
zipfile.ZipFile('docs/data/week02-cities-rivers.zip').extractall(work)
sr = arcpy.SpatialReference('USA Contiguous Equidistant Conic')
arcpy.env.overwriteOutput = True
gdb = arcpy.management.CreateFileGDB(str(work), 'cr.gdb')[0]


def proj(name):
    return arcpy.management.Project(str(work / f'{name}.shp'), f'{gdb}/{name}_p', sr)[0]


boundary, cities, rivers = proj('us_boundary'), proj('us_cities'), proj('us_rivers')
total = int(arcpy.management.GetCount(cities)[0])
for miles in (10, 5):
    buf = arcpy.analysis.Buffer(rivers, f'{gdb}/near_{miles}', f'{miles} Miles', dissolve_option='ALL')[0]
    hit = arcpy.analysis.Intersect([cities, buf], f'{gdb}/cities_{miles}')[0]
    print(f'{miles} miles: {arcpy.management.GetCount(hit)[0]} of {total} cities')


def rings(fc):
    out = []
    with arcpy.da.SearchCursor(fc, ['SHAPE@']) as cur:
        for (g,) in cur:
            if g is None:
                continue
            for part in g:
                pts, ring = [], []
                for p in part:
                    if p is None:          # inner-ring separator
                        pts.append(ring); ring = []
                    else:
                        ring.append((p.X, p.Y))
                pts.append(ring)
                out.append(pts)
    return out


fig, ax = plt.subplots(figsize=(11, 6.6), dpi=160)
ax.set_aspect('equal'); ax.axis('off')
for parts in rings(boundary):
    ax.add_patch(Polygon(parts[0], closed=True, facecolor='#eef0e6', edgecolor='#9aa08f', linewidth=0.6, zorder=1))
segs = []
for parts in rings(rivers):
    for ring in parts:
        if len(ring) > 1:
            segs.append(ring)
ax.add_collection(LineCollection(segs, colors='#2f6fb5', linewidths=1.1, zorder=2))
xs, ys = [], []
with arcpy.da.SearchCursor(cities, ['SHAPE@XY']) as cur:
    for ((x, y),) in cur:
        xs.append(x); ys.append(y)
ax.scatter(xs, ys, s=7, c='#c0392b', edgecolors='none', zorder=3)
ax.autoscale_view()
ax.margins(0.01)
ax.text(0.99, 0.02, 'USA Contiguous Equidistant Conic  |  Natural Earth 1:10m', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=7, color='#6b7280')
fig.tight_layout(pad=0.2)
fig.savefig('slides/week-02/images/mba-cities-rivers-problem.png', facecolor='white')
print('map written')
