"""Draw the four question icons for the Week 2 Part A "What is geoprocessing?" slide:
mba-gp-site.svg (stacked criteria layers -> one chosen cell), mba-gp-near.svg (buildings and their
nearest hydrant), mba-gp-route.svg (a route across contours), mba-gp-zone.svg (a plume over blocks).
Pure illustration: no data values appear anywhere."""
from pathlib import Path

NAVY, BLUE, ORANGE, GRAY = '#002e5d', '#0062b8', '#e8792b', '#8a94a3'
OUT = Path('slides/week-02/images')


def svg(body, w=200, h=160):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif">\n{body}\n</svg>\n')


# 1. site selection: three tilted layers stacked, an arrow, one highlighted cell in the result
def layer(x, y, fill, cells=None):
    # a parallelogram 110 wide, 40 tall, sheared
    s = f'<polygon points="{x},{y+40} {x+110},{y+40} {x+140},{y} {x+30},{y}" fill="{fill}" stroke="{NAVY}" stroke-width="1.5"/>'
    for i in range(1, 4):   # grid lines
        s += f'<line x1="{x+i*27.5}" y1="{y+40}" x2="{x+30+i*27.5}" y2="{y}" stroke="{NAVY}" stroke-width="0.7" opacity="0.5"/>'
        s += f'<line x1="{x+i*7.5}" y1="{y+40-i*10}" x2="{x+110+i*7.5}" y2="{y+40-i*10}" stroke="{NAVY}" stroke-width="0.7" opacity="0.5"/>'
    return s

body = layer(20, 18, '#cfe2f3') + layer(20, 40, '#d9ead3') + layer(20, 62, '#fce5cd')
body += f'<path d="M108,108 v18 m0,0 l-7,-8 m7,8 l7,-8" fill="none" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>'
body += layer(30, 118, '#eef3f9')
body += f'<polygon points="85,148 112,148 120,138 93,138" fill="{ORANGE}" stroke="{NAVY}" stroke-width="1.2"/>'
(OUT / 'mba-gp-site.svg').write_text(svg(body), encoding='utf-8', newline='\n')

# 2. nearest hydrant: three buildings, two hydrants, a dashed line from each building to its nearest
def building(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#d6dde6" stroke="{NAVY}" stroke-width="1.5"/>'

def hydrant(x, y):
    return (f'<rect x="{x-6}" y="{y-10}" width="12" height="20" rx="3" fill="{ORANGE}" stroke="{NAVY}" stroke-width="1.2"/>'
            f'<rect x="{x-10}" y="{y-4}" width="20" height="6" rx="2" fill="{ORANGE}" stroke="{NAVY}" stroke-width="1.2"/>'
            f'<circle cx="{x}" cy="{y-13}" r="4" fill="{ORANGE}" stroke="{NAVY}" stroke-width="1.2"/>')

body = building(20, 20, 46, 34) + building(30, 95, 40, 45) + building(120, 30, 55, 40)
body += f'<line x1="66" y1="37" x2="92" y2="70" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5,4"/>'
body += f'<line x1="70" y1="112" x2="92" y2="84" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5,4"/>'
body += f'<line x1="150" y1="70" x2="160" y2="108" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5,4"/>'
body += hydrant(96, 78) + hydrant(163, 122)
(OUT / 'mba-gp-near.svg').write_text(svg(body), encoding='utf-8', newline='\n')

# 3. route over terrain: nested contour loops and a winding path from A to B
body = ''
for i, r in enumerate([85, 68, 51, 34, 18]):
    body += (f'<ellipse cx="118" cy="82" rx="{r*0.95}" ry="{r*0.7}" fill="none" stroke="#a5754a" '
             f'stroke-width="1.3" transform="rotate(-18 118 82)"/>')
body += (f'<path d="M22,140 C40,120 30,95 55,88 S95,120 120,150 S165,110 178,40" fill="none" '
         f'stroke="{ORANGE}" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="1,0"/>')
body += f'<circle cx="22" cy="140" r="7" fill="{NAVY}"/><text x="22" y="144" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">A</text>'
body += f'<circle cx="178" cy="40" r="7" fill="{NAVY}"/><text x="178" y="44" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">B</text>'
(OUT / 'mba-gp-route.svg').write_text(svg(body), encoding='utf-8', newline='\n')

# 4. contamination zone: a block grid with a plume polygon over part of it
body = ''
for r in range(4):
    for c in range(5):
        body += f'<rect x="{12+c*36}" y="{14+r*33}" width="36" height="33" fill="#f3efe6" stroke="{GRAY}" stroke-width="1"/>'
body += (f'<path d="M40,60 C55,30 110,25 150,45 C185,62 180,110 150,125 C115,142 70,130 48,105 C38,92 34,74 40,60 Z" '
         f'fill="{ORANGE}" fill-opacity="0.55" stroke="{ORANGE}" stroke-width="2"/>')
body += f'<circle cx="52" cy="66" r="5" fill="{NAVY}"/>'
for (x, y) in [(70, 50), (105, 42), (135, 60), (95, 85), (130, 100), (70, 108), (160, 90)]:
    body += f'<circle cx="{x}" cy="{y}" r="2.6" fill="{NAVY}"/>'
(OUT / 'mba-gp-zone.svg').write_text(svg(body), encoding='utf-8', newline='\n')
print('four geoprocessing icons written')
