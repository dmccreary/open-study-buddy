# Chapter 15, Test 03: A listener that survives a dead broker
# Uses mqtt_common.Link, which polls with check_msg(), pings, de-duplicates,
# and reconnects with a growing wait. Every 40 ms it calls link.service(), the
# same rhythm as an audio frame, and prints alerts, link changes, and a count
# line every 10 seconds. Needs only the Pico, Wi-Fi and a broker.
#
# PASS: alerts you publish from your computer print here. Then stop the broker
# for 20 seconds (on the Pi: sudo systemctl stop mosquitto) and start it again:
# the script prints that the link went down, shows the wait before each retry
# growing, and prints that it reconnected. Alerts sent after that arrive again,
# and sending the SAME alert id twice prints it only once ("dupes" goes up).

NAME = "03-link-listener.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import mqtt_common as mc

RUN_SECONDS = 180
PASS_MS = 40                # pretend frame

mc.connect_wifi()
link = mc.Link()
was_up = False
last_report = time.ticks_ms()
end = time.ticks_add(last_report, RUN_SECONDS * 1000)
try:
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        up = link.service()
        if up != was_up:
            if up:
                print("LINK UP   (connects {}, drops {})".format(link.connects, link.drops))
            else:
                print("LINK DOWN: {}".format(link.last_error or "starting"))
            was_up = up
        alert = link.take()
        while alert:
            print("ALERT [{}] {} | {} | {}".format(
                alert["type"], alert["title"], alert["when"], alert["id"]))
            alert = link.take()
        if time.ticks_diff(time.ticks_ms(), last_report) >= 10000:
            last_report = time.ticks_ms()
            print("... up={} connects={} drops={} dupes={} bad={} next retry in {} ms".format(
                link.up, link.connects, link.drops, link.dupes, link.bad,
                0 if link.up else max(0, time.ticks_diff(link.next_try, time.ticks_ms()))))
        time.sleep_ms(PASS_MS)
finally:
    link.close()
print("Done. connects={} drops={} dupes={}".format(link.connects, link.drops, link.dupes))

# Try This
#   1. Publish the same alert twice (same --id). Then publish one with --retain,
#      stop and start the broker, and watch the retained alert come back. Why
#      does it print only once?
#   2. Set the Wi-Fi router off for 30 seconds. What does LINK DOWN say?
#   3. Change PASS_MS to 1000. Alerts still arrive. What did you give up?
