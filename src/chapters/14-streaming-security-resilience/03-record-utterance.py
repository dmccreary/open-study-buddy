# Chapter 14, Test 03: Record an utterance as 16-bit audio, and time the conversion
# Hold MODE and talk (up to MAX_UTTERANCE_S seconds). The microphone's 32-bit
# words are converted to 16-bit samples AS they arrive, so a 5 s recording
# needs 128,000 bytes instead of 256,000. The script reports how long the
# conversion took, per 20 ms read, against the 20 ms (20,000 us) each read has
# to fit in (Chapter 8's frame budget). Needs the microphone, MODE, and display.
#
# PASS: bytes recorded matches the time you held the button (25,600 bytes per
# second), the worst conversion time is under 20,000 us, and the last line says
# PASS. Write down worst_us and the free heap: the chapter's tables depend on
# them. If worst_us is over 20,000, audio is being lost: see "Try This" 2.

NAME = "03-record-utterance.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import array
import gc
import math
import time

import config
import buddy_config
import utterance
from screen import Screen

screen = Screen("RECORD")
button = config.init_buttons()[0]       # MODE

gc.collect()
before = gc.mem_free()
pcm = utterance.make_buffer(buddy_config.MAX_UTTERANCE_S)
gc.collect()
print("heap free: {:,} before the buffer, {:,} after ({:,} bytes allocated)".format(
    before, gc.mem_free(), len(pcm)))

BUDGET_US = utterance.READ_SAMPLES * 1000000 // utterance.RATE      # 20,000

screen.status("hold MODE", config.YELLOW)
screen.message("talk, then let go", config.GRAY)
while button.value() != 0:
    time.sleep_ms(10)

screen.status("recording", config.RED)
started = time.ticks_ms()
count, stats = utterance.record(button, pcm)
held_ms = time.ticks_diff(time.ticks_ms(), started)
screen.status("recorded", config.GREEN)

samples = array.array("h")
samples.frombytes(bytes(memoryview(pcm)[:count]))
peak = max((abs(s) for s in samples), default=0)
rms = math.sqrt(sum(s * s for s in samples) / len(samples)) if samples else 0
seconds = count / 2 / utterance.RATE
screen.message("{:.1f} s, peak {}".format(seconds, peak))

print()
print("held the button : {:,} ms".format(held_ms))
print("recorded        : {:,} bytes = {:.2f} s".format(count, seconds))
print("peak / rms      : {} / {:.0f}  (full scale is 32767)".format(peak, rms))
if stats["reads"]:
    print("conversion time : worst {:,} us, average {:,} us, per read of {} us budget".format(
        stats["worst_us"], stats["total_us"] // stats["reads"], BUDGET_US))
gc.collect()
print("heap free after : {:,} bytes".format(gc.mem_free()))

fits = stats["reads"] > 0 and stats["worst_us"] < BUDGET_US
sized = abs(count - seconds * 2 * utterance.RATE) < 1 and count > 0
print()
print("PASS" if fits and sized else "CHECK: too short, or the conversion is slower than the 20 ms read")

# Try This
#   1. Speak loudly right at the microphone. Does peak reach 32767? That is
#      clipping (Chapter 3). Lower utterance.GAIN to 4 and compare.
#   2. If worst_us is over 20,000: record 32-bit words instead and convert after
#      you let go, as the kit's test 07 does (limit 3 s). Why is that slower
#      to start playing but safe for the microphone's ring buffer?
