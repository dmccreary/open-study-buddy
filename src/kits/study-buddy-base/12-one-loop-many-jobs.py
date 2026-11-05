# Lab 12: One Loop, Many Jobs
# Four jobs run at once, each at its own speed: the LED blinks, a dot
# spins around the rim, a clock counts seconds, and the buttons change the
# blink speed. There is no time.sleep() anywhere that matters.
#
# THE IDEA: CHECK THE CLOCK, DON'T WAIT FOR IT. time.sleep(0.5) freezes the
# whole Pico for half a second -- no spinning, no buttons. Instead each job
# remembers WHEN it should next run. The loop goes round thousands of times
# a second, and on each pass asks every job "is it your time yet?":
#
#     if time.ticks_diff(now, next_blink) >= 0:     # time to blink?
#         led.value(not led.value())
#         next_blink = time.ticks_add(next_blink, blink_ms)
#
# ticks_diff() and ticks_add() instead of plain - and +: the millisecond
# counter wraps back to zero after a while, and these two get the answer
# right across the wrap.
#
#   UP     blink faster        DOWN   blink slower
#   MODE   turn on "sleep mode": the loop calls time.sleep(0.5) each pass,
#          the way a first program usually would. Watch the spinner stutter
#          and the buttons stop answering. Press MODE (and hold it, since
#          the loop only looks every half second) to turn it off again.
#
# Parts: the LED, the buttons, and the display.
#
# PASS: the LED blinks, the dot spins smoothly, and the seconds count up,
# all at once. "loops per second" is in the thousands -- until you turn on
# sleep mode, when it drops to 2.

NAME = "12-one-loop-many-jobs.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config
import shapes

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
led = config.init_led()
mode_pin, up_pin, down_pin = config.init_buttons()

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
CX = config.CENTER_X
CY = config.CENTER_Y
SPIN_RADIUS = 150
SPIN_STEPS = 36                     # positions around the rim


def put(text, y, color, font=SMALL, width=26):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


put("ONE LOOP, MANY JOBS", 60, DIM)
put("UP faster  DOWN slower", 250, DIM)
put("MODE: sleep mode", 270, DIM)

# Each job: how often it runs (ms), and when it should run next.
now = time.ticks_ms()
blink_ms, next_blink = 500, now
spin_ms, next_spin = 50, now
clock_ms, next_clock = 1000, now
buttons_ms, next_buttons = 20, now
report_ms, next_report = 1000, now

spin_step = 0
seconds = 0
loops = 0
sleep_mode = False
last = [1, 1, 1]                    # last reading of MODE, UP, DOWN

while True:
    now = time.ticks_ms()
    loops += 1

    # Job 1: blink the LED.
    if time.ticks_diff(now, next_blink) >= 0:
        led.value(not led.value())
        next_blink = time.ticks_add(next_blink, blink_ms)

    # Job 2: move the spinning dot one step around the rim.
    if time.ticks_diff(now, next_spin) >= 0:
        for step, color in ((spin_step, config.BLACK),
                            ((spin_step + 1) % SPIN_STEPS, config.CYAN)):
            a = 2 * math.pi * step / SPIN_STEPS
            shapes.circle(display, round(CX + SPIN_RADIUS * math.sin(a)),
                          round(CY - SPIN_RADIUS * math.cos(a)), 6, color,
                          config.FILL)
        spin_step = (spin_step + 1) % SPIN_STEPS
        next_spin = time.ticks_add(next_spin, spin_ms)

    # Job 3: count seconds.
    if time.ticks_diff(now, next_clock) >= 0:
        put("%d s" % seconds, 104, config.WHITE, BIG, 8)
        seconds += 1
        next_clock = time.ticks_add(next_clock, clock_ms)

    # Job 4: read the buttons (a press is a 1 -> 0 edge).
    if time.ticks_diff(now, next_buttons) >= 0:
        for i, pin in enumerate((mode_pin, up_pin, down_pin)):
            value = pin.value()
            if value == 0 and last[i] == 1:
                if i == 0:
                    sleep_mode = not sleep_mode
                elif i == 1:
                    blink_ms = max(50, blink_ms // 2)
                else:
                    blink_ms = min(2000, blink_ms * 2)
                put("blink every %d ms" % blink_ms, 150, config.YELLOW)
                put("SLEEP MODE ON" if sleep_mode else "", 220, config.RED)
            last[i] = value
        next_buttons = time.ticks_add(next_buttons, buttons_ms)

    # Job 5: report how many times the loop went round in the last second.
    if time.ticks_diff(now, next_report) >= 0:
        put("%d loops per second" % loops, 186, config.GREEN)
        print("loops per second:", loops)
        loops = 0
        next_report = time.ticks_add(next_report, report_ms)

    if sleep_mode:
        time.sleep(0.5)             # the "obvious" way -- freezes everything

# Try This
#   1. Add a sixth job: every 3000 ms, print("still here"). You only need
#      three lines: a next_ time, an if, and a ticks_add.
#   2. Change job 2's ticks_add(next_spin, ...) to ticks_add(now, ...). Turn
#      on sleep mode, then off. What is different? (Which one "catches up"?)
#   3. Make blink_ms 5. What does loops per second do? Is the Pico working
#      harder, or just going round the loop more?
