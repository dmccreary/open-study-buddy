#!/usr/bin/env python3
"""Render a school buddy demo to a PNG on the computer, without a Pico.

Runs the demo program (src/schools/<id>/01-<slug>-buddy.py) in ordinary
Python with a stand-in for the kit's config module and display driver. The
stand-in draws into a 360 x 360 Pillow image using the kit's real bitmap
fonts, so the preview matches the round GC9B72 screen pixel for pixel.

It also checks every piece of text against the visible glass and prints a
warning for any letter the bezel would cut off.

    python3 preview_screen.py <repo-root> <school-id> [--out PATH]

Default output: docs/schools/<id>/img/<slug>-buddy-preview.png
Exit status 0 = drawn and everything fits, 1 = drawn with warnings,
2 = the program failed to run.
"""

import argparse
import glob
import math
import os
import runpy
import sys
import types
from pathlib import Path

from PIL import Image, ImageDraw

WIDTH = HEIGHT = 360
CENTER = 180
# Text corners must sit inside this radius. Calibrated on the working
# examples: Minnetonka's 29-letter bottom line reaches 172.7 px from the
# center and is fully visible on the real panel.
VISIBLE_RADIUS = 174


def color565(red, green=0, blue=0):
    try:
        red, green, blue = red
    except TypeError:
        pass
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


def rgb(c):
    r = (c >> 11) & 0x1F
    g = (c >> 5) & 0x3F
    b = c & 0x1F
    return (r * 255 // 31, g * 255 // 63, b * 255 // 31)


def load_font(path):
    module = types.ModuleType(Path(path).stem)
    exec(compile(Path(path).read_text(), str(path), "exec"), module.__dict__)
    return module


class FakeDisplay:
    def __init__(self):
        self.image = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
        self.pixels = self.image.load()
        self.texts = []          # (text, x, y, w, h)

    def fill(self, color):
        self.fill_rect(0, 0, WIDTH, HEIGHT, color)

    def fill_rect(self, x, y, w, h, color):
        ImageDraw.Draw(self.image).rectangle((x, y, x + w - 1, y + h - 1), fill=rgb(color))

    def blit_buffer(self, buf, x, y, w, h):
        data = bytes(buf)
        for row in range(h):
            for col in range(w):
                i = (row * w + col) * 2
                if x + col < WIDTH and y + row < HEIGHT:
                    self.pixels[x + col, y + row] = rgb(data[i] << 8 | data[i + 1])

    def text(self, font, text, x0, y0, color=0xFFFF, background=0):
        self.texts.append((text, x0, y0, len(text) * font.WIDTH, font.HEIGHT))
        bpr = font.WIDTH // 8
        glyph = bpr * font.HEIGHT
        fg, bg = rgb(color), rgb(background)
        for ch in text:
            code = ord(ch)
            if font.FIRST <= code < font.LAST and x0 + font.WIDTH <= WIDTH:
                base = (code - font.FIRST) * glyph
                for row in range(font.HEIGHT):
                    for b in range(bpr):
                        byte = font.FONT[base + row * bpr + b]
                        for bit in range(8):
                            on = byte & (0x80 >> bit)
                            self.pixels[x0 + b * 8 + bit, y0 + row] = fg if on else bg
            x0 += font.WIDTH


def make_config(kit_lib, display):
    config = types.ModuleType("config")
    config.WIDTH, config.HEIGHT = WIDTH, HEIGHT
    config.color565 = color565
    config.BLACK, config.WHITE = 0x0000, 0xFFFF
    config.SMALL_FONT = load_font(kit_lib / "vga1_8x16.py")
    config.BIG_FONT = load_font(kit_lib / "vga1_bold_16x32.py")
    config.init_display = lambda: display
    config.set_backlight = lambda on: None

    def centered_text(d, font, text, y, color=0xFFFF, background=0):
        d.text(font, text, (WIDTH - len(text) * font.WIDTH) // 2, y, color, background)

    config.centered_text = centered_text
    return config


def check_fit(texts):
    problems = []
    for text, x, y, w, h in texts:
        worst = max(math.hypot(cx - CENTER, cy - CENTER)
                    for cx in (x, x + w) for cy in (y, y + h))
        if worst > VISIBLE_RADIUS:
            problems.append("'{}' reaches {:.0f} px from the center (limit {}): "
                            "the bezel will cut it off".format(text, worst, VISIBLE_RADIUS))
    return problems


def round_screen(image):
    """Mask the corners and add a dark bezel ring so it looks like the device."""
    scale = 4
    size = WIDTH + 40
    big = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=(34, 34, 38, 255))
    out = big.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (WIDTH * scale, HEIGHT * scale), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, WIDTH * scale - 1, HEIGHT * scale - 1), fill=255)
    out.paste(image, (20, 20), mask.resize((WIDTH, HEIGHT), Image.LANCZOS))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path)
    ap.add_argument("school_id")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    repo = args.repo.resolve()
    src = repo / "src" / "schools" / args.school_id
    programs = sorted(glob.glob(str(src / "01-*.py")))
    if not programs:
        sys.exit("No 01-*.py demo program in {}".format(src))
    program = Path(programs[0])
    slug = program.stem[3:]                         # "01-mme-buddy" -> "mme-buddy"
    out = args.out or repo / "docs" / "schools" / args.school_id / "img" / "{}-preview.png".format(slug)

    display = FakeDisplay()
    sys.modules["config"] = make_config(repo / "src" / "kits" / "study-buddy-base" / "lib", display)
    old_cwd = os.getcwd()
    os.chdir(src)
    try:
        runpy.run_path(str(program), run_name="__main__")
    except SystemExit as e:
        if e.code not in (None, 0):
            print("FAILED: {} exited: {}".format(program.name, e.code))
            return 2
    except Exception as e:
        print("FAILED: {} raised {}: {}".format(program.name, type(e).__name__, e))
        return 2
    finally:
        os.chdir(old_cwd)

    out.parent.mkdir(parents=True, exist_ok=True)
    round_screen(display.image).save(out)
    print("preview:", out)

    problems = check_fit(display.texts)
    for p in problems:
        print("WARNING:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
