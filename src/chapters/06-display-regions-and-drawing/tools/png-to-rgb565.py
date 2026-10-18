# Run this on your COMPUTER, not on the Pico.
#
#   pip install pillow
#   python3 png-to-rgb565.py ../../../../docs/img/mascot/welcome.png ../sage.rgb565 120
#
# Shrinks a picture to fit a SIZE x SIZE square (default 120), centers it on
# black, blacks out everything outside the inscribed circle (the round display
# mask), and writes raw RGB565 pixels, high byte first, with no header. The
# output is SIZE * SIZE * 2 bytes: 28,800 bytes for 120.

import sys
from PIL import Image, ImageDraw


def convert(src, dst, size=120):
    image = Image.open(src).convert("RGBA")
    image.thumbnail((size, size))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    offset = ((size - image.width) // 2, (size - image.height) // 2)
    canvas.paste(image, offset, image)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    black = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    canvas = Image.composite(canvas, black, mask)
    rgb = canvas.convert("RGB").tobytes()
    with open(dst, "wb") as out:
        for i in range(0, len(rgb), 3):
            r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
            value = (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3
            out.write(value.to_bytes(2, "big"))


if len(sys.argv) < 3:
    sys.exit("usage: png-to-rgb565.py SOURCE.png DEST.rgb565 [SIZE]")
convert(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 120)
print("wrote", sys.argv[2])
