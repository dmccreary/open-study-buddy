# checks.py -- Chapter 18: one check per subsystem
#
# Each check_* function returns (verdict, detail) where verdict is one of:
#   PASS  the program measured something and it is right
#   FAIL  the program measured something and it is wrong
#   ASK   the program cannot tell; a human must look or listen
#   SKIP  the part is not wired or not configured
# The probes (02 to 06) run one check and explain the result. selftest.py runs
# them all and shows a summary on the round display.
#
# The honest limit: the display and the amplifier cannot report back to the
# Pico (kit README), so they can only ever be ASK (or, for the speaker, PASS
# when the microphone hears the tone).
#
# Hardware is touched only inside the functions, so this file imports cleanly
# on a computer and the pure helpers can be tested there.

import gc
import math
import os
import struct
import time

PASS, FAIL, ASK, SKIP = "PASS", "FAIL", "ASK", "SKIP"

FRAME_SAMPLES = 512
FRAME_BYTES = FRAME_SAMPLES * 4          # 32-bit samples
FRAME_FORMAT = "<512i"
SKIP_FRAMES = 8                          # the microphone's start-up (kit test 06)
LOG2 = math.log(2)
CLIP_LEVEL = 8_000_000                   # 24-bit full scale is 8,388,607
MIN_RISE_BITS = 2.0                      # half of the 3.9 bits Chapter 8 measured on one board
RESERVED = (23, 24, 25, 29)              # belong to the wireless chip (Chapter 4)

# Pico GP number -> physical header pin (the standard Pico pinout; matches the
# Chapter 4 pin assignment table)
PHYSICAL = {0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
            10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
            18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34}


# ---- pure helpers (testable anywhere) ----------------------------------

def frame_stats(samples):
    """samples: a list of 24-bit ints. Returns a dict of what a probe needs."""
    n = len(samples)
    mean = sum(samples) // n                       # the DC offset
    average = sum(abs(s - mean) for s in samples) // n
    return {"min": min(samples), "max": max(samples),
            "spread": max(samples) - min(samples), "dc": mean,
            "bits": math.log(average + 1) / LOG2,
            "clipped": sum(1 for s in samples if abs(s) >= CLIP_LEVEL)}


def wiring_table(config):
    """Rows of (part, part pin, Pico pin, physical pin) from config.py.
    The numbers come from config, so a change there changes this table."""
    def gp(n):
        return ("GP{}".format(n), PHYSICAL.get(n, "?"))
    rows = [
        ("Display", "SCL", config.SCK_PIN), ("Display", "SDA", config.MOSI_PIN),
        ("Display", "RST", config.RST_PIN), ("Display", "DC", config.DC_PIN),
        ("Display", "CS", config.CS_PIN), ("Display", "BL", config.BL_PIN),
        ("Microphone", "SCK", config.MIC_SCK_PIN),
        ("Microphone", "WS", config.MIC_WS_PIN),
        ("Microphone", "SD", config.MIC_SD_PIN),
        ("Button MODE", "one leg", config.BUTTON_MODE_PIN),
        ("Button UP", "one leg", config.BUTTON_INCREMENT_PIN),
        ("Button DOWN", "one leg", config.BUTTON_DECREMENT_PIN),
        ("Amplifier", "DIN", config.I2S_DIN_PIN),
        ("Amplifier", "BCLK", config.I2S_BCLK_PIN),
        ("Amplifier", "LRC", config.I2S_LRC_PIN),
        ("Amplifier", "GAIN", config.I2S_GAIN_PIN),
    ]
    table = [(part, pin, "GP{}".format(n), PHYSICAL.get(n, "?"))
             for part, pin, n in rows]
    table += [
        ("Display", "VCC", "3V3", 36), ("Display", "GND", "GND", "any GND"),
        ("Microphone", "VDD", "3V3", 36),
        ("Microphone", "GND and L/R", "GND", "any GND"),
        ("Buttons", "other legs", "GND", "any GND"),
        ("Amplifier", "VIN", "VBUS or 3V3", "40 or 36"),
        ("Amplifier", "GND", "GND", "any GND"),
    ]
    return table


def check_pin_plan(config):
    problems = []
    for label, clock, word in (("speaker", config.I2S_BCLK_PIN, config.I2S_LRC_PIN),
                               ("microphone", config.MIC_SCK_PIN, config.MIC_WS_PIN)):
        if word != clock + 1:
            problems.append("{} word select GP{} must be GP{} (clock + 1)".format(
                label, word, clock + 1))
    if config.I2S_SPEAKER_ID == config.MIC_I2S_ID:
        problems.append("speaker and microphone share an I2S block")
    seen = {}
    for part, pin, name, _ in wiring_table(config):
        if name.startswith("GP"):
            n = int(name[2:])
            if n in seen:
                problems.append("GP{} used by '{}' and '{}'".format(n, seen[n], part + " " + pin))
            seen[n] = part + " " + pin
            if n in RESERVED:
                problems.append("GP{} ('{} {}') belongs to the wireless chip".format(n, part, pin))
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, "{} pins, I2S pairs adjacent, none reserved or doubled".format(len(seen))


# ---- hardware checks ---------------------------------------------------

def check_files():
    need = ("config.py", "lib/gc9b72.py", "lib/vga1_8x16.py", "lib/vga1_bold_16x32.py")
    missing = []
    for path in need:
        try:
            os.stat(path)
        except OSError:
            missing.append(path)
    if missing:
        return FAIL, "missing on the board: " + ", ".join(missing)
    return PASS, "config.py, driver and both fonts are present"


def check_memory():
    gc.collect()
    free = gc.mem_free()
    try:
        block = bytearray(3 * 12800 * 4)
        del block
        fits = True
    except MemoryError:
        fits = False
    gc.collect()
    if not fits:
        return FAIL, "heap {:,} bytes free but a 3 s recording (153,600) does not fit".format(free)
    return PASS, "heap {:,} bytes free; a 3 s recording fits".format(free)


def check_flash():
    block, _, total, free = os.statvfs("/")[:4]
    free_bytes = block * free
    if free_bytes < 64 * 1024:
        return FAIL, "only {:,} bytes of flash free".format(free_bytes)
    return PASS, "{:,} bytes of flash free".format(free_bytes)


def read_frames(mic, count, buf=None):
    """Read `count` frames; returns a list of frame_stats dicts."""
    buf = buf or bytearray(FRAME_BYTES)
    out = []
    for _ in range(count):
        mic.readinto(buf)
        samples = [s >> 8 for s in struct.unpack(FRAME_FORMAT, buf)]
        out.append(frame_stats(samples))
    return out


def check_mic(config, frames=12):
    """Returns (verdict, detail, stats) where stats is the list from read_frames."""
    mic = None
    try:
        mic = config.init_microphone()
        buf = bytearray(FRAME_BYTES)
        for _ in range(SKIP_FRAMES):
            mic.readinto(buf)
        stats = read_frames(mic, frames, buf)
    except Exception as error:
        hint = ""
        if "sck+1" in str(error):
            hint = " (word select must be the pin after the clock: SCK GP10, WS GP11)"
        return FAIL, "microphone failed to start: {}{}".format(error, hint), []
    finally:
        if mic is not None:
            mic.deinit()
    lo = min(s["min"] for s in stats)
    hi = max(s["max"] for s in stats)
    bits = sum(s["bits"] for s in stats) / len(stats)
    dc = sum(s["dc"] for s in stats) // len(stats)
    if hi == lo:
        return FAIL, ("flat line: every sample is {}. Check SCK GP10, WS GP11, SD GP12; "
                      "VDD on 3V3; GND and L/R on GND; the mute switch").format(lo), stats
    clipped = sum(s["clipped"] for s in stats)
    if clipped:
        return FAIL, ("{} samples at full scale: too loud, or the SD wire is picking up "
                      "noise").format(clipped), stats
    return PASS, "spread {:,}, loudness {:.1f} bits, DC offset {:,}".format(hi - lo, bits, dc), stats


def tone_chunk(config, freq=1000, volume=30):
    """One 40 ms chunk of a sine that loops without a click when freq is 1000 Hz
    at 12,800 Hz (512 samples = 40 whole cycles)."""
    rate = config.MIC_SAMPLE_RATE
    amp = 32767 * min(volume, config.VOLUME) // 100
    chunk = bytearray(FRAME_SAMPLES * 2)
    for i in range(FRAME_SAMPLES):
        struct.pack_into("<h", chunk, i * 2,
                         int(amp * math.sin(2 * math.pi * freq * i / rate)))
    return chunk


def open_speaker(config):
    from machine import I2S, Pin
    config.set_gain()
    return I2S(config.I2S_SPEAKER_ID, sck=Pin(config.I2S_BCLK_PIN),
               ws=Pin(config.I2S_LRC_PIN), sd=Pin(config.I2S_DIN_PIN),
               mode=I2S.TX, bits=16, format=I2S.MONO,
               rate=config.MIC_SAMPLE_RATE, ibuf=8192)


def close_speaker(speaker, config):
    """Let the buffer drain before deinit, or the end of the sound is cut off
    (Chapter 8): 8,192 bytes at 2 bytes per sample and the sample rate."""
    speaker.write(bytes(FRAME_SAMPLES * 2))
    time.sleep_ms(8192 * 1000 // (config.MIC_SAMPLE_RATE * 2) + 50)
    speaker.deinit()


def check_speaker(config, with_mic=True, tone_frames=25):
    """Plays a quiet 1 kHz tone. With the microphone wired, PASS if the
    microphone hears it MIN_RISE_BITS above the room; otherwise ASK."""
    chunk = tone_chunk(config)
    speaker = mic = None
    try:
        speaker = open_speaker(config)
        if not with_mic:
            for _ in range(tone_frames):
                speaker.write(chunk)
            return ASK, "tone played; did you hear a steady beep?", 0.0
        mic = config.init_microphone()
        buf = bytearray(FRAME_BYTES)
        for _ in range(SKIP_FRAMES):
            mic.readinto(buf)
        quiet = read_frames(mic, 10, buf)
        loud = []
        for _ in range(tone_frames):
            speaker.write(chunk)
            loud += read_frames(mic, 1, buf)
        floor = sum(s["bits"] for s in quiet) / len(quiet)
        during = loud[5:]                       # skip the first frames of the tone
        level = sum(s["bits"] for s in during) / len(during)
        rise = level - floor
        if min(s["spread"] for s in quiet) == 0 and max(s["spread"] for s in quiet) == 0:
            return ASK, "microphone is a flat line, so it cannot check the speaker", rise
        if rise >= MIN_RISE_BITS:
            return PASS, "microphone heard the tone {:.1f} bits above the room".format(rise), rise
        return ASK, ("microphone heard only {:.1f} bits more than the room; "
                     "did you hear the beep?").format(rise), rise
    except Exception as error:
        return FAIL, "speaker failed to start: {}".format(error), 0.0
    finally:
        if mic is not None:
            mic.deinit()
        if speaker is not None:
            close_speaker(speaker, config)


def check_buttons(config, press=False, wait_ms=8000):
    """Idle check: all three read 1. With press=True, also wait for each to be
    pressed and report how many bounces it made."""
    buttons = config.init_buttons()
    names = ("MODE", "UP", "DOWN")
    pins = (config.BUTTON_MODE_PIN, config.BUTTON_INCREMENT_PIN,
            config.BUTTON_DECREMENT_PIN)
    held = [names[i] + " (GP{})".format(pins[i]) for i in range(3) if buttons[i].value() == 0]
    if held:
        return FAIL, "reads pressed with nobody touching: " + ", ".join(held) + \
            " (held, shorted to GND, or wired to the wrong side of the button)"
    if not press:
        return PASS, "all three read 1 (not pressed); an unconnected wire also reads 1"
    report = []
    for i in range(3):
        print("Press and release", names[i], "...")
        start = time.ticks_ms()
        while buttons[i].value() == 1:
            if time.ticks_diff(time.ticks_ms(), start) > wait_ms:
                return FAIL, "no press seen on {} (GP{}): loose wire or wrong pin".format(
                    names[i], pins[i])
            time.sleep_ms(1)
        edges, last, t0 = 0, 0, time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < 50:       # watch the bounce
            v = buttons[i].value()
            if v != last:
                edges += 1
                last = v
            time.sleep_ms(1)
        while buttons[i].value() == 0:
            time.sleep_ms(1)
        report.append("{} bounced {} edges".format(names[i], edges))
    return PASS, "; ".join(report)


def check_wifi(config):
    try:
        import network
    except ImportError:
        return SKIP, "no network module"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    found = wlan.scan()
    if not found:
        return FAIL, "the radio sees no networks at all"
    try:
        import secrets
        ssid, password = secrets.wifi_ssid, secrets.wifi_pass
    except (ImportError, AttributeError):
        return PASS, "radio sees {} network(s); no secrets.py, so no connection tried".format(len(found))
    wlan.connect(ssid, password)
    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > 15000:
            return FAIL, "saw {} network(s) but could not join '{}' in 15 s (2.4 GHz network? password?)".format(len(found), ssid)
        time.sleep_ms(200)
    return PASS, "joined '{}' as {}".format(ssid, wlan.ifconfig()[0])


# ---- asking a human --------------------------------------------------------

def ask_yes_no(config, display, question, seconds=20):
    """Shows question on the display. UP = yes, DOWN = no. Returns True, False,
    or None if nobody answered. (Buttons read 0 while pressed.)"""
    print(question, "  [UP = yes, DOWN = no]")
    if display is not None:
        config.centered_text(display, config.SMALL_FONT, question[:38].center(38), 292,
                             config.WHITE)
        config.centered_text(display, config.SMALL_FONT, "UP = yes   DOWN = no".center(38), 312,
                             config.YELLOW)
    _, up, down = config.init_buttons()
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < seconds * 1000:
        if up.value() == 0:
            return True
        if down.value() == 0:
            return False
        time.sleep_ms(10)
    return None
