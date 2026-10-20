# calibration.py -- save and load the microphone calibration (Chapter 11)
#
# The calibration is a small JSON file, calibration.json, in the Pico's flash:
#
#   {"version": 1, "noise_floor": 12.9, "noise_ceiling": 13.4, ...}
#
# (the values come from 04-calibrate.py; see the chapter for what each means).
# If the file is missing or damaged, load() returns DEFAULTS, so programs
# still run before the first calibration. DEFAULTS["calibrated"] is False so a
# program can warn that it is using guesses.
#
# FLASH CAUTION: flash can be rewritten only a limited number of times, and a
# write that is cut off by a power loss can leave a damaged file. So:
#   * save() is called only when the person presses a button to save, never
#     from a loop.
#   * save() writes a temporary file first and only then swaps it in, so the
#     old file stays whole until the new one is complete.
#
# This file is copied unchanged into src/chapters/12-wake-word-detection/.

import json
import os

import levels

PATH = "calibration.json"

DEFAULTS = {
    "version": 1,
    "calibrated": False,
    "noise_floor": 13.0,        # kit boards measured 12.5 and 13.1 bits in quiet rooms
    "noise_ceiling": 13.5,      # a guess: half a bit above the floor
    "speech_level": 17.0,       # a guess
    "speech_floor": 15.0,       # floor + 2.0 bits, the rule kit test 06 uses
    "gate_close": 14.5,         # half a bit below speech_floor
    "record_shift": levels.DEFAULT_SHIFT,
    "distance_cm": 30,
}


def load(path=PATH):
    """Returns the calibration dict (DEFAULTS if there is no good file)."""
    cal = dict(DEFAULTS)
    try:
        with open(path) as f:
            stored = json.load(f)
        cal.update(stored)
        cal["calibrated"] = True
    except (OSError, ValueError):
        pass
    return cal


def save(cal, path=PATH):
    """Write the calibration to flash. Call only when the person says save."""
    stored = {}
    for key in cal:
        if key != "calibrated":
            stored[key] = cal[key]
    temporary = path + ".tmp"
    with open(temporary, "w") as f:
        json.dump(stored, f)
    try:
        os.remove(path)
    except OSError:
        pass                     # there was no old file
    os.rename(temporary, path)


def gate_from(cal):
    """A LevelGate set from the calibration's speech floor and close level."""
    return levels.LevelGate(cal["speech_floor"], cal["gate_close"])
