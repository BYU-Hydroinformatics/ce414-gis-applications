"""Draw the two small DEM figures on the Week 2 Part A DEM slide:
mba-dem-grid.svg    - a 6 x 6 raster of elevation values (meters), and
mba-dem-columns.svg - the same 36 values as vertical columns in an oblique 3-D view.
The values are an illustrative smooth hill, not a real DEM."""
import math
from pathlib import Path

N = 6
Z = [[int(round(1200 + 68 * math.exp(-((x - 3.4) ** 2 + (y - 2.4) ** 2) / 4.5) + 6 * x - 3 * y))
      for x in range(N)] for y in range(N)]
zmin, zmax = min(map(min, Z)), max(map(max, Z))


def ramp(z):
    t = (z - zmin) / (zmax - zmin)
    a, b = (180, 215, 150), (150, 105, 60)          # low green to high brown
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def darker(hexcol, f):
    r, g, b = int(hexcol[1:3], 16), int(hexcol[3:5], 16), int(hexcol[5:7], 16)
    return '#%02x%02x%02x' % (int(r * f), int(g * f), int(b * f))


# --- figure 1: the grid of numbers
cw = 60
s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N*cw+4} {N*cw+4}" '
     'font-family="Segoe UI, Helvetica, Arial, sans-serif">']
for y in range(N):
    for x in range(N):
        s.append(f'<rect x="{2+x*cw}" y="{2+y*cw}" width="{cw}" height="{cw}" fill="{ramp(Z[y][x])}" '
                 'stroke="#222" stroke-width="2"/>')
        s.append(f'<text x="{2+x*cw+cw/2}" y="{2+y*cw+cw/2+6}" text-anchor="middle" font-size="17" '
                 f'font-weight="600" fill="#1a1a1a">{Z[y][x]}</text>')
s.append('</svg>')
Path('slides/week-02/images/mba-dem-grid.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')

# --- figure 2: oblique columns
W, H = 460, 360
cw = 48
dx, dy = 0.55 * cw, -0.36 * cw       # depth axis runs up and to the right
hs = 1.7                             # px per meter above zmin
base_x, base_y = 30, 330


def P(x, y, h):
    return (base_x + x * cw + y * dx, base_y + y * dy - h * hs)


def poly(pts, fill, sw=1.2):
    return '<polygon points="%s" fill="%s" stroke="#222" stroke-width="%s" stroke-linejoin="round"/>' % (
        ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts), fill, sw)


s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
     'font-family="Segoe UI, Helvetica, Arial, sans-serif">']
s.append(poly([P(0, 0, 0), P(N, 0, 0), P(N, N, 0), P(0, N, 0)], '#f3efe6'))
for d in range(N - 1, -1, -1):              # far rows first; depth d = N-1 maps to the grid's top row
    y = d
    gy = N - 1 - d                          # grid row shown at this depth
    for x in range(N - 1, -1, -1):          # right to left so each column's left face stays visible
        h = Z[gy][x] - zmin + 8             # keep the lowest cell a visible slab
        col = ramp(Z[gy][x])
        top = [P(x, y, h), P(x + 1, y, h), P(x + 1, y + 1, h), P(x, y + 1, h)]
        front = [P(x, y, 0), P(x + 1, y, 0), P(x + 1, y, h), P(x, y, h)]
        left = [P(x, y, 0), P(x, y, h), P(x, y + 1, h), P(x, y + 1, 0)]
        s.append(poly(left, darker(col, 0.72)))
        s.append(poly(front, darker(col, 0.88)))
        s.append(poly(top, col))
        fx, fy = P(x + 0.5, y + 0.5, h)
        s.append(f'<text x="{fx:.1f}" y="{fy+3.5:.1f}" text-anchor="middle" font-size="10" '
                 f'font-weight="600" fill="#111">{Z[gy][x]}</text>')
s.append('</svg>')
Path('slides/week-02/images/mba-dem-columns.svg').write_text('\n'.join(s), encoding='utf-8', newline='\n')
print('grid values', zmin, zmax)
