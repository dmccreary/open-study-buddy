#!/usr/bin/env python3
"""Make every image on the Sample Gallery page (docs/gallery/index.md).

Three kinds of picture land in docs/gallery/img/:

1. KIT SCREENS. The labs and demos in src/kits/study-buddy-base, run
   through the GC9B72 display simulator from the clocks-and-watches repo,
   so each picture is what the real code draws. The simulator has no
   microphone, so this script feeds it a steady whistle for the labs that
   listen.
2. CLOCK FACES. Screens copied from the clocks-and-watches kits that use
   the same round GC9B72 display (sw-gc9b72, big-round-speaker-clock,
   mondaine). Those repos render them with the same simulator.
3. CONCEPT ART. Mock-ups of samples nobody has written yet, drawn here
   with Pillow on the same round bezel. The gallery labels them as ideas.

    python3 scripts/render-gallery-images.py              # everything
    python3 scripts/render-gallery-images.py --only demo   # names containing "demo"

Set CLOCKS_REPO if clocks-and-watches is not next to this repo.
Needs Python 3.10+ and Pillow.
"""

import argparse
import contextlib
import importlib.util
import io
import json
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
KIT = os.path.join(REPO, "src", "kits", "study-buddy-base")
OUT = os.path.join(REPO, "docs", "gallery", "img")
CLOCKS = os.environ.get("CLOCKS_REPO",
                        os.path.join(os.path.dirname(REPO), "clocks-and-watches"))
SIM = os.path.join(CLOCKS, "src", "display-simulators", "gc9b72")
DRIVER = os.path.join(HERE, "gallery-demo-driver.py")

# ---------------------------------------------------------------------------
# 1. Kit screens: (image name, program, snapshot ms, presses, whistle Hz)
#    A program starting with "demo_" runs through gallery-demo-driver.py.
# ---------------------------------------------------------------------------
KIT_SHOTS = [
    ("lab-02-probe", "02-probe.py", None, (), 0),
    ("lab-03-buttons", "03-buttons.py", 3000,
     (("mode", 500, 700), ("up", 1200, 1400), ("down", 1900, 2100)), 0),
    ("lab-04-hello-world", "04-hello-world.py", None, (), 0),
    ("lab-05-speaker-tones", "05-speaker-tones.py", None, (), 0),
    ("lab-06-listen-meter", "06-listen-meter.py", 4000, (), 600),
    ("lab-07-record-playback", "07-record-playback.py", 1500,
     (("mode", 800, 2500),), 500),
    ("lab-08-color-mixing", "08-color-mixing.py", None, (), 0),
    ("lab-09-angles-to-pixels", "09-angles-to-pixels.py", 3000, (), 0),
    ("lab-10-flicker-free-text", "10-flicker-free-text.py", None, (), 0),
    ("lab-11-button-bounce", "11-button-bounce.py", 3000,
     (("mode", 500, 700), ("up", 1200, 1400), ("down", 1900, 2100),
      ("up", 2400, 2600)), 0),
    ("lab-12-one-loop-many-jobs", "12-one-loop-many-jobs.py", 3200, (), 0),
    ("lab-13-modes-state-machine", "13-modes-state-machine.py", 2500,
     (("up", 1000, 1100),), 0),
    ("lab-14-samples-make-sound", "14-samples-make-sound.py", 3000, (), 0),
    ("lab-15-sound-envelopes", "15-sound-envelopes.py", 3000, (), 0),
    ("lab-16-mic-oscilloscope", "16-mic-oscilloscope.py", 3000, (), 440),
    ("lab-17-whistle-tuner", "17-whistle-tuner.py", 3000, (), 880),
    ("lab-18-network-layers", "18-network-layers.py", None, (), 0),
    ("lab-19-pattern-game", "19-pattern-game.py", 2600, (), 0),
    ("demo-showcase", "main.py", 1500, (), 0),
    ("demo-clock", "demo_clock", 3000, (), 0),
    ("demo-alarm", "demo_alarm", 2000, (), 0),
    ("demo-timer", "demo_timer", 6000, (("up", 500, 560),), 0),
    ("demo-stopwatch", "demo_stopwatch", 7300,
     (("up", 500, 560), ("down", 2600, 2660), ("down", 5200, 5260)), 0),
    ("demo-school", "demo_school", 2000, (), 0),
    ("demo-tones", "demo_tones", 2500, (), 0),
    ("demo-listen", "demo_listen", 4000, (), 600),
    ("demo-record", "demo_record", 2000, (), 0),
    ("demo-quote", "demo_quote", 2000, (), 0),
    ("demo-spanish", "demo_spanish", 2500, (), 0),
    ("demo-vocab", "demo_vocab", 2000, (), 0),
]

# Labs that print to the shell instead of drawing: their picture is the
# shell window, showing what the real program printed.
CONSOLE = {"lab-02-probe", "lab-03-buttons", "lab-05-speaker-tones"}

# Lab 10 times itself with ticks_us(), which never moves the simulator's
# fake clock, so it runs for a few real seconds and keeps its last screen.
REAL_SECONDS = {"lab-10-flicker-free-text": 4}

# The microphone hears a quiet room first, so programs that measure the
# noise floor at start-up calibrate, then the whistle starts.
WHISTLE_FROM_MS = 1500

# ---------------------------------------------------------------------------
# 2. Clock faces from clocks-and-watches: (image name, kit, image file)
# ---------------------------------------------------------------------------
CLOCK_COPIES = [
    ("clock-digital", "sw-gc9b72", "03-digital-clock.png"),
    ("clock-analog", "sw-gc9b72", "05-analog-watch-face.png"),
    ("clock-set-time", "sw-gc9b72", "07-set-time.png"),
    ("clock-digital-watch", "sw-gc9b72", "08-digital-watch-face.png"),
    ("clock-weather", "sw-gc9b72", "09-weather-clock.png"),
    ("clock-stopwatch", "sw-gc9b72", "10-stopwatch.png"),
    ("clock-countdown", "sw-gc9b72", "11-timer-running.png"),
    ("clock-big", "big-round-speaker-clock", "09-mode-0-big.png"),
    ("clock-temperature", "big-round-speaker-clock", "09-mode-1-temp.png"),
    ("clock-forecast", "big-round-speaker-clock", "09-mode-2-forecast.png"),
    ("clock-alarm", "big-round-speaker-clock", "09-mode-3-alarm.png"),
    ("clock-phrase", "big-round-speaker-clock", "09-mode-8-phrase.png"),
    ("clock-holidays", "big-round-speaker-clock", "09-mode-9-calendar.png"),
    ("clock-railway", "mondaine", "15-mondaine-clock.png"),
    ("clock-railway-dial", "mondaine", "04-minute-markers.png"),
    ("clock-railway-sweep", "mondaine", "10-smooth-sweep.png"),
]

# Lab 01 has nothing on the screen and prints one line, so its picture is
# a crop of the kit photo around the Pico: (image name, photo, crop box).
PHOTO_CROPS = [
    ("lab-01-blink", os.path.join(REPO, "docs", "img", "study-buddy-rear-view.jpg"),
     (1000, 500, 3000, 2500)),
]

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("--only", default="", help="only images whose name contains this")
parser.add_argument("--job", help=argparse.SUPPRESS)      # one kit screen, in a child process
args = parser.parse_args()


def wanted(name):
    return args.only in name


def load_concepts():
    spec = importlib.util.spec_from_file_location(
        "gallery_concepts", os.path.join(HERE, "gallery-concepts.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# One kit screen, run in its own process: the simulator's fakes replace
# machine, time and friends for the whole process.
# ---------------------------------------------------------------------------
def run_job(name):
    name, program, at, presses, whistle = next(s for s in KIT_SHOTS if s[0] == name)
    sys.path.insert(0, SIM)
    from gc9b72_sim import runner, render, hardware, pico2w

    pico2w.pretend()
    phase = [0.0]

    def readinto(self, buf):
        """A microphone hearing a steady whistle: 32-bit samples, as the
        INMP441 sends them, with the DC offset the real one has."""
        n = len(buf) // 4
        step = 2 * math.pi * whistle / self.rate
        mv = memoryview(buf)
        for k in range(n):
            level = 15000
            if whistle and runner.state["ms"] >= WHISTLE_FROM_MS:
                level += int(9000 * math.sin(phase[0]))
            level += (k * 7919) % 41 - 20                 # a little hiss
            phase[0] += step
            mv[4 * k:4 * k + 4] = (level << 8).to_bytes(4, "little", signed=True)
        runner._advance(max(1, int(n * 1000 / self.rate)))
        return n * 4

    hardware.I2S.readinto = readinto
    # Two calls the simulator does not fake yet: Pin.init() (lab 02 checks
    # the button pulls) and WLAN.status("rssi") (lab 18 shows the signal).
    hardware.Pin.init = lambda self, *a, **k: None
    status = hardware.WLAN.status
    hardware.WLAN.status = lambda self, param=None: (
        -59 if param == "rssi" else status(self))
    hardware._Response.text = property(lambda self: json.dumps(self.json()))
    hardware.FORECAST["current"] = {"time": "2026-09-25T10:00",
                                    "temperature_2m": 64.2, "wind_speed_10m": 7.4}
    if name in REAL_SECONDS:
        runner.REAL_TIMEOUT_S = REAL_SECONDS[name]
    runner.use_kit(KIT)
    os.chdir(KIT)                       # demos open spanish/*.wav and the like
    lab = program
    if program.startswith("demo_"):
        os.environ["GALLERY_DEMO"] = program
        lab = DRIVER
    snaps = [at] if at else []
    limit = (at or 4000) + 100
    if name in CONSOLE:
        shell = io.StringIO()
        with contextlib.redirect_stdout(shell):
            runner.run_lab(lab, limit, list(presses), snaps, None)
        lines = [line.rstrip() for line in shell.getvalue().splitlines() if line.strip()]
        load_concepts().terminal("Shell: " + program, lines,
                                 os.path.join(OUT, name + ".png"))
        return
    runner.run_lab(lab, limit, list(presses), snaps, None)
    px = runner.state["snaps"][at] if at else list(hardware.screen.px)
    render.save_png(px, os.path.join(OUT, name + ".png"))


if args.job:
    run_job(args.job)
    sys.exit(0)

os.makedirs(OUT, exist_ok=True)
failed = []

for shot in KIT_SHOTS:
    if wanted(shot[0]):
        done = subprocess.run([sys.executable, __file__, "--job", shot[0]],
                              capture_output=True, text=True)
        timed_out = "WARNING" in done.stderr and shot[0] not in REAL_SECONDS
        if done.returncode != 0 or timed_out:
            failed.append(shot[0])
            print("FAILED", shot[0], done.stderr.strip().splitlines()[-1:])
        else:
            print("wrote", shot[0])

for name, photo, box in PHOTO_CROPS:
    if wanted(name):
        from PIL import Image, ImageDraw
        img = Image.open(photo).convert("RGB").crop(box).resize((400, 400), Image.LANCZOS)
        mask = Image.new("L", (400, 400), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, 399, 399), 24, fill=255)
        img.putalpha(mask)
        img.save(os.path.join(OUT, name + ".png"), optimize=True)
        print("cropped", name)

for name, kit, image in CLOCK_COPIES:
    if wanted(name):
        shutil.copyfile(os.path.join(CLOCKS, "docs", "kits", kit, "img", image),
                        os.path.join(OUT, name + ".png"))
        print("copied", name)

# ---------------------------------------------------------------------------
# 3. Concept art
# ---------------------------------------------------------------------------
concepts = load_concepts()
for name, draw in concepts.CONCEPTS:
    if wanted(name):
        concepts.save(draw, os.path.join(OUT, name + ".png"))
        print("drew", name)

if failed:
    print("\n%d kit screens failed: %s" % (len(failed), ", ".join(failed)))
    sys.exit(1)
