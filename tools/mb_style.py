"""Shared drawing code for figures in the ArcGIS Pro 3.7 ModelBuilder element style (verified against
the Pro 3.7.1 capture slides/week-02/images/mba-cities-rivers-model-pro.png): input data is a rounded
rectangle with a blue outline and a light-blue icon panel, a tool is a square-cornered box with a
yellow hammer panel, derived data is a rounded rectangle with a green outline and a green icon panel,
a value variable is an input-style element with a "0.01" icon. Connectors are gray curves with an
arrowhead. Used by tools/week02_three_ways.py; the pie and cookie scripts predate it and carry their
own copy of the same code."""

STYLE = {'in': ('#bfe4fb', '#1a7bd3', '#ffffff'), 'tool': ('#fff2b3', '#e0c200', '#ffffff'), 'out': ('#b9e8b9', '#3aa63a', '#ffffff')}
BW, BH, PW = 148, 44, 34

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


class Model:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.nodes = {}     # name: (x, y, kind, label, width, icon)
        self.edges = []     # (a, b, vertical)
        self.extra = []

    def add(self, name, x, y, kind, label=None, width=BW, icon=None):
        self.nodes[name] = (x, y, kind, label or name, width, icon or kind)

    def link(self, a, b, vertical=False):
        self.edges.append((a, b, vertical))

    def p_marker(self, name):
        x, y, _, _, w, _ = self.nodes[name]
        cx, cy = x + w / 2 - 4, y - BH / 2 + 2
        self.extra.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#fff" stroke="#666" stroke-width="1.5"/>'
                          f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#333">P</text>')

    def _edge(self, a, b, vertical):
        ax, ay, _, _, aw, _ = self.nodes[a]
        bx, by, _, _, bw, _ = self.nodes[b]
        if vertical:
            return (f'<path d="M{ax},{ay + BH/2} L{bx},{by - BH/2 - 2}" fill="none" stroke="#444" stroke-width="2.2" marker-end="url(#ah)"/>')
        x1, y1 = ax + aw / 2, ay
        x2, y2 = bx - bw / 2 - 2, by
        c = (x2 - x1) * 0.5
        return f'<path d="M{x1},{y1} C{x1+c},{y1} {x2-c},{y2} {x2},{y2}" fill="none" stroke="#444" stroke-width="2.2" marker-end="url(#ah)"/>'

    def _element(self, x, y, kind, label, width, icon):
        panel, outline, body = STYLE[kind]
        rx = 3 if kind == 'tool' else 14
        left, top = x - width / 2, y - BH / 2
        cid = f"clip-{int(x)}-{int(y)}"
        fs = 14 if len(label) <= 16 else 12
        return '\n'.join([
            f'<clipPath id="{cid}"><rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}"/></clipPath>',
            f'<rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}" fill="{body}"/>',
            f'<rect x="{left}" y="{top}" width="{PW}" height="{BH}" fill="{panel}" clip-path="url(#{cid})"/>',
            ICONS[icon](left + PW / 2, y),
            f'<rect x="{left}" y="{top}" width="{width}" height="{BH}" rx="{rx}" fill="none" stroke="{outline}" stroke-width="1.8"/>',
            f'<text x="{left + PW + (width - PW) / 2}" y="{y + 5}" text-anchor="middle" fill="#111" font-size="{fs}">{label}</text>'])

    def svg(self):
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="16">',
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
             '<path d="M0 0 L10 5 L0 10 z" fill="#444"/></marker></defs>']
        s += [self._edge(a, b, v) for a, b, v in self.edges]
        s += [self._element(*self.nodes[n]) for n in self.nodes]
        s += self.extra
        s.append('</svg>')
        return '\n'.join(s)

    def write(self, path):
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(self.svg())
        print(path)
