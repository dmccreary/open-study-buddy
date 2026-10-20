# Chapter 11, Test 09: Self-test of the calibration, gate and VAD logic
# Checks the pure-Python parts of this chapter with SYNTHETIC frames (synth.py,
# fixed seeds), so it needs no hardware and prints the same numbers every run.
# It runs on your computer (python3 09-calibration-selftest.py) and on the Pico.
# The chapter's tables of gate and VAD behavior come from this output.
#
# Checks: percentile, calibration values and their order, the problem flags
# (clipping, low SNR, noisy room), the level gate versus a single threshold,
# the VAD start and end frames, pre-roll and hang-over boundaries, the buffer
# arithmetic, the level-bar byte counts, and saving and loading the file.
#
# PASS: the last line says PASS. The numbers are synthetic, not measurements.

NAME = "09-calibration-selftest.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os

import calibration
import levels
import synth
import vad

ok = True


def check(label, good):
    global ok
    ok = ok and good
    print("  {:<62} {}".format(label, "ok" if good else "FAIL"))


def frames_bits(frames):
    return [levels.frame_stats(f)[0] for f in frames]


# ---------------------------------------------------------------------------
print()
print("1. percentile")
check("90th percentile of 1..10 is 9.1", abs(levels.percentile(list(range(1, 11)), 90) - 9.1) < 1e-9)
check("median of 1..10 is 5.5", abs(levels.percentile(list(range(1, 11)), 50) - 5.5) < 1e-9)
check("one reading: every percentile is that reading", levels.percentile([4.2], 95) == 4.2)

# ---------------------------------------------------------------------------
print()
print("2. Calibration from synthetic frames (quiet 13.0 bits, speech 17.0 bits)")
rng = synth.Rng(11)
quiet = frames_bits([synth.noise_frame(rng, 13.0 + 0.15 * rng.gauss()) for _ in range(60)])
speech = frames_bits([synth.speech_frame(rng, 17.0 + 0.4 * rng.gauss(), phase=i * 512)
                      for i in range(60)])
cal, problems = levels.make_calibration(quiet, speech, 300000, 0, 30)
for key in ("noise_floor", "noise_ceiling", "speech_level", "speech_floor",
            "gate_close", "record_shift", "distance_cm"):
    print("  {:<14} {}".format(key, cal[key]))
print("  problems       {}".format(problems if problems else "none"))
check("no problems flagged", problems == [])
check("order: floor < ceiling < gate_close < speech_floor < speech_level",
      cal["noise_floor"] < cal["noise_ceiling"] < cal["gate_close"]
      < cal["speech_floor"] < cal["speech_level"])
check("gate_close is above the noise ceiling", cal["gate_close"] > cal["noise_ceiling"])
check("speech_floor is 0.5 bit above gate_close (hysteresis)",
      abs(cal["speech_floor"] - cal["gate_close"] - 0.5) < 0.011)
check("a peak of 300,000 gives record_shift 5", cal["record_shift"] == 5)
print("  SNR = {:.2f} bits = {:.1f} dB".format(
    levels.snr_bits(cal["speech_level"], cal["noise_floor"]),
    levels.snr_db(cal["speech_level"], cal["noise_floor"])))

# ---------------------------------------------------------------------------
print()
print("3. Problem flags")
_, p = levels.make_calibration(quiet, [b - 3.0 for b in speech], 300000, 0, 30)
check("speech only 1 bit over the floor -> snr_low", "snr_low" in p)
_, p = levels.make_calibration(quiet, speech, 300000, 4, 30)
check("clipped speech frames -> clipping", "clipping" in p)
noisy = quiet[:55] + [floor + 3.0 for floor in quiet[:5]] + quiet[:5]
_, p = levels.make_calibration(noisy, speech, 300000, 0, 30)
check("a few loud frames in the quiet part -> room_not_quiet", "room_not_quiet" in p)
_, p = levels.make_calibration(quiet[:5], speech, 300000, 0, 30)
check("5 quiet frames -> too_few_frames", "too_few_frames" in p)
frame = synth.clipped_frame(synth.Rng(5))
bits, dc, dev_peak, clipped = levels.frame_stats(frame)
print("  a synthetic shouted frame: {:.2f} bits, peak {}, clipped samples {}".format(
    bits, dev_peak, clipped))
check("the shouted frame has clipped samples", clipped >= levels.CLIP_MIN_SAMPLES)
check("a normal frame has none", levels.frame_stats(synth.noise_frame(synth.Rng(1), 13.0))[3] == 0)
check("record_shift_for(8,000,000) is 8", levels.record_shift_for(8000000) == 8)
check("record_shift_for(16,000) is 0", levels.record_shift_for(16000) == 0)

# ---------------------------------------------------------------------------
print()
print("4. The level gate versus a single threshold")
# A level that wobbles around the threshold of 15.0 bits.
wobble = [14.8, 15.1, 14.9, 15.2, 14.7, 15.0, 14.9, 15.3, 14.6, 15.1, 15.4, 15.6,
          15.2, 14.9, 15.1, 14.8, 14.2, 13.4, 13.2, 13.5]
gate = levels.LevelGate(15.0, 14.5)
states = [gate.update(b) for b in wobble]
plain = [b >= 15.0 for b in wobble]


def flips(seq):
    return sum([1 for i in range(1, len(seq)) if seq[i] != seq[i - 1]])


print("  levels   ", " ".join(["{:.1f}".format(b) for b in wobble]))
print("  plain    ", " ".join(["  # " if s else "  . " for s in plain]))
print("  gate     ", " ".join(["  # " if s else "  . " for s in states]))
print("  flips: single threshold {}, gate with hysteresis {}".format(flips(plain), flips(states)))
check("the gate flips less than the single threshold", flips(states) < flips(plain))
check("the gate opens at 15.0 exactly (>=)", levels.LevelGate(15.0, 14.5).update(15.0))
check("the gate stays open at 14.5 exactly (closes only BELOW)", (lambda g: (g.update(15.2), g.update(14.5))[1])(levels.LevelGate(15.0, 14.5)))
check("the gate closes at 14.49", not (lambda g: (g.update(15.2), g.update(14.49))[1])(levels.LevelGate(15.0, 14.5)))

# ---------------------------------------------------------------------------
print()
print("5. VAD on synthetic noise, speech, noise (20 + 30 + 50 frames)")
rng = synth.Rng(21)
trace = ([synth.noise_frame(rng, 13.0) for _ in range(20)]
         + [synth.speech_frame(rng, 17.0, phase=i * 512) for i in range(30)]
         + [synth.noise_frame(rng, 13.0) for _ in range(50)])
bits = frames_bits(trace)
detector = vad.VAD(calibration.gate_from(cal))
events = []
for i, b in enumerate(bits):
    e = detector.update(b)
    if e:
        events.append((i, e))
print("  events (frame confirmed, kind):", events)
print("  start_index {}, end_index {}".format(detector.start_index, detector.end_index))
check("speech starts at frame 20", detector.start_index == 20)
check("speech ends at frame 49", detector.end_index == 49)
check("start is confirmed 2 frames later (START_FRAMES - 1)", events[0] == (22, "start"))
check("end is confirmed END_FRAMES frames after the last loud one", events[1] == (49 + vad.END_FRAMES, "end"))
first, stop = vad.boundaries(detector.start_index, detector.end_index, len(bits))
print("  keep frames {} to {} ({} frames, {} ms)".format(first, stop - 1, stop - first,
                                                       (stop - first) * levels.FRAME_MS))
check("pre-roll 4 -> first kept frame is 16", first == 16)
check("hang-over 5 -> last kept frame is 54", stop - 1 == 54)
check("boundaries stay inside the recording", vad.boundaries(1, 148, 150) == (0, 150))

# a click and a pause inside speech
click = [13.0] * 10 + [18.0] + [13.0] * 10
d2 = vad.VAD(calibration.gate_from(cal))
check("a one-frame click does not start speech", all([d2.update(b) is None for b in click]))
words = [13.0] * 5 + [17.0] * 8 + [13.0] * 6 + [17.0] * 8 + [13.0] * 20
d3 = vad.VAD(calibration.gate_from(cal))
ev = [(i, d3.update(b)) for i, b in enumerate(words)]
ev = [(i, e) for i, e in ev if e]
print("  two words with a 6-frame (240 ms) pause: events", ev)
check("a 240 ms pause inside the phrase does not end it (one start, one end)",
      [e for _, e in ev] == ["start", "end"] and d3.end_index == 26)

# ---------------------------------------------------------------------------
print()
print("6. Buffer and display arithmetic")
rate = levels.RATE
print("  16-bit mono at {} Hz = {} bytes per second".format(rate, rate * 2))
print("  {} s buffer = {} bytes = {} frames".format(
    6, 6 * rate * 2, 6 * rate // levels.FRAME_SAMPLES))
check("6 s of 16-bit = 153,600 bytes, the size of kit test 07's 3 s of 32-bit",
      6 * rate * 2 == 153600 == 3 * rate * 4)
check("one frame is 1,024 bytes of 16-bit samples", levels.FRAME16_BYTES == 1024)
check("the buffer holds exactly 150 frames", 153600 // levels.FRAME16_BYTES == 150)
bar_bytes = 200 * 22 * 2
print("  a full 200 x 22 bar = {} bytes = {:.2f} ms at 24 MHz".format(bar_bytes, bar_bytes * 8 / 24000))
print("  a full 360 x 360 screen = {} bytes = {:.1f} ms at 24 MHz".format(
    360 * 360 * 2, 360 * 360 * 2 * 8 / 24000))
print("  the bar growing by 10 columns = {} bytes = {:.3f} ms".format(10 * 22 * 2, 10 * 22 * 2 * 8 / 24000))
check("full screen wire time is 86.4 ms (Chapter 5)", abs(360 * 360 * 2 * 8 / 24000 - 86.4) < 0.01)
check("a full bar is 8,800 bytes", bar_bytes == 8800)

# ---------------------------------------------------------------------------
print()
print("7. Saving and loading calibration.json")
test_path = "calibration-selftest.json"
calibration.save(cal, test_path)
back = calibration.load(test_path)
os.remove(test_path)
check("what is loaded equals what was saved",
      all([back[k] == cal[k] for k in cal]) and back["calibrated"])
check("no .tmp file is left behind", test_path + ".tmp" not in os.listdir())
check("a missing file gives the defaults", not calibration.load("no-such-file.json")["calibrated"])

print()
print("PASS" if ok else "FAIL")
