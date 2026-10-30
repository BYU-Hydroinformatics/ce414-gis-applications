"""minwin.py [TITLE_SUBSTRING ...] -- list visible top-level windows, and minimize those whose title
contains any of the given substrings (case-insensitive). Clears Chrome, Task Manager and the like
off the screen before a capture session. An elevated window (Task Manager) may refuse."""
import ctypes
import sys
from ctypes import wintypes

ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
needles = [a.lower() for a in sys.argv[1:]]


@ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
def cb(hw, _):
    if not u.IsWindowVisible(hw) or u.IsIconic(hw):
        return True
    n = u.GetWindowTextLengthW(hw)
    if not n:
        return True
    buf = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(hw, buf, n + 1)
    r = wintypes.RECT()
    u.GetWindowRect(hw, ctypes.byref(r))
    hit = any(k in buf.value.lower() for k in needles)
    if hit:
        u.ShowWindow(hw, 6)  # SW_MINIMIZE
    print(("MIN " if hit else "    ") + f"{buf.value[:60]!r} {r.left},{r.top},{r.right},{r.bottom}")
    return True


u.EnumWindows(cb, 0)
