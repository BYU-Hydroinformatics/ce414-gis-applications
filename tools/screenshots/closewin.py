"""closewin.py TITLE_SUBSTRING ... -- send WM_CLOSE to visible top-level windows whose title contains
any of the given substrings (case-insensitive). Closes the File Explorer windows opened for a capture."""
import ctypes
import sys
from ctypes import wintypes

u = ctypes.windll.user32
needles = [a.lower() for a in sys.argv[1:]]


@ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
def cb(hw, _):
    if u.IsWindowVisible(hw):
        buf = ctypes.create_unicode_buffer(512)
        u.GetWindowTextW(hw, buf, 512)
        if any(k in buf.value.lower() for k in needles):
            u.PostMessageW(hw, 0x0010, 0, 0)  # WM_CLOSE
            print("closed", buf.value)
    return True


u.EnumWindows(cb, 0)
