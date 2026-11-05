# demo_spanish.py -- demo 10 of 20-demo-template.py: a Spanish listening quiz.
#
# The speaker says one Spanish word. Four English words are on the screen;
# pick the one it means.
#
#   UP / DOWN      move the highlight (the last row plays the word again)
#   MODE (short)   choose
#   after an answer, any button (or a few seconds) brings the next word
#
# WHERE THE VOICE COMES FROM. A Pico cannot turn text into speech, so each
# word is a short recording: spanish/<word>.wav, 16-bit mono at 16000 Hz,
# about 20 KB a word. tools/make-spanish-audio.sh makes them on a Mac with
# its built-in Spanish voice, and upload-code.sh copies the spanish/
# folder to the Pico. demo_kit.Speaker.play_wav() streams a file from
# flash a block at a time, so a word needs only 2 KB of RAM to play.
#
# If a word's file is missing, the quiz shows the Spanish word instead,
# and it becomes a reading quiz for that word.
#
# The fonts only have plain ASCII letters, so the words here have no
# accents (no arbol or lapiz).

import os
import random
import time

import config
from demo_kit import (BLACK, WHITE, DIM, FAINT, SMALL, BIG, CX, put,
                      centered, menu_hint, make_speaker)

WORDS = (
    ("hola", "hello"), ("gracias", "thank you"), ("perro", "dog"),
    ("gato", "cat"), ("casa", "house"), ("libro", "book"),
    ("agua", "water"), ("manzana", "apple"), ("escuela", "school"),
    ("amigo", "friend"), ("rojo", "red"), ("verde", "green"),
    ("sol", "sun"), ("leche", "milk"), ("mesa", "table"),
    ("ventana", "window"),
)
FOLDER = "spanish"
NEXT_AFTER_MS = 4000

HIGHLIGHT = config.color565(30, 60, 140)
RIGHT = config.color565(0, 150, 60)
WRONG = config.color565(190, 30, 30)

TITLE_Y = 34
PROMPT_Y = 58
WORD_Y = 82
CHOICE_Y = 122
CHOICE_PITCH = 36
CHOICE_CHARS = 12
REPLAY_Y = CHOICE_Y + 4 * CHOICE_PITCH + 4
MENU_Y = 302
REPLAY = 4                     # the fifth row


def start(display, kit, saved):
    global _display, _kit, speaker, score, asked, last
    _display = display
    _kit = kit
    speaker = make_speaker()
    random.seed(time.ticks_us())
    score = 0 if saved is None else saved["score"]
    asked = 0 if saved is None else saved["asked"]
    last = None
    new_question()


def new_question():
    global word, answer, choices, selected, answered, answered_at, has_sound
    global last
    display = _display
    display.fill(BLACK)
    show_score()
    put(display, SMALL, "UP/DOWN pick  MODE choose", PROMPT_Y, DIM, 26)
    menu_hint(display, MENU_Y)

    i = last
    while i == last:
        i = random.randrange(len(WORDS))
    last = i
    word, answer = WORDS[i]
    others = [english for spanish, english in WORDS if english != answer]
    choices = [answer]
    while len(choices) < 4:
        pick = random.choice(others)
        if pick not in choices:
            choices.append(pick)
    shuffle(choices)
    selected = 0
    answered = None
    answered_at = 0
    has_sound = speaker is not None and exists(wav_path())
    if not has_sound:
        print("No", wav_path(), "-- showing the word instead.",
              "Run tools/make-spanish-audio.sh, then upload-code.sh.")
    for row in range(5):
        draw_row(row)
    show_word("? ? ?" if has_sound else word, config.YELLOW)
    say()


def wav_path():
    return "%s/%s.wav" % (FOLDER, word)


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def show_word(text, color):
    """The line above the choices: big if it fits, small if not."""
    _display.fill_rect(40, WORD_Y, 280, BIG.HEIGHT, BLACK)
    if len(text) <= 15:
        centered(_display, BIG, text, WORD_Y, color)
    else:
        centered(_display, SMALL, text, WORD_Y + 8, color)


def shuffle(items):
    """MicroPython's random has no shuffle(), so: Fisher-Yates."""
    for i in range(len(items) - 1, 0, -1):
        j = random.randrange(i + 1)
        items[i], items[j] = items[j], items[i]


def show_score():
    put(_display, SMALL, "SPANISH QUIZ  %d / %d" % (score, asked), TITLE_Y,
        DIM, 22)


def say():
    """Play the word, if there is a recording of it."""
    if not has_sound:
        return
    try:
        speaker.play_wav(wav_path())
    except (OSError, ValueError) as error:
        print(wav_path(), error)


def draw_row(row):
    if row == REPLAY:
        color = WHITE if selected == REPLAY else DIM
        background = HIGHLIGHT if selected == REPLAY else BLACK
        put(_display, SMALL, "hear it again" if has_sound else "",
            REPLAY_Y, color, 17, background)
        return
    background = BLACK
    color = WHITE
    if answered is not None:
        if choices[row] == answer:
            background = RIGHT
        elif row == answered:
            background = WRONG
        else:
            color = FAINT
    elif row == selected:
        background = HIGHLIGHT
    put(_display, BIG, choices[row], CHOICE_Y + row * CHOICE_PITCH, color,
        CHOICE_CHARS, background)


def choose():
    global answered, answered_at, score, asked
    if selected == REPLAY:
        say()
        return
    answered = selected
    answered_at = time.ticks_ms()
    asked += 1
    right = choices[selected] == answer
    if right:
        score += 1
    for row in range(4):
        draw_row(row)
    show_score()
    show_word("%s = %s" % (word, answer),
              config.GREEN if right else config.RED)
    put(_display, SMALL, "Right!" if right else "Not quite.", PROMPT_Y,
        config.GREEN if right else config.RED, 26)
    put(_display, SMALL, "any button: next word", REPLAY_Y, DIM, 22)
    if speaker is not None:
        if right:
            for freq in (784, 1047):
                speaker.play(freq, 110)
        else:
            speaker.play(196, 300, "square")
        speaker.rest(150)
        say()


def on_mode():
    global mode_pressed
    mode_pressed = True


mode_pressed = False


def update(now):
    global selected, mode_pressed
    up = _kit.up.pressed(now)
    down = _kit.down.pressed(now)
    pressed = mode_pressed
    mode_pressed = False

    if answered is not None:
        if up or down or pressed or \
                time.ticks_diff(now, answered_at) >= NEXT_AFTER_MS:
            new_question()
        return

    if up or down:
        old = selected
        rows = 5 if has_sound else 4
        selected = (selected + (-1 if up else 1)) % rows
        draw_row(old)
        draw_row(selected)
    elif pressed:
        choose()


def stop():
    if speaker is not None:
        speaker.deinit()
    return {"score": score, "asked": asked}
