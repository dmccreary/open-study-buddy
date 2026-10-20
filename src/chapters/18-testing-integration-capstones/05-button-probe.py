# Chapter 18, Probe 05: Buttons
# First checks that all three buttons read "not pressed" when nobody touches
# them, then asks you to press MODE, UP, and DOWN in turn and reports how many
# edges (bounces) each press made in the first 50 ms. Needs only the buttons.
#
# PASS: the verdict says PASS and each button reports a small number of edges.
# A button that never reports has a loose wire or is on the wrong pin; one that
# reads pressed at the start is held, shorted, or wired to the wrong leg.

NAME = "05-button-probe.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import checks
import config

idle = checks.check_buttons(config, press=False)
print("Idle check :", idle[0], "-", idle[1])
if idle[0] == checks.PASS:
    full = checks.check_buttons(config, press=True)
    print("Press check:", full[0], "-", full[1])
