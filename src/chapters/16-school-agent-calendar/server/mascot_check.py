#!/usr/bin/env python3
"""Check a mascot image against the round display, and make the Pico file (Chapter 16).

    pip install pillow
    python3 mascot_check.py                       # report only
    python3 mascot_check.py --write               # also write ../griffin.rgb565 at the configured size

The glass is 360 x 360 pixels but the bezel hides the outside of a circle of
radius SAFE_RADIUS = 168 around (180, 180) (the kit's config.py). This reports
how much of the picture falls outside that circle and what each size costs in
bytes, then (with --write) scales the picture to the configured size, blacks out
everything outside its inscribed circle, and writes raw RGB565, high byte first.
"""
import argparse
import math
import os
import sys

import agent_config

SAFE_RADIUS = 168
WIDTH = 360
HERE = os.path.dirname(os.path.abspath(__file__))


def report(image):
    px = image.convert("RGBA").load()
    w, h = image.size
    opaque = outside = 0
    farthest = 0.0
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 0:
                opaque += 1
                r = math.hypot(x + 0.5 - w / 2, y + 0.5 - h / 2)
                farthest = max(farthest, r)
                if r > SAFE_RADIUS * w / WIDTH:
                    outside += 1
    return opaque, outside, farthest


def to_rgb565(image, size):
    from PIL import Image, ImageDraw
    image = image.convert("RGBA")
    image.thumbnail((size, size))
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2), image)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    canvas = Image.composite(canvas, Image.new("RGBA", (size, size), (0, 0, 0, 255)), mask)
    rgb = canvas.convert("RGB").tobytes()
    out = bytearray()
    for i in range(0, len(rgb), 3):
        value = (rgb[i] & 0xF8) << 8 | (rgb[i + 1] & 0xFC) << 3 | rgb[i + 2] >> 3
        out += value.to_bytes(2, "big")
    return bytes(out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--config", default=os.path.join(HERE, "agent.toml"))
    p.add_argument("--write", action="store_true")
    args = p.parse_args(argv)
    try:
        from PIL import Image
    except ImportError:
        sys.exit("This tool needs Pillow:  pip install pillow")
    cfg = agent_config.load(args.config)
    src = agent_config.resolve(cfg, cfg["mascot"]["source_png"])
    image = Image.open(src)
    print("%s: %d x %d" % (os.path.basename(src), *image.size))
    opaque, outside, farthest = report(image)
    print("  non-transparent pixels      : %d" % opaque)
    print("  outside the safe circle (r>%d): %d (%.1f%%)" % (SAFE_RADIUS, outside, 100.0 * outside / opaque))
    print("  farthest pixel from center  : %.1f" % farthest)
    print()
    print("  %-26s %10s" % ("size", "bytes"))
    for label, side in (("full frame 360 x 360", 360), ("safe circle 336 x 336", 336),
                        ("configured %d x %d" % (cfg["mascot"]["size"], cfg["mascot"]["size"]), cfg["mascot"]["size"]),
                        ("small 120 x 120", 120), ("layout region 64 x 64", 64)):
        print("  %-26s %10s" % (label, format(side * side * 2, ",")))
    if args.write:
        size = cfg["mascot"]["size"]
        data = to_rgb565(image, size)
        dest = os.path.join(os.path.dirname(cfg["_dir"]), cfg["mascot"]["file"])
        with open(dest, "wb") as f:
            f.write(data)
        print("\nwrote %s (%s bytes)" % (dest, format(len(data), ",")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
