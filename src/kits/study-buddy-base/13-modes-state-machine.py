# Lab 13: Modes as a State Machine
# Three buttons, but many jobs: MODE steps between three modes, and UP and
# DOWN do something different in each one.
#
#   COLOR   UP / DOWN change the ring's color
#   COUNT   UP / DOWN count up and down
#   DICE    UP rolls one die, DOWN rolls two
#
# THE IDEA: A STATE MACHINE. The program keeps one variable, `state`, that
# says which mode it is in. Each state is a small table entry with two
# functions:
#
#   enter()       draw the screen for this state, once, when we arrive
#   button(name)  what UP or DOWN means in this state
#
# The main loop does not care which state it is in. It finds the edge of a
# button press and hands it to the current state's button() function.
# Adding a fourth mode means writing two small functions and adding one
# line to STATES -- nothing else changes. Every watch, microwave, and phone
# menu works this way, and so does the demo in 20-demo-template.py.
#
# Parts: the buttons and the display.
#
# PASS: MODE moves the highlight along the top from COLOR to COUNT to DICE
# and back, and UP and DOWN do the right thing in each mode.

NAME = "13-modes-state-machine.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import random
import time

import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
pins = config.init_buttons()

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(110, 110, 110)
CX = config.CENTER_X
CY = config.CENTER_Y + 20
DEBOUNCE_MS = 40


def put(text, y, color, font=SMALL, width=26):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


def clear_stage():
    """Blank the area the states draw in (everything under the tabs)."""
    display.fill_rect(30, 80, 300, 230, config.BLACK)


# ---------------------------------------------------------------------
# State: COLOR
# ---------------------------------------------------------------------
COLORS = (("red", config.RED), ("orange", config.color565(255, 140, 0)),
          ("yellow", config.YELLOW), ("green", config.GREEN),
          ("cyan", config.CYAN), ("blue", config.BLUE),
          ("magenta", config.MAGENTA), ("white", config.WHITE))
color_index = 0


def color_enter():
    clear_stage()
    color_show()


def color_show():
    name, color = COLORS[color_index]
    shapes.circle(display, CX, CY, 70, color, config.FILL)
    put(name, 280, color, SMALL, 12)


def color_button(name):
    global color_index
    color_index = (color_index + (1 if name == "UP" else -1)) % len(COLORS)
    color_show()


# ---------------------------------------------------------------------
# State: COUNT
# ---------------------------------------------------------------------
count = 0


def count_enter():
    clear_stage()
    put("UP +1   DOWN -1", 270, DIM)
    count_show()


def count_show():
    put(str(count), CY - 16, config.WHITE, BIG, 6)


def count_button(name):
    global count
    count += 1 if name == "UP" else -1
    count_show()


# ---------------------------------------------------------------------
# State: DICE
# ---------------------------------------------------------------------
# Where the pips go on a die face, in thirds of its width: (column, row).
PIPS = {1: ((1, 1),), 2: ((0, 0), (2, 2)), 3: ((0, 0), (1, 1), (2, 2)),
        4: ((0, 0), (2, 0), (0, 2), (2, 2)),
        5: ((0, 0), (2, 0), (1, 1), (0, 2), (2, 2)),
        6: ((0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2))}
DIE = 80


def draw_die(x, y, value):
    display.fill_rect(x, y, DIE, DIE, config.WHITE)
    for column, row in PIPS[value]:
        shapes.circle(display, x + 16 + column * 24, y + 16 + row * 24, 7,
                      config.BLACK, config.FILL)


def dice_enter():
    clear_stage()
    put("UP: one die  DOWN: two", 282, DIM)


def dice_button(name):
    display.fill_rect(40, CY - DIE // 2, 280, DIE, config.BLACK)
    if name == "UP":
        value = random.randint(1, 6)
        draw_die(CX - DIE // 2, CY - DIE // 2, value)
        put("you rolled %d" % value, 254, config.YELLOW)
    else:
        a, b = random.randint(1, 6), random.randint(1, 6)
        draw_die(CX - DIE - 10, CY - DIE // 2, a)
        draw_die(CX + 10, CY - DIE // 2, b)
        put("%d + %d = %d" % (a, b, a + b), 254, config.YELLOW)


# ---------------------------------------------------------------------
# The machine: one table, one variable, one loop.
# ---------------------------------------------------------------------
STATES = (("COLOR", color_enter, color_button),
          ("COUNT", count_enter, count_button),
          ("DICE", dice_enter, dice_button))
state = 0


def draw_tabs():
    """The state names along the top, the current one highlighted."""
    x = CX - (len(STATES) * 7 * SMALL.WIDTH) // 2
    for i, (name, _, _) in enumerate(STATES):
        label = name.center(7)
        color = config.BLACK if i == state else DIM
        background = config.CYAN if i == state else config.BLACK
        display.text(SMALL, label, x + i * 7 * SMALL.WIDTH, 52, color,
                     background)


def go_to(new_state):
    global state
    state = new_state
    print("state ->", STATES[state][0])
    draw_tabs()
    STATES[state][1]()              # the new state's enter()


random.seed(time.ticks_us())
go_to(0)
last = [1, 1, 1]
changed_at = [0, 0, 0]
while True:
    now = time.ticks_ms()
    for i, name in enumerate(("MODE", "UP", "DOWN")):
        value = pins[i].value()
        if value != last[i] and time.ticks_diff(now, changed_at[i]) > DEBOUNCE_MS:
            last[i] = value
            changed_at[i] = now
            if value == 0:                       # a press
                if name == "MODE":
                    go_to((state + 1) % len(STATES))
                else:
                    STATES[state][2](name)       # the state's button()
    time.sleep_ms(5)

# Try This
#   1. Add a fourth state, "COIN": UP flips a coin and shows HEADS or TAILS.
#      Write coin_enter() and coin_button(), and add one line to STATES.
#   2. The count survives leaving and coming back to COUNT. Why? Make it
#      reset to 0 every time you enter the state instead.
#   3. Make a long press of MODE (over a second) go BACKWARDS through the
#      states. Where in the loop would you measure how long it was held?
