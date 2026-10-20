# Chapter 18, Test 08: The frame budget, scheduled
# Runs the cooperative scheduler for 10 seconds (250 frames) with FAKE tasks that
# just wait for a chosen number of milliseconds, so you can watch the budget
# work without any parts. A fake "microphone" paces the loop to one frame every
# 40 ms, as readinto() does. The overrun counter measures every pass.
# Needs only the Pico. Also runs on a computer with a fake time module; on a
# computer the waits do not take real time and the numbers are only a model.
#
# Change SCENARIO at the top:
#   "normal"   every task costs what Chapters 5, 6, and 8 measured (or an
#              ASSUMED value, marked below)
#   "stall"    the same, plus ONE full-screen redraw (129 ms) every 2 seconds
#   "bug"      a full-screen redraw on EVERY frame: the mistake to avoid
#   "sliced"   the same redraw as "stall", cut into 8 strips of one per pass
#
# The costs (ms) are INPUTS to this model, not measurements of this program:
#   audio 10.0     Chapter 8: plain-Python loudness took about 10 ms of a frame
#   spectrum 8.5   Chapter 6: the spectrum region took 8.5 ms (measured)
#   status 3.0     Chapter 6: the status bar region took 3.0 ms (measured)
#   time 3.8       Chapter 6: the time region took 3.8 ms (measured)
#   redraw 129.4   Chapter 5: a full-screen fill took 129.4 ms (measured)
#   buttons 0.5, network 2.0   ASSUMED. Replace them with your own timings.
#
# PASS: the table at the end shows the numbers the chapter prints for your
# SCENARIO, and the last line says PASS (frame overruns only where expected).

NAME = "08-scheduler-demo.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

from overrun import OverrunCounter
from scheduler import Scheduler

SCENARIO = "stall"                      # normal | stall | bug | sliced
FRAME_US = 40000
RUN_FRAMES = 250                        # 10 seconds

COST = {"audio": 10.0, "buttons": 0.5, "spectrum": 8.5, "status": 3.0,
        "time": 3.8, "network": 2.0, "redraw": 129.4}


def work(ms):
    """Pretend to compute for ms milliseconds."""
    time.sleep_us(int(ms * 1000))


class PacedFrames:
    """Stands in for the microphone: readinto() returns once per frame."""

    def __init__(self):
        self.next_us = time.ticks_add(time.ticks_us(), FRAME_US)

    def readinto(self, buf):
        wait = time.ticks_diff(self.next_us, time.ticks_us())
        if wait > 0:
            time.sleep_us(wait)
        self.next_us = time.ticks_add(self.next_us, FRAME_US)
        return len(buf)

    def deinit(self):
        pass


def redraw_job():
    """8 strips of the big redraw, one per pass."""
    for _ in range(8):
        work(COST["redraw"] / 8)
        yield


sched = Scheduler(frame_us=FRAME_US)
sched.add("audio", lambda: work(COST["audio"]), 0, 12)       # period 0 = every pass
sched.add("buttons", lambda: work(COST["buttons"]), 0, 1)
sched.add("spectrum", lambda: work(COST["spectrum"]), 0, 9)
sched.add("status", lambda: work(COST["status"]), 200, 4)
sched.add("network", lambda: work(COST["network"]), 200, 3)
sched.add("time", lambda: work(COST["time"]), 1000, 4)
if SCENARIO == "stall":
    sched.add("redraw", lambda: work(COST["redraw"]), 2000, 140)
elif SCENARIO == "bug":
    sched.add("redraw", lambda: work(COST["redraw"]), 0, 140)
elif SCENARIO == "sliced":
    sched.add_sliced("redraw", redraw_job, 2000, 17)

mic = OverrunCounter(PacedFrames(), frame_us=FRAME_US)
buf = bytearray(2048)
print("scenario:", SCENARIO)
print("{:>4}  {:>7}  {}".format("pass", "used ms", "tasks run (ms)"))
for n in range(RUN_FRAMES):
    mic.readinto(buf)
    used = sched.run_pass()
    if n < 6 or used > FRAME_US:
        if n < 6 or sched.pass_overruns <= 3:
            print("{:>4}  {:>7.1f}  {}".format(
                n, used / 1000,
                " ".join("{} {:.1f}".format(a, b / 1000) for a, b in sched.last)))
print()
sched.print_report()
print()
print("overrun counter:", mic.summary())
