# Chapter 7, Test 04: Check the state machine against the chapter
# Replays the six event sequences from the chapter's "Device Mode State
# Machine" activity, plus a few more, and compares the final mode and volume
# with the answers the chapter gives. Needs no hardware: it runs on the Pico
# or on your computer (python3 04-state-machine-selftest.py).
#
# PASS: every row says "ok" and the last line says PASS.

NAME = "04-state-machine-selftest.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from device import Device, NAMES

# Each step is ("button", name, event, held_ms) or ("internal", what)
B = "button"
I = "internal"
CASES = (
    ("1 hold MODE 1.5 s",
     [(B, "mode", "press", 0), (B, "mode", "release", 1500)], "THINKING", 40),
    ("2 bump MODE 0.1 s",
     [(B, "mode", "press", 0), (B, "mode", "release", 100)], "CLOCK", 40),
    ("3 ...then reply arrives",
     [(B, "mode", "press", 0), (B, "mode", "release", 1500), (I, "reply")], "SPEAKING", 40),
    ("4 UP long, DOWN, MODE tap",
     [(B, "up", "press", 0), (B, "up", "long", 0), (B, "up", "release", 900),
      (B, "down", "press", 0), (B, "mode", "press", 0), (B, "mode", "release", 100)],
     "SETTINGS", 30),
    ("5 cancel while thinking",
     [(B, "mode", "press", 0), (B, "mode", "release", 1500), (B, "mode", "press", 0),
      (B, "mode", "release", 100)], "CLOCK", 40),
    ("6 UP tap twice in CLOCK",
     [(B, "up", "press", 0), (B, "up", "release", 100),
      (B, "up", "press", 0), (B, "up", "release", 100)], "CLOCK", 60),
    ("7 whole conversation",
     [(B, "mode", "press", 0), (B, "mode", "release", 1500), (I, "reply"), (I, "done")],
     "CLOCK", 40),
    ("8 seven UP taps (clamp at 100)",
     [(B, "up", "press", 0), (B, "up", "release", 100)] * 7, "CLOCK", 100),
    ("9 nine DOWN taps (clamp at 0)",
     [(B, "down", "press", 0), (B, "down", "release", 100)] * 9, "CLOCK", 0),
    ("10 recording buffer fills",
     [(B, "mode", "press", 0), (I, "full")], "THINKING", 40),
    ("11 long MODE leaves SETTINGS",
     [(B, "up", "press", 0), (B, "up", "long", 0), (B, "up", "release", 900),
      (B, "mode", "press", 0), (B, "mode", "long", 0), (B, "mode", "release", 900)],
     "CLOCK", 40),
)

all_ok = True
print()
print("{:<32} {:<10} {:>6}  {}".format("case", "mode", "volume", ""))
for label, steps, want_mode, want_volume in CASES:
    d = Device()
    for step in steps:
        if step[0] == B:
            d.on_button(step[1], step[2], step[3])
        else:
            d.on_internal(step[1])
    mode = NAMES[d.state]
    good = mode == want_mode and d.volume == want_volume
    all_ok = all_ok and good
    print("{:<32} {:<10} {:>6}  {}".format(
        label, mode, d.volume, "ok" if good else "WRONG (want {} {})".format(want_mode, want_volume)))

print()
print("PASS" if all_ok else "FAIL")
