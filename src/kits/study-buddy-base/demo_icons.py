# demo_icons.py -- the pictures on the showcase screens, drawn from shapes.
#
# There are no image files here. Every icon is built from circles,
# rectangles, lines, and triangles (lib/shapes.py), so it costs no flash
# space and can be any color. Each function draws one icon centered on
# (cx, cy), about 90 pixels across, onto a black background.
#
#     import demo_icons
#     demo_icons.draw("clock", display, 180, 100)

import math
from array import array

import config
import shapes

BLACK = config.BLACK
WHITE = config.WHITE
FILL = config.FILL

ORANGE = config.color565(255, 150, 40)
BROWN = config.color565(140, 90, 50)
TAN = config.color565(225, 190, 140)
GOLD = config.color565(255, 200, 0)
SKY = config.color565(90, 170, 255)
SPAIN_RED = config.color565(200, 20, 30)
GRAY = config.color565(120, 120, 120)


def thick_line(display, x0, y0, x1, y1, width, color):
    """A line `width` pixels thick, as a filled four-sided polygon."""
    dx = x1 - x0
    dy = y1 - y0
    length = (dx * dx + dy * dy) ** 0.5 or 1
    ox = -dy / length * width / 2
    oy = dx / length * width / 2
    shapes.poly(display, 0, 0, array('h', [
        round(x0 + ox), round(y0 + oy), round(x1 + ox), round(y1 + oy),
        round(x1 - ox), round(y1 - oy), round(x0 - ox), round(y0 - oy)]),
        color, FILL)


def clock(display, cx, cy):
    shapes.circle(display, cx, cy, 42, config.CYAN, FILL)
    shapes.circle(display, cx, cy, 36, BLACK, FILL)
    for x, y in ((0, -30), (30, 0), (0, 30), (-30, 0)):
        display.fill_rect(cx + x - 2, cy + y - 2, 5, 5, WHITE)
    thick_line(display, cx, cy, cx + 14, cy - 12, 5, WHITE)    # hour hand
    thick_line(display, cx, cy, cx, cy - 28, 3, WHITE)         # minute hand
    shapes.circle(display, cx, cy, 4, config.CYAN, FILL)
    # A little sun peeking over the top right: the weather.
    shapes.circle(display, cx + 38, cy - 34, 12, GOLD, FILL)


def bell(display, cx, cy):
    color = GOLD
    shapes.ellipse(display, cx, cy - 8, 28, 30, color, FILL, shapes.TOP_HALF)
    display.fill_rect(cx - 28, cy - 8, 57, 26, color)
    display.fill_rect(cx - 38, cy + 18, 77, 8, color)
    shapes.circle(display, cx, cy + 32, 7, color, FILL)
    shapes.circle(display, cx, cy - 40, 5, color, FILL)
    # Sound waves on both sides: ))  and  ((
    for r in (12, 20):
        for step in range(2):
            shapes.circle(display, cx + 36, cy - 8, r + step, ORANGE, 0,
                          shapes.TOP_RIGHT + shapes.BOTTOM_RIGHT)
            shapes.circle(display, cx - 36, cy - 8, r + step, ORANGE, 0,
                          shapes.TOP_LEFT + shapes.BOTTOM_LEFT)


def hourglass(display, cx, cy):
    frame = TAN
    sand = GOLD
    display.fill_rect(cx - 30, cy - 44, 61, 7, frame)
    display.fill_rect(cx - 30, cy + 38, 61, 7, frame)
    shapes.triangle(display, cx - 24, cy - 37, cx + 24, cy - 37, cx, cy,
                    SKY, 0)
    shapes.triangle(display, cx - 24, cy + 37, cx + 24, cy + 37, cx, cy,
                    SKY, 0)
    shapes.triangle(display, cx - 12, cy - 18, cx + 12, cy - 18, cx, cy - 2,
                    sand, FILL)
    shapes.triangle(display, cx - 20, cy + 37, cx + 20, cy + 37, cx, cy + 18,
                    sand, FILL)
    display.vline(cx, cy, 20, sand)


def stopwatch(display, cx, cy):
    display.fill_rect(cx - 8, cy - 48, 17, 8, config.GREEN)
    display.fill_rect(cx - 3, cy - 42, 7, 8, config.GREEN)
    shapes.circle(display, cx, cy + 4, 38, config.GREEN, FILL)
    shapes.circle(display, cx, cy + 4, 32, BLACK, FILL)
    for i in range(12):
        # Tick marks: short lines pointing in from the rim.
        a = i * math.pi / 6
        s, c = math.sin(a), math.cos(a)
        display.line(round(cx + 26 * s), round(cy + 4 - 26 * c),
                     round(cx + 30 * s), round(cy + 4 - 30 * c), WHITE)
    thick_line(display, cx, cy + 4, cx + 18, cy - 14, 3, config.RED)
    shapes.circle(display, cx, cy + 4, 3, WHITE, FILL)


def owl(display, cx, cy, scale=1.0, background=BLACK):
    """The demo school's mascot: an owl. scale 1.0 is about 90 px tall."""
    def s(n):
        return int(n * scale)
    # Ear tufts, then the body and the lighter belly.
    shapes.triangle(display, cx - s(34), cy - s(48), cx - s(14), cy - s(30),
                    cx - s(36), cy - s(22), BROWN, FILL)
    shapes.triangle(display, cx + s(34), cy - s(48), cx + s(14), cy - s(30),
                    cx + s(36), cy - s(22), BROWN, FILL)
    shapes.ellipse(display, cx, cy, s(38), s(46), BROWN, FILL)
    shapes.ellipse(display, cx, cy + s(18), s(24), s(24), TAN, FILL)
    # Big round eyes.
    for side in (-1, 1):
        ex = cx + side * s(16)
        shapes.circle(display, ex, cy - s(16), s(14), WHITE, FILL)
        shapes.circle(display, ex, cy - s(16), s(14), GOLD, 0)
        shapes.circle(display, ex, cy - s(14), s(6), BLACK, FILL)
        shapes.circle(display, ex - s(2), cy - s(17), max(1, s(2)), WHITE,
                      FILL)
    shapes.triangle(display, cx - s(6), cy - s(2), cx + s(6), cy - s(2),
                    cx, cy + s(10), ORANGE, FILL)
    # Feathers on the belly: three little smiles.
    for dx, dy in ((-10, 14), (10, 14), (0, 26)):
        shapes.circle(display, cx + s(dx), cy + s(dy), s(5), BROWN, 0,
                      shapes.BOTTOM_HALF)
    # Feet.
    for side in (-1, 1):
        display.fill_rect(cx + side * s(12) - s(6), cy + s(44), s(12), s(5),
                          ORANGE)


def speaker(display, cx, cy):
    x = cx - 22
    display.fill_rect(x - 18, cy - 14, 18, 29, GRAY)
    shapes.poly(display, 0, 0, array('h', [x, cy - 14, x + 22, cy - 34,
                                           x + 22, cy + 34, x, cy + 14]),
                WHITE, FILL)
    for r, color in ((16, config.CYAN), (28, config.CYAN), (40, config.CYAN)):
        for step in range(3):
            shapes.circle(display, x + 22, cy, r + step, color, 0,
                          shapes.TOP_RIGHT + shapes.BOTTOM_RIGHT)


def mic(display, cx, cy):
    color = WHITE
    shapes.circle(display, cx, cy - 26, 15, color, FILL)
    display.fill_rect(cx - 15, cy - 26, 31, 24, color)
    shapes.circle(display, cx, cy - 2, 15, color, FILL)
    for step in range(3):
        shapes.circle(display, cx, cy - 4, 25 + step, GRAY, 0,
                      shapes.BOTTOM_HALF)
    display.fill_rect(cx - 1, cy + 22, 4, 16, GRAY)
    display.fill_rect(cx - 18, cy + 38, 37, 5, GRAY)
    # Meter bars on each side: the VU meter.
    for i, height in enumerate((10, 22, 34)):
        color = (config.GREEN, config.YELLOW, config.RED)[i]
        display.fill_rect(cx + 34 + i * 10, cy + 10 - height, 7, height,
                          color)
        display.fill_rect(cx - 40 - i * 10, cy + 10 - height, 7, height,
                          color)


def record(display, cx, cy):
    shapes.circle(display, cx, cy, 42, WHITE, FILL)
    shapes.circle(display, cx, cy, 37, BLACK, FILL)
    shapes.circle(display, cx, cy, 26, config.RED, FILL)
    display.text(config.SMALL_FONT, "REC", cx - 12, cy - 8, WHITE,
                 config.RED)


def quote(display, cx, cy):
    """Two big curly quotation marks."""
    for x in (cx - 22, cx + 22):
        shapes.circle(display, x, cy - 6, 16, GOLD, FILL)
        shapes.triangle(display, x + 2, cy + 4, x + 16, cy - 2,
                        x - 10, cy + 34, GOLD, FILL)


def bubble(display, cx, cy):
    """A speech bubble that says Hola! in Spain's red and gold."""
    shapes.ellipse(display, cx, cy - 6, 48, 32, GOLD, FILL)
    shapes.ellipse(display, cx, cy - 6, 48, 32, SPAIN_RED, 0)
    shapes.triangle(display, cx - 26, cy + 18, cx - 8, cy + 22,
                    cx - 36, cy + 42, GOLD, FILL)
    display.text(config.BIG_FONT, "Hola!", cx - 40, cy - 22, SPAIN_RED, GOLD)


def book(display, cx, cy):
    page = WHITE
    shapes.poly(display, 0, 0, array('h', [cx - 46, cy - 26, cx - 2, cy - 20,
                                           cx - 2, cy + 34, cx - 46, cy + 28]),
                page, FILL)
    shapes.poly(display, 0, 0, array('h', [cx + 2, cy - 20, cx + 46, cy - 26,
                                           cx + 46, cy + 28, cx + 2, cy + 34]),
                page, FILL)
    display.fill_rect(cx - 2, cy - 22, 4, 58, SKY)
    for i in range(5):
        y = cy - 12 + i * 8
        display.line(cx - 40, y - 1, cx - 8, y + 3, GRAY)
        display.line(cx + 8, y + 3, cx + 40, y - 1, GRAY)


ICONS = {
    "clock": clock, "bell": bell, "hourglass": hourglass,
    "stopwatch": stopwatch, "owl": owl, "speaker": speaker, "mic": mic,
    "record": record, "quote": quote, "bubble": bubble, "book": book,
}


def draw(name, display, cx, cy):
    ICONS[name](display, cx, cy)
