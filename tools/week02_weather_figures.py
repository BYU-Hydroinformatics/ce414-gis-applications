"""Regenerate the two Week 2 Part A weather-model figures as clean SVG:
slides/week-02/images/mba-weather-stations.svg and mba-thiessen-polygons.svg.
Station positions are illustrative; the Thiessen (Voronoi) polygons are computed from them by
clipping the bounding rectangle against the perpendicular-bisector half-planes of every other
station, so the polygon edges are exact."""
import io
from pathlib import Path

W, H = 600, 800
STATIONS = [(150,120),(400,95),(60,270),(265,255),(440,340),(150,390),
            (290,505),(450,560),(80,610),(360,700),(160,745),(430,740)]
PALETTE = ["#9ecae1","#fdd0a2","#c7e9c0","#dadaeb","#fee6a4","#f4b6c2","#b3e2cd","#ffe08a",
           "#cfe2f3","#e6c9a8","#d9ead3","#f9cb9c"]

def clip(poly, a, b):
    """Keep the part of poly closer to a than to b (Sutherland-Hodgman against one half-plane)."""
    (ax,ay),(bx,by) = a,b
    mx,my = (ax+bx)/2,(ay+by)/2
    nx,ny = bx-ax, by-ay                 # normal pointing toward b
    def inside(p): return (p[0]-mx)*nx + (p[1]-my)*ny <= 0
    out=[]
    for i,p in enumerate(poly):
        q=poly[i-1]
        pin,qin=inside(p),inside(q)
        if pin!=qin:
            dp=(p[0]-mx)*nx+(p[1]-my)*ny; dq=(q[0]-mx)*nx+(q[1]-my)*ny
            t=dq/(dq-dp); out.append((q[0]+t*(p[0]-q[0]), q[1]+t*(p[1]-q[1])))
        if pin: out.append(p)
    return out

def voronoi_cell(i):
    poly=[(0,0),(W,0),(W,H),(0,H)]
    for j,s in enumerate(STATIONS):
        if j!=i: poly=clip(poly, STATIONS[i], s)
    return poly

STATION_SYMBOL = '''<symbol id="stn" viewBox="-20 -34 40 44">
  <line x1="0" y1="-12" x2="0" y2="4" stroke="#222" stroke-width="3"/>
  <path d="M-11 8 L0 4 L11 8 Z" fill="#222"/>
  <line x1="0" y1="-24" x2="0" y2="-12" stroke="#222" stroke-width="2"/>
  <line x1="-13" y1="-24" x2="13" y2="-24" stroke="#222" stroke-width="2"/>
  <circle cx="-13" cy="-24" r="4" fill="#d62728"/>
  <circle cx="13" cy="-24" r="4" fill="#d62728"/>
  <circle cx="0" cy="-24" r="4" fill="#d62728"/>
  <line x1="-8" y1="-6" x2="-1" y2="-6" stroke="#222" stroke-width="2"/>
  <path d="M-16 -2 L-8 -6 L-16 -10 Z" fill="#0062b8"/>
</symbol>'''

def head():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            '<rect x="0" y="0" width="%d" height="%d" fill="#fff"/>\n' % (W,H))

def foot():
    return '<rect x="2" y="2" width="%d" height="%d" fill="none" stroke="#000" stroke-width="4"/>\n</svg>\n' % (W-4,H-4)

def write(path, body):
    Path(path).write_text(head()+body+foot(), encoding='utf-8', newline='\n')

stations = head()
stations = STATION_SYMBOL + '\n'
for x,y in STATIONS:
    stations += f'<use href="#stn" x="{x-40}" y="{y-68}" width="80" height="88"/>\n'
write('slides/week-02/images/mba-weather-stations.svg', stations)

cells=''
for i,(x,y) in enumerate(STATIONS):
    pts=' '.join(f'{px:.1f},{py:.1f}' for px,py in voronoi_cell(i))
    cells += f'<polygon points="{pts}" fill="{PALETTE[i%len(PALETTE)]}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>\n'
for x,y in STATIONS:
    cells += f'<circle cx="{x}" cy="{y}" r="7" fill="#222"/>\n'
write('slides/week-02/images/mba-thiessen-polygons.svg', cells)
print('wrote both SVGs')
