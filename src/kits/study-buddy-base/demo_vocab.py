# demo_vocab.py -- demo 11 of 20-demo-template.py: a vocabulary builder.
#
# Flash cards. A word comes up first on its own, so you can think about
# what it means; press MODE to turn the card over and see its meaning and
# the word used in a sentence.
#
#   MODE (short)   turn the card over (and back)
#   UP / DOWN      next / previous word
#
# The definitions are wrapped to fit the round glass by
# demo_kit.text_block(), in the big font when they are short enough.

import config
from demo_kit import (BLACK, WHITE, DIM, SMALL, BIG, CX, centered,
                      text_block, menu_hint)

# (word, part of speech, meaning, example). Words a middle or high
# school student meets in science, coding, and writing.
CARDS = (
    ("algorithm", "noun", "a step-by-step plan for solving a problem",
     "A recipe is an algorithm for making soup."),
    ("hypothesis", "noun", "a guess you can test with an experiment",
     "Her hypothesis was that plants grow toward light."),
    ("iterate", "verb", "to repeat a process, making it better each time",
     "We iterated on the robot until it could climb the ramp."),
    ("persevere", "verb", "to keep trying even when something is hard",
     "He persevered and finally fixed the bug."),
    ("curious", "adjective", "eager to learn or know about something",
     "The curious student asked how the speaker works."),
    ("evidence", "noun", "facts that show whether something is true",
     "The data from the sensor was our evidence."),
    ("collaborate", "verb", "to work together with others on a goal",
     "Our team collaborated on the science fair project."),
    ("debug", "verb", "to find and fix the mistakes in a program",
     "I had to debug my code before the demo."),
    ("precise", "adjective", "exact and careful, with no mistakes",
     "Use a precise measurement, like 12.5 cm."),
    ("infer", "verb", "to figure something out from clues",
     "From the wet streets we inferred that it had rained."),
    ("abstract", "adjective", "about ideas, not things you can touch",
     "Justice is an abstract idea."),
    ("resilient", "adjective", "able to bounce back after a problem",
     "A resilient coder learns from every error message."),
    ("variable", "noun", "a named place in a program that holds a value",
     "The variable score goes up by one for each right answer."),
    ("analyze", "verb", "to look at something closely to understand it",
     "We analyzed the sound with an FFT."),
    ("summarize", "verb", "to tell the main ideas in a few words",
     "Summarize the chapter in three sentences."),
)

TITLE_Y = 38
WORD_Y = 66
PART_Y = 104
MEANING_CENTER_Y = 168
EXAMPLE_CENTER_Y = 246
HINT_Y = 276
MENU_Y = 298

FAINT_QUESTION = config.color565(80, 80, 110)
HINT_COLOR = config.color565(110, 110, 110)


def start(display, kit, saved):
    global _display, _kit, index, flipped
    _display = display
    _kit = kit
    index = 0 if saved is None else saved["index"]
    flipped = False
    show()


def show():
    word, part, meaning, example = CARDS[index]
    display = _display
    display.fill(BLACK)
    centered(display, SMALL, "VOCABULARY  %d / %d" % (index + 1, len(CARDS)),
             TITLE_Y, DIM)
    centered(display, BIG, word, WORD_Y, config.YELLOW)
    centered(display, SMALL, "(" + part + ")", PART_Y, config.CYAN)
    if flipped:
        text_block(display, meaning, MEANING_CENTER_Y, WHITE,
                   fonts=((BIG, 2), (SMALL, 4)))
        text_block(display, '"' + example + '"', EXAMPLE_CENTER_Y, DIM,
                   fonts=(SMALL,), max_lines=2)
        hint = "MODE: hide  UP: next"
    else:
        centered(display, BIG, "?", MEANING_CENTER_Y - 16, FAINT_QUESTION)
        centered(display, SMALL, "What do you think it means?",
                 EXAMPLE_CENTER_Y - 8, DIM)
        hint = "MODE: meaning  UP: next"
    centered(display, SMALL, hint, HINT_Y, HINT_COLOR)
    menu_hint(display, MENU_Y)


def on_mode():
    global flipped
    flipped = not flipped
    show()


def update(now):
    global index, flipped
    step = 1 if _kit.up.pressed(now) else -1 if _kit.down.pressed(now) else 0
    if step:
        index = (index + step) % len(CARDS)
        flipped = False
        show()


def stop():
    return {"index": index}
