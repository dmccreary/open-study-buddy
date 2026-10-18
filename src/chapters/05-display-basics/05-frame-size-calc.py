# Chapter 5, Test 05: Frame size and update time table
# Prints the chapter's frame-size and bandwidth numbers: bytes for several
# rectangles, the best-case time to send them at three SPI speeds, and the
# bandwidth a given number of full-frame updates per second would need.
# Runs on the Pico or on your computer. Needs no hardware.
#
# PASS: the full frame is 259,200 bytes, takes 86.4 ms at 24 MHz, and 10
# full frames per second would need 20,736,000 bits per second.

NAME = "05-frame-size-calc.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

SHAPES = (
    ("Full frame, 2 bytes/pixel", 360, 360, 2),
    ("Full frame, 3 bytes/pixel", 360, 360, 3),
    ("Level meter (test 06)", 200, 22, 2),
    ("Clock-digit box", 100, 30, 2),
    ("One big-font letter", 16, 32, 2),
)
BAUDS = (8_000_000, 12_000_000, 24_000_000)

print()
print("{:<27} {:>9}  {}".format("rectangle", "bytes", "  ms at 8 / 12 / 24 MHz"))
for name, w, h, bpp in SHAPES:
    size = w * h * bpp
    times = ["{:7.2f}".format(size * 8 * 1000 / baud) for baud in BAUDS]
    print("{:<27} {:>9}  {}".format(name, "{:,}".format(size), " ".join(times)))

print()
frame_bits = 360 * 360 * 2 * 8
print("Bandwidth needed for full-frame updates (the link carries 24,000,000 bits/s at best):")
for fps in (1, 5, 10, 11, 12, 30):
    need = frame_bits * fps
    print("  {:>2} per second -> {:>12,} bits/s  ({:5.1f}% of 24 MHz)".format(
        fps, need, 100 * need / 24_000_000))

best_ms = frame_bits * 1000 / 24_000_000
print()
print("Best-case full frame at 24 MHz: {:.1f} ms = {:.1f} frames per second".format(
    best_ms, 1000 / best_ms))
print("Audio frame at 12,800 Hz, 512 samples: {:.0f} ms".format(512 * 1000 / 12800))
ok = abs(best_ms - 86.4) < 0.01 and frame_bits * 10 == 20_736_000
print("PASS" if ok else "FAIL")
