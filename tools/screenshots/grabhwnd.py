"""grabhwnd.py HWND OUT -- screen grab (physical pixels) of one window by its handle, for when several
untitled ArcGIS Pro popups exist and grabwin.py "-" picks the wrong one (list them with EnumWindows).
The window must be unobscured."""
import sys, ctypes, ctypes.wintypes as w
from PIL import ImageGrab
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
r = w.RECT(); u.GetWindowRect(int(sys.argv[1]), ctypes.byref(r))
im = ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True)
im.save(sys.argv[2]); print(sys.argv[2], im.size, (r.left, r.top, r.right, r.bottom))
