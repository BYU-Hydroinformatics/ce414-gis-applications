"""Move the Claude desktop window (or any window whose title contains the given text) off the
right edge of the screen so a screen grab of ArcGIS Pro is not contaminated. Minimizing is not
enough: the window restores itself, with focus, whenever a tool result arrives.
Usage: park.py [TITLE_SUBSTRING=Claude] [x=1914]"""
import ctypes, sys
from ctypes import wintypes
u = ctypes.windll.user32
try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception: pass
needle = sys.argv[1] if len(sys.argv) > 1 else "Claude"
x = int(sys.argv[2]) if len(sys.argv) > 2 else 1914
found = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
def cb(hw, _):
    if u.IsWindowVisible(hw):
        n = u.GetWindowTextLengthW(hw)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(hw, buf, n + 1)
            if needle.lower() in buf.value.lower(): found.append((hw, buf.value))
    return True
u.EnumWindows(cb, 0)
for hw, title in found:
    u.SetWindowPos(hw, 0, x, 0, 0, 0, 0x0001 | 0x0004 | 0x0010)   # NOSIZE | NOZORDER | NOACTIVATE
    print("parked:", title)
if not found: print("no window matched", needle)
