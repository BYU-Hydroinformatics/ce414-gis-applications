"""stitch.py OUT SKIP IN1 IN2 [IN3 ...] -- vertically stitch scrolled captures of the same width.
SKIP = height in px of a fixed (non-scrolling) header at the top of every capture; it is kept from the
first capture and removed from the rest. For each consecutive pair, the top 150 px of the next capture
(below the header) are located inside the accumulated result."""
import sys
import numpy as np
from PIL import Image

out, skip, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [np.asarray(Image.open(p).convert("RGB")).astype(np.int32) for p in paths]
W = ims[0].shape[1]
XR = W - 40                      # ignore the scrollbar column when matching
H = 150
result = ims[0]
for nxt in ims[1:]:
    nxt = nxt[skip:]
    strip = nxt[0:H, :XR]
    best, best_err = None, None
    for y in range(max(skip, result.shape[0] - 450), result.shape[0] - 60):
        n = min(H, result.shape[0] - y)
        err = np.abs(result[y:y + n, :XR] - strip[:n]).mean()
        if best_err is None or err < best_err:
            best, best_err = y, err
    print("overlap at", best, "err", round(float(best_err), 2))
    result = np.concatenate([result[:best], nxt], axis=0)
Image.fromarray(result.astype(np.uint8)).save(out)
print(out, result.shape[1], result.shape[0])
