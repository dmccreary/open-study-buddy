# screen.py -- the two text regions the networking chapters use
#
# status(): the status bar region from Chapter 6 (15 characters, top)
# message(): the agent message region (30 characters, bottom)
# Each call pads with spaces so it paints over the old text without a full redraw.

import config

SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
STATUS = (120, 30, 15)        # x, y, characters
MESSAGE = (60, 240, 30)
EXTRA = (60, 270, 30)         # a second line under the message, for hints


class Screen:
    def __init__(self, title=None):
        self.display = config.init_display()
        config.set_backlight(True)
        self.display.fill(config.BLACK)
        if title:
            config.centered_text(self.display, SMALL, title, 90, config.CYAN)

    def _put(self, region, text, color):
        x, y, width = region
        self.display.text(SMALL, text[:width].ljust(width), x, y, color, config.BLACK)

    def status(self, text, color=config.YELLOW):
        print("status :", text)
        self._put(STATUS, text, color)

    def message(self, text, color=config.WHITE):
        print("message:", text)
        self._put(MESSAGE, text, color)

    def hint(self, text, color=DIM):
        self._put(EXTRA, text, color)
