"""stitchat.py OUT A A_END B B_START [SCROLL_X0 SCROLL_X1] -- A[:A_END] on top of B[B_START:], optionally painting a
scrollbar column (x0..x1, below the 110 px header) with the dialog background so the join is invisible."""
import sys
from PIL import Image, ImageDraw
out, a, ae, b, bs = sys.argv[1], Image.open(sys.argv[2]).convert("RGB"), int(sys.argv[3]), Image.open(sys.argv[4]).convert("RGB"), int(sys.argv[5])
o = Image.new("RGB", (a.width, ae + b.height - bs), "white")
o.paste(a.crop((0, 0, a.width, ae)), (0, 0)); o.paste(b.crop((0, bs, b.width, b.height)), (0, ae))
if len(sys.argv) > 7:
    x0, x1 = int(sys.argv[6]), int(sys.argv[7])
    bg = o.getpixel((x0 - 6, 115))
    ImageDraw.Draw(o).rectangle((x0, 110, x1, o.height - 70), fill=bg)
o.save(out); print(out, o.size)
