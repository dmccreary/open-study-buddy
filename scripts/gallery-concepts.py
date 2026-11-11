"""Concept art for the Sample Gallery: samples nobody has written yet.

Each mock-up is drawn with Pillow on a 360 x 360 screen, using the kit's
own bitmap fonts (lib/vga1_8x16.py and lib/vga1_bold_16x32.py), then put
on the same round bezel as the simulator's real screenshots. They are
pictures of an idea, not output from MicroPython code, and the gallery
says so.

Used by render-gallery-images.py. `terminal()` also lives here: it draws a
Thonny-style shell for the labs that print instead of drawing.
"""

import importlib.util
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LIB = os.path.join(REPO, "src", "kits", "study-buddy-base", "lib")
CLOCKS = os.environ.get("CLOCKS_REPO",
                        os.path.join(os.path.dirname(REPO), "clocks-and-watches"))
sys.path.insert(0, os.path.join(CLOCKS, "src", "display-simulators", "gc9b72"))

W = 360
C = W // 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 150, 0)
DIM = (150, 150, 150)
DARK = (45, 45, 45)
NAVY = (10, 30, 70)


def _font(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(LIB, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SMALL = _font("vga1_8x16")
BIG = _font("vga1_bold_16x32")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def text(d, s, x, y, color, font=SMALL, scale=1):
    """Draw s with a kit bitmap font, top-left at x, y."""
    bpr = font.WIDTH // 8                     # bytes per glyph row
    size = bpr * font.HEIGHT
    for ch in s:
        code = ord(ch)
        if font.FIRST <= code <= font.LAST:
            base = (code - font.FIRST) * size
            for row in range(font.HEIGHT):
                bits = int.from_bytes(font._FONT[base + row * bpr:base + (row + 1) * bpr], "big")
                for col in range(font.WIDTH):
                    if bits & (1 << (font.WIDTH - 1 - col)):
                        px, py = x + col * scale, y + row * scale
                        d.rectangle((px, py, px + scale - 1, py + scale - 1), fill=color)
        x += font.WIDTH * scale


def width(s, font=SMALL, scale=1):
    return len(s) * font.WIDTH * scale


def centered(d, s, y, color, font=SMALL, scale=1, cx=C):
    text(d, s, cx - width(s, font, scale) // 2, y, color, font, scale)


def polar(cx, cy, r, degrees):
    """Clock angle (0 at 12 o'clock, clockwise) to x, y."""
    a = math.radians(degrees - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def hand(d, cx, cy, length, degrees, color, w):
    d.line((cx, cy) + polar(cx, cy, length, degrees), fill=color, width=w)


def ring(d, cx, cy, r, color, w=2, start=0, end=360):
    """An arc in clock degrees."""
    d.arc((cx - r, cy - r, cx + r, cy + r), start - 90, end - 90, fill=color, width=w)


def dot(d, cx, cy, r, color, outline=None):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color, outline=outline)


def ticks(d, cx, cy, r, color, n=60, major=5, long=14, short=6):
    for k in range(n):
        ln = long if k % major == 0 else short
        d.line(polar(cx, cy, r, k * 360 / n) + polar(cx, cy, r - ln, k * 360 / n),
               fill=color, width=3 if k % major == 0 else 1)


def seven_segment(d, digit, x, y, w, h, on, off, t=8):
    """One seven-segment digit in a w x h box."""
    segs = {0: "abcdef", 1: "bc", 2: "abged", 3: "abgcd", 4: "fgbc",
            5: "afgcd", 6: "afgedc", 7: "abc", 8: "abcdefg", 9: "abcdfg"}[digit]
    m = h // 2
    boxes = {"a": (x + t, y, x + w - t, y + t), "g": (x + t, y + m - t // 2, x + w - t, y + m + t // 2),
             "d": (x + t, y + h - t, x + w - t, y + h), "f": (x, y + t, x + t, y + m - t // 2),
             "b": (x + w - t, y + t, x + w, y + m - t // 2), "e": (x, y + m + t // 2, x + t, y + h - t),
             "c": (x + w - t, y + m + t // 2, x + w, y + h - t)}
    for name, box in boxes.items():
        d.rectangle(box, fill=on if name in segs else off)


def to_565(img):
    return [((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3) for r, g, b in img.getdata()]


def save(draw, path):
    from gc9b72_sim import render
    img = Image.new("RGB", (W, W), BLACK)
    draw(ImageDraw.Draw(img), img)
    render.watch_image(to_565(img)).save(path, optimize=True)


def terminal(title, lines, path):
    """A shell window showing what a lab printed, 400 x 400, transparent."""
    try:
        mono = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 14)
    except OSError:
        mono = ImageFont.load_default()
    out = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((4, 30, 395, 370), 14, fill=(30, 32, 36, 255), outline=(70, 70, 76, 255), width=2)
    d.rounded_rectangle((4, 30, 395, 64), 14, fill=(55, 57, 62, 255))
    d.rectangle((4, 50, 395, 64), fill=(55, 57, 62, 255))
    for k, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((18 + 20 * k, 41, 30 + 20 * k, 53), fill=color)
    d.text((90, 40), title, fill=(220, 220, 220), font=mono)
    y = 76
    for line in lines[:17]:
        color = (120, 230, 120) if "PASS" in line or "OK" in line else (
            (255, 200, 80) if "WARN" in line or "?" in line else (225, 225, 225))
        d.text((16, y), line[:44], fill=color, font=mono)
        y += 17
    out.save(path, optimize=True)


# ---------------------------------------------------------------------------
# Future clock faces (the time is 10:09:20, the simulator's default)
# ---------------------------------------------------------------------------
def binary_clock(d, img):
    centered(d, "BINARY CLOCK", 62, DIM)
    for row, (label, value) in enumerate((("H", 10), ("M", 9), ("S", 20))):
        y = 125 + row * 55
        text(d, label, 62, y - 8, DIM)
        for bit in range(6):
            lit = value & (1 << (5 - bit))
            dot(d, 105 + bit * 38, y, 13, CYAN if lit else DARK)
        text(d, "%2d" % value, 330 - 50, y - 8, YELLOW)
    centered(d, "32 16  8  4  2  1", 270, DIM)
    centered(d, "10:09:20", 296, WHITE)


WORDS = ["ITLISASTIME", "ACQUARTERDC", "HALFSTENFTO", "PASTERUNINE",
         "ONESIXTHREE", "FOURFIVETWO", "EIGHTELEVEN", "SEVENTWELVE", "TENSEOCLOCK"]
LIT = {(0, 0), (0, 1), (0, 3), (0, 4), (2, 5), (2, 6), (2, 7),
       (3, 0), (3, 1), (3, 2), (3, 3), (8, 0), (8, 1), (8, 2)}


def word_clock(d, img):
    for r, row in enumerate(WORDS):
        for k, ch in enumerate(row):
            x, y = 76 + k * 19, 63 + r * 26
            text(d, ch, x, y, YELLOW if (r, k) in LIT else (55, 55, 55), BIG)


def fibonacci_clock(d, img):
    u, x0, y0 = 30, 60, 100
    squares = ((0, 0, 2, BLUE), (2, 0, 1, WHITE), (2, 1, 1, WHITE),
               (0, 2, 3, RED), (3, 0, 5, RED))
    for x, y, s, color in squares:
        d.rectangle((x0 + x * u, y0 + y * u, x0 + (x + s) * u - 3, y0 + (y + s) * u - 3),
                    fill=color if color != WHITE else (230, 230, 230))
    centered(d, "FIBONACCI CLOCK", 70, DIM)
    centered(d, "red=hours green=min blue=both", 262, DIM)
    centered(d, "5+3+2 = 10 h   2x5 = 10 min", 284, WHITE)


def sun_moon_dial(d, img):
    r = 150
    ring(d, C, C, r, (20, 30, 90), 18)                         # night
    ring(d, C, C, r, (255, 190, 40), 18, 7.1 * 15, 18.9 * 15)  # sunrise 7:05 to sunset 18:55
    for h in range(0, 24, 3):
        x, y = polar(C, C, 122, h * 15)
        s = "%d" % h
        text(d, s, int(x - width(s) / 2), int(y - 8), DIM)
    sx, sy = polar(C, C, r, 10.15 * 15)
    dot(d, sx, sy, 13, YELLOW, outline=ORANGE)
    centered(d, "10:09", 128, WHITE, BIG)
    centered(d, "sunrise  7:05", 182, (255, 190, 40))
    centered(d, "sunset   6:55", 202, (255, 140, 60))
    centered(d, "8 h 46 min left", 232, DIM)


def small_dial(d, cx, cy, hh, mm, label, sub, face):
    dot(d, cx, cy, 44, face, outline=DIM)
    for k in range(12):
        d.line(polar(cx, cy, 44, k * 30) + polar(cx, cy, 38, k * 30), fill=WHITE)
    hand(d, cx, cy, 24, (hh % 12 + mm / 60) * 30, WHITE, 4)
    hand(d, cx, cy, 36, mm * 6, CYAN, 2)
    centered(d, label, cy + 52, YELLOW, cx=cx)
    centered(d, sub, cy + 70, DIM, cx=cx)


def world_clock(d, img):
    centered(d, "WORLD CLOCK", 46, DIM)
    small_dial(d, C, 120, 10, 9, "St. Paul", "10:09 AM", (20, 40, 80))
    small_dial(d, 105, 230, 16, 9, "London", "4:09 PM", (60, 30, 70))
    small_dial(d, 255, 230, 0, 9, "Tokyo", "12:09 AM+1", (5, 5, 25))


def moon_phase(d, img):
    cx, cy, r = C, 150, 85
    dot(d, cx, cy, r, (225, 225, 205))
    # waxing gibbous: shadow on the left, a sliver
    d.chord((cx - r, cy - r, cx + r, cy + r), 90, 270, fill=(40, 40, 50))
    d.ellipse((cx - int(r * 0.55), cy - r, cx + int(r * 0.55), cy + r), fill=(225, 225, 205))
    for x, y, s in ((cx + 25, cy - 30, 10), (cx - 10, cy + 25, 14), (cx + 40, cy + 30, 7)):
        dot(d, x, y, s, (195, 195, 175))
    centered(d, "Waxing Gibbous", 250, WHITE, BIG)
    centered(d, "78% lit   full in 3 days", 290, DIM)


def ring_clock(d, img):
    for r, frac, color in ((150, 10.15 / 12, RED), (125, 9.33 / 60, GREEN), (100, 20 / 60, CYAN)):
        ring(d, C, C, r, DARK, 16)
        ring(d, C, C, r, color, 16, 0, 360 * frac)
    centered(d, "10:09", 148, WHITE, BIG, 2)
    centered(d, "FRI SEP 25", 222, DIM)


def roman_face(d, img):
    dot(d, C, C, 178, (240, 232, 210))
    ring(d, C, C, 165, (60, 40, 20), 3)
    ticks(d, C, C, 160, (60, 40, 20), long=10, short=4)
    for k, s in enumerate(["XII", "I", "II", "III", "IIII", "V", "VI", "VII",
                           "VIII", "IX", "X", "XI"]):
        x, y = polar(C, C, 122, k * 30)
        text(d, s, int(x - width(s, BIG) / 2), int(y - 16), (60, 40, 20), BIG)
    hand(d, C, C, 80, 10.15 * 30, (20, 20, 20), 8)
    hand(d, C, C, 125, 9.33 * 6, (20, 20, 20), 5)
    hand(d, C, C, 140, 20 * 6, (180, 20, 20), 2)
    dot(d, C, C, 7, (20, 20, 20))


def nixie(d, img):
    for k, ch in enumerate("1009"):
        x = 62 + k * 62 + (14 if k > 1 else 0)
        d.rounded_rectangle((x, 108, x + 52, 238), 22, fill=(25, 12, 5), outline=(90, 70, 50), width=2)
        for gx in range(x + 8, x + 50, 10):
            d.line((gx, 116, gx, 230), fill=(45, 25, 10))
        text(d, ch, x + 2, 124, (120, 40, 0), BIG, 3)
        text(d, ch, x + 2, 122, (255, 120, 20), BIG, 3)
    dot(d, C, 155, 4, (255, 120, 20))
    dot(d, C, 190, 4, (255, 120, 20))
    centered(d, "NIXIE STYLE", 265, (200, 110, 40))


def exam_countdown(d, img):
    ring(d, C, C, 150, DARK, 14)
    ring(d, C, C, 150, MAGENTA, 14, 0, 360 * 0.7)
    centered(d, "NEXT TEST", 80, DIM)
    centered(d, "Biology", 110, YELLOW, BIG)
    centered(d, "2 d 4 h", 160, WHITE, BIG, 2)
    centered(d, "Thu Oct 1, period 2", 240, DIM)
    centered(d, "chimes 1 day before", 262, GREEN)


def bell_schedule(d, img):
    periods = ((8, 8.83, CYAN), (8.92, 9.75, GREEN), (9.83, 10.67, YELLOW),
               (10.75, 11.58, ORANGE), (11.67, 12.17, MAGENTA))
    for a, b, color in periods:
        ring(d, C, C, 150, color, 16, (a - 8) / 4.5 * 330 + 15, (b - 8) / 4.5 * 330 + 15)
    x, y = polar(C, C, 150, (10.15 - 8) / 4.5 * 330 + 15)
    dot(d, x, y, 10, WHITE)
    centered(d, "PERIOD 3", 92, YELLOW)
    centered(d, "Algebra", 118, WHITE, BIG)
    centered(d, "31 min", 168, WHITE, BIG, 2)
    centered(d, "left in class", 238, DIM)
    centered(d, "next: Art, Rm 112", 262, ORANGE)


def pomodoro(d, img):
    ring(d, C, C, 148, (60, 15, 15), 20)
    ring(d, C, C, 148, (230, 50, 40), 20, 0, 360 * 0.75)
    centered(d, "FOCUS", 92, (230, 50, 40), BIG)
    centered(d, "18:42", 140, WHITE, BIG, 2)
    centered(d, "break in 18 min", 218, DIM)
    for k in range(4):
        dot(d, C - 45 + k * 30, 258, 8, (230, 50, 40) if k < 2 else DARK)


def minimal_dots(d, img):
    dot(d, C, C, 178, (25, 35, 60))
    for k in range(12):
        x, y = polar(C, C, 145, k * 30)
        dot(d, x, y, 9 if k % 3 == 0 else 5, (240, 200, 170) if k % 3 == 0 else (150, 170, 200))
    hand(d, C, C, 85, 10.15 * 30, (240, 200, 170), 6)
    hand(d, C, C, 125, 9.33 * 6, (150, 170, 200), 4)
    dot(d, C, C, 8, (240, 200, 170))
    centered(d, "FRI 25", 225, (150, 170, 200))


def orbit_clock(d, img):
    for r in (60, 105, 150):
        ring(d, C, C, r, (50, 50, 70), 1)
    dot(d, C, C, 22, (255, 200, 40))
    x, y = polar(C, C, 60, 10.15 * 30)
    dot(d, x, y, 12, (80, 160, 255))
    x, y = polar(C, C, 105, 9.33 * 6)
    dot(d, x, y, 9, (200, 200, 200))
    x, y = polar(C, C, 150, 20 * 6)
    dot(d, x, y, 6, (255, 90, 90))
    centered(d, "planet=hour", 268, (80, 160, 255))
    centered(d, "moon=minute comet=second", 288, DIM)


def day_progress(d, img):
    rows = (("TODAY", 0.42, CYAN, "42%"), ("WEEK", 0.63, GREEN, "63%"),
            ("SEMESTER", 0.31, YELLOW, "31%"), ("YEAR", 0.73, MAGENTA, "73%"))
    centered(d, "10:09 AM", 52, WHITE, BIG)
    for k, (label, frac, color, pct) in enumerate(rows):
        y = 112 + k * 50
        text(d, label, 62, y, DIM)
        text(d, pct, 268, y, color)
        d.rectangle((62, y + 20, 298, y + 32), fill=DARK)
        d.rectangle((62, y + 20, 62 + int(236 * frac), y + 32), fill=color)


def retro_lcd(d, img):
    bg, on, off = (150, 165, 120), (25, 35, 25), (135, 150, 108)
    dot(d, C, C, 178, bg)
    for k, digit in enumerate((1, 0, 0, 9)):
        x = 52 + k * 66 + (18 if k > 1 else 0)
        seven_segment(d, digit, x, 130, 50, 96, on, off, 10)
    d.rectangle((C - 4, 155, C + 4, 163), fill=on)
    d.rectangle((C - 4, 192, C + 4, 200), fill=on)
    text(d, "FRI", 92, 82, on, BIG)
    text(d, "25", 220, 82, on, BIG)
    centered(d, "AM  ALARM 6:45", 252, on)


# ---------------------------------------------------------------------------
# Future study tools
# ---------------------------------------------------------------------------
def flash_quiz(d, img):
    centered(d, "STATE CAPITALS  7/10", 52, DIM)
    centered(d, "Capital of", 92, WHITE)
    centered(d, "Minnesota?", 112, YELLOW, BIG)
    for k, s in enumerate(("Duluth", "St. Paul", "Minneapolis")):
        y = 166 + k * 40
        if k == 1:
            d.rounded_rectangle((90, y - 4, 270, y + 30), 8, fill=(20, 110, 40))
        centered(d, s, y, WHITE, BIG)
    centered(d, "UP/DOWN pick  MODE choose", 290, DIM)


def math_facts(d, img):
    centered(d, "MATH FACTS", 58, DIM)
    centered(d, "7 x 8", 96, WHITE, BIG, 2)
    centered(d, "= ?", 162, YELLOW, BIG)
    for k, s in enumerate(("54", "56", "58")):
        x = 105 + k * 75
        d.rounded_rectangle((x - 28, 210, x + 28, 250), 8,
                            fill=(20, 110, 40) if k == 1 else DARK)
        centered(d, s, 214, WHITE, BIG, cx=x)
    centered(d, "streak 12   best 19", 270, GREEN)


def wake_word(d, img):
    for r, shade in ((150, 40), (120, 80), (90, 140)):
        ring(d, C, C, r, (0, shade, shade), 6)
    dot(d, C, C, 55, (0, 120, 140))
    centered(d, "Hey", 136, WHITE, BIG)
    centered(d, "Pico", 168, WHITE, BIG)
    centered(d, "heard you - ask away", 268, CYAN)


def ask_agent(d, img):
    centered(d, "ASK YOUR BUDDY", 50, DIM)
    centered(d, "You asked:", 80, DIM)
    centered(d, "\"When is the", 102, YELLOW)
    centered(d, "science fair?\"", 122, YELLOW)
    d.line((70, 152, 290, 152), fill=DARK)
    centered(d, "Thursday at", 168, WHITE, BIG)
    centered(d, "6 PM in the", 202, WHITE, BIG)
    centered(d, "gym.", 236, WHITE, BIG)
    centered(d, "hold MODE to talk", 290, DIM)


def spectrum(d, img):
    centered(d, "SPECTRUM (FFT)", 58, DIM)
    levels = (30, 55, 90, 120, 100, 80, 140, 110, 70, 60, 85, 50, 35, 25)
    for k, h in enumerate(levels):
        x = 64 + k * 17
        hue = k / len(levels)
        color =(int(255 * (1 - hue)), int(255 * min(1, hue * 2)), int(255 * hue))
        d.rectangle((x, 250 - h, x + 12, 250), fill=color)
    d.line((60, 254, 300, 254), fill=DIM)
    text(d, "100", 60, 262, DIM)
    text(d, "1k", C - 8, 262, DIM)
    text(d, "8k Hz", 256, 262, DIM)


def metronome(d, img):
    d.polygon(((C - 70, 290), (C + 70, 290), (C + 35, 70), (C - 35, 70)), fill=(90, 50, 25))
    d.polygon(((C - 52, 270), (C + 52, 270), (C + 26, 90), (C - 26, 90)), fill=(25, 15, 8))
    hand(d, C, 265, 165, -18, (230, 210, 150), 4)
    x, y = polar(C, 265, 110, -18)
    d.rectangle((x - 9, y - 7, x + 9, y + 7), fill=(230, 210, 150))
    centered(d, "96 BPM", 300, YELLOW)
    for k in range(4):
        dot(d, 50, 140 + k * 26, 7, CYAN if k == 1 else DARK)
    text(d, "4/4", 276, 150, DIM)


def breathing(d, img):
    for r, shade in ((150, 25), (125, 50), (100, 85)):
        dot(d, C, C, r, (shade // 2, shade, shade + 20))
    centered(d, "Breathe in", 150, WHITE, BIG)
    centered(d, "3", 188, CYAN, BIG)
    centered(d, "round 2 of 5", 260, (170, 210, 230))


def push_alert(d, img):
    centered(d, "10:09", 60, DIM, BIG)
    d.rounded_rectangle((60, 112, 300, 258), 14, fill=(30, 40, 70), outline=CYAN, width=2)
    d.polygon(((C - 14, 148), (C + 14, 148), (C + 18, 160), (C - 18, 160)), fill=YELLOW)
    d.pieslice((C - 14, 128, C + 14, 156), 180, 360, fill=YELLOW)
    centered(d, "Library book", 172, WHITE, BIG)
    centered(d, "due tomorrow", 206, WHITE)
    centered(d, "from: Media Center", 230, DIM)
    centered(d, "UP: got it  DOWN: later", 278, DIM)


def mode_library(d, img):
    centered(d, "MODE LIBRARY", 54, DIM)
    items = (("Flash Quiz", True), ("Math Facts", True), ("Periodic Table", False),
             ("Word of the Day", False), ("Metronome", True))
    for k, (name, have) in enumerate(items):
        y = 88 + k * 34
        if k == 2:
            d.rounded_rectangle((62, y - 6, 298, y + 24), 6, fill=(20, 60, 110))
        text(d, ("[x] " if have else "[ ] ") + name, 74, y, GREEN if have else WHITE)
    centered(d, "MODE: install", 270, YELLOW)
    centered(d, "from your teacher's list", 290, DIM)


def homework(d, img):
    centered(d, "TONIGHT", 56, YELLOW, BIG)
    tasks = (("Math p.112 #1-15", True), ("Read ch. 4", True),
             ("Spanish vocab", False), ("Lab report draft", False))
    for k, (task, done) in enumerate(tasks):
        y = 110 + k * 38
        d.rectangle((66, y, 84, y + 18), outline=DIM, width=2)
        if done:
            d.line((69, y + 9, 74, y + 15, 82, y + 3), fill=GREEN, width=3)
        text(d, task, 96, y + 2, DIM if done else WHITE)
    centered(d, "2 of 4 done", 270, GREEN)


def dice(d, img):
    d.rounded_rectangle((105, 80, 255, 230), 22, fill=WHITE)
    for x, y in ((135, 110), (225, 110), (C, 155), (135, 200), (225, 200)):
        dot(d, x, y, 13, BLACK)
    centered(d, "You rolled 5", 250, YELLOW, BIG)
    centered(d, "UP: roll  DOWN: 2 dice", 292, DIM)


def noise_monitor(d, img):
    d.rounded_rectangle((C - 50, 60, C + 50, 260), 20, fill=(30, 30, 30))
    dot(d, C, 100, 28, (70, 0, 0))
    dot(d, C, 160, 28, (255, 200, 0))
    dot(d, C, 220, 28, (0, 70, 0))
    centered(d, "A little loud", 276, YELLOW)
    centered(d, "62 dB  library voice <55", 296, DIM)


def note_trainer(d, img):
    centered(d, "EAR TRAINER", 54, DIM)
    for k in range(5):
        d.line((70, 100 + k * 14, 290, 100 + k * 14), fill=DIM)
    d.ellipse((165, 130, 189, 146), fill=WHITE)
    d.line((188, 138, 188, 90), fill=WHITE, width=2)
    centered(d, "Which note?", 170, WHITE)
    for k, s in enumerate(("C", "E", "G")):
        x = 115 + k * 65
        d.rounded_rectangle((x - 24, 196, x + 24, 236), 8, fill=(20, 110, 40) if k == 1 else DARK)
        centered(d, s, 200, WHITE, BIG, cx=x)
    centered(d, "DOWN: play it again", 262, DIM)


CONCEPTS = [
    ("concept-binary-clock", binary_clock),
    ("concept-word-clock", word_clock),
    ("concept-fibonacci-clock", fibonacci_clock),
    ("concept-sun-moon-dial", sun_moon_dial),
    ("concept-world-clock", world_clock),
    ("concept-moon-phase", moon_phase),
    ("concept-ring-clock", ring_clock),
    ("concept-roman-face", roman_face),
    ("concept-nixie", nixie),
    ("concept-exam-countdown", exam_countdown),
    ("concept-bell-schedule", bell_schedule),
    ("concept-pomodoro", pomodoro),
    ("concept-minimal-dots", minimal_dots),
    ("concept-orbit-clock", orbit_clock),
    ("concept-day-progress", day_progress),
    ("concept-retro-lcd", retro_lcd),
    ("concept-flash-quiz", flash_quiz),
    ("concept-math-facts", math_facts),
    ("concept-wake-word", wake_word),
    ("concept-ask-agent", ask_agent),
    ("concept-spectrum", spectrum),
    ("concept-metronome", metronome),
    ("concept-breathing", breathing),
    ("concept-push-alert", push_alert),
    ("concept-mode-library", mode_library),
    ("concept-homework", homework),
    ("concept-dice", dice),
    ("concept-noise-monitor", noise_monitor),
    ("concept-note-trainer", note_trainer),
]
