"""cap.py OUT [x0 y0 x1 y1]  -- full-res screen grab; bbox given in 1456x819 screenshot coords."""
import sys
from PIL import ImageGrab
out = sys.argv[1]
im = ImageGrab.grab()
if len(sys.argv) >= 6:
    f = im.width / 1456.0
    x0, y0, x1, y1 = [int(round(float(v) * f)) for v in sys.argv[2:6]]
    im = im.crop((x0, y0, x1, y1))
im.save(out)
print(out, im.size)
