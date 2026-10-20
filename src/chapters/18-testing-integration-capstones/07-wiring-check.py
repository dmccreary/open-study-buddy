# Chapter 18, Probe 07: Wiring verification
# Prints the wire list for every part, computed from config.py (so it cannot
# disagree with the code), runs the pin-plan rules, and then walks you through
# touching each button. Use it with the kit in front of you: put a finger on
# each wire on the list and say its Pico pin out loud.
# Needs only config.py on the Pico; the parts can be wired or not.
#
# PASS: the pin plan says PASS, and the wire list matches what you see.

NAME = "07-wiring-check.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import checks
import config

print("{:<12} {:<12} {:<12} {}".format("part", "part pin", "Pico pin", "header pin"))
for part, pin, pico, physical in checks.wiring_table(config):
    print("{:<12} {:<12} {:<12} {}".format(part, pin, pico, physical))
print()
verdict, detail = checks.check_pin_plan(config)
print("Pin plan:", verdict, "-", detail)
