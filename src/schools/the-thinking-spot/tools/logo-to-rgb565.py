# Run this on your COMPUTER, not on the Pico.
#
#   pip install pillow
#   python3 tools/logo-to-rgb565.py
#
# Shrinks the Thinking Spot tree logo (no text, white background) to fit a
# WIDTH x HEIGHT box, centers it on white, and writes raw RGB565 pixels, high
# byte first, with no header. 150 x 170 x 2 = 51,000 bytes. If you change
# WIDTH or HEIGHT here, change them in 01-buddy-is-live.py too.

from pathlib import Path
from PIL import Image

WIDTH = 150
HEIGHT = 170

here = Path(__file__).resolve().parent.parent
source = here / "../../../docs/schools/the-thinking-spot/logo-no-text-trim.jpg"
dest = here / "tree-logo.rgb565"

image = Image.open(source).convert("RGB")
image.thumbnail((WIDTH, HEIGHT), Image.LANCZOS)
canvas = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
canvas.paste(image, ((WIDTH - image.width) // 2, (HEIGHT - image.height) // 2))

# The JPEG background is a faint off-white that would show as a box on the
# white screen, so snap every nearly-white pixel to pure white.
rgb = bytearray(canvas.tobytes())
for i in range(0, len(rgb), 3):
    if rgb[i] > 225 and rgb[i + 1] > 225 and rgb[i + 2] > 225:
        rgb[i] = rgb[i + 1] = rgb[i + 2] = 255
with open(dest, "wb") as out:
    for i in range(0, len(rgb), 3):
        r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
        out.write(((r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3).to_bytes(2, "big"))
print("wrote", dest.name, dest.stat().st_size, "bytes")
