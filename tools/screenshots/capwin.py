"""capwin.py TITLE OUT [x0 y0 x1 y1 [pad]] -- PrintWindow capture of a top-level window (works when occluded).
bbox in 1456x819 screenshot coords (screen space); converted to window space using the window rect."""
import sys, ctypes, ctypes.wintypes as w
from PIL import Image
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # physical pixels under display scaling
u = ctypes.windll.user32; g = ctypes.windll.gdi32
title, out = sys.argv[1], sys.argv[2]
hw = u.FindWindowW(None, title)
if not hw:  # fall back to the first visible window whose title starts with TITLE
    found = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
    def cb(h, l):
        n = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, n, 512)
        if u.IsWindowVisible(h) and n.value.startswith(title): found.append(h)
        return True
    u.EnumWindows(cb, 0)
    if found: hw = found[0]
if not hw: sys.exit("window not found: " + title)
r = w.RECT(); u.GetWindowRect(hw, ctypes.byref(r))
W, H = r.right - r.left, r.bottom - r.top
hdc = u.GetWindowDC(hw); mdc = g.CreateCompatibleDC(hdc); bmp = g.CreateCompatibleBitmap(hdc, W, H)
g.SelectObject(mdc, bmp); u.PrintWindow(hw, mdc, 2)
class BMI(ctypes.Structure):
    _fields_ = [("biSize", w.DWORD), ("biWidth", w.LONG), ("biHeight", w.LONG), ("biPlanes", w.WORD), ("biBitCount", w.WORD), ("biCompression", w.DWORD), ("biSizeImage", w.DWORD), ("biXPelsPerMeter", w.LONG), ("biYPelsPerMeter", w.LONG), ("biClrUsed", w.DWORD), ("biClrImportant", w.DWORD)]
bi = BMI(); bi.biSize = ctypes.sizeof(BMI); bi.biWidth = W; bi.biHeight = -H; bi.biPlanes = 1; bi.biBitCount = 32
buf = ctypes.create_string_buffer(W * H * 4)
g.GetDIBits(mdc, bmp, 0, H, buf, ctypes.byref(bi), 0)
im = Image.frombuffer("RGB", (W, H), buf, "raw", "BGRX", 0, 1)
g.DeleteObject(bmp); g.DeleteDC(mdc); u.ReleaseDC(hw, hdc)
if len(sys.argv) >= 7:
    f = 1920 / 1456.0
    x0, y0, x1, y1 = [float(v) * f for v in sys.argv[3:7]]
    pad = float(sys.argv[7]) if len(sys.argv) > 7 else 0
    box = (int(x0 - r.left - pad), int(y0 - r.top - pad), int(x1 - r.left + pad), int(y1 - r.top + pad))
    im = im.crop(box)
im.save(out); print(out, im.size, (r.left, r.top, r.right, r.bottom))
