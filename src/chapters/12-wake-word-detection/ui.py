# ui.py -- small display helpers for Chapter 11: text and a level bar
#
# Both follow the Chapter 6 rule: draw only what changed. put() pads text to a
# fixed width so the new text covers the old. LevelBar remembers how wide its
# bar is now and draws only the columns that changed, so a typical frame costs
# a few hundred bytes of SPI traffic instead of the 8,800 bytes of a full bar.

import config


def put(display, text, y, font, color, width):
    """Draw text centered, padded to a fixed width so it covers what was there."""
    config.centered_text(display, font, text.center(width), y, color)


class LevelBar:
    def __init__(self, display, x, y, width, height, low_bits, high_bits,
                 track=None):
        self.display = display
        self.x, self.y, self.width, self.height = x, y, width, height
        self.low, self.high = low_bits, high_bits
        self.track = track if track is not None else config.color565(40, 40, 40)
        self.filled = 0                  # columns currently drawn as the bar
        self.color = None
        self.bytes_drawn = 0             # running total, for the chapter's arithmetic

    def column(self, bits):
        """How many columns a loudness of bits fills."""
        fraction = (bits - self.low) / (self.high - self.low)
        return int(self.width * max(0.0, min(1.0, fraction)))

    def frame(self):
        """Draw the outline and the empty track (once)."""
        d = self.display
        d.rect(self.x - 2, self.y - 2, self.width + 4, self.height + 4, config.WHITE)
        d.fill_rect(self.x, self.y, self.width, self.height, self.track)
        self.filled = 0
        self.color = None

    def tick(self, bits, color):
        """A small mark just above the bar, e.g. the gate's open level."""
        x = self.x + self.column(bits)
        self.display.fill_rect(x, self.y - 9, 2, 6, color)

    def set(self, bits, color):
        """Show a loudness. Draws only the part that changed."""
        d = self.display
        new = self.column(bits)
        if color != self.color:                      # color change: repaint both parts
            if new:
                d.fill_rect(self.x, self.y, new, self.height, color)
            if new < self.width:
                d.fill_rect(self.x + new, self.y, self.width - new, self.height, self.track)
            self.bytes_drawn += self.width * self.height * 2
            self.color = color
        elif new > self.filled:
            d.fill_rect(self.x + self.filled, self.y, new - self.filled, self.height, color)
            self.bytes_drawn += (new - self.filled) * self.height * 2
        elif new < self.filled:
            d.fill_rect(self.x + new, self.y, self.filled - new, self.height, self.track)
            self.bytes_drawn += (self.filled - new) * self.height * 2
        self.filled = new
