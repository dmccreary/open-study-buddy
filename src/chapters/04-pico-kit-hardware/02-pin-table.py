# Chapter 4, Test 02: Print and check the pin assignment table
# Prints the kit's pin assignment table from config.py, with the physical pin
# number of each Pico pin, and checks the three rules from the chapter:
#   1. no GP pin is used twice
#   2. the I2S word-select pin is the pin right after the clock pin
#   3. nothing uses GP23, GP24, GP25, or GP29 (the wireless chip's pins)
# Needs only config.py (it does not touch the hardware). Also runs on a
# computer if config.py is imported with a stub machine module; on the Pico
# just run it.
#
# PASS: the table prints and the last line says PASS.

NAME = "02-pin-table.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import config

# GP number -> physical pin on the 40-pin Pico header
PHYSICAL = {0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
            10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
            18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34}

ROWS = (
    ("Display", "SCL (SPI clock)", config.SCK_PIN),
    ("Display", "SDA (SPI data)", config.MOSI_PIN),
    ("Display", "RST", config.RST_PIN),
    ("Display", "DC", config.DC_PIN),
    ("Display", "CS", config.CS_PIN),
    ("Display", "BL (backlight)", config.BL_PIN),
    ("Button", "MODE", config.BUTTON_MODE_PIN),
    ("Button", "UP", config.BUTTON_INCREMENT_PIN),
    ("Button", "DOWN", config.BUTTON_DECREMENT_PIN),
    ("Microphone", "SCK", config.MIC_SCK_PIN),
    ("Microphone", "WS", config.MIC_WS_PIN),
    ("Microphone", "SD", config.MIC_SD_PIN),
    ("Amplifier", "BCLK", config.I2S_BCLK_PIN),
    ("Amplifier", "LRC", config.I2S_LRC_PIN),
    ("Amplifier", "DIN", config.I2S_DIN_PIN),
    ("Amplifier", "GAIN", config.I2S_GAIN_PIN),
)

print()
print("{:<11} {:<16} {:>5} {:>9}".format("part", "wire", "GP", "physical"))
used = {}
problems = []
for part, wire, gp in ROWS:
    print("{:<11} {:<16} {:>5} {:>9}".format(part, wire, "GP" + str(gp), PHYSICAL.get(gp, "?")))
    if gp in used:
        problems.append("GP{} is used by both {} and {}".format(gp, used[gp], part + " " + wire))
    used[gp] = part + " " + wire
    if gp in (23, 24, 25, 29):
        problems.append("GP{} belongs to the wireless chip".format(gp))

if config.MIC_WS_PIN != config.MIC_SCK_PIN + 1:
    problems.append("microphone WS must be SCK + 1")
if config.I2S_LRC_PIN != config.I2S_BCLK_PIN + 1:
    problems.append("amplifier LRC must be BCLK + 1")

print()
print("3V3 -> display VCC, microphone VDD, (amplifier VIN or VBUS)")
print("GND -> display GND, microphone GND and L/R, buttons, amplifier GND")
print()
if problems:
    for p in problems:
        print("PROBLEM:", p)
else:
    print("PASS: no pin is used twice, both I2S pairs are neighbors, no wireless pins used.")
