# Demo 20: The Study Buddy Demo -- a showcase and eleven live demos
# Copy this file to the Pico as main.py and it runs at power-up:
#
#     mpremote cp 20-demo-template.py :main.py
#
# MODE 0, THE SHOWCASE, is what you see at power-up: twelve screens, one
# for each thing the Study Buddy can do, changing every six seconds. Press
# UP or MODE to skip ahead, DOWN to go back.
#
# HOLD ANY BUTTON FOR ONE SECOND to try the demo the screen is showing.
# Hold MODE for one second inside a demo to come back to the showcase.
#
#    #   Module              Demo
#    1   demo_clock.py       Clock and weather forecast (WiFi)
#    2   demo_alarm.py       Alarm clock, set with the buttons
#    3   demo_timer.py       Countdown timer
#    4   demo_stopwatch.py   Stopwatch with laps
#    5   demo_school.py      School mascot and upcoming events
#    6   demo_tones.py       Sound lab: four kinds of wave, then a tune
#    7   demo_listen.py      Sound meter on the microphone
#    8   demo_record.py      Record 3 seconds, play it back
#    9   demo_quote.py       Quote of the day
#   10   demo_spanish.py     Spanish listening quiz
#   11   demo_vocab.py       Vocabulary flash cards
#
# The shared parts are in demo_kit.py (text that fits a round screen, the
# speaker) and demo_icons.py (the showcase pictures). The clock parts --
# lib/watchparts.py, wifi_time.py, forecast.py -- come from the sw-gc9b72
# kit in the clocks-and-watches repository. upload-code.sh uploads all of
# them, and the Spanish words in spanish/.
#
# Needs: every part of the kit (display, buttons, speaker, microphone).
# WiFi (secrets.py) is only for demo 1; without it the clock still runs.
#
# EACH DEMO IS A MODULE, LOADED ONLY WHILE IT IS ON THE SCREEN. Twelve
# demos at once would not fit in RAM -- the recorder alone needs 150 KB.
# So switching demos:
#
#   1. asks the current one to stop(), and keeps what it hands back
#   2. removes it -- and every module it brought in with it -- from
#      memory, and runs the garbage collector to free the space
#   3. imports the next one fresh, and calls its start()
#
# THE FUNCTIONS EVERY DEMO HAS. That is all this program knows about a
# demo, so adding a twelfth means writing one more module like these:
#
#   start(display, kit, saved)
#       Draw the whole screen. kit is a demo_kit.Kit: kit.mode, kit.up,
#       kit.down are watchparts.Button objects. saved is whatever stop()
#       returned the last time, or None.
#   update(now)
#       Called on every pass of the loop with time.ticks_ms(). Read UP and
#       DOWN, redraw only what changed. Return a demo number to switch to
#       it, or None (the usual answer) to stay.
#   on_mode()                                              (optional)
#       MODE was pressed and let go quickly. (A long press is this
#       program's: it goes back to the showcase.)
#   stop()
#       Turn off anything that is on (the speaker, the microphone), and
#       return a dict to keep until next time, or None. A dict with a
#       "wake_at" time -- a time.ticks_ms() value -- asks for the demo to
#       be shown again at that moment, which is how a running timer or an
#       alarm comes back to ring from the showcase or another demo.
#
# The showcase (demo_showcase.py) is mode 0 and works the same way, but it
# reads all three buttons itself: its update() returns the demo to launch.
#
# IF A DEMO CRASHES, the error is printed in the shell and shown on the
# screen for a few seconds, and then it is back to the showcase -- one bad
# demo does not stop the whole show at a science fair.

NAME = "20-demo-template.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import sys
import time

import config
import demo_kit
import watchparts
from watchparts import Button, SHORT, LONG

# (module, name), in the showcase's order. Index 0 is the showcase.
MODES = (
    ("demo_showcase", "Showcase"),
    ("demo_clock", "Clock and Weather"),
    ("demo_alarm", "Alarm Clock"),
    ("demo_timer", "Countdown Timer"),
    ("demo_stopwatch", "Stopwatch"),
    ("demo_school", "School Calendar"),
    ("demo_tones", "Sound Lab"),
    ("demo_listen", "Sound Meter"),
    ("demo_record", "Record and Play"),
    ("demo_quote", "Quote of the Day"),
    ("demo_spanish", "Spanish Quiz"),
    ("demo_vocab", "Vocabulary"),
)
SHOWCASE = 0
ERROR_SECONDS = 5


def show_error(name, error):
    """Print a demo's crash in the shell and put it on the screen."""
    print()
    print("Demo", name, "stopped with an error:")
    sys.print_exception(error)
    display.fill(config.BLACK)
    demo_kit.centered(display, config.BIG_FONT, "Oops!", 100, config.RED)
    demo_kit.centered(display, config.SMALL_FONT, name, 150, config.WHITE)
    demo_kit.text_block(display, "{}: {}".format(type(error).__name__,
                                                 error),
                        215, demo_kit.DIM, fonts=(config.SMALL_FONT,),
                        max_lines=4)
    time.sleep(ERROR_SECONDS)


def unload():
    """Stop the current demo and remove it, and every module it imported,
    from memory."""
    global mode
    if mode is None:
        return
    name = MODES[mode_index][0]
    try:
        kept = mode.stop()
    except Exception as error:
        print("stop() failed in", name)
        sys.print_exception(error)
        kept = None
    if kept is None:
        saved.pop(name, None)
    else:
        saved[name] = kept
    mode = None
    for module_name in list(sys.modules):
        if module_name not in loaded_before:
            del sys.modules[module_name]
    # watchparts stays loaded (this program uses its Button), and it keeps
    # every TickRing's shapes for reuse -- about 50 KB a ring. Drop them,
    # or the recorder's 150 KB buffer may not find room.
    watchparts._ring_cache.clear()
    gc.collect()


def switch_to(index):
    """Stop the current demo, then load and start demo `index`."""
    global mode, mode_index, loaded_before
    came_from = mode_index
    unload()
    if index == SHOWCASE and came_from != SHOWCASE:
        # Come back to the screen of the demo we just left.
        saved[MODES[SHOWCASE][0]] = {"index": came_from}

    mode_index = index
    name = MODES[index][0]
    loaded_before = set(sys.modules)
    try:
        mode = __import__(name)
        mode.start(display, kit, saved.get(name))
    except Exception as error:
        show_error(MODES[index][1], error)
        if index != SHOWCASE:
            # mode is still the half-started demo (if it imported at all),
            # so switching away calls its stop() -- which frees the speaker
            # or microphone it may have opened -- and unloads it.
            switch_to(SHOWCASE)
            saved.pop(name, None)   # start fresh next time
            return
        raise                       # the showcase itself is broken: stop
    gc.collect()
    print("Demo {}: {} -- {} KB free".format(index, MODES[index][1],
                                             gc.mem_free() // 1024))
    # A demo is often launched by a button that is still held down. Wait
    # for it to be let go, so the new demo does not see it as a press.
    demo_kit.settle(kit.buttons)


def due_to_wake(now):
    """The first demo not on screen that asked to be woken by now."""
    for i in range(len(MODES)):
        kept = saved.get(MODES[i][0])
        if (i != mode_index and kept is not None and "wake_at" in kept
                and time.ticks_diff(now, kept["wake_at"]) >= 0):
            return i
    return None


display = config.init_display()
config.set_backlight(True)
config.set_gain()
kit = demo_kit.Kit(display, *[Button(pin) for pin in config.init_buttons()])

saved = {}               # module name -> what its stop() returned
mode = None
mode_index = SHOWCASE
loaded_before = set()
gc.collect()
switch_to(SHOWCASE)

try:
    while True:
        now = time.ticks_ms()
        target = None
        try:
            if mode_index == SHOWCASE:
                target = mode.update(now)
            else:
                press = kit.mode.short_or_long(now)
                if press == LONG:
                    target = SHOWCASE
                else:
                    if press == SHORT:
                        on_mode = getattr(mode, "on_mode", None)
                        if on_mode is not None:
                            on_mode()
                    target = mode.update(now)
        except Exception as error:
            show_error(MODES[mode_index][1], error)
            if mode_index == SHOWCASE:
                raise
            target = SHOWCASE

        if target is None:
            target = due_to_wake(now)
        if target is not None and target != mode_index:
            switch_to(target)

        time.sleep_ms(5)
finally:
    # Ctrl-C or Stop in Thonny: turn off the speaker and microphone.
    unload()
    print("Stopped.")
