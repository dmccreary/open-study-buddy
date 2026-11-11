# Runs ONE demo module from the study-buddy-base kit, on its own, so the
# gallery renderer can take its picture. It is what main.py does for a
# single demo, minus the showcase and the hold-to-skip logic.
#
# The renderer (scripts/render-gallery-images.py) executes this file inside
# the GC9B72 display simulator and names the demo in GALLERY_DEMO. It is
# not a kit program and is never uploaded to a Pico.

import os
import time

import config
import demo_kit
from watchparts import Button, SHORT

display = config.init_display()
config.set_backlight(True)
config.set_gain()
kit = demo_kit.Kit(display, *[Button(pin) for pin in config.init_buttons()])

demo = __import__(os.environ["GALLERY_DEMO"])
demo.start(display, kit, None)

while True:
    now = time.ticks_ms()
    if kit.mode.short_or_long(now) == SHORT:
        on_mode = getattr(demo, "on_mode", None)
        if on_mode is not None:
            on_mode()
    demo.update(now)
    time.sleep_ms(5)
