# Run this on your COMPUTER, not on the Pico.
#
#   pip install pillow
#   python3 tools/mascot-to-rgb565.py
#
# Shrinks Gale the Griffin (the round 360 x 360 badge with transparent
# corners) to SIZE x SIZE, lays it on the demo's dark green background so the
# corners disappear into the screen, and writes raw RGB565 pixels, high byte
# first, with no header. 140 x 140 x 2 = 39,200 bytes. If you change SIZE
# here, change MASCOT_SIZE in 01-upcoming-events.py too.

from pathlib import Path
from PIL import Image

SIZE = 140

# Must match BACKGROUND in 01-upcoming-events.py (Cedar Ridge dark green).
BACKGROUND = (0x0F, 0x33, 0x20)

here = Path(__file__).resolve().parent.parent
source = here / "../../../docs/schools/cedar-ridge-high-school/img/griffin-360.png"
dest = here / "griffin-140.rgb565"

image = Image.open(source).convert("RGBA")
image = image.resize((SIZE, SIZE), Image.LANCZOS)
canvas = Image.new("RGBA", (SIZE, SIZE), BACKGROUND + (255,))
canvas.alpha_composite(image)

rgb = canvas.convert("RGB").tobytes()
with open(dest, "wb") as out:
    for i in range(0, len(rgb), 3):
        r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
        out.write(((r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3).to_bytes(2, "big"))
print("wrote", dest.name, dest.stat().st_size, "bytes")
