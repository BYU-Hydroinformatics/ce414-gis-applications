"""Figures for slides/week-05/elevation-data-lidar.md (the LiDAR half of the Week 5 Tuesday deck).

    python tools/week05_lidar_figures.py frames <path-to-video.mp4>   # NEON video stills
    python tools/week05_lidar_figures.py closeup                      # point-cloud close-up
    python tools/week05_lidar_figures.py returns                      # multiple-returns diagram
    python tools/week05_lidar_figures.py all <path-to-video.mp4>

Outputs (slides/week-05/images/):
  ed-lidar-video-frame-1..3.jpg  stills from NEON Science, "How Does LiDAR Remote Sensing Work? Light
                                 Detection and Ranging" (youtube.com/watch?v=EYbhNSUnIdU). Download the
                                 720p stream with yt-dlp (format 136) into a scratch folder, never into
                                 the repo.
  ed-point-cloud-closeup.png     illustration of what a point cloud is made of: irregularly spaced
                                 simulated returns on a real 1 m USGS 3DEP surface near Mount Rushmore,
                                 three of them labeled with their (x, y, z). Meant to sit beside
                                 ed-lidar-mount-rushmore.jpg, whose points are about one pixel each and
                                 do not survive magnification.
  ed-lidar-multiple-returns.png  schematic: one pulse, several returns (with the return waveform), and
                                 classify -> drop non-ground -> bare earth on a profile. Synthetic geometry.

Needs numpy, matplotlib, pillow, requests, tifffile, pyproj and imageio-ffmpeg.
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'slides' / 'week-05' / 'images'

plt.rcParams.update({'font.family': ['Segoe UI', 'Arial', 'DejaVu Sans'], 'font.size': 16})

INK = '#222222'
MUTED = '#666666'
LASER = '#d62728'
GROUND = '#8c5a2b'
VEG = '#2e8b3a'
BLDG = '#6b7280'
SKY = '#eef6fc'

# ---------------------------------------------------------------- 1. video frames
FRAMES = [  # (seconds, what it shows)
    (339.0, 'pulse down, range subtracted from altitude gives elevation at an x, y'),
    (401.0, 'one pulse, several returns: 1st to 4th, with the return waveform'),
    (405.5, 'the returns from that tree as a point cloud'),
]


def video_frames(video):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    for i, (t, _) in enumerate(FRAMES, 1):
        out = OUT / f'ed-lidar-video-frame-{i}.jpg'
        subprocess.run([ff, '-loglevel', 'error', '-y', '-ss', f'{t}', '-i', str(video), '-frames:v', '1',
                        '-q:v', '2', str(out)], check=True)
        print('wrote', out)


# ---------------------------------------------------------------- 2. point-cloud close-up
DEM_URL = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
# Patch center in NAD83 / UTM zone 13N (EPSG:26913): a rugged 20 m square of granite on the summit
# ridge (chosen as the roughest window with 10-16 m of relief in a 400 m square around the faces).
PATCH_X, PATCH_Y, PATCH = 623781.0, 4859689.0, 20.0


def fetch_patch():
    import requests
    import tifffile
    h = PATCH / 2 + 1
    n = int(2 * h)  # 1 m cells
    p = dict(bbox=f'{PATCH_X - h},{PATCH_Y - h},{PATCH_X + h},{PATCH_Y + h}', bboxSR=26913, imageSR=26913,
             size=f'{n},{n}', format='tiff', pixelType='F32', interpolation='RSP_BilinearInterpolation', f='image')
    r = requests.get(DEM_URL, params=p, timeout=60)
    r.raise_for_status()
    z = tifffile.imread(io.BytesIO(r.content)).astype(float)
    return z, h


def bilinear(z, h, x, y):
    """x, y in metres from patch centre; z row 0 is north."""
    n = z.shape[0]
    c = (x + h) * (n - 1) / (2 * h)
    r = (h - y) * (n - 1) / (2 * h)
    c0 = np.clip(np.floor(c).astype(int), 0, n - 2)
    r0 = np.clip(np.floor(r).astype(int), 0, n - 2)
    fc, fr = c - c0, r - r0
    return (z[r0, c0] * (1 - fc) * (1 - fr) + z[r0, c0 + 1] * fc * (1 - fr)
            + z[r0 + 1, c0] * (1 - fc) * fr + z[r0 + 1, c0 + 1] * fc * fr)


def closeup():
    z, h = fetch_patch()
    rng = np.random.default_rng(414)
    # Lidar-like sampling: scan lines roughly 0.6 m apart, points jittered along and across them.
    xs, ys = [], []
    for yl in np.arange(-PATCH / 2, PATCH / 2, 0.8):
        k = rng.integers(20, 27)
        xl = np.sort(rng.uniform(-PATCH / 2, PATCH / 2, k))
        xs.append(xl)
        ys.append(yl + rng.normal(0, 0.18, k) + 0.04 * xl)
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    keep = (np.abs(y) <= PATCH / 2)
    x, y = x[keep], y[keep]
    zz = bilinear(z, h, x, y) + rng.normal(0, 0.05, x.size)

    fig = plt.figure(figsize=(7.2, 8.0), dpi=100)
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([-0.02, 0.10, 1.04, 0.80], projection='3d')
    ax.set_proj_type('persp', focal_length=0.9)
    zmin = zz.min()
    zr = zz - zmin
    col = plt.get_cmap('copper')(zr / zr.max() * 0.85 + 0.1)
    ax.scatter(x, y, zr, c=col, s=18, depthshade=False, edgecolors='#3b2a1a', linewidths=0.3)
    ax.view_init(elev=24, azim=-58)
    ax.set_xlim(-PATCH / 2, PATCH / 2); ax.set_ylim(-PATCH / 2, PATCH / 2); ax.set_zlim(0, zr.max())
    ax.set_box_aspect((1, 1, zr.max() / PATCH))  # true scale: 1 m up = 1 m across
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    for a in (ax.xaxis, ax.yaxis, ax.zaxis):
        a.pane.set_facecolor((0.96, 0.96, 0.96, 1)); a.pane.set_edgecolor('#cccccc')
    ax.set_xlabel(f'x (east), {PATCH:.0f} m', labelpad=-12, fontsize=14, color=MUTED)
    ax.set_ylabel(f'y (north), {PATCH:.0f} m', labelpad=-12, fontsize=14, color=MUTED)
    ax.set_zlabel(f'z, {zr.max():.0f} m', labelpad=-14, fontsize=14, color=MUTED)

    # Label three points spread across the patch: the highest, one near the front-left corner and a
    # low one toward the front-right. Each label goes to the slot that keeps its leader line short and uncrossed.
    from itertools import permutations
    from mpl_toolkits.mplot3d import proj3d
    picks = [int(np.argmax(zz)),
             int(np.argmin(np.hypot(x + 6, y + 6))),
             int(np.argmin(zz + 0.3 * np.hypot(x - 8, y + 8)))]
    fig.canvas.draw()
    pts = []
    for p in picks:
        X, Y, _ = proj3d.proj_transform(x[p], y[p], zr[p], ax.get_proj())
        pts.append(fig.transFigure.inverted().transform(ax.transData.transform((X, Y))))
    slots = [(0.03, 0.905, 'top'), (0.66, 0.905, 'top'), (0.36, 0.105, 'bottom')]  # left x, y, va
    anchors = [(0.16, 0.80), (0.79, 0.80), (0.49, 0.21)]  # where each slot's leader leaves the box
    best = min(permutations(range(3)), key=lambda perm: sum(
        np.hypot(pts[i][0] - anchors[perm[i]][0], pts[i][1] - anchors[perm[i]][1]) for i in range(3)))
    for i, p in enumerate(picks):
        fx, fy, va = slots[best[i]]
        ax.scatter([x[p]], [y[p]], [zr[p]], s=110, c=LASER, edgecolors='white', linewidths=1.5,
                   depthshade=False, zorder=10)
        label = f'x = {PATCH_X + x[p]:,.2f}\ny = {PATCH_Y + y[p]:,.2f}\nz = {zz[p]:,.2f}'
        fig.text(fx, fy, label, fontsize=13, family='Consolas', color=INK, va=va,
                 bbox=dict(boxstyle='round,pad=0.35', fc='white', ec=LASER, lw=1.5), zorder=20)
        fig.add_artist(FancyArrowPatch(anchors[best[i]], tuple(pts[i]), transform=fig.transFigure,
                                       arrowstyle='-', color=LASER, lw=1.4, zorder=15))
    fig.text(0.5, 0.985, f'Zoom in: {len(x)} points, one per laser return', ha='center', va='top',
             fontsize=19, weight='bold', color=INK)
    fig.text(0.5, 0.012, 'Illustration: simulated returns on real USGS 3DEP 1 m elevation,\n'
             f'a {PATCH:.0f} m × {PATCH:.0f} m patch of the Mount Rushmore summit ridge. '
             'Coordinates in meters,\nNAD83 / UTM zone 13N; z is elevation above sea level.',
             ha='center', va='bottom', fontsize=11.5, color=MUTED, linespacing=1.3)
    out = OUT / 'ed-point-cloud-closeup.png'
    fig.savefig(out, dpi=100, facecolor='white')
    plt.close(fig)
    print('wrote', out)


# ---------------------------------------------------------------- 3. multiple returns
def airplane(ax, cx, cy, s=1.0):
    """Side-view light aircraft, nose to the right."""
    body = Ellipse((cx, cy), 20 * s, 3.6 * s, fc='#f4f4f4', ec='#555', lw=1.5, zorder=5)
    tail = Polygon([(cx - 9 * s, cy + 0.6 * s), (cx - 12 * s, cy + 5 * s), (cx - 9.6 * s, cy + 5 * s),
                    (cx - 6 * s, cy + 1.2 * s)], closed=True, fc='#f4f4f4', ec='#555', lw=1.5, zorder=4)
    wing = Polygon([(cx - 3 * s, cy + 0.3 * s), (cx + 4 * s, cy + 0.3 * s), (cx + 3 * s, cy - 0.6 * s),
                    (cx - 2.5 * s, cy - 0.6 * s)], closed=True, fc='#c9ced6', ec='#555', lw=1.2, zorder=6)
    stripe = Rectangle((cx - 8 * s, cy - 0.35 * s), 15 * s, 0.7 * s, fc=LASER, ec='none', zorder=6, alpha=.8)
    window = Ellipse((cx + 6.5 * s, cy + 0.7 * s), 3 * s, 1.3 * s, fc='#8fc1e8', ec='#555', lw=1, zorder=6)
    pod = Rectangle((cx - 1 * s, cy - 2.6 * s), 2 * s, 1.2 * s, fc='#333', ec='#333', zorder=6)
    for a in (tail, body, wing, stripe, window, pod):
        ax.add_patch(a)


def tree(ax, x0, g):
    ax.add_patch(Polygon([(x0 - 1.1, g), (x0 + 1.1, g), (x0 + 0.6, g + 24), (x0 - 0.6, g + 24)],
                         closed=True, fc='#6b4a2b', ec='none', zorder=2))
    ax.plot([x0, x0 + 6], [g + 14, g + 20], color='#6b4a2b', lw=4, zorder=2, solid_capstyle='round')
    ax.plot([x0, x0 - 5], [g + 11, g + 16], color='#6b4a2b', lw=4, zorder=2, solid_capstyle='round')
    for (dx, dy, w, hh, c) in [(0, 33, 22, 16, '#3f8f47'), (-6, 27, 13, 10, '#4c9e53'),
                               (7, 26, 12, 10, '#4c9e53'), (0, 24, 12, 8, '#5aab60')]:
        ax.add_patch(Ellipse((x0 + dx, g + dy), w, hh, fc=c, ec='#2f6f36', lw=1, zorder=3, alpha=.95))


def returns_panel(ax):
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    ax.add_patch(Rectangle((0, 8), 100, 92, fc=SKY, ec='none', zorder=0))
    g = 10
    ax.add_patch(Rectangle((0, 0), 100, g, fc='#a47148', ec='none', zorder=1))
    ax.plot([0, 100], [g, g], color='#6b4a2b', lw=2, zorder=1)
    tx = 30
    tree(ax, tx, g)
    ax.add_patch(Ellipse((tx - 16, g + 3), 7, 6, fc='#6fbf73', ec='#2f6f36', lw=1, zorder=3))  # shrub

    px, py = tx, 89
    airplane(ax, px - 2, py, 1.0)
    # pulse footprint: a narrow cone from the sensor to the ground
    ax.add_patch(Polygon([(px - 0.3, py - 2.6), (px + 0.3, py - 2.6), (px + 2.2, g), (px - 2.2, g)],
                         closed=True, fc=LASER, ec='none', alpha=.18, zorder=4))
    ax.plot([px, px], [py - 2.6, g], color=LASER, lw=2.2, zorder=4)
    ax.annotate('', xy=(px, py - 16), xytext=(px, py - 6),
                arrowprops=dict(arrowstyle='-|>', color=LASER, lw=2.4, mutation_scale=22), zorder=7)
    ax.text(px + 3.5, py - 10, 'laser pulse', color=LASER, fontsize=16, weight='bold', va='center')

    for yh in (g + 40.5, g + 30.5, g + 20.0, g):  # treetop, two branches, ground
        ax.plot(px, yh, 'o', ms=13, mfc='white', mec=LASER, mew=3, zorder=8)

    # waveform: returned energy against time (height), peaks at each hit
    wx0, wx1 = 58, 97
    ax.plot([wx0, wx0], [g - 2, 80], color=INK, lw=1.8, zorder=5)
    ax.annotate('', xy=(wx0 - 2.4, 56), xytext=(wx0 - 2.4, 76),
                arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=1.6, mutation_scale=16))
    ax.text(wx0 - 4.6, 66, 'later', rotation=90, ha='center', va='center', fontsize=13, color=MUTED)
    yy = np.linspace(g - 2, 78, 600)
    amp = [(g + 40.5, 16, 1.4), (g + 30.5, 8, 1.3), (g + 20.0, 6, 1.3), (g, 28, 1.1)]
    e = sum(a * np.exp(-0.5 * ((yy - m) / sd) ** 2) for m, a, sd in amp) + 0.4
    ax.fill_betweenx(yy, wx0, wx0 + e, color=LASER, alpha=.15, zorder=5)
    ax.plot(wx0 + e, yy, color=LASER, lw=2.4, zorder=6)
    ax.text((wx0 + wx1) / 2 + 2, 84, 'returned energy', ha='center', fontsize=14, color=INK, weight='bold')
    ax.text((wx0 + wx1) / 2 + 2, 80.5, '(the return waveform)', ha='center', fontsize=12.5, color=MUTED)
    for (m, a, _) in amp:
        ax.plot([px + 1.5, wx0 + a + 0.4], [m, m], ls=(0, (4, 3)), color='#888', lw=1.2, zorder=4)
    ax.text(wx0 + 17.5, g + 40.5, 'first return\n(treetop)', va='center', fontsize=15, weight='bold', color=INK)
    ax.text(wx0 + 10.5, g + 25.5, 'intermediate returns\n(branches)', va='center', fontsize=15, color=INK)
    ax.plot([wx0 + 9.5, wx0 + 9.5], [g + 20, g + 30.5], color=INK, lw=1.3)
    ax.text(wx0 + 29.5, g + 3.5, 'last return\n= ground', va='bottom', fontsize=15, weight='bold', color=GROUND)
    ax.text(50, 96.5, 'One pulse, several returns', ha='center', fontsize=21, weight='bold', color=INK)


def profile_data():
    rng = np.random.default_rng(5)
    xg = np.sort(rng.uniform(0, 100, 150))
    terrain = lambda x: 20 + 9 * np.sin(x / 17) + 4 * np.sin(x / 6.5 + 1) + 0.08 * x
    zg = terrain(xg) + rng.normal(0, 0.35, xg.size)
    veg_x, veg_z = [], []
    for cx, w, ht in [(14, 9, 17), (27, 7, 13), (58, 10, 19), (70, 8, 15), (90, 7, 12)]:
        n = int(w * 3.5)
        vx = rng.uniform(cx - w / 2, cx + w / 2, n)
        prof = np.sqrt(np.clip(1 - ((vx - cx) / (w / 2)) ** 2, 0, 1))
        vz = terrain(vx) + ht * (0.35 + 0.65 * prof * rng.uniform(0.55, 1.0, n))
        veg_x += list(vx); veg_z += list(vz)
    bx = rng.uniform(38, 48, 22)
    bz = terrain(np.full_like(bx, 43)) + 9 + rng.normal(0, 0.15, bx.size)
    # buildings and dense canopy hide the ground under them
    hide = ((xg > 37.5) & (xg < 48.5)) | (rng.random(xg.size) < 0.25) & (np.isin(np.round(xg / 10), [1, 6, 7]))
    return (xg[~hide], zg[~hide]), (np.array(veg_x), np.array(veg_z)), (bx, bz), terrain


def classify_panel(ax_top, ax_bot):
    (gx, gz), (vx, vz), (bx, bz), terrain = profile_data()
    for ax in (ax_top, ax_bot):
        ax.set_xlim(-1, 101); ax.set_ylim(5, 52)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color('#bbbbbb')
        ax.set_facecolor('#fbfbfb')
    ax_top.scatter(vx, vz, s=34, c=VEG, edgecolors='white', linewidths=0.5, label='vegetation', zorder=3)
    ax_top.scatter(bx, bz, s=44, c=BLDG, marker='s', edgecolors='white', linewidths=0.5, label='building', zorder=3)
    ax_top.scatter(gx, gz, s=34, c=GROUND, edgecolors='white', linewidths=0.5, label='ground', zorder=3)
    ax_top.legend(loc='upper left', ncol=3, fontsize=13.5, frameon=False, handletextpad=0.2, columnspacing=1.0,
                  bbox_to_anchor=(0.0, 1.02))
    ax_top.set_title('1   Classify every point', loc='left', fontsize=17, weight='bold', color=INK, pad=6)

    order = np.argsort(gx)
    ax_bot.fill_between(gx[order], 5, gz[order], color='#d8b98f', alpha=.55, zorder=1)
    ax_bot.plot(gx[order], gz[order], color=GROUND, lw=2.4, zorder=2)
    ax_bot.scatter(gx, gz, s=34, c=GROUND, edgecolors='white', linewidths=0.5, zorder=3)
    ax_bot.set_title('2   Drop non-ground points, connect the rest', loc='left', fontsize=17, weight='bold',
                     color=INK, pad=6)
    ax_bot.text(99, 9, 'bare-earth surface (DTM)', ha='right', fontsize=15, weight='bold', color='#5c3a1a')
    ax_bot.annotate('no ground points under the building:\nthe surface is interpolated across',
                    xy=(43, terrain(43) + 1.2), xytext=(2, 49), fontsize=13, color=MUTED, ha='left', va='top',
                    arrowprops=dict(arrowstyle='->', color=MUTED, lw=1.3))


def multiple_returns():
    fig = plt.figure(figsize=(14, 8), dpi=100)
    fig.patch.set_facecolor('white')
    returns_panel(fig.add_axes([0.01, 0.02, 0.50, 0.96]))
    fig.text(0.765, 0.955, 'From point cloud to bare earth', ha='center', va='top', fontsize=21,
             weight='bold', color=INK)
    top = fig.add_axes([0.54, 0.50, 0.44, 0.34])
    bot = fig.add_axes([0.54, 0.05, 0.44, 0.34])
    classify_panel(top, bot)
    fig.add_artist(FancyArrowPatch((0.76, 0.475), (0.76, 0.43), transform=fig.transFigure,
                                   arrowstyle='-|>', mutation_scale=26, color=INK, lw=2.5))
    out = OUT / 'ed-lidar-multiple-returns.png'
    fig.savefig(out, dpi=100, facecolor='white')
    plt.close(fig)
    print('wrote', out)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('frames', 'all') and len(sys.argv) > 2:
        video_frames(Path(sys.argv[2]))
    if what in ('closeup', 'all'):
        closeup()
    if what in ('returns', 'all'):
        multiple_returns()
