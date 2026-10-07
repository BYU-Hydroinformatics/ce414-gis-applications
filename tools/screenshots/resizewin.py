"""resizewin.py W H [LEFT] -- resize the largest untitled ArcGIS Pro popup (tool dialog) to W x H native pixels, keeping its position."""
import ctypes, sys
from ctypes import wintypes as w
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
W, H = int(sys.argv[1]), int(sys.argv[2])
found = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    if u.IsWindowVisible(h):
        n = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, n, 256)
        c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
        r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r))
        if n.value == "" and c.value.startswith("HwndWrapper[ArcGISPro") and r.right - r.left > 300:
            found.append((h, r))
    return True
u.EnumWindows(cb, 0)
x0 = int(sys.argv[3]) if len(sys.argv) > 3 else None
if x0 is not None:
    found = [t for t in found if t[1].left == x0]
h, r = max(found, key=lambda t: (t[1].right - t[1].left) * (t[1].bottom - t[1].top))
u.SetWindowPos(h, 0, 0, 0, W, H, 0x0002 | 0x0004)
print("resized", (r.left, r.top, r.right, r.bottom), "->", W, H)
