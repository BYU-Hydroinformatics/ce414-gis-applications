"""Draw slides/week-02/images/mbb-cookie-model.svg: the tidy cookie model for Week 2 Part B in the
same ArcGIS Pro 3.7 ModelBuilder element style as the Part A pie recipe (tools/week02_pie_recipe.py):
input data is a rounded rectangle with a blue outline and a light-blue icon panel, a tool is a
square-cornered box with a yellow hammer panel, derived data is a rounded rectangle with a green
outline and a green icon panel. Five ingredients feed Mix; Mix makes dough; Bake (with its
settings shown as a tool parameter) makes cookies. Run with any Python 3.

    python tools/week02_cookie_model.py
"""
from pathlib import Path

IN, TOOL, OUT = 'in', 'tool', 'out'
STYLE = {'in': ('#bfe4fb', '#1a7bd3', '#ffffff'), 'tool': ('#fff2b3', '#e0c200', '#ffffff'), 'out': ('#b9e8b9', '#3aa63a', '#ffffff')}
W, H = 1100, 400
BW, BH, PW = 148, 44, 34
nodes = {}


def add(name, x, y, kind, label=None):
    nodes[name] = (x, y, kind, label or name)


add('flour', 95, 50, IN)
add('sugar', 95, 110, IN)
add('eggs', 95, 170, IN)
add('butter', 95, 230, IN)
add('chocolate chips', 95, 290, IN)
add('mix', 330, 170, TOOL, 'Mix')
add('dough', 530, 170, OUT)
add('bake', 730, 170, TOOL, 'Bake')
add('cookies', 940, 170, OUT)
add('oven', 730, 60, IN, '350 °F, 11 minutes')
edges = [('flour', 'mix'), ('sugar', 'mix'), ('eggs', 'mix'), ('butter', 'mix'), ('chocolate chips', 'mix'),
         ('mix', 'dough'), ('dough', 'bake'), ('bake', 'cookies')]

s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16">',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
     '<path d="M0 0 L10 5 L0 10 z" fill="#444"/></marker></defs>']


def edge(a, b):
    x1, y1 = nodes[a][0] + BW / 2, nodes[a][1]
    x2, y2 = nodes[b][0] - BW / 2 - 2, nodes[b][1]
    c = (x2 - x1) * 0.5
    return f'<path d="M{x1},{y1} C{x1+c},{y1} {x2-c},{y2} {x2},{y2}" fill="none" stroke="#444" stroke-width="2.2" marker-end="url(#ah)"/>'


for a, b in edges:
    s.append(edge(a, b))
# the oven setting drops straight down into Bake
ox, oy = nodes['oven'][0], nodes['oven'][1]
s.append(f'<path d="M{ox},{oy + BH/2} L{ox},{nodes["bake"][1] - BH/2 - 2}" fill="none" stroke="#444" stroke-width="2.2" marker-end="url(#ah)"/>')

ICONS = {
    'tool': lambda cx, cy: (f'<path d="M{cx-9},{cy-9} l7,7 M{cx-2},{cy-2} l-8,8 l4,4 l8,-8 M{cx-11},{cy-7} l4,-4 l8,8 l-4,4 z" '
                            'fill="none" stroke="#8a6d1a" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>'),
    'in':   lambda cx, cy: (f'<path d="M{cx-11},{cy-6} l16,-5 l6,17 l-16,5 z" fill="#f2d96b" stroke="#8a6d1a" stroke-width="1.5"/>'
                            f'<circle cx="{cx-6}" cy="{cy-9}" r="3.5" fill="#f5a623"/>'),
    'out':  lambda cx, cy: (f'<rect x="{cx-11}" y="{cy-9}" width="22" height="18" rx="2" fill="#fff" stroke="#555" stroke-width="1.5"/>'
                            f'<path d="M{cx-11},{cy+2} q6,-10 12,-2 t10,-4" fill="none" stroke="#555" stroke-width="1.5"/>'),
    'value': lambda cx, cy: (f'<rect x="{cx-11}" y="{cy-8}" width="22" height="16" rx="2" fill="#fff" stroke="#555" stroke-width="1.5"/>'
                             f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="9" fill="#555">0.01</text>'),
}


def element(x, y, kind, label, icon=None, width=BW):
    panel, outline, body = STYLE[kind]
    rx = 3 if kind == 'tool' else 14
    left, top = x - width / 2, y - BH / 2
    cid = f"clip-{int(x)}-{int(y)}"
    fs = 14 if len(label) <= 16 else 12
    return '\n'.join([
        f'<clipPath id="{cid}"><rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}"/></clipPath>',
        f'<rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}" fill="{body}"/>',
        f'<rect x="{left}" y="{top}" width="{PW}" height="{BH}" fill="{panel}" clip-path="url(#{cid})"/>',
        ICONS[icon or kind](left + PW / 2, y),
        f'<rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}" fill="none" stroke="{outline}" stroke-width="1.8"/>',
        f'<text x="{left + PW + (width - PW) / 2}" y="{y + 5}" text-anchor="middle" fill="#111" font-size="{fs}">{label}</text>'])


for name, (x, y, kind, label) in nodes.items():
    if name == 'oven':
        s.append(element(x, y, kind, label, icon='value', width=170))
    elif name == 'cookies':
        s.append(element(x, y, kind, label, width=170))
    else:
        s.append(element(x, y, kind, label))

# a P marker on the oven setting: the thing Lab 1 Step 10 turns into a parameter
s.append(f'<circle cx="{ox + 85 - 4}" cy="{oy - BH/2 + 2}" r="11" fill="#fff" stroke="#666" stroke-width="1.5"/>')
s.append(f'<text x="{ox + 85 - 4}" y="{oy - BH/2 + 7}" text-anchor="middle" font-size="13" font-weight="700" fill="#333">P</text>')

# legend
s.append('<g transform="translate(250,352) scale(0.62)">')
for i, (kind, txt) in enumerate([('in', 'input data'), ('tool', 'tool'), ('out', 'derived data')]):
    s.append(element(BW / 2 + i * 260, BH / 2, kind, txt))
s.append('</g>')
s.append('</svg>')
Path('slides/week-02/images/mbb-cookie-model.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')
print('cookie model svg written')
