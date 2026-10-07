"""grabdlg.py OUT -- screen grab of the ArcGIS Pro tool dialog that is open now: the visible untitled
ArcGIS Pro popup that is the foreground window (or, failing that, the smallest visible untitled popup
over 300 px wide, which skips the stale full-width ones). Parks the Claude window first."""
import sys, ctypes, ctypes.wintypes as w, subprocess, os, time
from PIL import ImageGrab
ctypes.windll.shcore.SetProcessDpiAwareness(2)
u = ctypes.windll.user32
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(here, "park.py")], capture_output=True); time.sleep(0.8)
cands = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)
def cb(h, l):
    if not u.IsWindowVisible(h): return True
    n = ctypes.create_unicode_buffer(512); u.GetWindowTextW(h, n, 512)
    c = ctypes.create_unicode_buffer(256); u.GetClassNameW(h, c, 256)
    r = w.RECT(); u.GetWindowRect(h, ctypes.byref(r))
    if c.value.startswith("HwndWrapper[ArcGISPro") and n.value == "" and r.right - r.left > 300:
        cands.append((h, (r.left, r.top, r.right, r.bottom)))
    return True
u.EnumWindows(cb, 0)
fg = u.GetForegroundWindow()
pick = [c for c in cands if c[0] == fg] or sorted(cands, key=lambda c: (c[1][2] - c[1][0]) * (c[1][3] - c[1][1]))
if len(sys.argv) > 2: pick = [c for c in cands if c[0] == int(sys.argv[2])]
h, box = pick[0]
im = ImageGrab.grab(bbox=box, all_screens=True); im.save(sys.argv[1])
print(sys.argv[1], im.size, box, "candidates:", [(c[0], c[1]) for c in cands])
