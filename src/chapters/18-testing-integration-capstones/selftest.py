# selftest.py -- Chapter 18: one program that checks the whole kit
#
#   Run it:      mpremote run selftest.py        (or Run in Thonny)
#   Call it:     import selftest; selftest.run()   (for example at power-up)
#   Options:     selftest.run(ask=False)    no human questions: display and
#                                           speaker stay ASK
#                selftest.run(press=True)   also ask you to press each button
#                selftest.run(wifi=False)   skip the Wi-Fi check
#
# It prints PASS, FAIL, ASK, or SKIP for each subsystem with the reason, draws
# a summary on the round display, and returns the list of results. Each check
# lives in checks.py, where the probes (02 to 06) use the same functions.
#
# What PASS means here: the program MEASURED the right thing. The display and
# the amplifier cannot report back to the Pico, so they are ASK until a human
# answers (UP = yes, DOWN = no), except that the speaker is PASS when the
# microphone hears its tone.
#
# PASS: the summary line says no FAIL. A part you have not wired yet shows FAIL
# or SKIP, which is the useful answer, not a crash.

import time

import checks
from checks import PASS, FAIL, ASK, SKIP
from log import Log, INFO

NAME = "selftest.py"
VERSION = "1.0"


def run(ask=True, press=False, wifi=True):
    print("{} v{}".format(NAME, VERSION))
    log = Log(level=INFO, ring=30, echo=False)
    results = []                                   # (name, verdict, detail, ms)

    def record(name, verdict, detail, started):
        ms = time.ticks_diff(time.ticks_ms(), started)
        results.append((name, verdict, detail, ms))
        print("{:<11} {:<4} {}   ({} ms)".format(name, verdict, detail, ms))
        (log.error if verdict == FAIL else log.info)("%s %s", name, verdict)

    def step(name, fn):
        started = time.ticks_ms()
        try:
            out = fn()
        except Exception as error:                 # a check must never end the run
            out = (FAIL, "check crashed: {}".format(error))
        record(name, out[0], out[1], started)
        return out

    step("Files", checks.check_files)
    if results[-1][1] == FAIL:
        print("Cannot go on without the kit files. Run upload-chapter.sh.")
        return results
    import config
    step("Memory", checks.check_memory)
    step("Flash", checks.check_flash)
    step("Pin plan", lambda: checks.check_pin_plan(config))
    step("Buttons", lambda: checks.check_buttons(config, press=press))

    display = None
    started = time.ticks_ms()
    try:
        display = config.init_display()
        config.set_backlight(True)
        display.fill(config.BLACK)
        import shapes
        shapes.ring(display, config.CENTER_X, config.CENTER_Y, config.SAFE_RADIUS,
                    config.GREEN, 2)
        config.centered_text(display, config.BIG_FONT, "SELF-TEST".center(14), 150,
                             config.YELLOW)
        verdict, detail = ASK, "pattern drawn: a green ring and the word SELF-TEST"
        if ask:
            answer = checks.ask_yes_no(config, display, "Do you see the ring and text?")
            if answer is True:
                verdict, detail = PASS, "a person saw the ring and the text"
            elif answer is False:
                verdict, detail = FAIL, "a person saw no ring or no text"
    except Exception as error:
        verdict, detail = FAIL, "display failed to start: {}".format(error)
    record("Display", verdict, detail, started)

    step("Microphone", lambda: checks.check_mic(config)[:2])

    def speaker():
        verdict, detail, _ = checks.check_speaker(config, with_mic=results[-1][1] == PASS)
        if verdict == ASK and ask:
            answer = checks.ask_yes_no(config, display, "Did you hear a steady beep?")
            if answer is True:
                return PASS, "a person heard the beep"
            if answer is False:
                return FAIL, "a person heard nothing"
        return verdict, detail
    step("Speaker", speaker)

    if wifi:
        step("Wi-Fi", lambda: checks.check_wifi(config))
    else:
        record("Wi-Fi", SKIP, "skipped by the caller", time.ticks_ms())

    counts = {PASS: 0, FAIL: 0, ASK: 0, SKIP: 0}
    for _, verdict, _, _ in results:
        counts[verdict] += 1
    summary = "{} PASS  {} FAIL  {} ASK  {} SKIP".format(
        counts[PASS], counts[FAIL], counts[ASK], counts[SKIP])
    print()
    print(summary)
    if display is not None:
        show_summary(config, display, results, summary)
    return results


def show_summary(config, display, results, summary):
    """Draw one row per check. The word (PASS, FAIL, ASK, SKIP) carries the
    result; color is a second cue."""
    display.fill(config.BLACK)
    config.centered_text(display, config.SMALL_FONT, "SELF-TEST".center(20), 40, config.YELLOW)
    colors = {PASS: config.GREEN, FAIL: config.RED, ASK: config.YELLOW, SKIP: config.GRAY}
    y = 62
    for name, verdict, _, _ in results:
        config.centered_text(display, config.SMALL_FONT, "{:<11}{:>5}".format(name, verdict),
                             y, colors[verdict])
        y += 20
    config.centered_text(display, config.SMALL_FONT, summary.center(30), y + 12, config.WHITE)


if __name__ == "__main__":
    run()
