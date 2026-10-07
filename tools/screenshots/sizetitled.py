"""sizetitled.py TITLE_PREFIX X Y W H -- move/resize a top-level window found by title prefix (e.g. a floated
ArcGIS Pro pane such as "Geoprocessing"), in physical pixels."""
import ctypes, sys, ctypes.wintypes as w
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
t = sys.argv[1]; X, Y, W, H = (int(v) for v in sys.argv[2:6])
f = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    n = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, n, 256)
    if u.IsWindowVisible(h) and n.value.startswith(t): f.append(h)
    return True
u.EnumWindows(cb, 0)
for h in f:
    u.SetWindowPos(h, 0, X, Y, W, H, 0x0004)
    r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r)); print(h, r.left, r.top, r.right, r.bottom)
if not f: print("not found", t)
