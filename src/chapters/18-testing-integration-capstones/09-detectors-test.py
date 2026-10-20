# Chapter 18, Test 09: Test the capstone logic on synthetic sound
# Feeds detectors.py with SYNTHETIC frames and scripted button presses and prints
# what happened. Everything is generated from a fixed random seed, so you get the
# same numbers every time. No hardware needed: run it on a computer
# (python3 09-detectors-test.py) or on the Pico.
#
# Synthetic means invented by this program, not recorded in a classroom. The room
# is quiet noise whose loudness (about 12.5 bits) is chosen to resemble the
# quiet-room readings recorded on the test board in Chapters 3 and 8. A "clap"
# is an 8 ms burst that dies away in about 3 ms. The tests show how the LOGIC
# behaves; they do not tell you how a real clap, voice, or fan looks to your
# microphone. Use probe 03 and calibrate for that.
#
# PASS: every check line says ok and the last line says PASS.

NAME = "09-detectors-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import random

import detectors as dt

RATE = 12800
FRAME = 512
NOISE_AMP = 11600            # uniform +-11,600: average distance 5,800 = 12.5 bits
DC = 15000                   # a DC offset like the one test 07 measured

rng = random.Random(2026)
results = []


def check(label, ok, detail=""):
    results.append(ok)
    print("  {:<4} {}  {}".format("ok" if ok else "FAIL", label, detail))


# ---- synthetic frames ------------------------------------------------------
def noise(amp=NOISE_AMP):
    return [DC + rng.randint(-amp, amp) for _ in range(FRAME)]


def with_burst(frame, peak, start=200, ms=8, decay_ms=3):
    out = list(frame)
    n = int(RATE * ms / 1000)
    tau = RATE * decay_ms / 1000
    for i in range(n):
        j = start + i
        if j < FRAME:
            out[j] += int(rng.uniform(-1, 1) * peak * math.exp(-i / tau))
    return out


def scaled(frame, gain):
    return [DC + int((s - DC) * gain) for s in frame]


def bits(frame):
    return dt.bits_from_samples(frame)


def calibrate(frames=25):
    values = [bits(noise()) for _ in range(frames)]
    return dt.mean_std(values)


# ---- 1. calibration --------------------------------------------------------
print()
print("1. Calibration (25 quiet frames)")
floor, spread = calibrate()
print("   floor {:.2f} bits, spread {:.3f} bits".format(floor, spread))
check("floor is near the 12.5 bits the room was built to have", 12.0 < floor < 13.0)

# ---- 2. clap detector vs burst strength -------------------------------------
print()
print("2. Clap detector: 40 claps at each burst strength (peak / noise amplitude)")
print("   {:>8} {:>10} {:>10}".format("ratio", "detected", "frame bits"))
rates = {}
for ratio in (10, 20, 40, 80, 160):
    det = dt.ClapDetector(floor, spread)
    found = 0
    last_bits = 0.0
    for trial in range(40):
        for _ in range(30):
            det.update(bits(noise()))                 # a quiet stretch
        frame = with_burst(noise(), NOISE_AMP * ratio)
        last_bits = bits(frame)
        hit = det.update(last_bits)
        hit = det.update(bits(noise())) or hit        # the clap ends on the next frame
        found += 1 if hit else 0
    rates[ratio] = found
    print("   {:>8} {:>7}/40 {:>10.1f}".format(ratio, found, last_bits))
check("a very strong burst (ratio 160) is always found", rates[160] == 40)
check("a weak burst (ratio 10) is NOT found: the jump is not reached", rates[10] == 0)
print("   jump used: {:.1f} bits above the floor".format(dt.ClapDetector(floor, spread).jump))

# ---- 3. clap detector vs speech-like and steady sound ---------------------
print()
print("3. Clap detector on sounds that are not claps (180 s of each)")


def speech_like(seconds):
    """Syllables of 6 to 14 frames at 6 to 15 times the noise level, with pauses."""
    frames = []
    while len(frames) < seconds * 25:
        gain = rng.uniform(6, 15)
        for k in range(rng.randint(6, 14)):
            env = 0.5 + 0.5 * math.sin(math.pi * (k + 1) / 15)
            frames.append(scaled(noise(), 1 + (gain - 1) * env))
        for _ in range(rng.randint(3, 8)):
            frames.append(noise())
    return frames


def run_detector(frames):
    det = dt.ClapDetector(floor, spread)
    for _ in range(50):
        det.update(bits(noise()))
    det.claps = 0
    for f in frames:
        det.update(bits(f))
    return det.claps


speech_claps = run_detector(speech_like(180))
fan = [noise() for _ in range(50)] + [scaled(noise(), 4.0) for _ in range(25 * 180)]
fan_claps = run_detector(fan)
print("   speech-like (syllables 6 to 14 frames long): {} false claps".format(speech_claps))
print("   a fan switching on and staying on (4 x louder noise): {} false claps".format(fan_claps))
check("speech-like sound makes no false claps", speech_claps == 0)
check("a steady noise step makes at most 1 false clap", fan_claps <= 1)

# a very short loud 'consonant' IS a limit of this design
short = []
for _ in range(40):
    short += [noise() for _ in range(30)] + [scaled(noise(), 12.0)] + [noise()]
print("   single-frame spikes (a sharp 'p' or 'k'): {} claps from 40 spikes".format(run_detector(short)))
check("the design cannot tell a 1-frame spike from a clap (a known limit)",
      run_detector(short) == 40)

# ---- 4. noise monitor ----------------------------------------------------------
print()
print("4. Noise monitor on a scripted 60 s: 20 s quiet, 20 s talking, 10 s loud, 10 s quiet")
mon = dt.NoiseMonitor(floor)
script = [(20, 1.0), (20, 6.0), (10, 25.0), (10, 1.0)]
log = []
for seconds, gain in script:
    for _ in range(seconds * 25):
        band = mon.update(bits(scaled(noise(), gain)))
    log.append((seconds, gain, band, round(mon.ema - floor, 1)))
for seconds, gain, band, above in log:
    print("   after {:>2} s at {:>4}x noise: band {:<8} smoothed level {:+.1f} bits above floor".format(
        seconds, gain, band, above))
totals = mon.summary()
print("   seconds in each band:", {k: round(v, 1) for k, v in totals.items()})
check("ends QUIET after the final quiet stretch", log[-1][2] == dt.QUIET)
check("is TALKING after 20 s at 6 x", log[1][2] == dt.TALKING)
check("is LOUD after 10 s at 25 x", log[2][2] == dt.LOUD)
check("band counts add up to 60 s", abs(sum(totals.values()) - 60) < 0.01)
flap = dt.NoiseMonitor(floor)
changes, prev = 0, dt.QUIET
for i in range(25 * 20):
    gain = 6.0 if (i // 3) % 2 == 0 else 1.0           # 3-frame flicker around the boundary
    b = flap.update(bits(scaled(noise(), gain)))
    changes += b != prev
    prev = b
check("a flickering sound does not flap the band", changes <= 2, "({} changes in 20 s)".format(changes))

# ---- 5. study timer --------------------------------------------------------------
print()
print("5. Study timer, scripted")
t = dt.StudyTimer(focus_min=25, break_min=5, long_break_min=15, long_every=4)
now = 1000
check("starts IDLE showing 25:00", t.phase == dt.IDLE and t.remaining_ms(now) == 1500000)
check("MODE starts FOCUS", t.press("mode", now) == "focus_started" and t.phase == dt.FOCUS)
now += 10 * 60000
check("after 10 min, 15:00 remain", t.remaining_ms(now) // 1000 == 900)
t.press("mode", now)
check("MODE pauses", t.paused)
now += 30 * 60000
check("30 min later it is still 15:00 (paused)", t.remaining_ms(now) // 1000 == 900)
t.press("mode", now)
now += 15 * 60000
check("resumes, and ends focus after the 15 min left", t.tick(now) == "focus_done"
      and t.phase == dt.BREAK and t.cycles == 1)
now += 5 * 60000
check("5 min break then focus again", t.tick(now) == "break_done" and t.phase == dt.FOCUS)
for _ in range(2):                                   # finish focus 2 and 3
    now += 25 * 60000
    t.tick(now)
    now += 5 * 60000
    t.tick(now)
now += 25 * 60000
event = t.tick(now)
check("the 4th focus is followed by the 15 min long break",
      event == "focus_done" and t.cycles == 4 and t.remaining_ms(now) == 15 * 60000)
t2 = dt.StudyTimer()
t2.press("up", 0)
t2.press("up", 0)
t2.press("down", 0)
check("UP, UP, DOWN while idle: 25 -> 35 -> 30 minutes", t2.focus_min == 30)
t2.press("mode", 0)
t2.press("mode_long", 5000)
check("a long press skips to the break", t2.phase == dt.BREAK)
wrap = dt.StudyTimer(diff=lambda a, b: ((a - b + (1 << 29)) % (1 << 30)) - (1 << 29),
                     add=lambda a, b: (a + b) % (1 << 30))
start = (1 << 30) - 1000
wrap.press("mode", start)
check("the deadline survives the millisecond counter wrapping",
      wrap.tick((start + 25 * 60000) % (1 << 30)) == "focus_done")

# ---- 6. homework reminders ------------------------------------------------------
print()
print("6. Reminders on the Cedar Ridge calendar (synthetic school)")
EVENTS = [
    {"id": "crhs-017", "title": "Picture Retake Day", "date": "2026-10-19"},
    {"id": "crhs-018", "title": "TEST: Algebra II Unit 3 - Quadratics", "date": "2026-10-20"},
    {"id": "crhs-019", "title": "DUE: English 10 personal narrative draft", "date": "2026-10-21"},
    {"id": "crhs-020", "title": "DUE: Biology osmosis lab report", "date": "2026-10-22"},
    {"id": "crhs-021", "title": "Football vs. Eastbrook Eagles", "date": "2026-10-23"},
]
today = dt.parse_date("2026-10-19")
items = dt.upcoming(EVENTS, today)
for left, kind, title, ident in items:
    print("   {:<9} {:<4} {}".format(dt.when_text(left), kind, dt.short_title(title)))
check("three TEST/DUE items, soonest first", [i[0] for i in items] == [1, 2, 3])
check("the picture day and the game are not reminders", all(i[1] in ("TEST", "DUE") for i in items))
rem = dt.Reminders(alert_days=1)
first = rem.new_alerts(items)
again = rem.new_alerts(items)
check("the test tomorrow is announced once", len(first) == 1 and first[0][1] == "TEST" and not again)
tomorrow = dt.upcoming(EVENTS, today + 1)
check("next day the English draft is announced", [a[2][:11] for a in rem.new_alerts(tomorrow)] == ["DUE: Englis"])
check("day numbers: 2026-10-30 is 11 days after 2026-10-19",
      dt.parse_date("2026-10-30") - today == 11)
check("month ends are right: 2026-11-01 is 13 days after 2026-10-19",
      dt.parse_date("2026-11-01") - today == 13)
trip = all(dt.date_text(dt.day_number(y, m, d)) == "{:04d}-{:02d}-{:02d}".format(y, m, d)
           for y in (2024, 2026, 2027, 2100) for m in range(1, 13) for d in (1, 15, 28))
check("date_text undoes day_number for 576 dates, including a leap year", trip)
check("leap day: 2028-02-29 is the day before 2028-03-01",
      dt.parse_date("2028-03-01") - dt.parse_date("2028-02-29") == 1
      and dt.date_text(dt.parse_date("2028-02-28") + 1) == "2028-02-29")

print()
print("PASS" if all(results) else "FAIL")
