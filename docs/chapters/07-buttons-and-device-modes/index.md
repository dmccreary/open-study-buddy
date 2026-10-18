---
title: "Buttons, State Machines, and Device Modes"
description: "How to read the Mode, Up, and Down buttons reliably with debouncing, edge detection, and long presses, and how to organize the device's behavior as a non-blocking state machine with modes, a settings screen, and user feedback."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 11:08:20"
version: 1.11
---

# Buttons, State Machines, and Device Modes

## Summary

This chapter builds the physical interface for the device. Students read the Mode, Up, and Down buttons reliably with debouncing and edge detection, add long presses and menus, and organize the device's behavior as a state machine. They also learn non-blocking code so button handling never stalls the audio loop later in the book.

## Concepts Covered

This chapter covers the following 16 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Mode Button | 35 |
| Up Button | 10 |
| Down Button | 4 |
| Button Debouncing | 2 |
| Falling Edge Detection | 2 |
| Long Press | 1 |
| Menu Navigation | 2 |
| State Machine | 18 |
| Volume Control | 1 |
| Device Modes | 14 |
| Event Loop | 3 |
| Button Interrupt | 1 |
| Non-Blocking Code | 2 |
| User Feedback | 4 |
| Settings Screen | 1 |
| Status Indicator | 3 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 2: MicroPython Review for Embedded Systems](../02-micropython-review/index.md)
- [Chapter 4: The Pico Kit Hardware and Wiring](../04-pico-kit-hardware/index.md)
- [Chapter 6: Drawing Directly to Display Regions](../06-display-regions-and-drawing/index.md)

---

## Three Buttons, Many Behaviors

Your Study Buddy has a round screen, a microphone, and a speaker, but only three buttons to control all of them. That is a design puzzle. Each button must do different things at different times, and the device must always show the student what is happening. The solution is to give the device *modes* and to treat the buttons as events that move it from one mode to another.

!!! mascot-welcome "Three Buttons, One Smart Device"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter, three buttons will start a recording, change the volume, and open a settings screen, and none of them will ever miss a press or double-count one. Let's listen closely! A good interface is mostly good bookkeeping.

## The Three Buttons

The kit wires three buttons, each with its other leg to ground and an internal pull-up, so each reads 0 while pressed.

| Button | Pin | Role in this book |
|--------|-----|-------------------|
| Mode | GP13 | The main action: hold to talk, and move through screens |
| Up | GP14 | Raise the current value, such as the volume |
| Down | GP15 | Lower the current value |

### The Mode Button

The **Mode button** is the most important button because it changes what the device is doing. In the final device, pressing and holding it starts push-to-talk: the microphone listens while the button is down, and releasing it sends the question. Test 07 already works this way. *Worked example:* you hold MODE, the screen says "RECORDING" and the LED lights, you say "When is my next test?", you let go, and the device plays the audio back. In the same way, the finished device will release the recording to the buddy server instead of the speaker.

### The Up Button

The **Up button** raises the current value. Which value depends on the mode: on the clock it is the volume, and in the settings screen it is the selected setting. *Worked example:* with the volume at 40, one press of Up makes it 50. Seven presses from 40 would reach 100 after the sixth, and the seventh does nothing because the volume stops at the maximum.

### The Down Button

The **Down button** lowers the current value in the same way. *Worked example:* with the volume at 10, one press makes it 0, which is silent, and further presses keep it at 0. The upper and lower limits are called *clamping*, and the code for it is a single `max(0, min(100, value))`.

## Reading a Button Reliably

### Falling Edge Detection

A button that you press and hold is down for many loops of your program, but the *press* is a single moment. An **edge** is the instant a signal changes. With a pull-up, pressing the button makes the pin go from 1 to 0, which is a **falling edge**, and releasing it makes the pin go from 0 to 1, a rising edge. **Falling edge detection** means acting only at that moment of change: compare the pin now with the pin the last time you looked.

```python
was_down = False
while True:
    is_down = button.value() == 0
    if is_down and not was_down:
        print("pressed")        # runs once per press
    was_down = is_down
```

Without the comparison with `was_down`, the `print` would run on every loop for as long as you hold the button.

### Button Debouncing

Real buttons are not clean. When two metal contacts meet, they spring apart and touch again several times in a few milliseconds before settling. This **bounce** makes the pin flicker 1, 0, 1, 0, 0 before staying at 0. The microcontroller is fast enough to see every flicker, and counts them as separate presses.

**Button debouncing** is the fix: ignore any further change on a button for a short time after you accept one. Test 03 uses 30 ms.

```python
DEBOUNCE_MS = 30
if is_down != pressed[i] and time.ticks_diff(now, last_change[i]) > DEBOUNCE_MS:
    pressed[i] = is_down
    last_change[i] = now
```

Here `time.ticks_ms()` gives the current time in milliseconds, and `time.ticks_diff(now, last_change)` is the safe way to subtract two such times (it survives the counter wrapping around). The condition says: accept a change only if the button's state differs from what we last reported *and* more than 30 ms have passed since the last accepted change.

*Worked example.* The pin is sampled every 5 ms and reads 1, 1, 0, 1, 0, 1, 0, 0, 0, 0. The first 0 appears at 10 ms. With no debounce, every change counts: three presses (at 10, 20, and 30 ms). With a 30 ms debounce, the press is accepted at 10 ms and the flicker at 15 to 30 ms is ignored, so one press is counted.

The right debounce time is a balance. Too short (10 ms) and a noisy switch gets through. Too long (100 ms) and two quick taps merge into one. Try the visualizer to see where each setting fails.

#### Diagram: Button Bounce and Debounce Visualizer

<details markdown="1">
<summary>Button Bounce and Debounce Visualizer</summary>
Type: microsim
**sim-id:** debounce-bounce-visualizer<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** execute<br/>
**Learning Objective:** The learner will execute the debounce rule on 6 recorded pin traces by counting the presses accepted at a given debounce time, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** bounce, debounce time, falling edge, `ticks_diff` (all defined in the sections above this block). The debounce rule is shown in the Rules field and on screen throughout.

**Evidence of Mastery:** For each of the 6 items the learner types the number of presses the rule counts for the trace and debounce time shown. An answer is correct when it equals the Presses counted column in Content. Mastery is 5 of 6 on the first attempt. Changing the debounce time in the exploration trace is exploration, not evidence.

**Misconceptions:** (1) Every 0 in the trace is a separate press. (2) A longer debounce time is always safer. (3) Debouncing is only needed when a button is pressed, not when it is released.

**Instructional Rationale:** Apply-level execution of a rule requires the learner to step through data by hand. Seeing both a too-short and a too-long debounce time fail on the same kind of trace makes the learner see the trade-off, rather than memorize a number.

**Content:**

Each trace is the pin value (1 released, 0 down) sampled every 5 ms starting at 0 ms. The traces are listed with the sample number starting at 0.

| Trace | Samples (every 5 ms) | Description |
|---|---|---|
| A | 1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1 | A clean press |
| B | 1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0 | Press with 20 ms of bounce |
| C | 1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,1,1,1,1,1,1,1,1 | Clean press, then a bouncy release |
| D | 1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1 | Two real presses 40 ms apart |
| E | 1,0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0 | A noisy switch that chatters for 55 ms |

Items, in this order:

| # | Trace | Debounce time (ms) | Presses counted | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | A | 30 | 1 | A clean press has no bounce, so one press is counted. |
| 2 | B | 0 | 3 | With no debounce every flicker to 0 counts: at 10, 20, and 30 ms. |
| 3 | B | 30 | 1 | The press is accepted at 10 ms and the flicker up to 30 ms is ignored. |
| 4 | D | 100 | 1 | The release at 50 ms is ignored because it is within 100 ms of the press at 10 ms, so the second press is never separate. |
| 5 | E | 30 | 2 | The chatter lasts 55 ms, which is longer than 30 ms, so a later flicker is counted as a second press at 75 ms. |
| 6 | C | 10 | 2 | The bounce on release lasts longer than 10 ms, so the release is accepted and a second press is counted at 90 ms. |

**Provenance:** The traces are illustrative, and the sim labels them "illustrative." The rule is the logic of the debounce in `src/kits/study-buddy-base/03-buttons.py`. The counts were computed by executing the rule on each trace.

**Rules:** The state starts as released with the last accepted change set to a time long before 0 ms. At each sample time t with pin value v: if (v equals 0) differs from the state, and t minus the time of the last accepted change is greater than the debounce time, the state flips and the last accepted change becomes t; a flip to pressed adds 1 to the press count. For exploration the debounce time ranges from 0 to 100 ms in steps of 10 ms, default 30 ms.

**Learner Activity:**

1. The learner explores trace B: changes the debounce time and watches the accepted presses (marked on the trace) change.
2. The learner starts the 6 items. Item 1 shows trace A and the debounce time.
3. The learner types the number of presses and submits.
4. The sim marks each accepted change on the trace and shows the Why text.
5. After item 6, the sim shows the score. The learner should notice that traces D and E break a debounce time that is too long or too short.

**Feedback:** 6 items, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The rule counts <answer>: <Why>". The accepted changes are shown after each submission, and a running score "n of 6" is shown.

**Starting State:** Trace B is shown with a debounce time of 30 ms and the question "How many presses does the rule count?"

**Chapter Anchors:** The chapter states that test 03 uses a 30 ms debounce, that an unfiltered bouncy press can count three times, and that too long a debounce merges quick taps.
</details>

!!! mascot-tip "Use ticks_diff, Never Plain Subtraction"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    The millisecond counter wraps around after a long time, and a plain `now - last` can go wrong at that moment. `time.ticks_diff(now, last)` always gives the right answer, so use it for every time comparison, including the debounce.

### Long Press

A **long press** is holding a button for longer than a threshold, typically 800 ms. It gives each button a second job without another button. The detection needs one extra piece of memory: when the press started. If the button is still down and more than the threshold has passed, send a "long" event, and send it only once.

The next code puts the three ideas in this section together in one small class. It reads a pin and returns one of three events when you call `update()` often: `"press"` at the falling edge, `"long"` once when the hold reaches 800 ms, and `"release"` when the button comes back up, after which `held` tells you how long it was down.

```python
import time

class Button:
    def __init__(self, pin, debounce_ms=30, long_ms=800):
        self.pin = pin
        self.debounce_ms = debounce_ms
        self.long_ms = long_ms
        self.down = False
        self.changed_at = -1000
        self.pressed_at = 0
        self.long_sent = False
        self.held = 0

    def update(self):
        now = time.ticks_ms()
        is_down = self.pin.value() == 0
        if is_down != self.down and \
                time.ticks_diff(now, self.changed_at) > self.debounce_ms:
            self.down = is_down
            self.changed_at = now
            if is_down:
                self.pressed_at = now
                self.long_sent = False
                return "press"
            self.held = time.ticks_diff(now, self.pressed_at)
            return "release"
        if self.down and not self.long_sent and \
                time.ticks_diff(now, self.pressed_at) >= self.long_ms:
            self.long_sent = True
            return "long"
        return None
```

The first `if` is the debounced edge detection from test 03. The second `if` is new: while the button is down and the "long" event has not been sent yet, check whether the hold time has reached `long_ms`. The class never waits, so you can call `update()` on each of the three buttons many times a second.

*Worked example.* Hold a button for 1.2 seconds. `update()` returns `"press"` at the start, `"long"` at 800 ms, and `"release"` at 1.2 s with `held` equal to about 1,200. Tap the button for 100 ms and it returns only `"press"` then `"release"` with `held` near 100, so the program can tell a tap (held under 800) from a hold.

## Non-Blocking Code and the Event Loop

### The Event Loop

An **event loop** is a loop that runs forever and, on every pass, checks for events and handles any that have happened. The events here are button presses, and later they will be audio frames and network messages. The loop does a small piece of work and comes straight back.

```python
buttons = {"mode": Button(mode_pin), "up": Button(up_pin), "down": Button(down_pin)}

while True:
    for name, button in buttons.items():
        event = button.update()
        if event:
            device.on_button(name, event, button.held)
    time.sleep_ms(5)
```

Each pass asks each button whether anything happened and hands any event to the device. The 5 ms sleep keeps the loop from using the processor needlessly and is the same polling interval as test 03, so a press is noticed within about 5 ms.

### Non-Blocking Code

**Non-blocking code** never waits for something to happen. Blocking code stops everything until a condition is met, for example `time.sleep(1)` or `while button.value() == 0: pass`. While that line runs, nothing else does: the screen does not update and the microphone buffer overflows. A 1-second sleep in the middle of listening loses 25 audio frames of 40 ms each.

The non-blocking replacement is to *remember a deadline* and keep looping.

```python
deadline = time.ticks_add(time.ticks_ms(), 1000)
while True:
    # ... other work happens here ...
    if time.ticks_diff(time.ticks_ms(), deadline) >= 0:
        print("one second has passed")
        break
```

`time.ticks_add` adds milliseconds to a timestamp safely, and the `ticks_diff` test is true once the deadline has passed. Everything else in the loop keeps running in the meantime.

| Blocking | Non-blocking |
|----------|--------------|
| `time.sleep(1)` | Store a deadline; check it each loop |
| `while button.value() == 0: pass` | Handle the "release" event when it arrives |
| Wait for the server in a loop | Poll for the reply each pass (Chapter 13) |

!!! mascot-warning "A Sleep Is a Deaf Ear"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Test 07 pauses for a full second after showing "Too short". That is fine in a test, but in the real device a `sleep` while the microphone is open means missed audio. Replace long sleeps with a deadline that the event loop checks.

### Button Interrupts

A **button interrupt** asks the hardware to notice the falling edge for you, using the interrupt mechanism from Chapter 2. It is useful when the main loop is sometimes busy for a long time, such as during a slow display update, and a press must not be lost. The interrupt service routine only records the press, with the same 30 ms debounce, and the main loop does the work.

```python
last_press = 0
pressed = False

def on_fall(pin):
    global last_press, pressed
    now = time.ticks_ms()
    if time.ticks_diff(now, last_press) > 30:
        last_press = now
        pressed = True

mode_pin.irq(trigger=Pin.IRQ_FALLING, handler=on_fall)
```

The routine does nothing but compare two numbers and set a flag, which keeps it short enough to be safe inside an interrupt. For this book, polling every 5 ms is simpler and is fast enough next to 40 ms audio frames, so the code you build on uses the polled `Button` class, and interrupts are the tool to remember when a long task would otherwise hide a press.

## State Machines and Device Modes

### Device Modes

A **device mode** is a situation the device can be in, such as showing the clock or recording a question. The mode decides what the screen shows and what each button does. The finished Study Buddy has five.

| Mode | What the device is doing | What the screen shows |
|------|--------------------------|-----------------------|
| CLOCK | Idle, showing the time | Clock face and status bar |
| LISTENING | Recording the student's question | A level meter and "Listening" |
| THINKING | Waiting for the buddy server's reply | "Thinking..." |
| SPEAKING | Playing the reply | The reply text and mascot speaking |
| SETTINGS | Letting the student change options | A list of settings |

### The State Machine

A **state machine** is a way of organizing a program around a fixed set of states and rules for moving between them. At every moment the machine is in exactly one **state** (here, a mode). An **event**, such as a button press or a reply arriving, may cause a **transition** to another state. The rules are written as a table: the current state and the event select the next state.

The table below gives the rules for the Study Buddy. "Short" means released before 800 ms, and "long" means held 800 ms or more. MODE is not held long in LISTENING because the student holds it while talking.

| State | MODE | UP | DOWN | Other events |
|-------|------|----|------|--------------|
| CLOCK | press: go to LISTENING | short: volume up; long: go to SETTINGS | short: volume down | none |
| LISTENING | release after 0.2 s or more: THINKING; release sooner: CLOCK | ignored | ignored | buffer full: THINKING |
| THINKING | press: cancel, go to CLOCK | ignored | ignored | reply arrives: SPEAKING |
| SPEAKING | press: stop, go to CLOCK | press: volume up | press: volume down | speech finished: CLOCK |
| SETTINGS | short: next setting; long: go to CLOCK | press: raise the value | press: lower the value | none |

Reading across a row tells you what each button does in that mode, and that is exactly what the code does. Each button has a different meaning in different modes, which is how three buttons run a five-mode device.

!!! mascot-encourage "A Table Is the Whole Program"
    ![Sage encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    State machines can feel abstract on the first read, and that is normal. Put your finger on the starting row of the table, follow one button press to the next row, and repeat. If you can follow the table, you can follow the code, because the code is the table.

The code is a class that holds the state and one method that reacts to events, written as one `if` branch per state.

```python
CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS = range(5)
LONG_MS = 800
MIN_MS = 200

class Device:
    def __init__(self):
        self.state = CLOCK
        self.volume = 40

    def go(self, state):
        self.state = state          # a real build also redraws the status region

    def step_volume(self, direction):
        self.volume = max(0, min(100, self.volume + 10 * direction))

    def on_button(self, name, event, held_ms=0):
        s = self.state
        step = 1 if name == "up" else -1
        if s == CLOCK:
            if name == "mode" and event == "press":
                self.go(LISTENING)
            elif name == "up" and event == "long":
                self.go(SETTINGS)
            elif name != "mode" and event == "release" and held_ms < LONG_MS:
                self.step_volume(step)
        elif s == LISTENING:
            if name == "mode" and event == "release":
                self.go(THINKING if held_ms >= MIN_MS else CLOCK)
        elif s == THINKING:
            if name == "mode" and event == "press":
                self.go(CLOCK)
        elif s == SPEAKING:
            if name == "mode" and event == "press":
                self.go(CLOCK)
            elif name != "mode" and event == "press":
                self.step_volume(step)

    def on_internal(self, what):
        if self.state == LISTENING and what == "full":
            self.go(THINKING)
        elif self.state == THINKING and what == "reply":
            self.go(SPEAKING)
        elif self.state == SPEAKING and what == "done":
            self.go(CLOCK)
```

The `on_button` method reads like the table: each branch is a state, and each inner `if` is an event. `on_internal` handles events that are not buttons: the recording buffer filling, a reply arriving, and speech finishing. The settings branch is added in the section on the settings screen below. Notice that `go()` is the only place that changes the state, so it is also the one place to redraw the status region and set the LED.

*Worked example.* The student holds MODE for 1.5 seconds and then lets go. `on_button("mode", "press")` moves CLOCK to LISTENING. The release arrives with `held_ms` of 1,500, which is at least `MIN_MS` of 200, so the state becomes THINKING. When the reply arrives, `on_internal("reply")` moves to SPEAKING, and when playback ends `on_internal("done")` returns to CLOCK. A tap of only 100 ms is shorter than `MIN_MS`, and the release sends the device straight back to CLOCK, which is the "too short" case from test 07.

!!! mascot-thinking "States Make Bugs Visible"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Without a state machine, a program accumulates flags like `is_recording`, `is_playing`, and `is_waiting`, and bugs hide in the combinations that should never happen. With one `state` variable, the device can only be in one place, and any impossible situation shows up as a missing row in the table.

Practice following the table with the next activity.

#### Diagram: Device Mode State Machine

<details markdown="1">
<summary>Device Mode State Machine</summary>
Type: microsim
**sim-id:** device-mode-state-machine<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Template:** https://github.com/dmccreary/automating-instructional-design/tree/main/docs/sims/state-machine-template<br/>
**Bloom Level:** Apply<br/>
**Bloom Verb:** use<br/>
**Learning Objective:** The learner will use the device's state transition table to find the final mode and the final volume after 6 sequences of button events, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** device mode, state, event, transition, short press, long press, volume clamping (all defined in the sections above this block, with the table in the section "The State Machine").

**Evidence of Mastery:** For each of the 6 sequences the learner picks the final mode from the five modes and the final volume from the values 30, 40, 50, and 60. An answer is correct when both match the Final mode and Final volume columns in Content. Mastery is 5 of 6 on the first attempt. Stepping through the example sequence in exploration is exploration, not evidence.

**Misconceptions:** (1) A button does the same thing in every mode. (2) Releasing MODE always sends the recording to the server. (3) A long press of UP in CLOCK also changes the volume.

**Instructional Rationale:** Apply-level use of a table requires the learner to carry the state forward one event at a time. Keeping volume as a second answer makes the learner track more than one thing, as a real state machine does.

**Content:**

The sim starts every sequence in CLOCK with a volume of 40. The transition table is the one in the chapter section "The State Machine." The volume changes by 10 for each volume-up or volume-down step, between 0 and 100.

Sequences, in this order:

| # | Event sequence shown | Final mode | Final volume | Why (shown as feedback) |
|---|---|---|---|---|
| 1 | MODE pressed; MODE released after 1.5 s | THINKING | 40 | The hold is at least 0.2 s, so releasing sends the question and waits for the reply. |
| 2 | MODE pressed; MODE released after 0.1 s | CLOCK | 40 | The hold is under 0.2 s, so it was a bump, and the device returns to the clock. |
| 3 | MODE pressed; MODE released after 1.5 s; reply arrives | SPEAKING | 40 | A reply in THINKING moves the device to SPEAKING. |
| 4 | UP held for 1 s (a long press); DOWN pressed; MODE pressed and released after 0.1 s | SETTINGS | 30 | The long press of UP opens SETTINGS, DOWN lowers the value of the first setting (volume) by 10, and a short MODE press only moves to the next setting. |
| 5 | MODE pressed; MODE released after 1.5 s; MODE pressed again | CLOCK | 40 | A MODE press in THINKING cancels and returns to the clock. |
| 6 | UP pressed and released after 0.1 s; UP pressed and released after 0.1 s | CLOCK | 60 | Each short UP press in CLOCK raises the volume by 10, from 40 to 50 to 60. |

**Provenance:** The table and rules come from the chapter section "The State Machine." The sequences are illustrative, and the sim labels them "illustrative."

**Rules:** The mode changes only as the transition table says. Volume is limited to the range 0 to 100 and changes in steps of 10. A long press is 800 ms or more. In SETTINGS the first setting is Volume. A mode is unchanged by an event the table lists as "ignored."

**Learner Activity:**

1. The learner explores a sample sequence and steps through it, watching the mode highlight on a diagram of the five modes and the volume number change.
2. The learner starts the 6 sequences. Sequence 1 is shown as a list of events.
3. The learner picks a final mode and a final volume, then submits.
4. The sim replays the sequence on the diagram, showing the mode after each event, and shows the Why text.
5. After sequence 6, the sim shows the score. The learner should notice that the same button has different effects in CLOCK, THINKING, and SETTINGS.

**Feedback:** 6 sequences, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The device ends in <mode> at volume <volume>: <Why>". The replay is shown after every submission, and a running score "n of 6" is shown.

**Starting State:** The five modes are shown with CLOCK highlighted and volume 40, with the first sequence and the question "Where does the device end up?"

**Chapter Anchors:** The chapter states that the device has five modes (CLOCK, LISTENING, THINKING, SPEAKING, SETTINGS), that a long press is 800 ms or more, that a hold shorter than 0.2 s returns to CLOCK, and that the volume starts at 40 and moves in steps of 10 between 0 and 100.
</details>

## Feedback for the Student

### User Feedback

**User feedback** is anything the device does to tell the student that it noticed their action. A button press with no visible response feels broken. The rule of thumb is that something should change within about 100 ms. Our display regions make this cheap: redrawing the 120 by 20 status bar costs 4,800 bytes, or about 1.6 ms.

There are three channels the kit can use, and the best feedback often uses two.

| Channel | Example | Cost |
|---------|---------|------|
| Screen | Status bar shows "Vol 50" | About 1.6 ms |
| LED | Onboard LED lights during recording | Almost free |
| Sound | A short beep at the new volume | Takes the audio output |

### Status Indicators

A **status indicator** is a small, always-visible signal of the device's mode. The most important one is the one that shows when the microphone is open. In test 07, the onboard LED turns on at the start of recording and off when it ends (`led.value(1)` and `led.value(0)`), and the screen shows "RECORDING". A listening device must never listen silently, and Chapter 17 makes this a rule. In the code above, the place to set the indicator is `go()`: whenever the state becomes LISTENING, turn the LED on, and turn it off for any other state.

### Volume Control

**Volume control** lets the student set how loud the speaker is. The kit's `config.VOLUME` is a number from 0 (silent) to 100 (the loudest the amplifier is asked for), with a default of 40. In test 05 the volume sets the amplitude of the tone: the peak sample is `32767 * volume / 100`, so volume 40 gives peaks near 13,107 and volume 100 gives 32,767. The `step_volume()` method above moves it in steps of 10 and clamps it. A good habit is to play a short beep after each change so the student hears the new level.

## Menus and Settings

### Menu Navigation

**Menu navigation** is moving through a list of choices with the buttons. With only three buttons, the convention is: Mode moves from one item to the next, Up and Down change the value of the current item, and a long press of Mode leaves the menu. The code only needs a number for the selected item and the clamping you already know.

### The Settings Screen

The **settings screen** is the SETTINGS mode's display: a short list of settings with the current one highlighted and its value shown. Because the screen redraws regions, a change of selection only redraws two rows, the old one and the new one.

| Item | Values | UP and DOWN do |
|------|--------|----------------|
| Volume | 0 to 100 in steps of 10 | Raise and lower the volume |
| Theme | NIGHT or DAY | Switch between the two themes from Chapter 5 |

These lines extend `on_button` with the SETTINGS branch, using the `item` counter to pick which setting UP and DOWN change.

```python
ITEMS = ("Volume", "Theme")

# in __init__:  self.item = 0;  self.theme = 0
# in on_button:
        elif s == SETTINGS:
            if name == "mode" and event == "long":
                self.go(CLOCK)
            elif name == "mode" and event == "release" and held_ms < LONG_MS:
                self.item = (self.item + 1) % len(ITEMS)
            elif name != "mode" and event == "press":
                if self.item == 0:
                    self.step_volume(step)
                else:
                    self.theme = 1 - self.theme
```

A short release of MODE moves to the next item, wrapping from the last back to the first with the `%` operator. UP and DOWN change the volume when the item is 0, and flip the theme between 0 and 1 otherwise. A long press of MODE returns to the clock.

## Putting It All Together

The device now has a complete control scheme. A debounced `Button` class turns noisy pin readings into clean `press`, `long`, and `release` events. An event loop polls the three buttons every 5 ms without ever blocking. A `Device` state machine turns those events into mode changes, and each change updates the status regions, the LED, and the volume.

Key takeaways:

- Act at the falling edge, not while the button is held, by comparing the pin now with the pin the last time you looked.
- Debounce by ignoring changes for about 30 ms after accepting one; too short lets bounce through, too long merges quick taps.
- A long press is a hold of 800 ms or more, detected with a stored start time and sent once.
- An event loop checks for events on every pass; non-blocking code replaces `sleep` with a deadline.
- Interrupts catch presses the main loop would miss, but the polled `Button` class is enough for this book.
- A state machine has one state variable, a table of events and transitions, and `go()` as the single place to change it.
- Give feedback within about 100 ms: the screen, the LED, and sound; the LED must show when the microphone is open.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "A student taps UP twice quickly in CLOCK, 80 ms apart, with a debounce of 100 ms. How many presses count, and what is the fix? Click to expand"
    Only one press counts, because the second change falls inside the 100 ms lock-out. Lower the debounce time to about 30 ms so that real quick taps are kept while the contact bounce is still ignored.

??? question "Why is `time.sleep(1)` in the main loop a problem for a device that is listening? Click to expand"
    While the program sleeps, it cannot read the microphone buffer or check the buttons. A 1-second sleep loses 25 audio frames of 40 ms each. Store a deadline and check it on each pass of the event loop instead.

!!! mascot-celebration "Hands for the Buddy"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just built the control scheme: debounced edges, long presses, a non-blocking event loop, and a five-mode state machine with a settings screen. Your three buttons can now run the whole device.

In Chapter 8 we bring sound in and out of the Pico with the I2S bus.
