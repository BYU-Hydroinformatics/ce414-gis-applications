"""Draw slides/week-02/images/mba-environment-settings.svg for the Week 2 Part A environments
slide: a small model chain sitting inside a shaded "environment" panel, with the background
settings every tool reads shown as labelled chips around it."""
from pathlib import Path

NAVY, ORANGE, INK, MUTED = '#002e5d', '#e8792b', '#22262e', '#5a6472'
W, H = 760, 430
BW, BH, PW = 118, 40, 30
STYLE = {'in': ('#bfe4fb', '#1a7bd3'), 'tool': ('#fff2b3', '#e0c200'), 'out': ('#b9e8b9', '#3aa63a')}
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0 0 L10 5 L0 10 z" fill="#444"/></marker></defs>']

# the environment panel
s.append(f'<rect x="14" y="44" width="{W-28}" height="{H-58}" rx="18" fill="#eef3f9" stroke="{NAVY}" stroke-width="2" stroke-dasharray="9,6"/>')
s.append(f'<text x="{W/2}" y="30" text-anchor="middle" font-size="19" font-weight="700" fill="{NAVY}">The model\'s environment: settings saved in the background</text>')
s.append(f'<text x="{W/2}" y="74" text-anchor="middle" font-size="13.5" fill="{MUTED}">Every tool in the model reads these unless it overrides them</text>')


def element(x, y, kind, label):
    panel, outline = STYLE[kind]
    rx = 3 if kind == 'tool' else 13
    left, top = x - BW / 2, y - BH / 2
    return (f'<clipPath id="c{int(x)}"><rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}"/></clipPath>'
            f'<rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}" fill="#fff"/>'
            f'<rect x="{left}" y="{top}" width="{PW}" height="{BH}" fill="{panel}" clip-path="url(#c{int(x)})"/>'
            f'<rect x="{left}" y="{top}" width="{BW}" height="{BH}" rx="{rx}" fill="none" stroke="{outline}" stroke-width="1.6"/>'
            f'<text x="{left + PW + (BW-PW)/2}" y="{y+5}" text-anchor="middle" font-size="13" fill="{INK}">{label}</text>')


cy = 215
chain = [(150, 'in', 'input data'), (300, 'tool', 'tool'), (450, 'out', 'derived data'), (600, 'tool', 'tool')]
for i in range(len(chain) - 1):
    x1 = chain[i][0] + BW / 2; x2 = chain[i + 1][0] - BW / 2 - 2
    s.append(f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="#444" stroke-width="2" marker-end="url(#ah)"/>')
for x, kind, label in chain:
    s.append(element(x, cy, kind, label))

# setting chips: (x, y, title, meaning)
chips = [
    (40, 100, 'Current workspace', 'which geodatabase the outputs go to'),
    (400, 100, 'Scratch workspace', 'where temporary files live'),
    (40, 290, 'Output coordinate system', 'which projection every result gets'),
    (400, 290, 'Processing extent', 'how much of the map the tools work on'),
    (40, 350, 'Cell size', 'the resolution of raster outputs'),
    (400, 350, '…and many more', 'most of them you will never touch'),
]
for x, y, title, meaning in chips:
    s.append(f'<rect x="{x}" y="{y}" width="320" height="46" rx="8" fill="#fff" stroke="{NAVY}" stroke-width="1.4"/>')
    s.append(f'<rect x="{x}" y="{y}" width="8" height="46" rx="3" fill="{ORANGE}"/>')
    s.append(f'<text x="{x+20}" y="{y+19}" font-size="13.5" font-weight="700" fill="{NAVY}">{title}</text>')
    s.append(f'<text x="{x+20}" y="{y+37}" font-size="12.5" fill="{MUTED}">{meaning}</text>')
# faint connectors from the chain down to the settings rows
for x in (300, 600):
    s.append(f'<line x1="{x}" y1="{cy+BH/2}" x2="{x}" y2="{cy+BH/2+30}" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="4,4"/>')
for x in (300, 600):
    s.append(f'<line x1="{x}" y1="{cy-BH/2}" x2="{x}" y2="{cy-BH/2-64}" stroke="{ORANGE}" stroke-width="2" stroke-dasharray="4,4"/>')
s.append('</svg>')
Path('slides/week-02/images/mba-environment-settings.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')
print('environment figure written')
