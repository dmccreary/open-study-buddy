# demo_alarm.py -- demo 2 of 20-demo-template.py: an alarm clock.
#
# The time across the top, the alarm time under it. The alarm starts out
# set for one minute from now, so anyone trying the demo hears it ring.
#
#   Showing the time:
#     MODE (short)   set the alarm: hour first
#     UP             alarm on / off
#     DOWN           hear the alarm (a 4-second test)
#   Setting the alarm:
#     UP / DOWN      add / take away one (hold to go faster)
#     MODE (short)   hour -> minute -> done (setting it turns the alarm on)
#   Ringing:
#     UP             snooze for SNOOZE_MINUTES
#     DOWN or MODE   stop
#
# Leave the demo with the alarm on and it still rings: stop() hands back
# "wake_at", the moment the alarm is due, and 20-demo-template.py brings
# this demo back on screen at that moment, whatever is showing.
#
# The time comes from the Pico's clock. Demo 1 (Clock+Weather) sets it
# from the internet; Thonny also sets it whenever it connects.

import time

import config
from demo_kit import (BLACK, WHITE, DIM, SMALL, BIG, CX, Looper, put,
                      centered, menu_hint, make_speaker)
from watchparts import Digit, TextLine, DIGITS, BLANK

TWELVE_HOUR = True
SNOOZE_MINUTES = 1
RING_SECONDS = 60
TEST_SECONDS = 4
FLASH_MS = 400

GHOST = config.color565(24, 24, 30)
SETTING_COLOR = config.YELLOW
ON_COLOR = config.GREEN
OFF_COLOR = config.color565(120, 120, 120)
RING_COLOR = config.RED
ACCENT = config.CYAN

SHOWING, SET_HOUR, SET_MINUTE, RINGING = range(4)
HINTS = (("UP on/off   DOWN test", "MODE: set the alarm"),
         ("UP+  DOWN-  the hour", "MODE: next"),
         ("UP+  DOWN-  the minute", "MODE: done"),
         ("UP snooze  DOWN stop", ""))

DIGIT_W, DIGIT_H, DIGIT_T = 36, 68, 8
PAIR_GAP = 7
COLON_GAP = 8
TITLE_Y = 34
DIGIT_TOP = 58
LABEL_Y = 140
ALARM_Y = 160
STATUS_Y = 202
HINT_Y = 232
HINT2_Y = 254
MENU_Y = 296


def start(display, kit, saved):
    global _display, _kit, speaker, digits, colon_x, colon_y, ampm
    global hour_line, minute_line, alarm_ampm, status_line, hints
    global alarm_hour, alarm_minute, alarm_on, fired, state, shown
    global ring_until, ring_test, looper, flash_shown, shown_second
    _display = display
    _kit = kit
    display.fill(BLACK)
    centered(display, SMALL, "ALARM CLOCK", TITLE_Y, DIM)

    # The time, as in demo 1: a half digit for the 1 of 10, 11, and 12.
    first_width = DIGIT_T if TWELVE_HOUR else DIGIT_W
    ampm_width = 6 + 2 * SMALL.WIDTH if TWELVE_HOUR else 0
    row = first_width + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
    x = (config.WIDTH - row - ampm_width) // 2
    digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T, WHITE,
                    GHOST, half=TWELVE_HOUR)]
    x += first_width + PAIR_GAP
    digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                        WHITE, GHOST))
    x += DIGIT_W + COLON_GAP
    colon_x = x
    x += DIGIT_T + COLON_GAP
    for _ in range(2):
        digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                            WHITE, GHOST))
        x += DIGIT_W + PAIR_GAP
    colon_y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
               DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)
    for y in colon_y:
        display.fill_rect(colon_x, y, DIGIT_T, DIGIT_T, WHITE)
    ampm = TextLine(display, SMALL, x - PAIR_GAP + 6 + SMALL.WIDTH,
                    DIGIT_TOP + DIGIT_H - SMALL.HEIGHT, 2, ACCENT)

    # The alarm time: "07:05 AM", eight big letters, 128 px. Each part is
    # its own TextLine so the part being set can turn yellow.
    left = CX - 4 * BIG.WIDTH
    centered(display, SMALL, "alarm", LABEL_Y, DIM)
    hour_line = TextLine(display, BIG, left + BIG.WIDTH, ALARM_Y, 2, WHITE)
    display.text(BIG, ":", left + 2 * BIG.WIDTH, ALARM_Y, WHITE, BLACK)
    minute_line = TextLine(display, BIG, left + 4 * BIG.WIDTH, ALARM_Y, 2,
                           WHITE)
    alarm_ampm = TextLine(display, BIG, left + 7 * BIG.WIDTH, ALARM_Y, 2,
                          WHITE)
    status_line = TextLine(display, SMALL, CX, STATUS_Y, 22, WHITE)
    hints = (TextLine(display, SMALL, CX, HINT_Y, 24, DIM),
             TextLine(display, SMALL, CX, HINT2_Y, 24, DIM))
    menu_hint(display, MENU_Y)

    if saved is None:
        t = time.localtime()
        minutes = (t[3] * 60 + t[4] + 1) % 1440       # one minute from now
        alarm_hour, alarm_minute = minutes // 60, minutes % 60
        alarm_on = True
        fired = None
    else:
        alarm_hour = saved["hour"]
        alarm_minute = saved["minute"]
        alarm_on = saved["on"]
        fired = saved["fired"]

    speaker = make_speaker()
    looper = None
    state = SHOWING
    shown = None              # what the alarm lines show now
    ring_until = 0
    ring_test = False
    flash_shown = None
    shown_second = None
    if speaker is None:
        status_line.show("no speaker found")


# ---------------------------------------------------------------------
# Ringing
# ---------------------------------------------------------------------
def alarm_sound():
    """Beep-beep-beep-beep ... pause: about 1.1 s, looped while ringing."""
    parts = []
    for _ in range(4):
        parts.append(speaker.tone(1760, 90, "square"))
        parts.append(speaker.tone(0, 60))
    parts.append(speaker.tone(0, 500))
    from array import array
    whole = array('h')
    for part in parts:
        whole.extend(part)
    return whole


def ring(now, seconds, test=False):
    global state, ring_until, ring_test, looper
    state = RINGING
    ring_until = time.ticks_add(now, seconds * 1000)
    ring_test = test
    if speaker is not None:
        looper = Looper(speaker, alarm_sound())


def stop_ringing():
    global state, looper
    state = SHOWING
    looper = None


def snooze():
    """Move the alarm SNOOZE_MINUTES on from now (the old time is gone:
    a real clock would remember it, which is a good thing to add)."""
    global alarm_hour, alarm_minute
    t = time.localtime()
    minutes = (t[3] * 60 + t[4] + SNOOZE_MINUTES) % 1440
    alarm_hour, alarm_minute = minutes // 60, minutes % 60
    stop_ringing()


# ---------------------------------------------------------------------
# The mode
# ---------------------------------------------------------------------
def on_mode():
    global state, alarm_on
    if state == RINGING:
        stop_ringing()
    elif state == SHOWING:
        state = SET_HOUR
    elif state == SET_HOUR:
        state = SET_MINUTE
    else:
        state = SHOWING
        alarm_on = True


def holds_buttons():
    """While setting, holding UP or DOWN counts fast -- so a long hold
    must not skip to another demo."""
    return state == SET_HOUR or state == SET_MINUTE


def twelve(hour):
    return (hour % 12 or 12) if TWELVE_HOUR else hour


def show_time(t):
    hour, minute = t[3], t[4]
    shown_hour = twelve(hour)
    tens = shown_hour // 10
    first = DIGITS[tens] if (tens or not TWELVE_HOUR) else BLANK
    for digit, pattern in zip(digits, (first, DIGITS[shown_hour % 10],
                                       DIGITS[minute // 10],
                                       DIGITS[minute % 10])):
        digit.show(pattern)
    if TWELVE_HOUR:
        ampm.show("AM" if hour < 12 else "PM")


def minutes_until_alarm(t):
    now = t[3] * 60 + t[4]
    return (alarm_hour * 60 + alarm_minute - now) % 1440


def update(now):
    global alarm_hour, alarm_minute, alarm_on, fired, shown, flash_shown
    global shown_second
    up = _kit.up.pressed(now, repeat=state in (SET_HOUR, SET_MINUTE))
    down = _kit.down.pressed(now, repeat=state in (SET_HOUR, SET_MINUTE))
    t = time.localtime()

    if state == SHOWING:
        if up:
            alarm_on = not alarm_on
            shown_second = None           # repaint ON / OFF right away
        elif down:
            ring(now, TEST_SECONDS, test=True)
    elif state == SET_HOUR:
        step = 1 if up else -1 if down else 0
        alarm_hour = (alarm_hour + step) % 24
    elif state == SET_MINUTE:
        step = 1 if up else -1 if down else 0
        alarm_minute = (alarm_minute + step) % 60
    elif state == RINGING:
        if up and not ring_test:
            snooze()
        elif up or down or time.ticks_diff(now, ring_until) >= 0:
            stop_ringing()

    # Time to ring? Once per alarm minute: `fired` remembers which one.
    key = (t[2], alarm_hour, alarm_minute)
    if (alarm_on and state == SHOWING and (t[3], t[4]) == key[1:]
            and fired != key):
        fired = key
        ring(now, RING_SECONDS)

    if t[5] != shown_second:
        shown_second = t[5]
        show_time(t)
        if state != RINGING and speaker is not None:
            if alarm_on:
                left = minutes_until_alarm(t)
                if left == 0:
                    status_line.show("ON", ON_COLOR)
                elif left < 60:
                    status_line.show("ON - rings in %d min" % left,
                                     ON_COLOR)
                else:
                    status_line.show("ON - in %d h %d min" % (
                        left // 60, left % 60), ON_COLOR)
            else:
                status_line.show("OFF", OFF_COLOR)

    flash = (state == RINGING
             and (time.ticks_diff(now, ring_until) // FLASH_MS) % 2 == 0)
    wanted = (state, alarm_hour, alarm_minute, flash)
    if wanted != shown:
        hour_color = minute_color = WHITE
        if state == SET_HOUR:
            hour_color = SETTING_COLOR
        elif state == SET_MINUTE:
            minute_color = SETTING_COLOR
        elif state == RINGING:
            hour_color = minute_color = RING_COLOR if flash else WHITE
        hour_line.show("%2d" % twelve(alarm_hour), hour_color)
        minute_line.show("%02d" % alarm_minute, minute_color)
        alarm_ampm.show(("AM" if alarm_hour < 12 else "PM")
                        if TWELVE_HOUR else "", minute_color)
        if state == RINGING:
            status_line.show("TEST" if ring_test else "WAKE UP!", RING_COLOR)
        elif shown is not None and shown[0] == RINGING:
            shown_second = None           # repaint the status next pass
        if shown is None or shown[0] != state:
            first, second = HINTS[state]
            if state == RINGING and ring_test:
                first = "UP or DOWN: stop"
            hints[0].show(first)
            hints[1].show(second)
        shown = wanted

    if looper is not None:
        looper.update()


def stop():
    """Keep the alarm. If it is on, ask to be woken when it is due."""
    if speaker is not None:
        speaker.deinit(finish=False)      # leaving: no need to wait
    saved = {"hour": alarm_hour, "minute": alarm_minute, "on": alarm_on,
             "fired": fired}
    if alarm_on:
        t = time.localtime()
        seconds = minutes_until_alarm(t) * 60 - t[5]
        if seconds <= 0:
            seconds += 24 * 3600
        saved["wake_at"] = time.ticks_add(time.ticks_ms(), seconds * 1000)
    return saved
