# Lab 19: Pattern Memory Game -- Putting It All Together
# The buddy lights up a pattern of colored wedges, each with its own note.
# Repeat it with the buttons. Each round the pattern gets one step longer
# and a little faster. How long a pattern can you remember?
#
#   MODE = the red wedge (top)    UP = the green wedge    DOWN = the blue wedge
#
# THE IDEA: ONE PROGRAM, EVERY PART. This lab uses what labs 08 to 15
# taught, all at once:
#
#   * a STATE MACHINE (lab 13): READY -> SHOW -> LISTEN -> SHOW ... -> OVER
#   * a LIST as the game's memory: `pattern` grows by one random step a round
#   * ANGLES TO PIXELS (lab 09) to build each wedge
#   * SEND ONLY WHAT CHANGED (lab 10): a wedge is worked out once into a
#     list of horizontal runs, so lighting it later is just replaying them
#   * EDGES AND DEBOUNCE (lab 11) for the buttons
#   * NOT WAITING (lab 12): while you play, the loop never sleeps for long,
#     so a quick second press is never missed
#   * SAMPLES MAKE SOUND (lab 14): each wedge's note is made at the start
#
# The three notes are C5, E5, and G5: a C major chord, so any pattern
# sounds like a little tune.
#
# Parts: everything -- the display, the buttons, the speaker (and the LED,
# which lights while it is your turn).
#
# PASS: a pattern plays, the buttons light and sound their wedges, a right
# answer goes on to a longer pattern, and a wrong one (or 5 seconds of
# waiting) ends the game with your score.

NAME = "19-pattern-game.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import random
import struct
import time
from array import array
from machine import I2S, Pin

import config
import shapes

RATE = 16000
TONE_MS = 300            # how long a wedge sounds while the buddy shows it
PRESS_MS = 200           # ...and when you press it
DEBOUNCE_MS = 40
TIMEOUT_MS = 5000        # this long without a press ends the game
FIRST_GAP_MS = 300       # the pause between steps, shrinking every round
LEAST_GAP_MS = 60

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
CX = config.CENTER_X
CY = config.CENTER_Y
INNER = 82
OUTER = config.SAFE_RADIUS - 4

# One wedge per button: (name, middle angle, bright color, dim color, Hz).
WEDGES = (("MODE", 0, config.RED, config.color565(70, 0, 0), 523),
          ("UP", 120, config.GREEN, config.color565(0, 70, 0), 659),
          ("DOWN", 240, config.BLUE, config.color565(0, 0, 90), 784))

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
pins = config.init_buttons()
led = config.init_led()
config.set_gain()
audio = I2S(config.I2S_SPEAKER_ID, sck=Pin(config.I2S_BCLK_PIN),
            ws=Pin(config.I2S_LRC_PIN), sd=Pin(config.I2S_DIN_PIN),
            mode=I2S.TX, bits=16, format=I2S.MONO, rate=RATE, ibuf=8192)


# ---------------------------------------------------------------------
# Pictures: each wedge worked out ONCE into horizontal runs
# ---------------------------------------------------------------------
class RunRecorder:
    """Stands in for the display while shapes.poly() fills a shape, and
    keeps the horizontal runs it would have drawn."""

    def __init__(self):
        self.runs = []

    def hline(self, x, y, length, color):
        self.runs.append((x, y, length))


def wedge_runs(middle):
    """The runs of a ring-shaped wedge 110 degrees wide around `middle`."""
    corners = []
    for step in range(23):                       # the outer edge, 5 degrees apart
        a = math.radians(middle - 55 + step * 5)
        corners += [round(CX + OUTER * math.sin(a)),
                    round(CY - OUTER * math.cos(a))]
    for step in range(23):                       # the inner edge, back again
        a = math.radians(middle + 55 - step * 5)
        corners += [round(CX + INNER * math.sin(a)),
                    round(CY - INNER * math.cos(a))]
    recorder = RunRecorder()
    shapes.poly(recorder, 0, 0, array('h', corners), 0, config.FILL)
    return recorder.runs


def paint(which, lit):
    name, middle, bright, dim, freq = WEDGES[which]
    color = bright if lit else dim
    for x, y, length in runs[which]:
        display.hline(x, y, length, color)


def put(text, y, color, font=SMALL, width=14):
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color)


def center(top, middle, bottom, color=config.WHITE):
    """The three lines in the middle of the screen."""
    put(top, CY - 44, DIM)
    put(middle, CY - 16, color, BIG, 6)
    put(bottom, CY + 22, config.YELLOW)


# ---------------------------------------------------------------------
# Sounds: made once at the start
# ---------------------------------------------------------------------
def tone(freq, ms, wave="sine"):
    count = RATE * ms // 1000
    fade = RATE // 100
    peak = 32767 * config.VOLUME / 100
    buf = bytearray(count * 2)
    for i in range(count):
        phase = freq * i / RATE
        if wave == "sine":
            v = math.sin(2 * math.pi * phase)
        else:
            v = 0.5 if phase % 1 < 0.5 else -0.5   # a buzzy square wave
        level = min(1.0, i / fade, (count - i) / fade)
        struct.pack_into("<h", buf, i * 2, int(peak * v * level))
    return buf


put("getting ready", CY - 16, DIM)
runs = [wedge_runs(w[1]) for w in WEDGES]
show_tones = [tone(w[4], TONE_MS) for w in WEDGES]
press_tones = [tone(w[4], PRESS_MS) for w in WEDGES]
buzz = tone(110, 600, "square")
put("", CY - 16, DIM)            # clear "getting ready"

for i in range(3):
    paint(i, False)


def flash(which, sound, ms):
    """Light a wedge and play its note, then put it out. The light stays
    on for as long as the note plays."""
    paint(which, True)
    started = time.ticks_ms()
    audio.write(sound)            # returns once the sound is in the buffer
    left = ms - time.ticks_diff(time.ticks_ms(), started)
    if left > 0:
        time.sleep_ms(left)
    paint(which, False)


# ---------------------------------------------------------------------
# The game: a state machine
# ---------------------------------------------------------------------
READY, SHOW, LISTEN, OVER = range(4)
state = READY
pattern = []                     # the game's memory: wedge numbers
position = 0                     # how far through the pattern you are
best = 0
last_press = 0
over_at = 0                      # when the last game ended
lit = None                       # the wedge lit by your press, if any
lit_until = 0
last = [1, 1, 1]
changed_at = [0, 0, 0]
random.seed(time.ticks_us())


def pressed(now):
    """The number of a button that just went down, or None."""
    for i in range(3):
        value = pins[i].value()
        if value != last[i] and time.ticks_diff(now, changed_at[i]) > DEBOUNCE_MS:
            last[i] = value
            changed_at[i] = now
            if value == 0:
                return i
    return None


def ready():
    global state
    state = READY
    led.value(0)
    center("best %d" % best, "READY", "press a button")


def start_game():
    global state, pattern
    pattern = []
    state = SHOW
    time.sleep_ms(400)


def game_over(now):
    global state, best, over_at
    led.value(0)
    best = max(best, len(pattern) - 1)
    center("GAME OVER", str(len(pattern) - 1), "best %d" % best, config.RED)
    print("Game over: {} right. Best: {}".format(len(pattern) - 1, best))
    audio.write(buzz)
    # Show the step you should have pressed.
    for _ in range(3):
        flash(pattern[position], press_tones[pattern[position]], 150)
        time.sleep_ms(100)
    over_at = time.ticks_ms()
    state = OVER


ready()
try:
    while True:
        now = time.ticks_ms()
        button = pressed(now)

        if state == READY:
            if button is not None:
                start_game()

        elif state == OVER:
            # Ignore presses for a second (the wrong press may still be
            # bouncing), then a press starts again. Untouched, go to READY.
            waited = time.ticks_diff(now, over_at)
            if button is not None and waited > 1000:
                start_game()
            elif waited > 4000:
                ready()

        elif state == SHOW:
            pattern.append(random.randrange(3))
            round_number = len(pattern)
            center("ROUND", str(round_number), "watch...")
            print("Round {}: {}".format(round_number,
                                        " ".join(WEDGES[w][0] for w in pattern)))
            time.sleep_ms(500)
            gap = max(LEAST_GAP_MS, FIRST_GAP_MS - 20 * round_number)
            for step in pattern:
                flash(step, show_tones[step], TONE_MS)
                time.sleep_ms(gap)
            center("ROUND", str(round_number), "your turn")
            led.value(1)
            position = 0
            last_press = time.ticks_ms()
            state = LISTEN

        elif state == LISTEN:
            if lit is not None and time.ticks_diff(now, lit_until) >= 0:
                paint(lit, False)
                lit = None
            if button is not None:
                if lit is not None:
                    paint(lit, False)
                last_press = now
                if button != pattern[position]:
                    lit = None
                    game_over(now)
                    continue
                paint(button, True)
                audio.write(press_tones[button])
                lit = button
                lit_until = time.ticks_add(now, PRESS_MS)
                position += 1
                if position == len(pattern):        # the whole pattern: right!
                    time.sleep_ms(PRESS_MS)
                    paint(button, False)
                    lit = None
                    led.value(0)
                    time.sleep_ms(500)
                    state = SHOW
            elif time.ticks_diff(now, last_press) > TIMEOUT_MS:
                game_over(now)

        time.sleep_ms(2)
finally:
    led.value(0)
    audio.deinit()

# Try This
#   1. Add a fourth wedge? There are only three buttons -- but a long press
#      could be a fourth. What would have to change in WEDGES and pressed()?
#   2. Make the game end on the first mistake of a pattern you have already
#      seen twice. (Hint: you need to remember each round's result.)
#   3. Save the best score to a file (open("best.txt", "w")) so it survives
#      a power cycle. Read it back at the start.
