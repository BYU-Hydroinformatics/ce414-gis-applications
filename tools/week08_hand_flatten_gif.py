"""Week 8 Tuesday: the HAND idea as a stepped animation. A synthetic valley (a sloping river with
banks and terraces) is drawn in 3-D; frame by frame the river is pulled down to zero and the land
goes with it, so every point ends up at its height above the river; then a flat water surface rises
through the flattened valley and wets everything below it, the way a bathtub would.

Nothing here is measured: the surface is an equation, and the slide says so.

    python tools/week08_hand_flatten_gif.py   -> slides/week-08/images/fl-hand-flatten.gif (+ -still.png)
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from PIL import Image

IMG = pathlib.Path(__file__).resolve().parent.parent / "slides" / "week-08" / "images"
plt.rcParams.update({"font.family": "Segoe UI", "font.size": 12})

# the valley: x runs downstream (0 to 10 km), y across the valley (-2 to 2 km)
x = np.linspace(0, 10, 120)
y = np.linspace(-2, 2, 90)
X, Y = np.meshgrid(x, y)
bed = 60 - 4.5 * X                               # the river falls 45 m along the reach
rng = np.random.default_rng(7)
meander = 0.35 * np.sin(X * 1.1) + 0.15 * np.sin(X * 2.7 + 1)
d = np.abs(Y - meander)                          # distance from the river line, km
cross = 3.0 * d + 18 * (d / 2.0) ** 2            # a gentle floodplain, then rising valley sides
terrace = 2.5 * (d > 0.55) * (1 - np.exp(-(d - 0.55) * 6))   # a low terrace step
Z = bed + cross + terrace
Z += 0.6 * np.sin(Y * 9) * np.exp(-d * 2)        # some roughness on the floodplain
river = d < 0.08
HAND = Z - bed                                   # in this valley every point drains straight across to the river
HAND[river] = 0
H = 3.0                                          # the flood depth, m
WATER_BLUE = (0.20, 0.52, 0.86, 0.95)


def frame(t, water=None, title="", note=""):
    """t in [0,1]: how far the river has been pulled down. water: level in m, or None."""
    Zt = Z - t * bed
    Zt[river] = (1 - t) * bed[river]
    fig = plt.figure(figsize=(8, 5.2), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    ls = LightSource(azdeg=315, altdeg=50)
    base = np.array([0.86, 0.80, 0.66])
    shade = ls.hillshade(Zt, vert_exag=0.03, dx=x[1] - x[0], dy=y[1] - y[0])
    colors = np.ones(Zt.shape + (4,))
    colors[..., :3] = base * shade[..., None] * 1.15
    colors[..., :3] = np.clip(colors[..., :3], 0, 1)
    colors[river] = (0.1, 0.35, 0.8, 1)
    if water is not None:
        wet = Zt <= water
        colors[wet] = WATER_BLUE
    ax.plot_surface(X, Y, Zt, facecolors=colors, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    ax.set_zlim(-5, 80)
    ax.set_xlim(0, 10); ax.set_ylim(-2, 2)
    ax.view_init(elev=32, azim=-128)
    ax.set_xlabel("downstream (km)", labelpad=6); ax.set_ylabel("across (km)", labelpad=4)
    ax.set_zlabel("elevation (m)" if t < 1 else "height above river (m)", labelpad=4)
    ax.set_box_aspect((2.4, 1.1, 0.9))
    ax.set_title(title, loc="left", fontsize=14, color="#002e5d", pad=6)
    if note:
        fig.text(0.02, 0.03, note, fontsize=10.5, color="#4a5568")
    fig.tight_layout()
    fig.canvas.draw()
    im = Image.frombuffer("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba(), "raw", "RGBA", 0, 1).convert("RGB")
    plt.close(fig)
    return im


frames, durations = [], []
def add(im, ms):
    frames.append(im); durations.append(ms)

add(frame(0, title="1. The valley as the DEM sees it", note="A synthetic valley: the river falls 45 m down the reach. Elevation above sea level."), 1800)
for t in np.linspace(0, 1, 13)[1:]:
    add(frame(t, title="2. Pull the river down to zero, and the land with it",
              note="Every cell drops by the elevation of the river cell it drains to."), 110)
add(frame(1, title="3. HAND: every cell's height above its river", note="The river is flat at zero. The land keeps its height above the river."), 1800)
for w in np.linspace(0, H, 9)[1:]:
    add(frame(1, water=w, title=f"4. Fill it like a bathtub, to h = {w:.1f} m", note="One depth, applied to the flattened valley, floods the whole river at once."), 160)
add(frame(1, water=H, title=f"4. Fill it like a bathtub, to h = {H:.1f} m", note="One depth, applied to the flattened valley, floods the whole river at once."), 2600)

frames[0].save(IMG / "fl-hand-flatten.gif", save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
frames[-1].save(IMG / "fl-hand-flatten-still.png")
print("fl-hand-flatten.gif", len(frames), "frames;", (IMG / "fl-hand-flatten.gif").stat().st_size // 1024, "KB")
