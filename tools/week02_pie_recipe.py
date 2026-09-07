"""Draw slides/week-02/images/mba-pie-recipe.svg: the pumpkin-pie recipe as a flow diagram in the
ArcGIS Pro 3.7 ModelBuilder element style (verified against a Pro 3.7.1 capture,
mba-cities-rivers-model-pro.png): input data is a rounded rectangle with a blue outline and a
light-blue icon panel, a tool is a square-cornered box with a yellow hammer panel, derived data is a
rounded rectangle with a green outline and a green icon panel. Every ingredient gets its own arrow
into the tool that uses it. The pie photo is embedded so the SVG stays self-contained."""
import base64
from pathlib import Path

IN, TOOL, OUT = 'in', 'tool', 'out'
STYLE = {  # panel fill, outline, body fill
    'in':   ('#bfe4fb', '#1a7bd3', '#ffffff'),
    'tool': ('#fff2b3', '#e0c200', '#ffffff'),
    'out':  ('#b9e8b9', '#3aa63a', '#ffffff'),
}
W, H = 1200, 470
BW, BH = 148, 44
PW = 34   # icon panel width
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
ICONS = {
    'tool': lambda cx, cy: (f'<path d="M{cx-9},{cy-9} l7,7 M{cx-2},{cy-2} l-8,8 l4,4 l8,-8 M{cx-11},{cy-7} l4,-4 l8,8 l-4,4 z" '
                            'fill="none" stroke="#8a6d1a" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>'),
    'in':   lambda cx, cy: (f'<path d="M{cx-11},{cy-6} l16,-5 l6,17 l-16,5 z" fill="#f2d96b" stroke="#8a6d1a" stroke-width="1.5"/>'
                            f'<circle cx="{cx-6}" cy="{cy-9}" r="3.5" fill="#f5a623"/>'),
    'out':  lambda cx, cy: (f'<rect x="{cx-11}" y="{cy-9}" width="22" height="18" rx="2" fill="#fff" stroke="#555" stroke-width="1.5"/>'
                            f'<path d="M{cx-11},{cy+2} q6,-10 12,-2 t10,-4" fill="none" stroke="#555" stroke-width="1.5"/>'),
}


def element(x, y, kind, label):
    panel, outline, body = STYLE[kind]
    rx = 3 if kind == 'tool' else 14
    left, top = x - BW / 2, y - BH / 2
    out = [f'<clipPath id="clip-{int(x)}-{int(y)}"><rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}"/></clipPath>',
           f'<rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}" fill="{body}"/>',
           f'<rect x="{left}" y="{top}" width="{PW}" height="{BH}" fill="{panel}" clip-path="url(#clip-{int(x)}-{int(y)})"/>',
           ICONS[kind](left + PW / 2, y),
           f'<rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}" fill="none" stroke="{outline}" stroke-width="1.8"/>',
           f'<text x="{left + PW + (BW - PW) / 2}" y="{y + 5}" text-anchor="middle" fill="#111" font-size="14">{label}</text>']
    return '\n'.join(out)


for name, (x, y, kind, label) in nodes.items():
    s.append(element(x, y, kind, label))

# final output: the pie photo as the derived-data node
pie = base64.b64encode(Path('slides/week-02/images/mba-pumpkin-pie.jpg').read_bytes()).decode()
px, py = 1085, 220
s.append(f'<path d="M{900+BW/2},{py} L{px-100},{py}" fill="none" stroke="#444" stroke-width="2.2" '
         'marker-end="url(#ah)"/>')
s.append(f'<clipPath id="pc"><rect x="{px-95}" y="{py-70}" width="190" height="140" rx="16"/></clipPath>')
s.append(f'<image href="data:image/jpeg;base64,{pie}" x="{px-100}" y="{py-100}" width="200" height="200" '
         'preserveAspectRatio="xMidYMid slice" clip-path="url(#pc)"/>')
s.append(f'<rect x="{px-95}" y="{py-70}" width="190" height="140" rx="16" fill="none" stroke="#3aa63a" stroke-width="3"/>')
s.append(f'<text x="{px}" y="{py+100}" text-anchor="middle" font-weight="700" font-size="19" '
         'fill="#002e5d">Pumpkin Pie</text>')

# legend, drawn with the same element function at reduced size
s.append('<g transform="translate(250,418) scale(0.62)">')
for i, (kind, text) in enumerate([('in', 'input data'), ('tool', 'tool'), ('out', 'derived data')]):
    s.append(element(BW / 2 + i * 260, BH / 2, kind, text))
s.append('</g>')
s.append('</svg>')
Path('slides/week-02/images/mba-pie-recipe.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')
print('pie recipe svg written')
