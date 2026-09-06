"""capwin2.py OUT -- PrintWindow capture of the (first) visible untitled ArcGIS Pro popup window (tool dialogs in ModelBuilder)."""
import sys, ctypes, ctypes.wintypes as w
from PIL import Image
u = ctypes.windll.user32; g = ctypes.windll.gdi32
found = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    if u.IsWindowVisible(h):
        n = u.GetWindowTextLengthW(h); c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
        r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r))
        if n == 0 and c.value.startswith("HwndWrapper[ArcGISPro") and (r.right - r.left) > 100: found.append((h, r))
    return True
u.EnumWindows(cb, 0)
if not found: sys.exit("no untitled ArcGIS Pro popup found")
hw, r = found[0]; W, H = r.right - r.left, r.bottom - r.top
hdc = u.GetWindowDC(hw); mdc = g.CreateCompatibleDC(hdc); bmp = g.CreateCompatibleBitmap(hdc, W, H)
g.SelectObject(mdc, bmp); u.PrintWindow(hw, mdc, 2)
class BMI(ctypes.Structure):
    _fields_ = [("biSize", w.DWORD), ("biWidth", w.LONG), ("biHeight", w.LONG), ("biPlanes", w.WORD), ("biBitCount", w.WORD), ("biCompression", w.DWORD), ("biSizeImage", w.DWORD), ("biXPelsPerMeter", w.LONG), ("biYPelsPerMeter", w.LONG), ("biClrUsed", w.DWORD), ("biClrImportant", w.DWORD)]
bi = BMI(); bi.biSize = ctypes.sizeof(BMI); bi.biWidth = W; bi.biHeight = -H; bi.biPlanes = 1; bi.biBitCount = 32
buf = ctypes.create_string_buffer(W * H * 4); g.GetDIBits(mdc, bmp, 0, H, buf, ctypes.byref(bi), 0)
im = Image.frombuffer("RGB", (W, H), buf, "raw", "BGRX", 0, 1)
g.DeleteObject(bmp); g.DeleteDC(mdc); u.ReleaseDC(hw, hdc)
im.save(sys.argv[1]); print(sys.argv[1], im.size, (r.left, r.top, r.right, r.bottom))
