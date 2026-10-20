# Chapter 16, Test 03: Page a daily briefing across the message region
# The school server pushes a briefing alert (type "briefing", up to 300
# characters of text) at 7:30 each morning. The message region holds only two
# lines of 30 characters, so this script wraps the text into pages and shows
# each page for PAGE_MS, WITHOUT sleeping: it keeps calling link.service()
# every 40 ms like the audio loop. With no broker set up (mqtt_host missing in
# secrets.py) it shows the sample briefing below instead. Needs the display;
# for the real thing also Wi-Fi, a broker, and server/push_daily.py --send.
#
# PASS: the briefing's title and "when" show first, then the sentences appear
# two lines at a time (a last page of one line shows "n/total" on line 2), and
# the screen goes quiet after the last page. Run server/push_daily.py --send twice: the second briefing has
# the same id, so the device ignores it (dupes goes up, nothing redraws).

NAME = "03-briefing-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import alert_view
import config
import edition
import mqtt_common as mc

PAGE_MS = 3500
RUN_SECONDS = 120
LINE = alert_view.CHARS             # 30 characters per line

# From server/push_daily.py --now 2026-10-19T07:30, Cedar Ridge's demo morning.
SAMPLE = {
    "id": "20261019-briefing", "type": "briefing", "title": "Good morning, Cedar Ridge",
    "when": "Test tomorrow",
    "text": ("Good morning from Cedar Ridge. Picture Retake Day is today. Location: Library. "
             "Your next Algebra II test is tomorrow at 8 AM. English 10 personal narrative draft "
             "is due on Wednesday. Biology osmosis lab report is due on Thursday. Griffins aim high!"),
}


def wrap(text, width=LINE):
    """Break text into lines of at most `width` characters, at spaces."""
    lines = []
    line = ""
    for word in text.split():
        if len(word) > width:                       # a word longer than a line: cut it
            word = word[:width - 3] + "..."
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = word if not line else line + " " + word
    if line:
        lines.append(line)
    return lines


def pages_of(text, lines_per_page=2):
    lines = wrap(text)
    return [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)]


# self-check of the wrapper, so a typo shows up before the display does
assert wrap("a b c", 3) == ["a b", "c"]
assert wrap("") == []
assert all(len(l) <= LINE for p in pages_of(SAMPLE["text"]) for l in p)

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)

use_broker = mc.HOST is not None
link = None
if use_broker:
    mc.connect_wifi()
    link = mc.Link()
else:
    print("No mqtt_host in secrets.py: showing the sample briefing.")

pages = []
page = 0
next_page_at = 0
current = None
start = time.ticks_ms()
end = time.ticks_add(start, RUN_SECONDS * 1000)
pending_sample = not use_broker
try:
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        now = time.ticks_ms()
        alert = None
        if link is not None:
            link.service()
            alert = link.take()
        elif pending_sample:
            alert, pending_sample = SAMPLE, False
        if alert is not None and alert["type"] == "briefing":
            current = alert
            pages = pages_of(alert["text"])
            page = -1                               # -1 shows the title first
            next_page_at = now
            print("briefing {}: {} page(s)".format(alert["id"], len(pages)))
        if current is not None and time.ticks_diff(now, next_page_at) >= 0:
            if page == -1:
                alert_view.show_alert(display, {"type": "briefing", "title": current["title"],
                                                "when": current["when"]})
            elif page < len(pages):
                lines = pages[page]
                alert_view.show_alert(display, {
                    "type": "briefing",
                    "title": lines[0],
                    "when": lines[1] if len(lines) > 1 else "{}/{}".format(page + 1, len(pages))})
            else:
                alert_view.clear_alert(display)
                current = None
                print("briefing finished")
            page += 1
            next_page_at = time.ticks_add(now, PAGE_MS)
        time.sleep_ms(40)
finally:
    if link is not None:
        link.close()
print("Done.")

# Try This
#   1. The page lasts 3,500 ms for 60 characters, about 17 characters a second.
#      Is that comfortable to read? Change PAGE_MS and ask a classmate.
#   2. Chapter 14's text-to-speech can speak the same text. Which is slower, the
#      pages or the speech? What should the device do if the student presses MODE?
