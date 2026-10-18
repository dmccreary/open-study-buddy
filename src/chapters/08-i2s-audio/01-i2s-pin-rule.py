# Chapter 8, Test 01: The "ws must be sck + 1" rule
# Tries to create I2S buses with good and bad pin pairs and prints what
# happens. Good pairs should start (and are shut down again); bad pairs should
# raise an error right away. Needs only the Pico: no part has to be wired,
# because the error comes before anything is started.
#
# PASS: the kit's pairs (SCK 10 / WS 11 and BCLK 20 / LRC 21) start; the swapped
# or non-adjacent pairs fail with an error. Copy the exact error text into
# your notes: it is what you will see if a wire is moved.

NAME = "01-i2s-pin-rule.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import I2S, Pin

# (label, I2S block, sck, ws, sd, mode, should it work?)
CASES = (
    ("microphone as wired    ", 1, 10, 11, 12, I2S.RX, True),
    ("microphone, WS on 13   ", 1, 10, 13, 12, I2S.RX, False),
    ("microphone, SCK/WS swapped", 1, 11, 10, 12, I2S.RX, False),
    ("amplifier as wired     ", 0, 20, 21, 19, I2S.TX, True),
    ("amplifier, LRC on 22   ", 0, 20, 22, 19, I2S.TX, False),
    ("amplifier, BCLK/LRC swapped", 0, 21, 20, 19, I2S.TX, False),
)

ok = True
print()
for label, block, sck, ws, sd, mode, should_work in CASES:
    try:
        bus = I2S(block, sck=Pin(sck), ws=Pin(ws), sd=Pin(sd), mode=mode,
                  bits=16, format=I2S.MONO, rate=12800, ibuf=2048)
        bus.deinit()
        worked = True
        message = "started"
    except (ValueError, OSError) as e:
        worked = False
        message = "{}: {}".format(type(e).__name__, e)
    good = worked == should_work
    ok = ok and good
    print("{:<28} sck={:>2} ws={:>2}  {:<48} {}".format(
        label, sck, ws, message, "ok" if good else "UNEXPECTED"))

print()
print("PASS" if ok else "CHECK: a pair behaved differently than the chapter says")
