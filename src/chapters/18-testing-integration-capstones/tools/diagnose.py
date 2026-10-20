#!/usr/bin/env python3
"""Chapter 18: three diagnosis trees, as data.

    python3 diagnose.py list              the three trees
    python3 diagnose.py mic               answer y/n questions about a silent microphone
    python3 diagnose.py audio             ... about distorted audio
    python3 diagnose.py display           ... about a blank or wrong display
    python3 diagnose.py mic --table       print the rows (the chapter's tables)

Each tree is a list of rows, asked in order. A "yes" ends the walk at that row's
likely cause; a "no" goes on to the next row; the last row has no question and is
reached when every answer was "no". The row ids (M1, A2, D3 ...) are the ones in
the chapter's tables. Every cause, test, and fix comes from the kit README, a test
file's header, or Chapters 2 to 8 (the 'source' field says where). A tree names
the LIKELY cause: run the quick test before you change anything.
"""
import sys

# (id, question or None, likely cause, quick test, fix, source)
MIC = [
    ("M1", "An error at start, and it says 'must be sck+1'?",
     "The WS (word select) wire is not on the pin after SCK",
     "Compare with the pin table: SCK GP10, WS GP11",
     "Move the wire back. Do not edit config.py: SCK on GP12 would need WS on GP13, the MODE button",
     "kit README; Ch 4, 8"),
    ("M2", "An error at start, with another message?",
     "A previous run left the I2S block open, or memory is short (likely)",
     "Ctrl-D, run again, print gc.mem_free()",
     "Close the microphone in a finally block",
     "Ch 2"),
    ("M3", "No error, but the spread is 0 (a flat line)?",
     "Swapped SCK, WS, or SD wires; no power; or the mute switch is on",
     "In order: SCK, WS, SD; VDD on 3V3 (not 5 V); GND and L/R on GND; the mute switch",
     "Re-seat the wires. A swapped microphone starts with no error and sends zeros",
     "kit README; Ch 4, 17"),
    ("M4", "The loudness barely changes when you talk next to it?",
     "L/R is on 3V3, so the microphone answers in the right slot while the program reads the left",
     "Look at where L/R goes",
     "Move L/R to GND",
     "Ch 8"),
    ("M5", "The meter is pinned at the top?",
     "The 32-bit samples were not shifted right by 8 (values 256 times too big), or the room or SD wire is noisy",
     "Print a few samples before and after >> config.MIC_SAMPLE_SHIFT",
     "Shift by MIC_SAMPLE_SHIFT and subtract the frame's DC offset",
     "Ch 8"),
    ("M6", None,
     "The microphone works; the level you chose is the problem",
     "Probe 03: does a clap jump several bits?",
     "Calibrate the noise floor first; for quiet playback raise PLAYBACK_GAIN",
     "kit test 07; Ch 11"),
]

AUDIO = [
    ("A1", "Is the speaker silent, not distorted?",
     "No power or ground at the amplifier, or a signal wire is wrong",
     "Probe 04; VIN and GND, then BCLK GP20, LRC GP21, DIN GP19",
     "Fix the wire. If I2S() raises an error, LRC must be right after BCLK",
     "kit test 05"),
    ("A2", "Does it crackle only when loud?",
     "The samples clip: peaks are cut flat",
     "Lower VOLUME; the crackle should go",
     "Reduce VOLUME (test 05) or PLAYBACK_GAIN (test 07)",
     "Ch 3; kit tests 05, 07"),
    ("A3", "Is the pitch wrong, too high and fast or too low and slow?",
     "The playback sample rate is not the recording rate",
     "Print both rates",
     "Use MIC_SAMPLE_RATE for both",
     "kit test 07; Ch 8"),
    ("A4", "Does it stutter or have gaps?",
     "The loop takes longer than one 40 ms frame: a frame overrun",
     "Wrap the microphone in OverrunCounter; read the summary",
     "Redraw only changed regions, or slice big jobs (scheduler.py)",
     "Ch 5, 6, 8, 18"),
    ("A5", "Is the start clicky, or the end cut off?",
     "deinit() ran before the buffer drained; or a WAV header was played as sound",
     "Listen with and without f.seek(44); lengthen the tail",
     "Write silence and wait the buffer's length; skip the 44-byte header; fade 10 ms",
     "Ch 3, 8"),
    ("A6", "Is there hiss or buzz even when nothing plays?",
     "Power or ground noise: loose grounds, long wires",
     "Re-seat every GND; keep microphone and amplifier wires apart",
     "Shorter wires and one solid ground rail",
     "Ch 4"),
    ("A7", None,
     "No cause matched",
     "Play the 05 tone and a 07 recording separately",
     "Fix the path that distorts",
     "kit tests 05, 07"),
]

DISPLAY = [
    ("D1", "Is the screen completely dark, with no light?",
     "The backlight is off: BL not wired, VCC or GND missing, or set_backlight(True) never ran",
     "Check BL to GP7, VCC to 3V3, GND",
     "Wire BL to GP7 and call config.set_backlight(True)",
     "Ch 4, 5"),
    ("D2", "Did the program stop with an error before drawing?",
     "A kit file is missing: config.py, lib/gc9b72.py, or a font",
     "Self-test 'Files', or 02-probe.py section 4",
     "Run upload-chapter.sh",
     "kit README; Ch 2"),
    ("D3", "Is it lit but only black or random noise?",
     "A control wire is wrong: SCL GP2, SDA GP3, RST GP4, DC GP5, or CS GP6",
     "07-wiring-check.py; touch each wire",
     "Fix the wire; the colors are in config.py",
     "config.py; Ch 4"),
    ("D4", "Is the picture speckled or torn?",
     "The SPI speed is too fast for the wiring",
     "Print the SPI object to see the rate you got",
     "BAUDRATE = 12_000_000 (nothing exists between 12 and 24 MHz)",
     "config.py; Ch 5"),
    ("D5", "Is part of what you drew missing?",
     "It was drawn outside the visible circle: corners and edge are hidden",
     "Chapter 4's 04-display-visible-area.py",
     "Stay inside SAFE_RADIUS, 168 pixels from the center",
     "Ch 4, 6"),
    ("D6", "Is the picture rotated or mirrored?",
     "The driver's rotation argument",
     "Try 0, 1, 2, 3 in config.init_display()",
     "Choose the one that matches",
     "Ch 5"),
    ("D7", "Are old letters left over, or is the picture sheared or striped?",
     "Text was not padded to a fixed width, or a buffer is not width x height x 2 bytes",
     "Print len(buffer) and compare",
     "Pad with .center(width); size buffers exactly",
     "Ch 6"),
    ("D8", None,
     "A program from an earlier kit may be running as main.py",
     "mpremote fs ls",
     "mpremote fs rm main.py",
     "kit README; Ch 2"),
]

TREES = {"mic": ("silent microphone", MIC), "audio": ("distorted audio", AUDIO),
         "display": ("blank display", DISPLAY)}


def diagnose(rows, answers):
    """Walk a tree with a function answers(question) -> True/False. Returns the row."""
    for row in rows[:-1]:
        if answers(row[1]):
            return row
    return rows[-1]


def main(argv):
    if len(argv) < 2 or argv[1] not in TREES:
        for key, (name, rows) in TREES.items():
            print("  {:<8} {} ({} rows)".format(key, name, len(rows)))
        return 0
    name, rows = TREES[argv[1]]
    if "--table" in argv:
        for rid, question, cause, test, fix, source in rows:
            print("{}  {}".format(rid, question or "None of the above"))
            print("     cause:", cause)
            print("     test :", test)
            print("     fix  :", fix)
        return 0

    def ask(question):
        answer = ""
        while answer not in ("y", "n"):
            answer = input(question + " [y/n] ").strip().lower()[:1]
        return answer == "y"

    rid, _, cause, test, fix, source = diagnose(rows, ask)
    print()
    print("Row         :", rid)
    print("Likely cause:", cause)
    print("Quick test  :", test)
    print("Fix         :", fix)
    print("Source      :", source)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
