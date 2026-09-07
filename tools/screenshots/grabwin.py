"""grabwin.py TITLE OUT [x0 y0 x1 y1 [pad]] -- screen grab (physical pixels) of a top-level window found by title prefix.
TITLE "-" means the first visible untitled ArcGIS Pro popup (ModelBuilder tool dialogs). Optional crop box is in
1456x819 screenshot coords (screen space). Use this instead of capwin.py under display scaling: PrintWindow renders
Pro's windows at 96 dpi, a screen grab keeps the scaled rendering. The window must be unobscured."""
import sys, ctypes, ctypes.wintypes as w
from PIL import ImageGrab
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
title, out = sys.argv[1], sys.argv[2]
found = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    if not u.IsWindowVisible(h): return True
    n = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, n, 512)
    c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
    r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r))
    if r.right - r.left < 100: return True
    if title == "-":
        if n.value == "" and c.value.startswith("HwndWrapper[ArcGISPro"): found.append((h, r))
    elif n.value.startswith(title): found.append((h, r))
    return True
u.EnumWindows(cb, 0)
if not found: sys.exit("window not found: " + title)
hw, r = max(found, key=lambda t: (t[1].right - t[1].left) * (t[1].bottom - t[1].top))  # largest match (skips tooltips)
box = [r.left, r.top, r.right, r.bottom]
if len(sys.argv) >= 7:
    f = 1920 / 1456.0; pad = float(sys.argv[7]) if len(sys.argv) > 7 else 0
    x0, y0, x1, y1 = [float(v) * f for v in sys.argv[3:7]]
    box = [int(x0 - pad), int(y0 - pad), int(x1 + pad), int(y1 + pad)]
im = ImageGrab.grab(bbox=tuple(box), all_screens=True)
im.save(out); print(out, im.size, tuple(box))
