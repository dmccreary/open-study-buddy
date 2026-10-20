# Chapter 15, Test 07: Publish device status
# Connects with mqtt_common.Link (which announces "online" and sets the last
# will), then publishes a small JSON telemetry message every REPORT_S seconds:
# uptime, volume, free memory, and how many times the link has connected.
# Needs only the Pico, Wi-Fi and a broker.
#
# PASS: from your computer, `python3 server/watch.py 'school/crhs/device/+/#'`
# shows "online" (with the R retained flag) once, then a telemetry line every
# REPORT_S seconds. Unplug the Pico: "offline" appears after the broker's
# keepalive timeout (1.5 x 30 = 45 s), published by the broker, not by the Pico.

NAME = "07-status-heartbeat.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import config
import mqtt_common as mc

REPORT_S = 30
RUN_SECONDS = 300

mc.connect_wifi()
link = mc.Link()
start = time.ticks_ms()
last_report = time.ticks_add(start, -REPORT_S * 1000)       # report right away
end = time.ticks_add(start, RUN_SECONDS * 1000)
sent = 0
try:
    while time.ticks_diff(time.ticks_ms(), end) < 0:
        up = link.service()
        now = time.ticks_ms()
        if up and time.ticks_diff(now, last_report) >= REPORT_S * 1000:
            gc.collect()
            if link.publish_telemetry(config.VOLUME, gc.mem_free()):
                sent += 1
                print("telemetry #{} sent to {}".format(sent, mc.TELEMETRY_TOPIC))
            last_report = now
        link.take()
        time.sleep_ms(40)
finally:
    link.close()
print("Done. {} telemetry message(s); the broker was told 'offline' on the way out.".format(sent))

# Try This
#   1. The telemetry has no "last wake" yet (it is null). After Chapter 12, pass
#      the seconds since the last wake word to publish_telemetry().
#   2. Make REPORT_S 5. Watch the free memory number. Does it drift? Why does
#      the script call gc.collect() before reading it?
#   3. Subscribe a second computer with server/watch.py started AFTER the Pico.
#      Which message does it receive immediately, and which does it wait for?
