# recorder.py -- push-to-talk recording into a pre-allocated buffer (Chapter 11)
#
# record() opens the microphone, reads 40 ms frames, converts each to 16-bit
# samples straight into the caller's buffer, and stops when the person lets go
# of the button, the buffer is full, or (if you ask) the VAD hears the speech
# end. It always closes the microphone before it returns, so the speaker can
# play without the self-hearing problem (Chapter 8).
#
# The buffer is made ONCE by the caller (see new_buffer()), early in the
# program, before the heap fragments (Chapter 2). Nothing in the frame loop
# allocates a buffer.
#
# The 16-bit samples are signed, little-endian, mono, at config.MIC_SAMPLE_RATE
# (12,800 per second): 25,600 bytes for every second of sound.

import array
import gc
import time

import config
import levels
import vad as vadmod

MAX_SECONDS = 6                                  # longest utterance
MAX_FRAMES = MAX_SECONDS * 1000 // levels.FRAME_MS      # 150
SKIP_FRAMES = 3                                  # microphone start-up: 120 ms
MIN_FRAMES = 5                                   # under 200 ms is a bump (Chapter 7's MIN_MS)


def new_buffer():
    """Allocate the recording buffer: MAX_SECONDS of 16-bit samples (153,600 bytes)."""
    gc.collect()
    return bytearray(MAX_FRAMES * levels.FRAME16_BYTES)


def record(rec, button, cal, bar=None, use_vad=False, auto_stop=False,
           on_frame=None):
    """Record while button (a buttons.Button, already pressed) is held.

    rec         the buffer from new_buffer()
    cal         the calibration dict (calibration.load())
    bar         an optional ui.LevelBar to update each frame
    use_vad     also run voice activity detection on every frame
    auto_stop   with use_vad: stop as soon as the speech has ended
    on_frame    optional function called as on_frame(n, bits, gate_open)

    Returns a dict describing the recording."""
    frame = bytearray(levels.FRAME_BYTES)
    shift = cal["record_shift"]
    gate = levels.LevelGate(cal["speech_floor"], cal["gate_close"])
    detector = vadmod.VAD(gate)
    bits_by_frame = array.array("f", [0.0] * MAX_FRAMES)

    n = 0                                        # frames stored
    peak = 0
    clipped_frames = 0
    work_total = 0
    work_max = 0
    overruns = 0
    stopped = "full"
    start_index = end_index = None

    mic = config.init_microphone()
    try:
        for _ in range(SKIP_FRAMES):             # the microphone's first moments
            mic.readinto(frame)
        while n < MAX_FRAMES:
            mic.readinto(frame)                  # waits for the next 40 ms of sound
            t0 = time.ticks_us()
            bits, dc, dev_peak, clipped = levels.frame_stats(
                frame, rec, n * levels.FRAME16_BYTES, shift)
            bits_by_frame[n] = bits
            peak = max(peak, dev_peak)
            if clipped >= levels.CLIP_MIN_SAMPLES:
                clipped_frames += 1
            event = detector.update(bits) if use_vad else None
            if event == "start" and start_index is None:
                start_index = detector.start_index          # keep the FIRST start
            elif event == "end":
                end_index = detector.end_index
            if bar is not None:
                bar.set(bits, config.GREEN if detector.gate.is_open else config.YELLOW)
            if on_frame is not None:
                on_frame(n, bits, detector.gate.is_open)
            n += 1
            used = time.ticks_diff(time.ticks_us(), t0)
            work_total += used
            work_max = max(work_max, used)
            if used > levels.FRAME_MS * 1000:
                overruns += 1
            if auto_stop and event == "end":
                stopped = "vad"
                break
            if button.update() == "release":
                stopped = "release"
                break
    finally:
        mic.deinit()                             # always: the speaker may play next

    if start_index is not None and detector.state in (vadmod.SPEECH, vadmod.ENDING):
        end_index = detector.last_loud           # still talking when we stopped
    return {
        "frames": n,
        "bytes": n * levels.FRAME16_BYTES,
        "seconds": n * levels.FRAME_MS / 1000,
        "stopped": stopped,
        "peak": peak,                                   # 24-bit units, before the shift
        "peak16": min(32767, peak >> shift),            # what the 16-bit samples reached
        "limited": (peak >> shift) > 32767,             # True: the 16-bit copy was cut off
        "clipped_frames": clipped_frames,
        "work_ms_avg": (work_total / n / 1000) if n else 0,
        "work_ms_max": work_max / 1000,
        "overruns": overruns,
        "start_index": start_index,
        "end_index": end_index,
        "bits": bits_by_frame,
    }
