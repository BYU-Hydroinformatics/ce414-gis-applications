"""Draw slides/week-02/images/mba-pie-recipe.svg: the pumpkin-pie recipe as a ModelBuilder-style
flow diagram (blue ovals = input data, yellow boxes = tools, green ovals = derived data), with an
individual arrow from every ingredient into the tool that uses it. The pie photo is embedded so the
SVG stays self-contained."""
import base64
from pathlib import Path

IN, TOOL, OUT = '#8ec1ea', '#ffd966', '#9fd89f'
W, H = 1200, 470
BW, BH = 138, 40
nodes = {}   # name: (x, y, kind, label)


def add(name, x, y, kind, label=None):
    nodes[name] = (x, y, kind, label or name)


add('flour', 95, 45, IN)
add('salt', 95, 100, IN)
add('shortening', 95, 155, IN)
add('cut', 260, 100, TOOL)
add('pie dough', 420, 100, OUT)
add('roll out', 580, 100, TOOL)
add('pie crust', 740, 100, OUT)
add('eggs', 95, 235, IN)
add('beat', 260, 235, TOOL)
add('beaten eggs', 420, 235, OUT)
add('pumpkin puree', 95, 315, IN)
add('evaporated milk', 95, 370, IN)
add('spices', 95, 425, IN)
add('mix', 580, 340, TOOL)
add('pie filling', 740, 340, OUT)
add('fill pan & bake', 900, 220, TOOL, 'fill pan &amp; bake')
edges = [('flour', 'cut'), ('salt', 'cut'), ('shortening', 'cut'), ('cut', 'pie dough'),
         ('pie dough', 'roll out'), ('roll out', 'pie crust'),
         ('eggs', 'beat'), ('beat', 'beaten eggs'),
         ('pumpkin puree', 'mix'), ('evaporated milk', 'mix'), ('spices', 'mix'), ('beaten eggs', 'mix'),
         ('mix', 'pie filling'), ('pie crust', 'fill pan & bake'), ('pie filling', 'fill pan & bake')]

s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
     'font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16">',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
     'orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#444"/></marker></defs>']


def edge(a, b):
    x1, y1 = nodes[a][0] + BW / 2, nodes[a][1]
    x2, y2 = nodes[b][0] - BW / 2 - 2, nodes[b][1]
    c = (x2 - x1) * 0.5
    return (f'<path d="M{x1},{y1} C{x1+c},{y1} {x2-c},{y2} {x2},{y2}" fill="none" stroke="#444" '
            'stroke-width="2.2" marker-end="url(#ah)"/>')


for a, b in edges:
    s.append(edge(a, b))
for name, (x, y, kind, label) in nodes.items():
    if kind == TOOL:
        s.append(f'<rect x="{x-BW/2}" y="{y-BH/2}" width="{BW}" height="{BH}" rx="6" fill="{kind}" '
                 'stroke="#7a6a20" stroke-width="1.5"/>')
    else:
        s.append(f'<ellipse cx="{x}" cy="{y}" rx="{BW/2}" ry="{BH/2}" fill="{kind}" '
                 'stroke="#2a5d8f" stroke-width="1.5"/>')
    s.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" fill="#111">{label}</text>')

# final output: the pie photo as the derived-data node
pie = base64.b64encode(Path('slides/week-02/images/mba-pumpkin-pie.jpg').read_bytes()).decode()
px, py = 1085, 220
s.append(f'<path d="M{900+BW/2},{py} L{px-100},{py}" fill="none" stroke="#444" stroke-width="2.2" '
         'marker-end="url(#ah)"/>')
s.append(f'<clipPath id="pc"><ellipse cx="{px}" cy="{py}" rx="95" ry="72"/></clipPath>')
s.append(f'<image href="data:image/jpeg;base64,{pie}" x="{px-100}" y="{py-100}" width="200" height="200" '
         'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>')
s.append(f'<ellipse cx="{px}" cy="{py}" rx="95" ry="72" fill="none" stroke="#2f7a2f" stroke-width="3"/>')
s.append(f'<text x="{px}" y="{py+100}" text-anchor="middle" font-weight="700" font-size="19" '
         'fill="#002e5d">Pumpkin Pie</text>')

# legend
lx, ly = 270, 440
s.append(f'<ellipse cx="{lx}" cy="{ly}" rx="26" ry="11" fill="{IN}" stroke="#2a5d8f"/>'
         f'<text x="{lx+34}" y="{ly+5}" fill="#444" font-size="14">input data</text>')
s.append(f'<rect x="{lx+120}" y="{ly-11}" width="52" height="22" rx="4" fill="{TOOL}" stroke="#7a6a20"/>'
         f'<text x="{lx+180}" y="{ly+5}" fill="#444" font-size="14">tool (process)</text>')
s.append(f'<ellipse cx="{lx+310}" cy="{ly}" rx="26" ry="11" fill="{OUT}" stroke="#2a5d8f"/>'
         f'<text x="{lx+344}" y="{ly+5}" fill="#444" font-size="14">derived data</text>')
s.append('</svg>')
Path('slides/week-02/images/mba-pie-recipe.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')
print('pie recipe svg written')
