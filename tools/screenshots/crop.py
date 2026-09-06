"""crop.py IN OUT x0 y0 x1 y1 [pad] -- bbox in 1456x819 screenshot coords, output native pixels."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]); f = im.width / 1456.0
x0, y0, x1, y1 = [float(v) * f for v in sys.argv[3:7]]
pad = float(sys.argv[7]) if len(sys.argv) > 7 else 0
box = (max(0, int(x0 - pad)), max(0, int(y0 - pad)), min(im.width, int(x1 + pad)), min(im.height, int(y1 + pad)))
im.crop(box).save(sys.argv[2]); print(sys.argv[2], box)
