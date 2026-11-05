# demo_tones.py -- demo 6 of 20-demo-template.py: the sound lab.
#
# Plays a short show on the speaker, and draws each sound as it plays:
#
#   1. Four kinds of wave, all at 440 Hz (the A above middle C): sine,
#      square, triangle, sawtooth. Same pitch, different "color" of sound.
#   2. One sine wave going up in octaves: 220, 440, 880, 1760 Hz. Each
#      octave doubles the frequency -- twice as many waves on the screen.
#   3. The start of the Mario theme in square waves, the sound of old
#      video games.
#
# Then:  UP plays it all again,  DOWN plays just the tune.
#
# This is test 05 without the volume steps, and with the waves drawn. The
# sound is made by demo_kit.Speaker, which steps through a 256-point table
# of one wave cycle (see its notes for why that is faster than test 05).
#
# HOW THE SHOW RUNS WHILE THE BUTTONS STILL WORK. The show is a generator:
# a function with `yield` in it. Each time update() calls next() on it,
# the function runs until its next `yield` -- one sound -- and pauses
# there, so the template's loop gets to look at the buttons in between.

import time

import config
from demo_kit import (BLACK, WHITE, DIM, FAINT, TRACK, SMALL, BIG, CX, put,
                      centered, menu_hint, make_speaker,
                      SINE, SQUARE, TRIANGLE, SAWTOOTH, WAVES)

WAVE_COLORS = {SINE: config.CYAN, SQUARE: config.YELLOW,
               TRIANGLE: config.GREEN, SAWTOOTH: config.MAGENTA}
WAVE_WORDS = {SINE: "smooth and pure, like a flute",
              SQUARE: "buzzy, like an old video game",
              TRIANGLE: "soft and hollow",
              SAWTOOTH: "bright and brassy"}

# The first notes of the Super Mario Bros. theme, in eighth notes:
# (name, Hz, ms). Name "-" is a rest. Swap in any tune you like -- Try
# This 2 in test 05 has the start of Twinkle Twinkle.
TUNE_NAME = "the Mario theme"
TUNE = (("E5", 659, 150), ("E5", 659, 150), ("-", 0, 150),
        ("E5", 659, 150), ("-", 0, 150), ("C5", 523, 150),
        ("E5", 659, 300), ("G5", 784, 300), ("-", 0, 300),
        ("G4", 392, 300), ("-", 0, 300))
NOTE_GAP_MS = 25           # a breath between notes, so repeats sound twice

AHEAD_MS = 100             # start the next sound when this little is left

TITLE_Y = 34
NAME_Y = 62
FREQ_Y = 100
PLOT_X, PLOT_Y, PLOT_W, PLOT_H = 60, 146, 240, 76
WORDS_Y = 238
PROMPT_Y = 268
MENU_Y = 300


def start(display, kit, saved):
    global _display, _kit, speaker, name_line, freq_line, show
    _display = display
    _kit = kit
    display.fill(BLACK)
    centered(display, SMALL, "SOUND LAB", TITLE_Y, DIM)
    menu_hint(display, MENU_Y)
    speaker = make_speaker()
    show = None
    if speaker is None:
        centered(display, BIG, "No speaker", 150, config.RED)
        centered(display, SMALL, "check the amplifier wires", 196, DIM)
        return
    show = program(True)


def big(y, words, color):
    """A line of big text, padded to 14 letters to cover the last one."""
    put(_display, BIG, words, y, color, 14)


def plot(wave, cycles, color):
    """Draw `cycles` cycles of a wave in the plot box, from the very table
    the speaker is playing."""
    display = _display
    display.fill_rect(PLOT_X, PLOT_Y, PLOT_W, PLOT_H, BLACK)
    middle = PLOT_Y + PLOT_H // 2
    display.hline(PLOT_X, middle, PLOT_W, TRACK)
    table = speaker._table(wave, speaker.volume)
    peak = max(max(table), -min(table)) or 1
    half = PLOT_H // 2 - 2
    previous = None
    for x in range(0, PLOT_W, 2):
        index = int(x * cycles * 256 // PLOT_W) % 256
        y = middle - table[index] * half // peak
        if previous is not None:
            display.line(PLOT_X + x - 2, previous, PLOT_X + x, y, color)
        previous = y


def program(everything):
    """The show. Each `yield` is a pause between sounds."""
    _display.fill_rect(30, PROMPT_Y, 300, 16, BLACK)
    if everything:
        for wave in WAVES:
            color = WAVE_COLORS[wave]
            big(NAME_Y, wave.upper(), color)
            big(FREQ_Y, "440 Hz", WHITE)
            plot(wave, 2, color)
            put(_display, SMALL, WAVE_WORDS[wave], WORDS_Y, DIM, 34)
            print("{:9} 440 Hz".format(wave))
            speaker.play(440, 900, wave)
            speaker.rest(250)
            yield

        for octave, freq in enumerate((220, 440, 880, 1760)):
            big(NAME_Y, "OCTAVES", WAVE_COLORS[SINE])
            big(FREQ_Y, "%d Hz" % freq, WHITE)
            plot(SINE, 1 << octave, WAVE_COLORS[SINE])
            put(_display, SMALL, "double the Hz: one octave up"
                if octave else "a low A, 220 waves a second", WORDS_Y,
                DIM, 34)
            print("sine      {} Hz".format(freq))
            speaker.play(freq, 600)
            speaker.rest(150)
            yield

    big(NAME_Y, "A TUNE", WAVE_COLORS[SQUARE])
    plot(SQUARE, 2, WAVE_COLORS[SQUARE])
    put(_display, SMALL, TUNE_NAME + ", square waves", WORDS_Y, DIM, 34)
    print("Tune:", TUNE_NAME)
    for name, freq, ms in TUNE:
        if freq:
            big(FREQ_Y, "%s %d Hz" % (name, freq), WHITE)
            speaker.play(freq, ms - NOTE_GAP_MS, SQUARE)
            speaker.rest(NOTE_GAP_MS)
        else:
            speaker.rest(ms)
        yield

    speaker.rest(200)
    yield
    centered(_display, SMALL, "UP: all again   DOWN: tune", PROMPT_Y,
             config.YELLOW)


def update(now):
    global show
    if speaker is None:
        return
    if show is None:
        if _kit.up.pressed(now):
            show = program(True)
        elif _kit.down.pressed(now):
            show = program(False)
        return
    # Feed the next sound only when the one before has nearly finished, so
    # the picture changes when the sound does.
    if time.ticks_diff(speaker._ends_at, now) > AHEAD_MS:
        return
    try:
        next(show)
    except StopIteration:
        show = None


def stop():
    if speaker is not None:
        speaker.deinit()
    return None
