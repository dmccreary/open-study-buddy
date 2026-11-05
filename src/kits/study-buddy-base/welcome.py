# welcome.py -- the welcome screen of 20-demo-template.py.
#
# The first screen of the showcase (mode 0), so it is the first thing on
# the glass at power-up: "Study Buddy Kit" across the top and a list of
# the parts in the kit. The showcase comes back to it after the last demo
# screen, and adds the "Hold any button" hint and the row of dots under
# it.
#
#     import welcome
#     welcome.show(display)
#
# To run it on its own, as a quick "is the display alive" check:
#     mpremote run welcome.py

import config
import shapes

TITLE = "Study Buddy Kit"

# (part, what it is), one line each. Keep each line to 28 letters or
# fewer: the list sits in the middle of the round glass, where a line of
# the small font holds about 36.
PARTS = (
    ("Pico 2 W", "the brain, with WiFi"),
    ("Display", "2.1 in round, 360x360"),
    ("Buttons", "MODE, UP, DOWN"),
    ("Speaker", "MAX98357A amplifier"),
    ("Microphone", "INMP441, digital"),
)

TITLE_COLOR = config.CYAN
PART_COLOR = config.YELLOW
TEXT_COLOR = config.WHITE
RULE_COLOR = config.color565(60, 60, 70)
BULLET_COLORS = (config.GREEN, config.CYAN, config.YELLOW, config.MAGENTA,
                 config.color565(255, 150, 40))

TITLE_Y = 66            # the big font's 240 px only fit this far down
RULE_Y = 108
LIST_Y = 124
LIST_PITCH = 28
NAME_CHARS = 11         # the part names line up in one column


def show(display):
    """Draw the whole welcome screen (it clears the screen first)."""
    small = config.SMALL_FONT
    display.fill(config.BLACK)
    config.centered_text(display, config.BIG_FONT, TITLE, TITLE_Y,
                         TITLE_COLOR)
    display.hline(config.CENTER_X - 100, RULE_Y, 200, RULE_COLOR)

    # Every line is the same width, so the column of part names and the
    # column of descriptions both line up.
    width = NAME_CHARS + max(len(text) for _, text in PARTS)
    left = config.CENTER_X - width * small.WIDTH // 2 + 6
    for i, (part, text) in enumerate(PARTS):
        y = LIST_Y + i * LIST_PITCH
        shapes.circle(display, left - 10, y + small.HEIGHT // 2, 3,
                      BULLET_COLORS[i % len(BULLET_COLORS)], config.FILL)
        display.text(small, part, left, y, PART_COLOR, config.BLACK)
        display.text(small, text, left + NAME_CHARS * small.WIDTH, y,
                     TEXT_COLOR, config.BLACK)


if __name__ == "__main__":
    screen = config.init_display()
    config.set_backlight(True)
    show(screen)
    print("Drawn: look at the screen.")
