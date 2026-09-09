"""Three ModelBuilder diagrams of the Cities Near Rivers question for Week 2 Part B ("how many ways?"),
in the ArcGIS Pro 3.7 element style (tools/mb_style.py):

  1. Project, Buffer, Project, Intersect: the Part A model (256 cities, planar 10 miles)
  2. Select Layer By Location within a geodesic distance, then Copy Features (257 cities)
  3. Near with a geodesic search radius writes NEAR_FID and NEAR_DIST onto the cities; Select keeps the
     ones that found a river (NEAR_FID <> -1)

    python tools/week02_three_ways.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mb_style import Model  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slides', 'week-02', 'images')

# 1. Buffer + Intersect
m = Model(1100, 190)
m.add('rivers', 95, 50, 'in', 'us_rivers')
m.add('proj1', 280, 50, 'tool', 'Project')
m.add('privers', 465, 50, 'out', 'Projected Rivers')
m.add('buffer', 650, 50, 'tool', 'Buffer (10 miles)')
m.add('areas', 835, 50, 'out', 'Areas Near Rivers')
m.add('cities', 95, 140, 'in', 'us_cities')
m.add('proj2', 280, 140, 'tool', 'Project')
m.add('pcities', 465, 140, 'out', 'Projected Cities')
m.add('intersect', 835, 140, 'tool', 'Intersect')
m.add('result', 1010, 140, 'out', 'Cities Near Rivers')
for a, b in [('rivers', 'proj1'), ('proj1', 'privers'), ('privers', 'buffer'), ('buffer', 'areas'),
             ('cities', 'proj2'), ('proj2', 'pcities'), ('pcities', 'intersect'), ('intersect', 'result')]:
    m.link(a, b)
m.link('areas', 'intersect', vertical=True)
m.write(os.path.join(OUT, 'mbb-way1-buffer-intersect.svg'))

# 2. Select Layer By Location
m = Model(1100, 190)
m.add('cities', 95, 70, 'in', 'us_cities')
m.add('rivers', 95, 140, 'in', 'us_rivers')
m.add('dist', 340, 30, 'in', '10 Miles, geodesic', width=170, icon='value')
m.add('sel', 340, 105, 'tool', 'Select Layer By Location', width=200)
m.add('selected', 570, 105, 'out', 'us_cities (selected)', width=170)
m.add('copy', 780, 105, 'tool', 'Copy Features')
m.add('result', 985, 105, 'out', 'Cities Near Rivers')
for a, b in [('cities', 'sel'), ('rivers', 'sel'), ('sel', 'selected'), ('selected', 'copy'), ('copy', 'result')]:
    m.link(a, b)
m.link('dist', 'sel', vertical=True)
m.write(os.path.join(OUT, 'mbb-way2-select-by-location.svg'))

# 3. Near, then Select
m = Model(1100, 190)
m.add('cities', 95, 70, 'in', 'us_cities')
m.add('rivers', 95, 140, 'in', 'us_rivers')
m.add('radius', 320, 30, 'in', '10 Miles, geodesic', width=170, icon='value')
m.add('near', 320, 105, 'tool', 'Near')
m.add('updated', 535, 105, 'out', 'us_cities + NEAR_FID', width=180)
m.add('expr', 760, 30, 'in', 'NEAR_FID &lt;&gt; -1', width=150, icon='value')
m.add('select', 760, 105, 'tool', 'Select')
m.add('result', 985, 105, 'out', 'Cities Near Rivers')
for a, b in [('cities', 'near'), ('rivers', 'near'), ('near', 'updated'), ('updated', 'select'), ('select', 'result')]:
    m.link(a, b)
m.link('radius', 'near', vertical=True)
m.link('expr', 'select', vertical=True)
m.write(os.path.join(OUT, 'mbb-way3-near-select.svg'))
