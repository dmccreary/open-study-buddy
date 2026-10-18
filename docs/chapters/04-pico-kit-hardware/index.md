---
title: "The Pico Kit Hardware and Wiring"
description: "The five parts of the Open Study Buddy kit, what each one does, how they are powered and grounded, and how to wire them to the Pico 2 W using the pin assignment table."
generated_by: claude skill chapter-content-generator
date: "2026-10-18 11:00:10"
version: 1.11
---

# The Pico Kit Hardware and Wiring

## Summary

This chapter introduces the five hardware parts of the kit and how they are wired together on a breadboard. Students meet the Pico 2 W, the round display, the microphone, the amplifier and speaker, and the three push buttons, along with power, ground, and pull-up wiring. After this chapter, students can wire the kit correctly using the pin assignment table and spot common wiring mistakes.

## Concepts Covered

This chapter covers the following 22 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| MEMS Microphone | 320 |
| Speaker | 30 |
| Raspberry Pi Pico 2 W | 768 |
| Class-D Amplifier | 29 |
| RP2350 Microcontroller | 27 |
| Wi-Fi Radio | 133 |
| Round Color Display | 248 |
| INMP441 Microphone | 319 |
| MAX98357A Amplifier | 28 |
| Breadboard | 10 |
| USB Power | 2 |
| Dual Core Processor | 2 |
| Cortex-M33 Core | 23 |
| SRAM | 1 |
| Display Controller | 49 |
| Push Button | 125 |
| Dupont Wires | 1 |
| Pin Assignment Table | 6 |
| Ground Wiring | 2 |
| Pull-Up Resistor | 3 |
| Kit Bill of Materials | 1 |
| Power Supply Noise | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Personal Agents and the Open Study Buddy Architecture](../01-personal-agents-architecture/index.md)

---

## Meet the Parts

In Chapter 1 you learned that the Open Study Buddy is an agent terminal: it listens, shows, and speaks. This chapter is where that sentence turns into a pile of small boards on your desk. Five parts do all the work, and each one has a single clear job.

!!! mascot-welcome "Parts, Meet Builder"
    ![Sage waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    By the end of this chapter you will have wired a Pico to a screen, a microphone, a speaker, and three buttons, and you will know how to find a loose wire in minutes instead of hours. Let's listen closely! Every part in this kit has a job, and a wired-up kit is the proof you understood it.

### The Kit Bill of Materials

A **bill of materials** is the shopping list for a project. The parts in the base kit are all inexpensive, and together they cost a few tens of dollars.

| Part | What it is | Job in the kit |
|------|-----------|----------------|
| Raspberry Pi Pico 2 W | Microcontroller board with Wi-Fi | Runs your MicroPython and talks to every other part |
| 2.1 inch round display | 360 by 360 color screen with a GC9B72 controller | Shows the face, text, and level meter |
| INMP441 microphone board | Digital MEMS microphone | Turns sound into numbers |
| MAX98357A amplifier board plus a small speaker | Digital audio amplifier | Turns numbers into sound |
| Three push buttons | Tactile switches (Mode, Up, Down) | Let you choose, adjust, and talk |
| Breadboard, Dupont wires, USB cable | Solderless wiring supplies | Connect and power everything |

The activity below lets you check that you know which part does which job before we go deeper into each one.

#### Diagram: Kit Parts Infographic

<details markdown="1">
<summary>Kit Parts Infographic</summary>
Type: infographic
**sim-id:** kit-parts-infographic<br/>
**Library:** html<br/>
**Status:** Specified<br/>
**Bloom Level:** Remember<br/>
**Bloom Verb:** identify<br/>
**Learning Objective:** The learner will identify which of the five kit parts performs each of 5 described jobs, with at least 4 of 5 correct on the first attempt.

**Prerequisites:** the five parts and their one-line jobs, listed in the table "The Kit Bill of Materials" above this block.

**Evidence of Mastery:** The learner is shown 5 job statements one at a time and picks the matching part from the five. A pick is correct when it matches the Correct part column in Content. Mastery is 4 of 5 on the first attempt. Selecting a part to read its description beforehand is exploration, not evidence.

**Misconceptions:** (1) The Pico itself contains the microphone and speaker. (2) The amplifier makes the sound by itself. (3) The buttons are wired to the display.

**Instructional Rationale:** A Remember-level objective asks the learner to recall a fact accurately. Reading a labeled picture first, then answering a job question from memory, gives both a cue to learn from and a retrieval attempt that strengthens recall.

**Content:**

The infographic shows the five parts as a labeled picture. Selecting a part reveals its name and description.

| Part | Description shown on selection |
|---|---|
| Raspberry Pi Pico 2 W | The brain. It runs your MicroPython program and connects to Wi-Fi. |
| Round display | The face. A 360 by 360 color screen that shows text, shapes, and meters. |
| INMP441 microphone | The ear. It senses sound and sends 24-bit digital numbers to the Pico. |
| MAX98357A amplifier and speaker | The voice. The amplifier turns digital audio into power for the speaker. |
| Mode, Up, and Down buttons | The hands. Three switches you press to change modes, settings, and to talk. |

Job statements, in this order:

| # | Job statement shown to the learner | Correct part | Why (shown as feedback) |
|---|---|---|---|
| 1 | Turns room sound into digital numbers. | INMP441 microphone | The converter is built into the microphone board. |
| 2 | Runs the MicroPython program. | Raspberry Pi Pico 2 W | The Pico is the only part that runs your code. |
| 3 | Drives the speaker from digital audio. | MAX98357A amplifier and speaker | The amplifier takes I2S audio and powers the speaker. |
| 4 | Shows a level meter and text. | Round display | The display draws what the Pico tells it to draw. |
| 5 | Lets the student start push-to-talk. | Mode, Up, and Down buttons | A held button is read as a signal on a Pico pin. |

**Provenance:** The parts and jobs come from the chapter section "The Kit Bill of Materials."

**Rules:** Each job statement has exactly one correct part. The five parts are always offered together, in a fixed order.

**Learner Activity:**

1. The learner selects any part to read its description.
2. The learner starts the check. Job statement 1 is shown with the five parts as choices.
3. The learner picks one part.
4. The sim shows whether it was correct and the Why text, then moves to the next statement.
5. After statement 5, the sim shows the score.

**Feedback:** 5 statements, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. This is the job of the <correct part>: <Why>". The correct part is revealed right after each pick, and a running score "n of 5" is shown.

**Starting State:** The five parts are shown labeled and unselected, with the instruction "Select a part to learn its job."

**Chapter Anchors:** The chapter names the five parts as the Pico 2 W, the round display, the microphone, the amplifier with a speaker, and the three buttons.
</details>

## The Brain: Raspberry Pi Pico 2 W

The **Raspberry Pi Pico 2 W** is a small circuit board that carries a microcontroller, memory, a wireless chip, and a row of pins you can wire to. It is about the size of a stick of gum. It runs on 3.3 volts and has a micro-USB connector for power and for loading programs. You cannot run a web browser on it, but it has everything an agent terminal needs.

Four things on the board matter for this book.

| Feature | What the Pico 2 W has | Why the book cares |
|---------|----------------------|--------------------|
| Processor | RP2350 chip, up to 150 MHz | Runs audio code in real time |
| Memory | 520 KB of SRAM, 4 MB of flash | Holds buffers and your program files |
| Wireless | 2.4 GHz Wi-Fi (and Bluetooth) | Reaches the buddy server |
| Pins | 26 usable GPIO pins | Connect the display, buttons, and audio parts |

*Worked example.* The Pico's processor makes 150 million clock ticks per second, so one tick lasts about 6.7 nanoseconds. The audio frames in later chapters are 40 ms long, and \( 0.04 \times 150{,}000{,}000 = 6{,}000{,}000 \) ticks. Divide that by the 512 samples in a frame and you get about 11,700 ticks of work available for each sample before the next frame arrives. That is a big number, but MicroPython spends hundreds of ticks on a single line, which is why Chapter 10 teaches faster code.

### The RP2350 Microcontroller

The **RP2350** is the chip at the center of the Pico 2 W. A *microcontroller* is a computer on one chip: processor, memory, and input/output circuits together. The RP2350 adds two features that matter for this book. It has special programmable circuits called PIO blocks, which MicroPython's I2S audio uses to move sound in and out without help from your code. And its processor cores have instructions for fast math, which we use for the FFT.

### The Cortex-M33 Core and Dual Cores

A **core** is one processor inside the chip. The RP2350 has two **Arm Cortex-M33** cores, so it is a **dual core processor**. The Cortex-M33 is a 32-bit core that includes a hardware unit for decimal (floating-point) math and instructions for the multiply-and-add operations that signal processing uses constantly.

MicroPython normally runs your program on the first core only. The second core can run a separate task through the `_thread` module. This book keeps the work on one core, and Chapter 10 shows how to make that single core fast enough.

### SRAM

**SRAM** is the fast memory that holds your running program's variables. The RP2350 has 520 KB of it, shared by MicroPython itself and your data. It is the "RAM" you counted against in Chapter 2, where a 3-second recording took 150 KB. SRAM loses its contents when power is removed, while the 4 MB of flash keeps your files.

### The Wi-Fi Radio

The Pico 2 W's **Wi-Fi radio** is a separate wireless chip (the CYW43439) that sits next to the RP2350 and speaks 2.4 GHz Wi-Fi. Your MicroPython program controls it through the `network` module, which Chapter 13 uses to connect to the school network. Because the chip is separate, it uses a few of the Pico's pins for itself: GP23, GP24, GP25, and GP29. The onboard LED hangs off the wireless chip too, which is why you write `Pin("LED")`.

*Worked example.* A school offers two networks, "School-5G" on the 5 GHz band and "School-2G" on the 2.4 GHz band. The Pico can join only "School-2G", because its radio does not support 5 GHz. If your classroom network is 5 GHz only, the Pico will not see it, and you will need the school's IT team to provide a 2.4 GHz network.

| Wi-Fi fact | Detail |
|------------|--------|
| Band | 2.4 GHz only |
| Standard | 802.11n |
| Pins used by the radio chip | GP23, GP24, GP25, GP29 |
| Book chapters that use it | 13 (HTTP), 14 (streaming), 15 (MQTT) |

## Power: USB, Ground, and Noise

### USB Power

The Pico gets its power from its **micro-USB port**. A USB port supplies 5 volts, and the Pico has a voltage regulator that turns the 5 V into the 3.3 V the chip and its pins use. Two pins on the board give that power to your parts: **VBUS** passes the USB 5 V straight through, and **3V3** is the regulated 3.3 V output. A normal computer USB port provides up to about 500 mA, which is enough for this kit at the volumes used in the tests.

The rule for choosing between them is simple: use 3V3 for the display and the microphone, which are 3.3 V parts, and use VBUS or 3V3 for the amplifier. Connecting a 5 V wire to a pin that expects 3.3 V can damage it.

!!! mascot-warning "The Microphone Is a 3.3 Volt Part"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The INMP441's VDD pin goes to 3V3, never to VBUS. A 5 V wire is an easy mistake because the amplifier next to it is happy on 5 V. Before you power up, trace the microphone's red wire back to the 3V3 pin.

### Ground Wiring

**Ground** is the 0 V reference that every voltage in the circuit is measured against. For a signal to mean anything, the sender and the receiver must share the same ground. That is the whole idea of **ground wiring**: every part's GND pin connects back to a GND pin on the Pico. The Pico has eight GND pins spread around its edges, so you can always find one near the part you are wiring. On a breadboard you usually run one wire from a Pico GND pin to the long blue (or black) rail and then connect each part to that rail.

A missing or loose ground rarely gives a clean "no." It gives strange behavior: a screen that flickers, a microphone that hisses, or a speaker that crackles. When something misbehaves, check the grounds first.

### Power Supply Noise

**Power supply noise** is the small, fast fluctuation in the voltage that comes from the other parts sharing it. The amplifier is the main source: it draws sudden pulses of current when it plays loud sounds, and those pulses ripple through the shared power and ground wires. The microphone is the most sensitive listener, because it measures tiny changes. Three habits keep the noise down: use short wires, keep the microphone's wires away from the amplifier's, and give the microphone its power from 3V3.

## The Eyes: The Round Display

### The Round Color Display

The kit's **round color display** is a 2.1 inch screen with 360 by 360 pixels. A **pixel** is one dot of color, and 360 by 360 gives \( 360 \times 360 = 129{,}600 \) of them. The memory addresses are square, but the glass is circular, so only the circle inscribed in the square can be seen. The corners are hidden under the bezel.

*Worked example.* The visible circle has radius 180 pixels, so it shows \( \pi \times 180^2 \approx 101{,}788 \) pixels, about 78.5 percent of the square. Because the very edge is also covered by the bezel, the kit's `SAFE_RADIUS` is 168, and a ring at that radius is the largest circle you can see completely. That circle has about 88,668 pixels, 68.4 percent of the square. Drawing in the corners wastes time on pixels nobody can see.

| Display fact | Value |
|--------------|-------|
| Size | 2.1 inches, round |
| Resolution | 360 by 360 pixels (some listings wrongly say 640 by 640) |
| Controller chip | GC9B72 |
| Bus | SPI, using SPI block 0 |
| Pixel format | 16-bit color (RGB565, Chapter 5) |
| Safe drawing radius | 168 pixels from the center (180, 180) |

### The Display Controller

The display glass cannot work alone. Behind it is a **display controller**, a chip that holds the screen's own memory and lights each pixel. In this kit it is the GC9B72. Your Pico sends it *commands* and *pixel data* over SPI, and the controller keeps the picture on the screen until you send something new. The Pico does not store the picture.

The controller uses four control wires besides the data and clock.

| Pin | Name | Job |
|-----|------|-----|
| CS | Chip select | Pulled low while the Pico is talking to the display |
| DC | Data/command | Low means the byte is a command, high means it is data |
| RST | Reset | A brief low pulse restarts the controller |
| BL | Backlight | High turns the screen's light on |

*Worked example.* Here is what happens on the wires when you call `display.pixel(10, 20, config.RED)`. The driver sends the "set column" command and then the x range (10 to 10), the "set row" command and the y range (20 to 20), and the "write memory" command, and finally the two bytes of the red color. Every command byte is sent with DC low, and every data byte with DC high.

| Step | SPI bytes sent | DC level |
|------|----------------|----------|
| Set column command | 1 byte (0x2A) | low |
| Column range 10 to 10 | 4 bytes: 00 0A 00 0A | high |
| Set row command | 1 byte (0x2B) | low |
| Row range 20 to 20 | 4 bytes: 00 14 00 14 | high |
| Write memory command | 1 byte (0x2C) | low |
| The pixel (red, 0xF800) | 2 bytes: F8 00 | high |

That is 13 bytes of traffic to color a single pixel. Keep this number in mind: it is the reason Chapters 5 and 6 teach you to send whole rectangles of pixels at once.

!!! mascot-thinking "The Display Remembers"
    ![Sage thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The Pico does not keep a copy of the picture, because the controller does. That is why you can draw one small box and leave everything else alone, and it is also why a bad wire can leave the screen showing old pixels instead of an error.

## The Ears: The INMP441 Microphone

### The MEMS Microphone

A **MEMS microphone** is a microphone built like a computer chip. MEMS stands for micro-electro-mechanical system: a membrane thinner than a hair is etched into silicon, and sound pressure makes it move, which changes an electrical signal. It is small, cheap, and consistent from one unit to the next, which is why phones use it.

### The INMP441 Board

The **INMP441** is a MEMS microphone with the analog-to-digital converter inside the same package, so it sends finished numbers to the Pico. Its output is 24-bit audio on an I2S bus, and the kit asks for 12,800 samples each second. Its datasheet lists a response from about 60 Hz to 15 kHz, which easily covers the kit's 6,400 Hz limit from Chapter 3.

The board has six pins.

| Pin | Connects to | Job |
|-----|-------------|-----|
| SCK | GP10 | Serial clock from the Pico |
| WS | GP11 | Word select from the Pico |
| SD | GP12 | Serial data, microphone to Pico |
| L/R | GND | Picks the left channel (3V3 would pick right) |
| VDD | 3V3 | Power, a 3.3 V part |
| GND | GND | Ground |

*Worked example.* In a quiet room, test 06 reports a noise floor of about 12.5 bits. As a number, \( 2^{12.5} \approx 5{,}800 \). The largest 24-bit sample is \( 2^{23} = 8{,}388{,}608 \). The room noise is therefore about \( 20 \log_{10}(5800 / 8388608) \approx -63 \) dB below the loudest sound the microphone can report. Your own value will differ with the room, which is why the test calibrates instead of assuming.

!!! mascot-tip "Two Wires You Can Swap by Accident"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    The microphone's SCK and WS wires, and also SCK and SD, are easy to swap because the board's pin labels are tiny. A swapped microphone starts without any error and sends only zeros, so test 02 prints "flat line." Check in this order: SCK on GP10, WS on GP11, SD on GP12.

## The Voice: Amplifier and Speaker

### The Speaker

A **speaker** turns an electrical signal into sound. A coil of wire attached to a paper or plastic cone sits in a magnetic field. When the signal flows through the coil, the cone moves in and out and pushes the air, recreating the pressure wave from Chapter 3. Speakers are rated by *impedance* in ohms (small ones are usually 4 or 8 ohms; check the label on yours) and by the power they can handle.

*Worked example.* The power in a speaker is \( P = V^2 / R \). To deliver 1 watt into a 4 ohm speaker the voltage across it must be \( V = \sqrt{P \times R} = \sqrt{1 \times 4} = 2 \) volts. The Pico's pins can only supply a tiny current, so they cannot drive a speaker directly. That is the job of the amplifier.

### The Class-D Amplifier

A **class-D amplifier** makes sound with switches. Its output transistors are always either fully on or fully off, and they flip thousands of times each second, varying the width of each pulse to match the sound. Because a transistor that is fully on or off wastes almost no power, class-D amplifiers are very efficient and run cool. That matters in a small USB-powered device.

*Worked example.* Suppose the speaker needs 1 watt. A class-D amplifier that is 90 percent efficient draws about \( 1 / 0.9 \approx 1.11 \) watts from the supply and wastes about 0.11 W as heat. An older design that is only 50 percent efficient would draw 2 watts and waste a full watt, enough to warm a small board.

### The MAX98357A Amplifier

The **MAX98357A** combines a digital-to-analog converter and a class-D amplifier in one chip. It takes digital audio over I2S and drives the speaker directly, so there is no separate converter to wire and no resistor to choose. Its breakout board has these connections.

| Pin | Connects to | Job |
|-----|-------------|-----|
| BCLK | GP20 | Bit clock from the Pico |
| LRC | GP21 | Left/right (word select) clock from the Pico |
| DIN | GP19 | Audio data from the Pico |
| GAIN | GP18 | Sets loudness: the Pico can float it, pull it low, or push it high |
| VIN | VBUS (5 V) or 3V3 | Power |
| GND | GND | Ground |
| Output terminals | Speaker | The amplified sound |

The GAIN pin has three settings, chosen by what the pin is tied to. The kit's `set_gain()` function picks one in software, and the default is 9 dB.

| Pin state | Gain |
|-----------|------|
| Tied high (to the amplifier's VIN) | 6 dB (only if VIN is 3.3 V) |
| Left floating (the default) | 9 dB |
| Tied to GND | 12 dB |

!!! mascot-warning "BCLK and LRC Must Be Neighbors"
    ![Sage warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    MicroPython's I2S needs the left/right clock on the pin right after the bit clock. Here BCLK is GP20 and LRC is GP21. If you move one without the other, `I2S()` raises an error. The same rule holds for the microphone: SCK on GP10 and WS on GP11.

## The Hands: Push Buttons

### The Push Button

A **push button** (also called a tactile switch) is a switch that connects two wires only while you press it. The small square ones in the kit have four legs, but they are really two pairs. The two legs on one side are joined inside the button all the time, and pressing the button joins the two sides together.

That construction creates a common mistake. If you wire the button with both of its wires on the *same* side, the button is always connected and always reads "pressed." Place the button so that the two wires go to legs on opposite sides.

*Worked example.* To wire MODE, put one leg's wire on GP13 (physical pin 17) and the opposite side's wire on any GND. The kit's `config.init_buttons()` then sets GP13 as an input with a pull-up. The button reads 1 when released and 0 while pressed. Test 03 confirms it by printing each press and release.

### The Pull-Up Resistor

A **pull-up resistor** is a resistor that gently connects a pin to 3.3 V, so the pin has a definite value when nothing else is driving it. Without it, a button that is not pressed leaves the pin *floating*, which means it picks up stray signals and reads randomly. With the pull-up, the pin reads 1 until the button connects it to ground, and then reads 0. The Pico has pull-up resistors built in, which `Pin.PULL_UP` turns on, so the buttons need no extra parts.

#### Diagram: Pull-Up Button Circuit

<details markdown="1">
<summary>Pull-Up Button Circuit</summary>
Type: microsim
**sim-id:** pull-up-button-circuit<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Understand<br/>
**Bloom Verb:** infer<br/>
**Learning Objective:** The learner will infer the value a GPIO input pin reads for 6 button circuits, given the pin's pull setting, what the button's other leg connects to, and whether the button is pressed, with at least 5 of 6 correct.

**Prerequisites:** push button, pull-up resistor, floating pin, GPIO input (all defined in the sections above this block and in Chapter 2).

**Evidence of Mastery:** For each of the 6 circuits the learner commits to "reads 1", "reads 0", or "unpredictable" before the result is shown. A prediction is correct when it matches the Pin reads column in Content. Mastery is 5 of 6 on the first attempt. Pressing the button in the example circuit and watching the reading is exploration, not evidence.

**Misconceptions:** (1) A button always reads 1 when pressed. (2) A pin with nothing attached reads 0. (3) The pull-up is what makes the pin read 1 even while the button is pressed to ground.

**Instructional Rationale:** An Understand-level inference needs the learner to reason from a circuit's parts to a result. Predicting before the result is shown makes the learner apply the rule that a connected path wins over a pull.

**Content:**

The circuit shows a Pico input pin, an optional internal pull, and a button whose other leg connects to GND or to 3V3.

| # | Pin pull setting | Button's other leg connects to | Button | Pin reads | Why (shown as feedback) |
|---|---|---|---|---|---|
| 1 | Pull-up | GND | Released | 1 | Nothing pulls the pin down, so the pull-up holds it at 1. |
| 2 | Pull-up | GND | Pressed | 0 | The button connects the pin to GND, which beats the weak pull-up. |
| 3 | None (floating) | GND | Released | unpredictable | With no pull and no connection, the pin picks up stray signals. |
| 4 | Pull-up | 3V3 | Pressed | 1 | Both the pull-up and the button push the pin toward 3.3 V. |
| 5 | Pull-down | 3V3 | Pressed | 1 | The button connects the pin to 3V3, which beats the weak pull-down. |
| 6 | Pull-down | 3V3 | Released | 0 | Nothing pulls the pin up, so the pull-down holds it at 0. |

**Provenance:** The reasoning rule comes from the chapter section "The Pull-Up Resistor." The six circuits are illustrative, and the sim labels them "illustrative."

**Rules:** A connection from the pin to GND or 3V3 through a pressed button overrides the pin's internal pull (pull-up or pull-down). With a released button and a pull setting, the pin reads the pull's level (1 for pull-up, 0 for pull-down). With a released button and no pull, the pin reads an unpredictable value that the sim shows as alternating 0 and 1.

**Learner Activity:**

1. The learner explores a sample circuit (pull-up, GND, button released) and presses the button to watch the reading change from 1 to 0.
2. The learner starts the challenges. Circuit 1 is shown with the button state.
3. The learner picks "reads 1," "reads 0," or "unpredictable."
4. The sim shows the reading and the Why text, then moves to the next circuit.
5. After circuit 6, the sim shows the score. The learner should notice that circuit 4 is the wiring mistake that makes a button seem dead.

**Feedback:** 6 circuits, fixed order, one attempt each. Correct: "Correct: <Why>". Incorrect: "Not quite. The pin reads <answer>: <Why>". The answer is revealed right after each pick, and a running score "n of 6" is shown.

**Starting State:** The sample circuit is shown with the button released and the pin reading 1, with the question "What will the pin read when the button is pressed?"

**Chapter Anchors:** The chapter states that with a pull-up and the button to ground, a released button reads 1 and a pressed button reads 0, and that the kit uses the pull-up built into the Pico.
</details>

## Wiring It Up

### The Breadboard

A **breadboard** is a plastic board with rows of small holes. Metal strips under the holes connect them in groups, so you can join parts by pushing wires into the same group instead of soldering. In the middle area, each short row of five holes is connected, and a gap down the center separates the left half from the right. Along the long edges are power rails, which connect all the way along.

*Worked example.* Place the Pico so that it straddles the center gap, one row of its pins on each side. That leaves four free holes beside every pin, in the same connected group, so you can plug a wire right next to any pin. A wire in a hole beside GP13 is electrically connected to GP13.

| Breadboard area | How the holes connect |
|-----------------|-----------------------|
| Middle rows | Groups of five holes in a row are connected |
| Center gap | Separates the two halves, so they are not connected |
| Long edge rails | All holes in one rail are connected, from end to end |

### Dupont Wires

**Dupont wires** are the thin jumper cables with small plastic ends. Male ends have a pin that pushes into a breadboard hole, and female ends have a socket that slides over the pins on a module. You need male-to-male wires between breadboard holes and male-to-female wires from the breadboard to a module's header. The display wiring in `config.py` records the color of each wire, which makes tracing a mistake much easier: SCL orange, SDA yellow, RST green, DC blue, CS purple, BL gray, VCC red, and GND black.

### The Pin Assignment Table

A **pin assignment table** is a table that lists, for every part, which Pico pin each of its wires goes to. It is the one document you wire from and debug against. Everything in the kit's `config.py` comes from this table.

| Part | Part pin | Pico pin | Physical pin |
|------|----------|----------|--------------|
| Display | SCL | GP2 | 4 |
| Display | SDA | GP3 | 5 |
| Display | RST | GP4 | 6 |
| Display | DC | GP5 | 7 |
| Display | CS | GP6 | 9 |
| Display | BL | GP7 | 10 |
| Display | VCC, GND | 3V3, GND | 36, any GND |
| Microphone | SCK | GP10 | 14 |
| Microphone | WS | GP11 | 15 |
| Microphone | SD | GP12 | 16 |
| Microphone | L/R, GND | GND | any GND |
| Microphone | VDD | 3V3 | 36 |
| Button MODE | one leg | GP13 | 17 |
| Button UP | one leg | GP14 | 19 |
| Button DOWN | one leg | GP15 | 20 |
| Buttons | other legs | GND | any GND |
| Amplifier | DIN | GP19 | 25 |
| Amplifier | BCLK | GP20 | 26 |
| Amplifier | LRC | GP21 | 27 |
| Amplifier | GAIN | GP18 | 24 |
| Amplifier | VIN | VBUS or 3V3 | 40 or 36 |
| Amplifier | GND | GND | any GND |

Three rules hold the table together. First, each GP pin appears once, so no two wires share a pin. Second, the I2S pairs are neighbors: microphone SCK and WS on GP10 and GP11, amplifier BCLK and LRC on GP20 and GP21. Third, nothing connects to GP23, GP24, GP25, or GP29, which belong to the wireless chip.

The kit is built in stages, and each test checks exactly the parts wired so far. That makes any wiring error easy to localize.

| Test | Wire first | What to look for |
|------|-----------|------------------|
| 01 | Nothing (just the Pico) | The onboard LED blinks |
| 02 | Anything you have | No warnings for the parts you wired |
| 03 | The three buttons | Each press and release prints, then "PASS" |
| 04 | The display | "Hello World!" inside a cyan ring |
| 05 | Amplifier and speaker | A beep, a scale, three volumes |
| 06 | Microphone (with the display) | The meter moves when you talk |
| 07 | Everything together | Hold MODE, talk, hear it back |

!!! mascot-tip "Wire One Part, Then Test"
    ![Sage giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Do not wire all five parts and then run everything. Add one part, run its test from the table, and only then add the next. When a test fails, you know the problem is in the part you just added.

The last activity of the chapter puts the pin assignment table to work on six wiring listings that each contain one mistake.

#### Diagram: Kit Wiring Fault Finder

<details markdown="1">
<summary>Kit Wiring Fault Finder</summary>
Type: microsim
**sim-id:** kit-wiring-fault-finder<br/>
**Library:** p5.js<br/>
**Status:** Specified<br/>
**Bloom Level:** Analyze<br/>
**Bloom Verb:** examine<br/>
**Learning Objective:** The learner will examine 6 wiring listings against the pin assignment table and identify the one wrong connection in each, with at least 5 of 6 correct on the first attempt.

**Prerequisites:** pin assignment table, ground wiring, pull-up resistor, the I2S neighbor rule, the 3.3 V rule for the microphone (all defined in the sections above this block).

**Evidence of Mastery:** For each listing the learner selects the one line that does not match the pin assignment table. A selection is correct when it equals the Faulty line column in Content. Mastery is 5 of 6 on the first attempt. Reading the pin assignment table while answering is allowed, and is not scored.

**Misconceptions:** (1) A wiring mistake always produces an error message. (2) Any 5 V part can use the 5 V pin. (3) The two I2S pins can be assigned in either order.

**Instructional Rationale:** Analyze-level examination requires comparing a whole against a reference and locating the departure. A listing with exactly one fault trains the learner to check each line against the table, which is the same skill used when debugging a real kit.

**Content:**

Each listing shows the wires of one part as "part pin to Pico pin or rail." The reference is the table "The Pin Assignment Table" in this chapter.

| # | Part | Listing shown | Faulty line | Correct connection | What the learner would see (shown as feedback) |
|---|---|---|---|---|---|
| 1 | Microphone | SCK to GP10; WS to GP11; SD to GP12; L/R to GND; VDD to VBUS (5 V); GND to GND | VDD to VBUS (5 V) | VDD to 3V3 | The INMP441 is a 3.3 V part. A 5 V supply can damage it. |
| 2 | Microphone | SCK to GP10; WS to GP13; SD to GP12; L/R to GND; VDD to 3V3; GND to GND | WS to GP13 | WS to GP11 | I2S() raises "invalid ws (must be sck+1)", and GP13 is also the MODE button. |
| 3 | Amplifier | BCLK to GP20; LRC to GP22; DIN to GP19; GAIN to GP18; VIN to VBUS; GND to GND | LRC to GP22 | LRC to GP21 | I2S() raises an error because the left/right clock must be the pin right after the bit clock. |
| 4 | Button MODE | One leg to GP13; the leg on the opposite side to 3V3 | Opposite leg to 3V3 | Opposite leg to GND | With a pull-up, the pin always reads 1, so test 03 never reports a press. |
| 5 | Display | SCL to GP2; SDA to GP3; RST to GP4; DC to GP5; CS to GP6; BL not connected; VCC to 3V3; GND to GND | BL not connected | BL to GP7 | The screen stays dark in test 04 because the backlight never turns on. |
| 6 | Amplifier | BCLK to GP20; LRC to GP21; DIN to GP19; GAIN to GP18; VIN to VBUS; GND not connected | GND not connected | GND to GND | Test 05 is silent because the amplifier has no ground return. |

**Provenance:** The listings and symptoms come from the kit README and the headers of tests 03, 04, and 05 in `src/kits/study-buddy-base/`, and from the table "The Pin Assignment Table" in this chapter.

**Rules:** Each listing has exactly one faulty line. A selection is correct only if it is the faulty line. The reference table is always available to the learner.

**Learner Activity:**

1. The learner reads listing 1 and selects the line that does not match the pin assignment table.
2. The sim shows whether it was correct, the correct connection, and the symptom text.
3. The learner continues through listing 6.
4. After listing 6, the sim shows the score. The learner should notice that only some mistakes produce an error message.

**Feedback:** 6 listings, fixed order, one attempt each. Correct: "Correct: <symptom text>". Incorrect: "Not quite. The faulty line is <faulty line>: <symptom text>". The correct line is revealed right after each selection, and a running score "n of 6" is shown.

**Starting State:** Listing 1 is shown with the pin assignment table beside it and the question "Which line does not match the table?"

**Chapter Anchors:** The chapter states the microphone pins SCK GP10, WS GP11, SD GP12, the amplifier pins BCLK GP20, LRC GP21, DIN GP19, GAIN GP18, the display backlight on GP7, and the MODE button on GP13.
</details>

## Putting It All Together

You now have the five parts, the rules that connect them, and a table to check every wire against. The Pico is the brain and the Wi-Fi link. The round display and its controller are the eyes. The INMP441 and its built-in converter are the ears. The MAX98357A and a speaker are the voice. Three buttons wired to ground with built-in pull-ups are the hands.

Key takeaways:

- The kit has five parts: the Pico 2 W, the round display, the INMP441 microphone, the MAX98357A amplifier with a speaker, and three push buttons.
- The RP2350 chip has two Cortex-M33 cores, 520 KB of SRAM, and a 2.4 GHz Wi-Fi radio chip that takes pins GP23, GP24, GP25, and GP29.
- The display controller keeps the picture; the Pico sends commands and pixels over SPI, using DC to tell them apart.
- Both the microphone and the amplifier use I2S, and each needs its word-select pin right after its clock pin.
- The microphone is a 3.3 V part; the amplifier can use 5 V.
- A push button wired to ground with a pull-up reads 0 when pressed.
- Every part shares one ground, and wiring one part at a time with its test finds mistakes quickly.

Test yourself with these two questions, and click each one to reveal its answer.

??? question "Your microphone starts without errors, but test 02 reports a flat line. What do you check first? Click to expand"
    The SCK, WS, and SD wires: SCK on GP10, WS on GP11, SD on GP12. A swapped microphone sends only zeros without any error. Then check that VDD is on 3V3 and that GND and L/R are both on ground.

??? question "Why does coloring one pixel take 13 bytes of SPI traffic? Click to expand"
    The driver must tell the controller which column and row to write (two commands with four bytes of range each), send the write-memory command, and then send the two bytes of the color. The overhead is far larger than the pixel, so Chapters 5 and 6 send whole rectangles at once.

!!! mascot-celebration "Kit Wired and Understood"
    ![Sage celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You just learned what each of the five parts does, how they share power and ground, and how to check every wire against the pin assignment table. With a wired kit and passing tests 01 to 07, you are ready to put pictures on that round screen.

In Chapter 5 we start with the display, and find out why drawing a whole frame is so slow.
