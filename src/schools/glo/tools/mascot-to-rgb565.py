# Run this on your COMPUTER, not on the Pico.
#
#   pip install pillow
#   python3 tools/mascot-to-rgb565.py
#
# Builds the round GLO badge: a white disc with a cyan ring on the demo's
# Groves blue background, with the waving GLO Coding Club griffin (a
# transparent PNG) fitted inside the disc. The blue griffin needs the white
# disc behind it, or its body would vanish into the blue screen. Writes raw
# RGB565 pixels, high byte first, with no header. 140 x 140 x 2 = 39,200
# bytes. If you change SIZE here, change MASCOT_SIZE in 01-glo-buddy.py too.

from pathlib import Path
from PIL import Image, ImageDraw

SIZE = 140
SCALE = 4          # draw the disc 4x larger, then shrink, for smooth edges
RING = 4           # cyan ring width, in final pixels
MASCOT_HEIGHT = 116

# Must match BACKGROUND in 01-glo-buddy.py (Groves blue).
BACKGROUND = (0x00, 0x64, 0x9B)
CYAN = (0x01, 0xBA, 0xDE)
WHITE = (0xFF, 0xFF, 0xFF)

here = Path(__file__).resolve().parent.parent
source = here / "../../../docs/schools/glo/img/griffin-welcome.png"
dest = here / "griffin-140.rgb565"

big = SIZE * SCALE
badge = Image.new("RGBA", (big, big), BACKGROUND + (255,))
draw = ImageDraw.Draw(badge)
draw.ellipse((0, 0, big - 1, big - 1), fill=CYAN)
inset = RING * SCALE
draw.ellipse((inset, inset, big - 1 - inset, big - 1 - inset), fill=WHITE)
badge = badge.resize((SIZE, SIZE), Image.LANCZOS)

mascot = Image.open(source).convert("RGBA")
width = round(mascot.width * MASCOT_HEIGHT / mascot.height)
mascot = mascot.resize((width, MASCOT_HEIGHT), Image.LANCZOS)
badge.alpha_composite(mascot, ((SIZE - width) // 2, (SIZE - MASCOT_HEIGHT) // 2))

rgb = badge.convert("RGB").tobytes()
with open(dest, "wb") as out:
    for i in range(0, len(rgb), 3):
        r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
        out.write(((r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3).to_bytes(2, "big"))
print("wrote", dest.name, dest.stat().st_size, "bytes")
