# Chapter 17, Test 03: The indicator can never lie
# Replays the Listener through fake parts and checks one rule after EVERY step:
#
#       the microphone is open  ->  the indicator is on
#
# It also runs two deliberately broken listeners and checks that this test
# FAILS for them. A test that has never been seen to fail proves nothing.
# Finally it searches the other .py files in this folder for code that opens
# the microphone without going through the Listener.
#
# Needs no hardware. Runs on a computer (python3 03-indicator-test.py) or on
# the Pico.
#
# PASS: every scenario prints ok, both broken listeners are CAUGHT, the source
# audit finds no direct microphone opens, and the last line says PASS.

NAME = "03-indicator-test.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import os
import sys

sys.path.append(".")
from listening_indicator import Listener, LedIndicator, OFF, LISTENING, MUTED


class World:
    """Fake parts that write every event into one shared list."""

    def __init__(self):
        self.events = []
        self.mic_open = False
        self.led = 0
        self.violations = []
        self.mute_level = 1                       # 1 = switch off (not muted)

    def check(self, what):
        if self.mic_open and not self.led:
            self.violations.append("after '{}': microphone open, indicator off".format(what))

    # fake LED pin
    def value(self, v=None):
        if v is None:
            return self.led
        self.led = v
        self.events.append("led " + ("on" if v else "off"))
        self.check("led " + ("on" if v else "off"))


class FakeLedPin:
    def __init__(self, world):
        self.w = world
    def value(self, v=None):
        return self.w.value(v)


class FakeMutePin:
    def __init__(self, world):
        self.w = world
    def value(self):
        return self.w.mute_level


class FakeMic:
    def __init__(self, world, fail_close=False):
        self.w = world
        self.fail_close = fail_close
        world.mic_open = True
        world.events.append("mic open")
        world.check("mic open")
    def readinto(self, buf):
        return len(buf)
    def deinit(self):
        if self.fail_close:
            raise OSError("deinit failed")
        self.w.mic_open = False
        self.w.events.append("mic closed")
        self.w.check("mic closed")


def build(world, opener=None, fail_close=False, cls=Listener):
    opener = opener or (lambda: FakeMic(world, fail_close))
    return cls(opener, [LedIndicator(FakeLedPin(world))], FakeMutePin(world))


class BrokenOpenFirst(Listener):
    """BUG 1: opens the microphone, then lights the indicator."""
    def start(self):
        self._mic = self._open_mic()
        self._set(LISTENING)
        return True


class BrokenIndicatorFirstOff(Listener):
    """BUG 2: turns the indicator off, then closes the microphone."""
    def stop(self):
        self._set(OFF)
        if self._mic is not None:
            self._mic.deinit()
            self._mic = None


results = []


def scenario(name, fn):
    w = World()
    try:
        fn(w)
    except Exception as error:
        w.violations.append("check failed: {} {}".format(type(error).__name__, error))
    good = not w.violations
    results.append(good)
    print("  {:<4} {}".format("ok" if good else "FAIL", name))
    for v in w.violations:
        print("         ", v)
    return w


def s_normal(w):
    l = build(w); l.start(); l.readinto(bytearray(8)); l.stop()
    assert w.events == ["led off", "led on", "mic open", "mic closed", "led off"], w.events

def s_restart(w):
    l = build(w); l.start(); l.start(); l.stop(); l.stop()
    assert w.events.count("mic open") == 1

def s_open_fails(w):
    def bad(): raise OSError("I2S failed")
    l = build(w, opener=bad)
    try:
        l.start()
    except OSError:
        pass
    assert w.led == 0 and not w.mic_open and l.state == OFF

def s_close_fails(w):
    l = build(w, fail_close=True); l.start()
    try:
        l.stop()
    except OSError:
        pass
    assert w.mic_open and w.led == 1, "must stay lit when close fails"

def s_muted_before_start(w):
    w.mute_level = 0
    l = build(w); ok = l.start()
    assert not ok and not w.mic_open and l.state == MUTED

def s_mute_mid_stream(w):
    l = build(w); l.start(); l.readinto(bytearray(8))
    w.mute_level = 0
    n = l.readinto(bytearray(8))
    assert n == 0 and not w.mic_open and l.state == MUTED

print()
print("Scenarios (rule checked after every event):")
scenario("normal start, read, stop", s_normal)
scenario("start twice opens once", s_restart)
scenario("open fails -> indicator back off", s_open_fails)
scenario("close fails -> indicator stays on", s_close_fails)
scenario("muted before start -> never opens", s_muted_before_start)
scenario("mute switch flipped mid-stream -> closes", s_mute_mid_stream)

print()
print("Broken listeners (this test must catch both):")
caught = 0
for label, cls in (("opens mic before lighting indicator", BrokenOpenFirst),
                   ("turns indicator off before closing mic", BrokenIndicatorFirstOff)):
    w = World()
    l = build(w, cls=cls)
    l.start(); l.stop()
    if w.violations:
        caught += 1
        print("  CAUGHT  {}".format(label))
    else:
        print("  MISSED  {}   <-- the test is too weak".format(label))

print()
print("Source audit (no direct microphone opens outside the Listener):")
direct = []
for fname in sorted(os.listdir(".")):
    if not fname.endswith(".py") or fname in ("listening_indicator.py", NAME):
        continue
    with open(fname) as f:
        for number, line in enumerate(f, 1):
            code = line.split("#")[0]
            if "init_microphone(" in code or "I2S(" in code:
                direct.append("{}:{}".format(fname, number))
if direct:
    for place in direct:
        print("  DIRECT OPEN at", place)
else:
    print("  none found")

print()
passed = all(results) and caught == 2 and not direct
print("PASS" if passed else "FAIL")
