# demo_timer.py -- demo 3 of 20-demo-template.py: a countdown timer.
#
# Big digits, and a ring of 60 ticks that empties as the time runs out.
# The last ten seconds turn red, and at zero the speaker chimes until a
# button is pressed.
#
#   Ready:     UP start          DOWN next preset     MODE set your own
#   Running:   UP pause                               MODE pause
#   Paused:    UP go on          DOWN reset
#   Setting:   UP+ / DOWN- (hold to go faster)        MODE minutes -> seconds -> done
#   Time's up: any button
#
# The presets are a quick demo, a minute, a short break, and a 25-minute
# "pomodoro" homework sprint.
#
# This is the timer of the sw-gc9b72 kit (clocks-and-watches repository,
# lab 11 and mode_timer.py), changed to set with a short MODE press, to
# chime on the speaker instead of a buzzer, and with presets.
#
# Leaving the demo does not stop a running timer: stop() hands back
# "wake_at", and 20-demo-template.py brings this demo back at zero.

import time
from array import array

import config
from demo_kit import (BLACK, WHITE, DIM, SMALL, CX, CY, Looper, menu_hint,
                      make_speaker)
from watchparts import Digit, TickRing, TextLine, DIGITS, BLANK

PRESETS = ((0, 15), (1, 0), (5, 0), (25, 0))     # (minutes, seconds)
WARNING_MS = 10_000
FLASH_MS = 500

SETTING_COLOR = config.YELLOW
WARNING_COLOR = config.RED
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)

SET_MINUTES, SET_SECONDS, READY, RUNNING, PAUSED, DONE = range(6)
STATE_NAMES = ("SET MINUTES", "SET SECONDS", "READY", "RUNNING", "PAUSED",
               "TIME'S UP!")
STATE_COLORS = (SETTING_COLOR, SETTING_COLOR, DIM, config.GREEN,
                config.YELLOW, WARNING_COLOR)
HINTS = ("UP+  DOWN-  MODE next", "UP+  DOWN-  MODE done",
         "UP start  DOWN preset", "UP pause", "UP go  DOWN reset",
         "any button: stop")

DIGIT_W, DIGIT_H, DIGIT_T = 50, 100, 12
PAIR_GAP = 10
COLON_GAP = 12
DIGIT_TOP = CY - DIGIT_H // 2
TITLE_Y = 50
HINT_Y = 76
STATE_Y = 100
NOTE_Y = DIGIT_TOP + DIGIT_H + 14
MENU_Y = 292


def start(display, kit, saved):
    global _kit, digits, hint, status, note, ring, speaker, looper
    global state, preset, set_minutes, set_seconds, remaining_ms, end_ticks
    global done_at, shown_state, shown_flash
    _kit = kit
    display.fill(BLACK)

    row = 4 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
    x = (config.WIDTH - row) // 2
    digit_x = (x, x + DIGIT_W + PAIR_GAP,
               x + 2 * DIGIT_W + PAIR_GAP + 2 * COLON_GAP + DIGIT_T,
               x + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T)
    colon_x = x + 2 * DIGIT_W + PAIR_GAP + COLON_GAP
    digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                    WHITE, GHOST) for x in digit_x]
    for y in (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
              DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2):
        display.fill_rect(colon_x, y, DIGIT_T, DIGIT_T, WHITE)

    TextLine(display, SMALL, CX, TITLE_Y, 5, DIM).show("TIMER")
    hint = TextLine(display, SMALL, CX, HINT_Y, 23, DIM)
    status = TextLine(display, SMALL, CX, STATE_Y, 11, DIM)
    note = TextLine(display, SMALL, CX, NOTE_Y, 18, DIM)
    menu_hint(display, MENU_Y)
    ring = TickRing(display, CX, CY, config.SAFE_RADIUS - 2,
                    config.SAFE_RADIUS - 10, config.SAFE_RADIUS - 16)

    if saved is None:
        state = READY
        preset = 0
        set_minutes, set_seconds = PRESETS[0]
        remaining_ms = total_ms()
        end_ticks = 0
    else:
        state = saved["state"]
        preset = saved["preset"]
        set_minutes = saved["set_minutes"]
        set_seconds = saved["set_seconds"]
        remaining_ms = saved["remaining_ms"]
        end_ticks = saved["end_ticks"]
    speaker = make_speaker()
    looper = None
    done_at = 0
    shown_state = None
    shown_flash = None


def total_ms():
    return (set_minutes * 60 + set_seconds) * 1000


def chime():
    """C6, E6, G6, then a rest: about 1 s, looped until a button."""
    whole = array('h')
    for freq in (1047, 1319, 1568):
        whole.extend(speaker.tone(freq, 140))
    whole.extend(speaker.tone(0, 550))
    return whole


def finish(now):
    global state, done_at, looper
    state = DONE
    done_at = now
    if speaker is not None:
        looper = Looper(speaker, chime())


def reset():
    global state, remaining_ms, looper
    looper = None
    remaining_ms = total_ms()
    state = READY


def on_mode():
    global state, remaining_ms
    if state == DONE:
        reset()
    elif state == SET_MINUTES:
        state = SET_SECONDS
    elif state == SET_SECONDS:
        reset()
    elif state == RUNNING:
        pause(time.ticks_ms())
    else:                                   # READY or PAUSED
        state = SET_MINUTES


def holds_buttons():
    """While setting, holding UP or DOWN counts fast -- so a long hold
    must not skip to another demo."""
    return state == SET_MINUTES or state == SET_SECONDS


def pause(now):
    global state, remaining_ms
    remaining_ms = max(0, time.ticks_diff(end_ticks, now))
    state = PAUSED


def show_digits(minutes, seconds, colors):
    values = (minutes // 10, minutes % 10, seconds // 10, seconds % 10)
    for i in range(4):
        digits[i].show(DIGITS[values[i]], colors[i // 2])


def show_ring(lit):
    for second in range(60):
        ring.paint(second, ACCENT if second < lit else TICK_OFF)


def update(now):
    global state, preset, set_minutes, set_seconds, remaining_ms, end_ticks
    global shown_state, shown_flash
    setting = state == SET_MINUTES or state == SET_SECONDS
    up = _kit.up.pressed(now, repeat=setting)
    down = _kit.down.pressed(now, repeat=setting)

    if setting:
        step = 1 if up else -1 if down else 0
        if state == SET_MINUTES:
            set_minutes = (set_minutes + step) % 100
        else:
            set_seconds = (set_seconds + step) % 60
    elif state == READY:
        if up and total_ms() > 0:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif down:
            preset = (preset + 1) % len(PRESETS)
            set_minutes, set_seconds = PRESETS[preset]
            remaining_ms = total_ms()
            shown_state = None              # repaint the "Set to" note
    elif state == RUNNING:
        remaining_ms = max(0, time.ticks_diff(end_ticks, now))
        if up:
            pause(now)
        elif remaining_ms == 0:
            finish(now)
    elif state == PAUSED:
        if up:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif down:
            reset()
    elif state == DONE:
        if up or down:
            reset()

    if state == SET_MINUTES or state == SET_SECONDS:
        show_digits(set_minutes, set_seconds,
                    (SETTING_COLOR if state == SET_MINUTES else WHITE,
                     SETTING_COLOR if state == SET_SECONDS else WHITE))
        show_ring(60 if total_ms() > 0 else 0)
    elif state == DONE:
        flash = (time.ticks_diff(now, done_at) // FLASH_MS) % 2 == 0
        if flash != shown_flash:
            for digit in digits:
                digit.show(DIGITS[0] if flash else BLANK, WARNING_COLOR)
            shown_flash = flash
        show_ring(0)
    else:
        seconds_left = (remaining_ms + 999) // 1000
        warn = state == RUNNING and remaining_ms <= WARNING_MS
        color = WARNING_COLOR if warn else WHITE
        show_digits(seconds_left // 60, seconds_left % 60, (color, color))
        total = total_ms()
        show_ring((remaining_ms * 60 + total - 1) // total if total else 0)

    if state != shown_state:
        status.show(STATE_NAMES[state], STATE_COLORS[state])
        hint.show(HINTS[state])
        if state == DONE:
            note.show("Press any button")
        elif state == SET_MINUTES or state == SET_SECONDS:
            note.show("Hold to go faster")
        else:
            note.show("Set to %02d:%02d" % (set_minutes, set_seconds))
        if state != DONE:
            shown_flash = None
        shown_state = state

    if looper is not None:
        looper.update()


def stop():
    """Keep the timer. A running one also says when it reaches zero."""
    if speaker is not None:
        speaker.deinit(finish=False)      # leaving: no need to wait
    saved = {"state": DONE if state == DONE else state, "preset": preset,
             "set_minutes": set_minutes, "set_seconds": set_seconds,
             "remaining_ms": remaining_ms, "end_ticks": end_ticks}
    if state == DONE:                       # leaving silences it for good
        saved["state"] = READY
        saved["remaining_ms"] = total_ms()
    if state == RUNNING:
        saved["wake_at"] = end_ticks
    return saved
