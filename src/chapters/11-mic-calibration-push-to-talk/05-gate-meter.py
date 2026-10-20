# Chapter 11, Test 05: Watch the level gate work
# Shows a live level bar with marks for the noise floor (cyan), the level where
# the gate OPENS (green), and the level where it CLOSES. The word under the bar
# says OPEN or closed. After 30 seconds it prints how many times the gate
# opened, and how many times a plain single-threshold gate (no hysteresis)
# would have flipped on the same frames. Reads calibration.json if you saved
# one with 04-calibrate.py, otherwise uses the defaults. Needs the display and
# the microphone.
#
# PASS: the bar moves, the gate opens when you talk and closes soon after you
# stop, and the summary prints both flip counts. Hold a steady hum or tap
# near the threshold: the single-threshold count should be larger than the
# gate's. WRITE DOWN both counts.

NAME = "05-gate-meter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import calibration
import config
import levels
import ui

RUN_SECONDS = 30
SETTLE_FRAMES = 8

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

cal = calibration.load()
if not cal["calibrated"]:
    print("No calibration.json: using the DEFAULT guesses. Run 04-calibrate.py first.")
gate = calibration.gate_from(cal)
print("gate opens at {:.2f} bits, closes below {:.2f} bits".format(gate.open_at, gate.close_at))

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
ui.put(display, "LEVEL GATE", 70, SMALL, config.CYAN, 20)
bar = ui.LevelBar(display, config.CENTER_X - 100, 190, 200, 22, 9, 21)
bar.frame()
bar.tick(cal["noise_floor"], config.CYAN)
bar.tick(gate.open_at, config.GREEN)
bar.tick(gate.close_at, config.YELLOW)
ui.put(display, "opens {:.1f}  closes {:.1f} bits".format(
    gate.open_at, gate.close_at), 150, SMALL, DIM, 30)

frame = bytearray(levels.FRAME_BYTES)
mic = config.init_microphone()
shown = None
opens = 0
plain_flips = 0
plain_open = False
frames = RUN_SECONDS * 1000 // levels.FRAME_MS
try:
    for _ in range(SETTLE_FRAMES):
        mic.readinto(frame)
    for n in range(frames):
        mic.readinto(frame)
        bits = levels.frame_stats(frame)[0]

        was_open = gate.is_open
        is_open = gate.update(bits)
        if is_open and not was_open:
            opens += 1
            print("frame {:>4}  OPEN   at {:.2f} bits".format(n, bits))
        elif was_open and not is_open:
            print("frame {:>4}  closed at {:.2f} bits".format(n, bits))

        # the same frames through a single threshold at the open level
        now_open = bits >= gate.open_at
        if now_open != plain_open:
            plain_flips += 1
            plain_open = now_open

        bar.set(bits, config.GREEN if is_open else config.YELLOW)
        if is_open != shown:                      # redraw the word only when it changes
            shown = is_open
            ui.put(display, "OPEN" if is_open else "closed", 235, BIG,
                   config.GREEN if is_open else DIM, 10)
finally:
    mic.deinit()

print()
print("In {} seconds ({} frames):".format(RUN_SECONDS, frames))
print("  the gate with hysteresis opened {} times".format(opens))
print("  a single threshold at {:.2f} bits flipped {} times (opens + closes)".format(
    gate.open_at, plain_flips))
print("  the gate flipped {} times (opens + closes)".format(opens * 2))
print("Bytes the bar sent to the display: {}  (a full redraw of it is {} each time)".format(
    bar.bytes_drawn, 200 * 22 * 2))
