# Chapter 15, Test 05: Show alerts in the message region
# Draws six sample alerts (from the Cedar Ridge calendar) one after another in
# the display's agent-message region, 3 seconds each, and prints how long each
# draw took. No Wi-Fi and no broker: this tests the layout only. Needs the
# display.
#
# PASS: each alert shows its title on line 1 and its "when" on line 2, inside
# the round screen, nothing cut off by the bezel; the long title ends in "...";
# the rest of the screen stays black. The draw times print (write them down).

NAME = "05-alert-display.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import alert_view
import alerts
import config

SAMPLES = (
    {"id": "s1", "type": "test", "title": "Algebra II test", "when": "Tomorrow 8:00 AM",
     "text": "Algebra II test tomorrow at 8 AM."},
    {"id": "s2", "type": "due", "title": "Biology osmosis lab report", "when": "Due Thursday",
     "text": "Your biology lab report is due Thursday."},
    {"id": "s3", "type": "event", "title": "Football vs. Eastbrook Eagles", "when": "Fri 7:00 PM, Griffin Field",
     "text": "Football game Friday at 7 PM."},
    {"id": "s4", "type": "notice", "title": "No school Friday", "when": "Friday Oct 23",
     "text": "No school on Friday."},
    {"id": "s5", "type": "briefing", "title": "Good morning from Cedar Ridge", "when": "2 things today",
     "text": "Good morning."},
    {"id": "s6", "type": "test", "title": "World History Unit 1 - Ancient River Valleys",
     "when": "Thursday Oct 8 at 11:03 AM", "text": "World History test."},
)

# The last sample is too long on purpose, to show what fit() does when a title
# slips past the server's 30-character limit. The others must be valid.
for sample in SAMPLES[:-1]:
    found = alerts.problems(sample)
    if found:
        raise SystemExit("sample {} is invalid: {}".format(sample["id"], found))

display = config.init_display()
config.set_backlight(True)
display.fill(config.BLACK)
print("Region {},{} {}x{} = {} bytes".format(
    alert_view.X, alert_view.Y, alert_view.W, alert_view.H, alert_view.W * alert_view.H * 2))

for sample in SAMPLES:
    start = time.ticks_us()
    alert_view.show_alert(display, sample)
    elapsed = time.ticks_diff(time.ticks_us(), start)
    print("{:<9} {:>7.1f} ms  {!r}".format(sample["type"], elapsed / 1000, sample["title"]))
    time.sleep_ms(3000)

alert_view.clear_alert(display)
print("PASS if every alert was readable and inside the round screen.")

# Try This
#   1. Change COLORS in alert_view.py so test is YELLOW with black text. Which
#      alert types are now easy to confuse at a glance?
#   2. Show a title of exactly 30 characters. Then 31. What does fit() do?
#   3. Which alert took longest to draw? Is it the one with the most text?
