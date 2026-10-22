# Run this on your COMPUTER, not on the Pico.
#
#   pip install pillow
#   python3 tools/mascot-to-rgb565.py
#
# Shrinks the round sailboat badge (a 360 x 360 PNG with transparent corners)
# to SIZE x SIZE and lays it on the demo's Minnetonka blue background, so the
# corners match the screen. Writes raw RGB565 pixels, high byte first, with no
# header. 140 x 140 x 2 = 39,200 bytes. If you change SIZE here, change
# MASCOT_SIZE in 01-mme-buddy.py too.
#
# To change the drawing itself, edit sailboat.svg and re-render the PNG:
#   cairosvg sailboat.svg -o sailboat-360.png -W 360 -H 360

from pathlib import Path
from PIL import Image

SIZE = 140

# Must match BACKGROUND in 01-mme-buddy.py (Minnetonka blue).
BACKGROUND = (0x00, 0x36, 0x98)

here = Path(__file__).resolve().parent.parent
source = here / "../../../docs/schools/minnetonka-middle-school-east/img/sailboat-360.png"
dest = here / "sailboat-140.rgb565"

badge = Image.open(source).convert("RGBA").resize((SIZE, SIZE), Image.LANCZOS)
canvas = Image.new("RGBA", (SIZE, SIZE), BACKGROUND + (255,))
canvas.alpha_composite(badge)

rgb = canvas.convert("RGB").tobytes()
with open(dest, "wb") as out:
    for i in range(0, len(rgb), 3):
        r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
        out.write(((r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3).to_bytes(2, "big"))
print("wrote", dest.name, dest.stat().st_size, "bytes")
