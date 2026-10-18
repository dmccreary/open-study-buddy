# Chapter 2, Test 04: Polling versus an interrupt
# Counts presses of the MODE button three ways at the same time:
#   raw edges   every falling edge the interrupt sees, bounce included
#   interrupt   falling edges with a 30 ms debounce, counted in the ISR
#   polling     presses a slow loop notices (checks the pin every POLL_MS)
# Needs the MODE button (GP13).
#
# PASS: press the button quickly 20 times. Expect: raw edges >= interrupt, and
# interrupt >= polling when POLL_MS is large. If raw edges is much bigger than
# the number of presses you made, that is contact bounce. Change POLL_MS and
# run again: a bigger number misses more quick presses.
#
# Ctrl-C prints the totals.

NAME = "04-button-interrupt.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

POLL_MS = 100          # try 5, 20, 100, 250
DEBOUNCE_MS = 30

button = Pin(13, Pin.IN, Pin.PULL_UP)

raw_edges = 0
irq_presses = 0
last_irq = 0


def on_fall(pin):
    """Keep this short: count and get out."""
    global raw_edges, irq_presses, last_irq
    raw_edges += 1
    now = time.ticks_ms()
    if time.ticks_diff(now, last_irq) > DEBOUNCE_MS:
        last_irq = now
        irq_presses += 1


button.irq(trigger=Pin.IRQ_FALLING, handler=on_fall)

poll_presses = 0
was_down = False
print("Polling every {} ms. Press the MODE button quickly, 20 times. Ctrl-C to stop.".format(POLL_MS))

try:
    last_report = time.ticks_ms()
    while True:
        is_down = button.value() == 0
        if is_down and not was_down:
            poll_presses += 1
        was_down = is_down
        time.sleep_ms(POLL_MS)
        if time.ticks_diff(time.ticks_ms(), last_report) >= 2000:
            last_report = time.ticks_ms()
            print("raw edges {:3d}   interrupt {:3d}   polling {:3d}".format(
                raw_edges, irq_presses, poll_presses))
except KeyboardInterrupt:
    print()
    print("TOTALS: raw edges {}, interrupt {}, polling {} (POLL_MS={})".format(
        raw_edges, irq_presses, poll_presses, POLL_MS))
finally:
    button.irq(handler=None)
