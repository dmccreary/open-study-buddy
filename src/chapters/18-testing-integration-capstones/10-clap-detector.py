# Chapter 18, Capstone 10: Clap detector
# Listens for claps. One clap adds to the count; two claps within 1 second switch
# a "light" on the screen on and off. The threshold is NOT built in: the program
# first listens to the quiet room for 2 seconds and works out how much louder a
# clap must be (detectors.ClapDetector).
#
# Needs: display, microphone. Stay quiet for the first 2 seconds.
# Level only: nothing is recorded or kept (Chapter 17).
#
# PASS: after "Quiet please", the screen shows the floor and jump it measured;
# a clap near the microphone adds 1; a double clap toggles the light; talking
# and steady noise do not count. The shell prints an overrun summary every 10 s.
# WRITE DOWN how far from the microphone a clap still works (0.5 m, 1 m, 2 m).

NAME = "10-clap-detector.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
from detectors import ClapDetector
from listen import Mic

BIG, SMALL = config.BIG_FONT, config.SMALL_FONT
DIM = config.color565(150, 150, 150)
DOUBLE_MS = 1000

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)


def put(text, y, font, color, width):
    config.centered_text(display, font, text.center(width), y, color)


def draw_light(on):
    display.fill_rect(config.CENTER_X - 25, 225, 50, 50,
                      config.YELLOW if on else config.color565(50, 50, 50))


put("Clap detector", 70, BIG, config.YELLOW, 14)
put("Quiet please...", 130, BIG, config.CYAN, 14)
mic = Mic()
mic.open()
try:
    floor, spread = mic.calibrate(50)                  # 2 seconds of the quiet room
    det = ClapDetector(floor, spread)
    print("floor {:.2f} bits, spread {:.3f}, jump {:.1f} bits".format(floor, spread, det.jump))
    put("Listening", 130, BIG, config.GREEN, 14)
    put("floor {:.1f}  jump {:.1f} bits".format(floor, det.jump), 190, SMALL, DIM, 36)
    draw_light(False)
    light = False
    shown = -1
    last_clap = None
    flash = 0
    frame = 0
    while True:
        bits = mic.bits()
        now = time.ticks_ms()
        if det.update(bits):
            print("clap #{}  (peak {:.1f} bits, {:.1f} above the floor)".format(
                det.claps, det.last_peak, det.last_peak - floor))
            if last_clap is not None and time.ticks_diff(now, last_clap) <= DOUBLE_MS:
                light = not light
                draw_light(light)
                last_clap = None
                print("double clap: light", "ON" if light else "OFF")
            else:
                last_clap = now
            put("CLAP!", 130, BIG, config.MAGENTA, 14)
            flash = 10                                  # show it for 10 frames (0.4 s)
        elif flash:
            flash -= 1
            if flash == 0:
                put("Listening", 130, BIG, config.GREEN, 14)
        if det.claps != shown:                          # redraw the count only when it changes
            shown = det.claps
            put("{} claps".format(shown), 280, SMALL, config.WHITE, 20)
        frame += 1
        if frame % 250 == 0:
            print(mic.overrun_summary())
finally:
    mic.close()

# Try This
#   1. Clap at 0.5 m, 1 m, 2 m, and 4 m. Where does it stop counting? Why?
#   2. Say "pop" and "tap" sharply. Do they count? (The chapter explains why.)
#   3. Raise ClapDetector's jump_min to 3.0. What do you gain and lose?
#   4. Add a crest-factor check (peak divided by average in the frame) to
#      reject sharp consonants, and test it with 09-detectors-test.py's spikes.
