# Test 02: Hardware Probe
# Checks everything about this kit that software can check, and prints a
# report to the Thonny shell. Run it first on a new board, and again any
# time something stops working -- it tells you whether the problem is
# the board, the files, the wiring, or your code.
#
#   1. Board and firmware   which chip, which MicroPython build, CPU speed
#   2. RAM                  how much there is, and whether a 3-second
#                           recording (test 07) would fit in it
#   3. Flash                filesystem space, and every file on it
#   4. Kit files            are the driver, fonts, and config on the board?
#   5. Pin plan             do the pins in config.py follow the I2S rules,
#                           and does any pin get used twice?
#   6. Buttons              are MODE / UP / DOWN all reading "not pressed"?
#   7. Display wiring       are the SCL, SDA and BL wires (and the
#                           display's power) connected?
#   8. Microphone           start the INMP441 and look at what it sends
#
# Nothing here writes to flash or changes a setting, so it is always safe
# to run. A part you have not wired yet shows up as a WARNING, not a crash,
# so run this after adding each part to see that part go from WARNING to ok.
#
# Tests 04 and 05 check the display and the speaker by eye and by ear.
# Neither the GC9B72 nor the MAX98357A can report back to the Pico --
# the display's SDO pin never answers (test 08 tried every known way).
# Section 7 checks what it can without the display's help.

import gc
import os
import sys
import time
import machine
from machine import Pin

NAME = "02-probe.py"
VERSION = "1.1"

warnings = []


def warn(message):
    """Record a problem for the summary at the end, and print it now."""
    warnings.append(message)
    print("  WARNING:", message)


def heading(title):
    print()
    print("=" * 56)
    print(title)
    print("=" * 56)


def kb(n):
    return "{:,} bytes ({:.1f} KB)".format(n, n / 1024)


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


print("{} v{}".format(NAME, VERSION))

# ---------------------------------------------------------------------
heading("1. Board and firmware")
# ---------------------------------------------------------------------
board = sys.implementation._machine
print("board     :", board)
print("MicroPython", os.uname().release)
print("CPU clock : {} MHz".format(machine.freq() // 1_000_000))
if "Pico W" not in board and "Pico 2 W" not in board:
    warn("this kit needs a Pico W or Pico 2 W, but this board is: " + board)

# ---------------------------------------------------------------------
heading("2. RAM")
# ---------------------------------------------------------------------
gc.collect()
free = gc.mem_free()
print("heap free :", kb(free))

# Test 07 records into one unbroken block of memory. The only honest test
# of whether it fits is to try.
RECORD_BYTES = 3 * 12800 * 4          # 3 s of 32-bit samples at 12800 Hz
try:
    block = bytearray(RECORD_BYTES)
    print("3 s record: fits -- needs", kb(RECORD_BYTES))
    del block
except MemoryError:
    warn("a 3-second recording ({}) does not fit in RAM".format(
        kb(RECORD_BYTES)))
gc.collect()

# ---------------------------------------------------------------------
heading("3. Flash")
# ---------------------------------------------------------------------
block_size, _, total_blocks, free_blocks = os.statvfs("/")[:4]
print("filesystem:", kb(block_size * total_blocks))
print("  free    :", kb(block_size * free_blocks))
if block_size * free_blocks < 64 * 1024:
    warn("less than 64 KB of flash free")

print()
print("Files on flash:")


def list_files(path="/", indent=1):
    for entry in sorted(os.ilistdir(path)):
        name, kind = entry[0], entry[1]
        full = path.rstrip("/") + "/" + name
        if kind == 0x4000:                     # a directory
            print("  " * indent + name + "/")
            list_files(full, indent + 1)
        else:
            size = entry[3] if len(entry) > 3 else os.stat(full)[6]
            print("  " * indent + "{:<28} {:>7,} bytes".format(name, size))


list_files()

# ---------------------------------------------------------------------
heading("4. Kit files")
# ---------------------------------------------------------------------
# Checked before importing config.py, because config.py imports the
# driver and both fonts -- if any of them is missing, the import itself
# would crash and this probe would never get to tell you which one.
REQUIRED = (
    ("lib/gc9b72.py", "the display driver"),
    ("lib/vga1_8x16.py", "the small font"),
    ("lib/vga1_bold_16x32.py", "the big font"),
    ("config.py", "pin numbers and settings"),
)
for path, purpose in REQUIRED:
    if exists(path):
        print("  ok      {:<24} {}".format(path, purpose))
    else:
        print("  MISSING {:<24} {}".format(path, purpose))
        warn(path + " is not on the board -- run upload-code.sh")

config = None
if all(exists(path) for path, _ in REQUIRED):
    import config
else:
    print()
    print("Skipping sections 5-8 until the missing files are uploaded.")

if config is not None:
    # -----------------------------------------------------------------
    heading("5. Pin plan")
    # -----------------------------------------------------------------
    # MicroPython's I2S on the Pico needs the word-select pin (LRC on the
    # amplifier, WS on the microphone) on the pin right after the bit
    # clock. Break the rule and I2S() raises an error.
    for label, bclk, ws in (
            ("speaker", config.I2S_BCLK_PIN, config.I2S_LRC_PIN),
            ("mic", config.MIC_SCK_PIN, config.MIC_WS_PIN)):
        if ws == bclk + 1:
            print("  ok      {:<8} clock GP{}, word select GP{}".format(
                label, bclk, ws))
        else:
            warn("{} I2S needs word select on the pin right after the "
                 "clock, but they are GP{} and GP{}".format(label, ws, bclk))

    if config.I2S_SPEAKER_ID == config.MIC_I2S_ID:
        warn("speaker and microphone share I2S block {} -- they could "
             "not run at the same time".format(config.MIC_I2S_ID))

    # A pin number used by two parts means two wires on one pin.
    PLAN = (
        ("display SCK", config.SCK_PIN), ("display MOSI", config.MOSI_PIN),
        ("display RST", config.RST_PIN), ("display DC", config.DC_PIN),
        ("display CS", config.CS_PIN), ("display BL", config.BL_PIN),
        ("button MODE", config.BUTTON_MODE_PIN),
        ("button UP", config.BUTTON_INCREMENT_PIN),
        ("button DOWN", config.BUTTON_DECREMENT_PIN),
        ("speaker BCLK", config.I2S_BCLK_PIN),
        ("speaker LRC", config.I2S_LRC_PIN),
        ("speaker DIN", config.I2S_DIN_PIN),
        ("speaker GAIN", config.I2S_GAIN_PIN),
        ("mic SCK", config.MIC_SCK_PIN), ("mic WS", config.MIC_WS_PIN),
        ("mic SD", config.MIC_SD_PIN),
    )
    if hasattr(config, "SDO_PIN"):
        PLAN += (("display SDO", config.SDO_PIN),)
    seen = {}
    for label, pin in PLAN:
        if pin in seen:
            warn("GP{} is used by both '{}' and '{}'".format(
                pin, seen[pin], label))
        seen[pin] = label
        if pin in (23, 24, 25, 29):
            warn("GP{} ('{}') belongs to the wireless chip".format(pin, label))
    print("  checked {} pins for duplicates".format(len(PLAN)))

    # -----------------------------------------------------------------
    heading("6. Buttons")
    # -----------------------------------------------------------------
    # Pull-ups hold every button at 1. A 0 here, with nobody touching
    # anything, means a button is being held, is wired to the wrong pin,
    # or its pin is shorted to GND.
    buttons = config.init_buttons()
    for label, pin_number, pin in zip(
            ("MODE", "UP", "DOWN"),
            (config.BUTTON_MODE_PIN, config.BUTTON_INCREMENT_PIN,
             config.BUTTON_DECREMENT_PIN),
            buttons):
        value = pin.value()
        state = "1 (not pressed)" if value else "0 (PRESSED or shorted)"
        print("  {:<5} GP{:<3} {}".format(label, pin_number, state))
        if not value:
            warn("{} button (GP{}) reads pressed".format(label, pin_number))
    print("  (an unconnected button also reads 1, so this cannot see a "
          "missing wire -- test 03 can)")

    # -----------------------------------------------------------------
    heading("7. Display wiring")
    # -----------------------------------------------------------------
    # The display cannot answer the Pico, but three of its pads have a
    # resistor on the module itself: SCL and SDA are pulled UP to the
    # display's VCC, and BL is pulled DOWN. The Pico can feel those
    # resistors. Turn on the Pico's own (weaker) pull in the OPPOSITE
    # direction: a connected wire wins and holds the pin where the module
    # wants it, while a missing wire lets the pin follow the Pico's pull.
    #
    # RST, DC, CS and SDO have no resistor, so a connected wire and a
    # missing one look the same. Those you check by eye with test 04.
    def pin_state(number):
        """Returns 'high', 'low' or 'floats' for a pin with nothing
        driving it but whatever is on the other end of its wire."""
        pin = Pin(number, Pin.IN, Pin.PULL_DOWN)
        time.sleep_ms(5)
        down = pin.value()
        pin.init(Pin.IN, Pin.PULL_UP)
        time.sleep_ms(5)
        up = pin.value()
        pin.init(Pin.IN)                # leave it with no pull
        if down == up:
            return "high" if up else "low"
        return "floats"

    CHECKED = (("SCL", config.SCK_PIN, "high"),
               ("SDA", config.MOSI_PIN, "high"),
               ("BL", config.BL_PIN, "low"))
    UNCHECKED = (("RST", config.RST_PIN), ("DC", config.DC_PIN),
                 ("CS", config.CS_PIN))
    if hasattr(config, "SDO_PIN"):
        UNCHECKED += (("SDO", config.SDO_PIN),)

    states = {}
    for label, number, expected in CHECKED:
        states[label] = pin_state(number)
        print("  {:<4} GP{:<3} reads {:<7} (connected reads {})".format(
            label, number, states[label], expected))

    if states["SCL"] == "floats" and states["SDA"] == "floats":
        # Both pull-ups gone at once is far more likely to be the display
        # missing its power than two wires falling out.
        warn("SCL and SDA both float -- is the display unplugged, or are "
             "its VCC (3V3) and GND wires loose?")
    else:
        for label, number, expected in CHECKED:
            state = states[label]
            if state == expected:
                print("  ok      {} wire is connected".format(label))
            elif state == "floats":
                warn("the display's {} wire to GP{} is missing or "
                     "loose".format(label, number))
            else:
                warn("GP{} reads {}, but the {} wire should make it {} -- "
                     "is a wire on the wrong pin?".format(
                         number, state, label, expected))

    # These should all float. One that is held is most likely an SCL/SDA
    # (held high) or BL (held low) wire pushed into the wrong pin.
    for label, number in UNCHECKED:
        state = pin_state(number)
        if state == "floats":
            print("  --      {:<4} GP{:<3} floats (connected or not -- "
                  "check by eye)".format(label, number))
        else:
            warn("GP{} ({}) is held {} -- it should float; is a wire on "
                 "the wrong pin?".format(number, label, state))
    print("  (RST, DC and CS cannot be checked here. If this section is")
    print("   all ok but test 04 shows a blank screen, check those three.)")

    # -----------------------------------------------------------------
    heading("8. Microphone")
    # -----------------------------------------------------------------
    # The INMP441 puts out 24-bit audio in 32-bit words. A wired mic in a
    # quiet room sends small, wobbling numbers. A missing mic, or one with
    # a loose SD wire, sends a flat line: every sample the same.
    import struct
    mic = None
    try:
        mic = config.init_microphone()
        buf = bytearray(2048)                      # 512 samples
        for _ in range(8):                         # skip the start-up clicks
            mic.readinto(buf)
        mic.readinto(buf)
        samples = [s >> config.MIC_SAMPLE_SHIFT
                   for s in struct.unpack("<512i", buf)]
        low, high = min(samples), max(samples)
        print("I2S       : started at {} Hz, {}-bit".format(
            config.MIC_SAMPLE_RATE, config.MIC_SAMPLE_BITS))
        print("pins      : SCK GP{}  WS GP{}  SD GP{}".format(
            config.MIC_SCK_PIN, config.MIC_WS_PIN, config.MIC_SD_PIN))
        print("512 samples: lowest {}, highest {}, spread {}".format(
            low, high, high - low))
        if high == low:
            warn("the microphone sends a flat line (every sample is {}) -- "
                 "check VDD, GND, and the SD wire (GP{})".format(
                     low, config.MIC_SD_PIN))
        else:
            print("  ok      the microphone is sending changing numbers")
    except Exception as error:
        warn("microphone failed to start: {}".format(error))
    finally:
        if mic is not None:
            mic.deinit()

# ---------------------------------------------------------------------
heading("Summary")
# ---------------------------------------------------------------------
if warnings:
    print("{} warning(s):".format(len(warnings)))
    for message in warnings:
        print("  -", message)
else:
    print("Everything software can check looks good.")
