# alert_view.py -- show one alert in the display's "agent message" region
# (Chapter 15). The region is Chapter 6's: x=60, y=240, 240 wide, 32 high, with
# all four corners inside the 168-pixel safe circle. It holds two lines of the
# 8 x 16 font, 30 characters each: the alert's title, then its "when".

import config

X, Y, W, H = 60, 240, 240, 32
CHARS = W // 8                          # 30 characters per line

# type -> (background, text). The words in the title carry the meaning; color
# is a second cue, not the only one.
COLORS = {
    "test": (config.RED, config.WHITE),
    "due": (config.YELLOW, config.BLACK),
    "event": (config.CYAN, config.BLACK),
    "notice": (config.BLUE, config.WHITE),
    "briefing": (config.GREEN, config.BLACK),
}


def fit(text, width=CHARS):
    """Cut text to `width` characters, ending in '...' if it was cut."""
    if len(text) <= width:
        return text
    return text[:width - 3] + "..."


def show_alert(display, alert):
    """Draw the alert. Only this region is written: 15,360 bytes for the
    background, plus the glyph pixels for up to 60 characters."""
    bg, fg = COLORS.get(alert["type"], COLORS["notice"])
    display.fill_rect(X, Y, W, H, bg)
    for row, key in enumerate(("title", "when")):
        line = fit(alert[key])
        x = X + (W - len(line) * 8) // 2
        display.text(config.SMALL_FONT, line, x, Y + row * 16, fg, bg)


def clear_alert(display):
    display.fill_rect(X, Y, W, H, config.BLACK)
