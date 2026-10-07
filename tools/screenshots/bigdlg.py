"""bigdlg.py [X Y W H] -- move/resize the newest-looking untitled ArcGIS Pro tool dialog (the one not at 58,354)."""
import ctypes, sys
from ctypes import wintypes as w
ctypes.windll.shcore.SetProcessDpiAwareness(2); u = ctypes.windll.user32
X, Y, W, H = (int(v) for v in sys.argv[1:5]) if len(sys.argv) > 4 else (500, 60, 1300, 936)
f = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    if u.IsWindowVisible(h):
        n = ctypes.create_unicode_buffer(256); u.GetWindowTextW(h, n, 256); c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
        r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r))
        if n.value == "" and c.value.startswith("HwndWrapper[ArcGISPro") and r.right - r.left > 300 and (r.left, r.top) != (58, 354):
            f.append(h)
    return True
u.EnumWindows(cb, 0)
for h in f:
    u.SetWindowPos(h, 0, X, Y, W, H, 0x0004); r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r)); print(h, (r.left, r.top, r.right, r.bottom))
