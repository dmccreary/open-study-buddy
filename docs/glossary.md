---
title: Glossary of Terms
description: ISO 11179-style definitions of the concepts used in Open Study Buddy.
---

# Glossary of Terms

#### Agent Approval Rules

Settings that require a person to confirm certain actions before the agent performs them.

**Example:** The agent asks for confirmation before enabling always-on listening.

#### Agent Configuration File

A file containing the settings that define an agent's behavior.

**Example:** It lists the calendar source and allowed tools.

#### Agent Data Flow

The path that information takes from a spoken question through the device to the agent and back to the speaker and display.

**Example:** Microphone, Pico, Wi-Fi, buddy server, reply text, speaker output.

#### Agent Memory

Information an agent keeps between requests so it can use earlier facts or preferences.

**Example:** The agent remembers a student's preferred reminder time.

#### Agent Permissions

The limits on what an agent is allowed to access or do.

**Example:** The agent may read the calendar but not send email.

#### Agent Progression Levels

The staged path from a simple rule-based server, to one using speech services and a language model, to an optional self-hosted open-source agent.

**Example:** Level 1 matches keywords; level 2 adds one LLM call.

#### Agent Terminal

The small device that gives an agent a face, voice, ears, and buttons while the agent's thinking happens elsewhere.

**Example:** The Pico acts as an agent terminal by sending recorded speech out and showing the reply.

#### Agent Tools

Functions an agent can call to get information or take action, such as looking up a calendar.

**Example:** An "upcoming events" tool returns the next three calendar entries.

#### Alert Message Format

The agreed structure of an alert sent over MQTT.

**Example:** JSON with a title, date, and category.

#### Aliasing

False low frequencies that appear when a signal contains frequencies above the Nyquist limit.

**Example:** A 10,000 Hz tone sampled at 16,000 Hz appears as 6,000 Hz.

#### Always-On Approval Process

The steps needed to approve continuous listening.

**Example:** Request, review, written approval, then enable.

#### Always-On Device

A device that stays powered and ready so it can respond at any moment.

**Example:** A desk buddy plugged into USB power waits for a button press all day.

#### Always-On Listening

A mode in which the microphone constantly monitors for the wake word.

**Example:** Always-on listening requires explicit approval from a parent or school.

Contrast with: Push-to-Talk

#### Amplifier Shutdown Pin

A pin that turns the amplifier output on or off.

**Example:** The program pulls the pin low to silence the speaker.

#### Amplitude

The size of a wave's swing, which relates to loudness.

**Example:** A louder tone has greater amplitude.

#### Analog to Digital Conversion

Turning a continuous electrical signal into numbers.

**Example:** The microphone chip performs the conversion before sending data to the Pico.

#### Animation

A sequence of changing images that creates an impression of motion.

**Example:** Spectrum bars rise and fall with the sound.

#### Array Passed By Address

Giving a function the memory location of an array so no copy is made.

**Example:** Assembly code receives the address of the audio buffer.

#### Assembly FFT

An FFT whose inner loop is written in assembly for speed.

**Example:** The assembly FFT fits inside the frame time budget.

#### Audio Buffer

A block of memory that holds a group of audio samples.

**Example:** A 1,024-sample buffer is processed each frame.

#### Audio Chunk Size

The number of bytes sent in each piece of an upload.

**Example:** A 4,096-byte chunk size balances memory use and speed.

#### Audio Clipping

Distortion that occurs when a signal exceeds the largest value that can be represented.

**Example:** A very loud sound flattens at the maximum sample value.

#### Audio Frame

A group of consecutive samples processed together.

**Example:** A 512-sample frame at 16,000 Hz lasts 32 ms.

#### Audio Not Stored

A design in which audio is discarded after use.

**Example:** Only the text reply is kept.

#### Authentication Token

A secret string that proves a device is allowed to use a service.

**Example:** The device sends its token in a request header.

#### Avoiding Allocation

Writing code that creates no new objects inside time-critical loops.

**Example:** Reusing one buffer prevents garbage collection pauses.

#### Backlight Control

Adjusting the brightness of the light behind the display.

**Example:** The device dims the backlight at night.

#### Band Energy

The total strength within a range of frequencies.

**Example:** The bass band sums bins from 0 to 250 Hz.

#### Barge-In Interruption

A user interrupting the device while it is speaking.

**Example:** Pressing Mode stops the spoken reply.

#### Benchmarking

Measuring performance under controlled, repeatable conditions.

**Example:** Run each FFT version 100 times and compare averages.

#### Bin Width

The frequency range covered by one bin, equal to the sample rate divided by the FFT size.

**Example:** 16,000 Hz divided by 512 gives 31.25 Hz.

#### Bit Clock

The I2S signal that marks when each data bit is valid.

**Example:** The bit clock ticks once per transmitted bit.

#### Bit Depth

The number of bits used to store each sample.

**Example:** 16-bit samples have 65,536 possible values.

#### Bit-Reversal Table

A lookup table that reorders samples for the FFT.

**Example:** Index 1 in a 8-point FFT maps to index 4.

#### Boot and Main Scripts

The two files MicroPython runs at startup: `boot.py` first for setup, then `main.py` for the program.

**Example:** `main.py` starts the device loop after power-up.

#### Breadboard

A reusable board with connected holes for building circuits without soldering.

**Example:** The display and microphone wires plug into a breadboard.

#### Broker Exposure Risk

The danger of making an MQTT broker reachable from the public internet.

**Example:** An open broker lets strangers send alerts.

#### Broker on Raspberry Pi

Running the MQTT broker software on a Raspberry Pi.

**Example:** A Pi in the library hosts Mosquitto.

#### Buddy Server

A program on the school network that receives requests from the device and returns replies, optionally using speech services or a language model.

**Example:** A 100-line buddy server answers "What is due?" from a JSON file.

#### Button Debouncing

Filtering out the rapid false presses that occur as a switch settles.

**Example:** The code ignores changes for 20 ms after an edge.

#### Button Interrupt

An interrupt triggered by a button pin change.

**Example:** A button interrupt records a press even while the display is drawing.

#### Byte Arrays

Mutable sequences of bytes that hold raw data such as audio samples.

**Example:** `bytearray(1024)` creates a 1,024-byte audio buffer.

#### Calendar Polling

Checking a calendar source at regular intervals.

**Example:** The server fetches the ICS feed every 15 minutes.

#### Calibration Config Value

A stored setting produced by calibration.

**Example:** `NOISE_FLOOR = 120` in the config file.

#### Capstone Project

A final project that combines the skills from the course.

**Example:** A homework-reminder buddy for a class.

#### Certificate Handling

Checking or storing the digital certificate that proves a server's identity.

**Example:** The device verifies the server certificate before sending data.

#### Chatbot Versus Agent

A comparison between software that only answers one message at a time and software that plans and performs several steps toward a goal.

**Example:** A chatbot explains what a calendar is; an agent reads your calendar and tells you what is due.

#### check_msg Polling

Calling `check_msg` to process incoming MQTT messages without blocking.

**Example:** The audio loop calls check_msg once per frame.

#### Chunked Audio Upload

Sending audio to a server in small pieces instead of one large block.

**Example:** The Pico sends 4 KB chunks to stay within memory limits.

#### Clap Detector

A program that detects a sudden loud sound pattern.

**Example:** A clap toggles the display light.

#### Class-D Amplifier

An efficient amplifier that switches its output on and off rapidly to reproduce sound.

**Example:** The MAX98357A is a Class-D amplifier, so it stays cool at low volume.

#### Classroom Noise Monitor

A device feature that measures and displays room loudness.

**Example:** The screen turns red when the room is too loud.

#### Clipping Detection

Checking whether samples reach the maximum possible value.

**Example:** A warning appears when many samples are clipped.

#### Clock Face Geometry

The math for placing marks and hands on a circular clock.

**Example:** Twelve tick marks are spaced 30 degrees apart.

#### Cloud Agent

An agent that runs on a vendor's remote computers and is usually reached over the internet for a recurring fee.

**Example:** A subscription assistant that stores your messages on the vendor's servers is a cloud agent.

Contrast with: Self-Hosted Agent

#### Color Themes

Named sets of colors applied consistently across the interface.

**Example:** A school theme uses its team colors for the background and digits.

#### Config File Pattern

A practice of keeping settings such as Wi-Fi names and server addresses in a separate file instead of in program logic.

**Example:** A `config.py` file holds the server address.

#### Consent

Permission freely given by a person to collect or use their data.

**Example:** A parent signs a form before always-on listening.

#### Cortex-M33 Core

The ARM processor design used in the RP2350 that includes instructions helpful for signal processing.

**Example:** Assembly code uses Cortex-M33 instructions to speed up the FFT.

#### Course Information

Details about classes that the agent can report.

**Example:** The next class meets in room 204.

#### Custom Wake Phrase

A wake phrase chosen by a school or student.

**Example:** "Hey Griffin" replaces "Hey Pico."

#### Cycle Counter

A hardware register that counts processor clock cycles.

**Example:** Reading it before and after code reveals how many cycles were used.

#### Daily Briefing

A morning summary of the day's events.

**Example:** "Today you have one test and one project due."

#### Data Minimization

Collecting only the data needed for a task.

**Example:** Send only the recorded question, not continuous audio.

#### Data Retention

How long collected data is kept.

**Example:** Transcripts are deleted after one day.

#### DC Offset Removal

Subtracting the average value from a signal so it centers on zero.

**Example:** Removing the offset prevents a false strong low-frequency bin.

#### Decibels

A logarithmic unit for comparing signal strengths.

**Example:** Doubling amplitude adds about 6 dB.

#### Detection Threshold

The score above which the detector reports the wake word.

**Example:** A threshold of 0.8 requires a close match.

#### Detector Math Test

A test that runs the scoring calculation on known numbers.

**Example:** Identical vectors must score near 1.

#### Detector Self-Test

A built-in check that confirms the wake-word code works.

**Example:** The device plays a stored sample and expects a detection.

#### Device Modes

The distinct behaviors the device can be in, such as clock, listening, thinking, speaking, and settings.

**Example:** In listening mode the display shows a live spectrum.

#### Device Status Topic

A topic where a device reports its condition.

**Example:** `school/room12/pico1/status` carries online or offline.

#### Diagnosing Blank Display

Finding why the screen shows nothing.

**Example:** Check power, SPI wiring, and backlight pin.

#### Diagnosing Distorted Audio

Finding why sound is crackly or harsh.

**Example:** Look for clipping or buffer underruns.

#### Diagnosing Silent Microphone

Finding why the microphone produces no sound.

**Example:** Check the left-right select wire and I2S pins.

#### Direct Region Write

Sending pixels only for a chosen rectangle of the screen instead of the whole frame.

**Example:** Redrawing just the clock digits after a minute change.

#### Dirty Region

The part of the screen that has changed and needs redrawing.

**Example:** A spectrum bar that grew is marked as a dirty region.

#### Discrete Fourier Transform

The Fourier transform applied to a finite list of samples.

**Example:** A DFT of 512 samples gives frequency values for 512 bins.

#### Display Controller

The chip inside a screen module that receives commands and pixel data and drives the panel.

**Example:** The controller accepts a window command followed by pixel data.

#### Display Refresh Rate

How many times per second the screen image is updated.

**Example:** A spectrum display aims for a smooth number of updates per second.

#### Dot Product Score

A sum of products of matching values that measures similarity.

**Example:** The detector multiplies feature and template values and adds them.

#### Down Button

The button that lowers a value or moves down in a menu.

**Example:** Down lowers the speaker volume.

#### Drawing Window

The rectangle on the display that incoming pixel data fills.

**Example:** The code sets a window, then streams the pixels for that area.

#### Dual Core Processor

A processor with two cores that can run separate tasks at the same time.

**Example:** One core handles audio while the other updates the display.

#### Dual Core Use

Assigning different tasks to the two processor cores.

**Example:** Core 1 computes the FFT while core 0 handles the network.

#### Dupont Wires

Plug-in jumper wires with connector ends used to link parts on a breadboard.

**Example:** Dupont wires link the microphone's pins to the Pico.

#### DWT Timer

The Cortex-M debug counter that supplies a cycle count.

**Example:** The DWT timer measures an FFT in cycles.

#### Edge Device

A small computer that works at the place where data is collected, such as a classroom desk, rather than in a data center.

**Example:** The Pico captures microphone audio at the edge before sending it onward.

#### Event Categories

Groups that classify events by kind.

**Example:** Categories include test, due, and general.

#### Event Loop

A main loop that repeatedly checks for events and handles them.

**Example:** The loop checks buttons, audio, and network messages in turn.

#### Event Parsing

Reading event text and extracting its date, title, and category.

**Example:** The server turns an ICS entry into a structured event.

#### Events JSON File

A hand-edited file that lists events in JSON.

**Example:** A teacher adds a TEST entry to the file.

#### Exceptions

Error objects raised when a program cannot continue normally, which can be caught and handled.

**Example:** A failed Wi-Fi connection raises an exception that the code catches and retries.

#### Falling Edge Detection

Noticing the moment an input changes from high to low.

**Example:** A falling edge marks the instant a pulled-up button is pressed.

#### False Accept

A detection reported when the wake word was not spoken.

**Example:** A cough triggers the device.

#### False Reject

A missed detection when the wake word was spoken.

**Example:** "Hey Pico" said quickly is ignored.

#### Feature Extraction

Converting raw audio into a smaller set of numbers that describe it.

**Example:** Band energies from each frame form the feature vector.

#### FFT

A fast algorithm for computing the discrete Fourier transform.

**Example:** The FFT turns each audio frame into a spectrum in real time.

#### FFT Size

The number of samples fed to one FFT.

**Example:** An FFT size of 512 uses 512 samples.

#### Fixed-Point Math

Using integers with an implied decimal point to represent fractions.

**Example:** A value of 1.5 is stored as 384 with 8 fractional bits.

#### Flash File System

The storage area in a board's flash memory that holds program and data files.

**Example:** Scripts and images are saved in the Pico's flash file system.

#### Floating Point Cost

The extra time that decimal-number math takes compared with integer math.

**Example:** Floating point FFT arithmetic is slower than fixed-point.

#### Fonts

Sets of character shapes used when drawing text.

**Example:** A larger font makes the time readable from across a desk.

#### Fourier Transform

A mathematical method that converts a signal from time domain to frequency domain.

**Example:** It reveals that a signal is mostly a 440 Hz tone.

#### Frame Buffer

A block of memory holding the color of every pixel for one screen image.

**Example:** A full RGB565 frame buffer for this display is about 259 KB.

#### Frame Overrun

A frame whose processing takes longer than its time budget.

**Example:** An overrun causes the next audio frame to be missed.

#### Frame Overrun Counter

A count of how many frames took longer than their budget.

**Example:** A rising counter shows the code is too slow.

#### Frame Size Calculation

The arithmetic that multiplies width, height, and bytes per pixel to find the memory a frame needs.

**Example:** 360 × 360 × 2 bytes equals 259,200 bytes.

#### Frame Time Budget

The time available to finish processing one audio frame before the next arrives.

**Example:** A 32 ms frame leaves 32 ms for the FFT and drawing.

#### Frequency

How many times per second a repeating wave completes a cycle, measured in hertz.

**Example:** Middle A has a frequency of 440 Hz.

#### Frequency Bin

One slot of an FFT result that represents a narrow range of frequencies.

**Example:** Bin 10 represents frequencies near ten bin-widths.

#### Frequency Domain

A view of a signal as the strength of each frequency it contains.

**Example:** A spectrum plot shows the frequency domain.

#### Full-Frame Update

Redrawing every pixel of the screen for each change.

**Example:** Sending 259 KB to change one digit is a full-frame update.

Contrast with: Direct Region Write

#### Garbage Collection

Automatic cleanup in which the runtime frees memory that a program no longer uses.

**Example:** A garbage collection pause can cause a brief audio glitch.

#### Google Calendar API

A web interface for reading Google Calendar data.

**Example:** The server uses it to read class events.

#### GPIO Pin

A general-purpose connection on a microcontroller that a program can set as an input or output.

**Example:** GPIO 15 is configured as an input for a button.

#### Ground Wiring

The shared return connections that give all parts the same zero-volt reference.

**Example:** Every module's ground pin connects to a Pico ground pin.

#### Hand Drawing

Drawing a clock hand as a line from the center to a computed endpoint.

**Example:** The minute hand is redrawn when the minute changes.

#### Hann Window

A bell-shaped window function that tapers smoothly to zero at both ends.

**Example:** Each frame is multiplied by a Hann window.

#### Hardware Mute Switch

A physical switch that cuts the microphone off.

**Example:** Sliding the switch ensures no audio is captured.

#### Heap Fragmentation

A condition in which free memory is split into pieces too small to satisfy a large request.

**Example:** A program fails to allocate a 4 KB buffer even though total free memory is larger.

#### Hey Pico Phrase

The default wake phrase for the device.

**Example:** Saying "Hey Pico" triggers a confirmation beep.

#### Home Assistant

An open-source home-automation platform that can use MQTT.

**Example:** Home Assistant shows device status on a dashboard.

#### Home Automation

Using networked devices to control or monitor a building.

**Example:** A message turns on a light when a test is tomorrow.

#### Homework Reminder Buddy

A buddy that announces homework due dates for a class.

**Example:** It says "Math worksheet due tomorrow."

#### HTTP POST

An HTTP request that sends data to a server.

**Example:** The device POSTs a JSON question.

#### HTTP Protocol

The rules web clients and servers use to exchange requests and responses.

**Example:** The Pico sends an HTTP request to the buddy server.

#### HTTPS

HTTP carried over TLS encryption.

**Example:** `https://` addresses use TLS.

#### I2S Bus

A three-wire serial connection designed for digital audio.

**Example:** The microphone and amplifier both connect over I2S.

#### I2S Receive

Reading audio data in from an I2S device.

**Example:** The Pico receives microphone samples.

#### I2S Transmit

Sending audio data out to an I2S device.

**Example:** The Pico transmits tone samples to the amplifier.

#### iCalendar Format

A standard text format for calendar events.

**Example:** An `.ics` file uses the iCalendar format.

#### Icons

Small pictures that represent a status or action.

**Example:** A speaker icon shows when the device is talking.

#### ICS Feed

A web address that supplies calendar events in iCalendar format.

**Example:** The server downloads the school's ICS feed.

#### Image Loading

Reading an image file from storage and preparing its pixels for the display.

**Example:** The mascot image is loaded from flash at startup.

#### In-Place Transform

An algorithm that overwrites its input with its output instead of using a second array.

**Example:** The FFT reuses the same buffer to save memory.

#### Inline Assembly

Processor instructions written directly inside a MicroPython function.

**Example:** An assembly loop multiplies and adds samples.

#### INMP441 Microphone

A digital microphone module that sends audio to a microcontroller over the I2S bus.

**Example:** The INMP441 supplies the audio used for the FFT and wake-word detection.

#### Interrupt

A hardware signal that pauses the main program so a short handler can respond to an event immediately.

**Example:** A button press triggers an interrupt without the main loop polling.

See also: Interrupt Service Routine

#### Interrupt Service Routine

The short function that runs when an interrupt occurs.

**Example:** An ISR sets a flag that the main loop checks later.

#### IP Address

A number that identifies a device on a network.

**Example:** The buddy server is at 192.168.1.50.

#### JSON

A text format for structured data using keys and values.

**Example:** `{"text": "What is due?"}`

#### Keep-Alive

A periodic signal that tells the broker a client is still connected.

**Example:** A 60-second keep-alive interval.

#### Kit Bill of Materials

The list of every part needed to build the device, with quantities.

**Example:** The kit list includes one Pico 2 W, one display, one microphone, and three buttons.

#### Language and Tone

The words and manner the agent uses with students.

**Example:** Short, friendly sentences.

#### Last Will

A message the broker publishes if a client disconnects unexpectedly.

**Example:** A device's last will reports it offline.

#### Left-Right Channel

The two sides of a stereo signal, selected by word select.

**Example:** The microphone is set to send on the left channel.

#### Level Gate

A rule that passes audio only when its level exceeds a threshold.

**Example:** Recording starts when the level gate opens.

#### Listening Indicator

A visible signal that the microphone is active.

**Example:** A red ring appears on the display.

#### LLM-Backed Agent

An agent that sends the user's request to a large language model to compose its reply.

**Example:** The server forwards a transcript and calendar summary to an LLM and speaks the result.

#### Local Network

A network that connects devices in one place, such as a classroom.

**Example:** The Pico and server share a local network.

#### Local Versus Cloud Processing

A comparison of handling data on nearby equipment versus remote servers.

**Example:** Wake-word matching is local; transcription may be remote.

#### Log Magnitude

Magnitude converted to a logarithmic scale.

**Example:** Log magnitude makes quiet and loud frequencies both visible.

#### Log-Spaced Bands

Frequency bands whose widths grow with frequency to match hearing.

**Example:** Each band spans a doubling of frequency.

#### Logging

Recording messages about what a program does.

**Example:** The device logs each Wi-Fi retry.

#### Long Press

A button hold longer than a set time that triggers a different action.

**Example:** Holding Mode for two seconds opens settings.

#### machine Library

The MicroPython module that gives programs access to hardware such as pins, timers, and buses.

**Example:** `from machine import Pin` controls a GPIO pin.

#### machine.I2S Class

The MicroPython class that sends and receives I2S audio.

**Example:** Create an I2S object to read from the microphone.

#### Magnitude Spectrum

A list of how strong each frequency bin is.

**Example:** Bars on the display show the magnitude spectrum.

#### MAX98357A Amplifier

An I2S digital audio amplifier module that drives a small speaker.

**Example:** The Pico sends audio samples to the MAX98357A, which powers the speaker.

#### mDNS Discovery

Finding devices by name on a local network without a central server.

**Example:** The device finds `buddy.local`.

#### Mean Subtraction

Subtracting the average from a set of values so they center on zero.

**Example:** Removing the mean prevents loudness alone from raising the score.

#### Memory Limits

The small amount of RAM and flash on a microcontroller that restricts what a program can store.

**Example:** A 259 KB frame buffer does not fit comfortably in the Pico's RAM alongside other data.

#### memoryview

An object that gives a window into existing memory without copying it.

**Example:** A memoryview lets code write into part of a buffer in place.

#### MEMS Microphone

A microphone built from a microscopic mechanical structure on a silicon chip.

**Example:** The INMP441 is a MEMS microphone.

#### Menu Navigation

Moving through a list of choices using the buttons.

**Example:** Up and Down move the highlight, and Mode selects.

#### MFCC Features

Audio features based on a perceptual frequency scale, commonly used in speech recognition.

**Example:** A trained model might take MFCC features as input.

#### Mic Distance Effect

The change in recorded level as the speaker moves nearer or farther from the microphone.

**Example:** Speech from across the room is much quieter than speech at 20 cm.

#### Microphone Calibration

Measuring the room and speaker levels to set thresholds.

**Example:** Calibration records five seconds of silence and a spoken sentence.

#### MicroPython Review

A short refresher of the MicroPython skills the course assumes before building the device.

**Example:** Flash the Pico, open the REPL, and blink an LED.

#### mip Package Manager

MicroPython's tool for downloading and installing libraries onto a board.

**Example:** Installing the umqtt library with mip.

#### Mode Button

The button that switches the device between modes or confirms a choice.

**Example:** Pressing Mode moves from the clock to listening.

#### Modules and Imports

Python files that hold reusable code, and the `import` statement that loads them into a program.

**Example:** `import time` makes the sleep function available.

#### Mono and Stereo

One audio channel versus two channels, left and right.

**Example:** The kit's microphone records in mono.

#### Mosquitto

An open-source MQTT broker.

**Example:** Mosquitto runs on a school Raspberry Pi.

#### mpremote

A command-line tool for copying files to, and running code on, a MicroPython board.

**Example:** `mpremote cp main.py :` copies a script to the Pico.

#### MQTT Authentication

Using a username and password to control access to the broker.

**Example:** The broker rejects clients without credentials.

#### MQTT Broker

The server that receives published messages and delivers them to subscribers.

**Example:** Mosquitto is the broker for the school.

#### MQTT Protocol

A lightweight publish/subscribe messaging protocol for small devices.

**Example:** A school publishes alerts that many devices receive.

#### Mute and Resume

Pausing audio output or input and later restarting it.

**Example:** The microphone is muted while the speaker talks.

#### Network Failure Handling

Code that responds safely when a connection fails.

**Example:** The device shows "Offline" instead of freezing.

#### Network Station Mode

A Wi-Fi mode in which the device joins an existing network as a client.

**Example:** `network.WLAN(network.STA_IF)` selects station mode.

#### Noise Floor

The level of background sound present when nobody is speaking.

**Example:** A quiet room might have a low noise floor RMS value.

#### Non-Blocking Code

Code that never waits long for one task, so other tasks keep running.

**Example:** Checking for an MQTT message without pausing the audio loop.

#### Nyquist Limit

Half the sample rate, which is the highest frequency a sampled signal can represent correctly.

**Example:** At 16,000 Hz sampling, the Nyquist limit is 8,000 Hz.

#### OAuth

A standard that lets a program access an account without handling its password.

**Example:** The server obtains permission to read a calendar through OAuth.

#### Offline Fallback

Behavior that keeps the device useful when the network is unavailable.

**Example:** The clock keeps working without Wi-Fi.

#### Open Hardware

Physical designs whose specifications are published so anyone can study, build, and modify them.

**Example:** The kit uses common parts that any student can buy and wire without special licenses.

#### Open Source Software

Software whose source code is published under a license that lets people read, change, and share it.

**Example:** Mosquitto and MicroPython are open source programs used in this book.

#### Open Study Buddy Device

The desk companion built in this course from a Pico 2 W, round display, microphone, speaker amplifier, and three buttons that listens, shows, and speaks.

**Example:** Pressing Mode on the device starts a question that appears as text on the round display.

#### Open-Source Agent Framework

A publicly available software toolkit for building agents that use tools, memory, and approval rules.

**Example:** A school installs a framework on its own server and points the device at it.

#### Parent and School Approval

The permission required from guardians and the school before enabling listening.

**Example:** Always-on mode stays off until both approve.

#### Peak Frequency Detection

Finding the frequency bin with the greatest magnitude.

**Example:** A tuner reports the peak frequency of a whistle.

#### Per-School Customization

Adjusting the device and agent for a particular school.

**Example:** Each school sets its own mascot and calendar.

#### Performance Trade-Offs

Choices in which gaining speed costs something else, such as readability or accuracy.

**Example:** Assembly is faster but harder to maintain.

#### Personal Agent

Software that carries out multi-step tasks on one person's behalf, such as checking calendars, summarizing information, and returning when it needs a decision.

**Example:** A personal agent notices a test on Friday and reminds you on Thursday evening.

See also: Chatbot Versus Agent

#### Pin Assignment Table

A table that lists which Pico pin connects to each part signal.

**Example:** The table shows that the speaker amplifier uses specific I2S pins.

#### Pixel

The smallest individually colored dot on a display.

**Example:** The round display has 129,600 pixels.

#### Plain HTTP LAN Use

Using unencrypted HTTP only on a trusted classroom network.

**Example:** A lab with no outside access may use plain HTTP.

#### Polar to Cartesian

Converting an angle and distance from a center into x and y coordinates.

**Example:** A clock hand's tip is found from its angle and length.

#### Power Supply Noise

Unwanted electrical variation on a power line that can leak into audio.

**Example:** Display activity can add a faint hum to the speaker output.

#### Pre-Allocated Buffers

Memory reserved once at startup and reused.

**Example:** The FFT buffer is created before the main loop.

#### Privacy

A person's control over how information about them is collected and used.

**Example:** Students decide whether audio may leave the room.

#### Privacy and Consent Plan

A document describing how a device protects privacy and gets permission.

**Example:** A teacher reviews the plan before the device is deployed.

#### Probe Programs

Small programs that test one part of the hardware.

**Example:** A probe prints microphone levels.

#### Profiling

Measuring where a program spends its time or memory.

**Example:** Profiling shows that drawing takes more time than the FFT.

#### Project Due Date

The date a project must be handed in.

**Example:** `DUE: History poster` marks a due date.

#### Prompt Injection

Hidden instructions in text that trick an agent into unwanted actions.

**Example:** A calendar title says "ignore your rules."

#### Publish-Subscribe Pattern

A messaging style in which senders publish to topics and receivers subscribe to the topics they want.

**Example:** All classroom devices subscribe to one alert topic.

#### Publisher

An MQTT client that sends messages to a topic.

**Example:** The school server is the publisher of alerts.

#### Pull-Up Resistor

A resistor that holds an input at a high voltage until a switch pulls it low.

**Example:** An internal pull-up keeps a button pin high when unpressed.

#### Pure Python FFT

An FFT written only in ordinary Python code.

**Example:** It is easy to read but too slow for the frame budget.

#### Push Button

A switch that connects a circuit only while it is pressed.

**Example:** The Mode button is a push button wired to a GPIO pin.

#### Push-to-Talk

A mode in which the device listens only while a button is held or after it is pressed.

**Example:** Hold Mode to ask a question.

#### QoS Levels

MQTT settings that control how reliably a message is delivered.

**Example:** QoS 1 delivers at least once.

#### Raspberry Pi Pico 2 W

A low-cost microcontroller board with the RP2350 chip and a Wi-Fi radio.

**Example:** The Pico 2 W is the brain of the Open Study Buddy device.

#### Real-Time Constraint

A requirement that work finish within a fixed time.

**Example:** Audio must be processed as fast as it arrives.

#### Real-Valued Input

Input made of ordinary numbers, with no imaginary part, as audio samples are.

**Example:** Microphone samples are real-valued input to the FFT.

#### Recording an Utterance

Capturing the audio of one spoken request.

**Example:** The device records until the button is released.

#### Region Layout

A screen design divided into areas that update independently.

**Example:** Separate regions hold time, mascot, spectrum, message, and status.

#### Reminder

A notification sent before an event.

**Example:** The device reminds you the night before a test.

#### REPL

An interactive prompt that reads one Python statement, runs it, and prints the result.

**Example:** Typing `1 + 1` at the REPL prints `2`.

#### Request-Reply Contract

The small, fixed message format that the device and server agree on, so either side can be replaced without changing the other.

**Example:** The device sends JSON with a text field and expects JSON with a reply field.

#### Request-Response Pattern

A messaging style in which a client asks and a server replies.

**Example:** HTTP uses request-response.

#### requests Library

A MicroPython library for making HTTP requests.

**Example:** `requests.post(url, json=data)` sends a question.

#### REST Endpoint

A web address that accepts requests for a specific action.

**Example:** `/ask` accepts questions.

#### Retained Message

A message the broker stores and gives to new subscribers.

**Example:** A new device immediately gets the latest test alert.

#### Retry and Backoff

Trying again after a failure while waiting longer between attempts.

**Example:** Retries occur after 1, 2, then 4 seconds.

#### RGB565 Color

A 16-bit color format with 5 bits of red, 6 of green, and 5 of blue.

**Example:** Pure red in RGB565 is `0xF800`.

#### Ring Buffer

A fixed-size buffer in which new data overwrites the oldest when it reaches the end.

**Example:** A ring buffer holds the latest second of audio.

#### RMS Loudness

A measure of signal strength found from the square root of the average of squared samples.

**Example:** A louder room produces a higher RMS value.

#### Rolling Window

A moving span of the most recent data.

**Example:** The detector keeps the last second of features.

#### Room Acoustics

How a room's size and surfaces affect sound.

**Example:** Echoes in a gym raise the noise floor.

#### Round Color Display

A circular screen that shows full-color images and text, here 360 by 360 pixels.

**Example:** The round display shows the clock face and the school mascot.

#### Round Display Mask

A rule that skips pixels outside the circular visible area.

**Example:** Corner pixels of a square image are not drawn.

#### RP2350 Microcontroller

The chip on the Pico 2 that contains two processor cores, memory, and input/output hardware.

**Example:** The RP2350 runs MicroPython and the FFT code.

#### Rule-Based Agent

An agent that picks replies from fixed rules written by a programmer instead of generated by a language model.

**Example:** If the question contains "test," the agent reads the next TEST event.

#### Sample Rate

The number of samples taken each second.

**Example:** A 16,000 Hz sample rate gives 16,000 samples per second.

#### Sampling

Measuring a continuous signal at regular instants.

**Example:** The microphone is sampled thousands of times per second.

#### School Calendar

A schedule of school events, tests, and due dates.

**Example:** The calendar lists a science test on Friday.

#### School Mascot

A character that represents a school, shown on the device display.

**Example:** A griffin appears on the clock screen.

#### School Mascot Design

Preparing a mascot image for the round display.

**Example:** A simple design with strong colors reads well at small size.

#### School-Hosted Agent

An agent run by a school on its own equipment, under school rules for data and configuration.

**Example:** A school runs the agent on a Raspberry Pi in the library and connects it to the school calendar.

#### Secrets Management

Keeping passwords and tokens out of shared code and logs.

**Example:** Credentials live in a private config file.

#### Self-Hearing Problem

The device's microphone picking up its own speaker output.

**Example:** The agent mistakes its own spoken reply for a new question.

#### Self-Hosted Agent

An agent that runs on computers the user or school controls, so the owner chooses its settings and which data it may touch.

**Example:** A buddy server running on a school Raspberry Pi is self-hosted.

#### Self-Test Program

A program that checks every part and reports results.

**Example:** It tests the display, microphone, speaker, and buttons.

#### Serial Data Line

The I2S wire that carries the audio bits.

**Example:** The microphone puts samples on the serial data line.

#### Serial Debugging

Finding problems by printing messages over the USB serial connection.

**Example:** Print the RMS value to the REPL.

#### Server-Side Parsing

Processing data on the server rather than on the Pico.

**Example:** The server parses ICS files because the Pico has little memory.

#### Settings Screen

A display page where users change options such as volume.

**Example:** The settings screen lists volume and brightness.

#### Signal-to-Noise Ratio

The ratio of desired signal strength to background noise strength.

**Example:** A high ratio means speech stands out clearly.

#### Sine Table

A precomputed list of sine values used to build tones quickly.

**Example:** Tone code reads values from the table instead of computing each one.

#### Single-Speaker Limits

The loss of accuracy when someone other than the enrolled speaker says the phrase.

**Example:** A friend's voice may not match the template.

#### Sound Wave

A pressure variation traveling through air that the ear perceives as sound.

**Example:** A tone is a repeating sound wave.

#### Speaker

A device that turns an electrical signal into sound.

**Example:** The kit speaker plays tones and spoken answers.

#### Speaking Pace Sensitivity

A weakness in which detection changes when the wake phrase is spoken faster or slower.

**Example:** A slow "Hey Pico" scores lower than the enrolled one.

#### Spectral Leakage

Spread of a frequency's energy into neighboring bins.

**Example:** A pure tone shows energy in bins on both sides without a window.

#### Spectrogram

A display showing how the spectrum changes over time.

**Example:** Brighter colors mark stronger frequencies as time scrolls.

#### Spectrum Display

A screen graphic showing frequency strengths as bars.

**Example:** Twelve bars move with the sound of speech.

#### Speech Floor Gate

A threshold set above the noise floor that decides if sound might be speech.

**Example:** Audio below the gate is ignored.

#### Speech Level

The loudness of a person talking near the microphone.

**Example:** Speech level is measured while a student reads a sentence.

#### Speech-to-Text Service

A service that converts recorded speech into written text.

**Example:** The server transcribes the utterance before answering.

#### SPI Bus

A fast serial connection that uses a clock line and data lines to move data between a controller and a peripheral.

**Example:** The Pico sends pixel data to the display over SPI.

#### SPI Display Driver

Code that sends commands and pixel data to a display over SPI.

**Example:** The driver provides functions to set a window and write pixels.

#### Sprite

A small image that can be drawn and moved on the screen.

**Example:** A mascot sprite blinks on the display.

#### SRAM

Fast working memory that loses its contents when power is removed.

**Example:** Audio buffers live in SRAM while the program runs.

#### State Machine

A program structure with a fixed set of states and rules for moving between them.

**Example:** The device moves from clock to listening to thinking to speaking.

#### Status Indicator

A display element that shows the device's current condition.

**Example:** A red dot shows that the microphone is listening.

#### Stored Audio Playback

Playing sound from a saved file or buffer.

**Example:** A saved greeting plays when the device starts.

#### Streaming Audio

Sending audio continuously as it is captured.

**Example:** Samples flow to the server while the user is still speaking.

#### Student Privacy Law

Laws that protect information about students.

**Example:** A school consults its policies before deployment.

#### Study Timer Buddy

A buddy that times study sessions and responds to questions.

**Example:** It counts 25 minutes and announces a break.

#### Subscriber

An MQTT client that receives messages for topics it follows.

**Example:** Each device is a subscriber.

#### Swappable Brain

A design in which the software that produces answers can be exchanged for another without changing the device code.

**Example:** Replacing a rule-based server with an LLM-backed one while the Pico code stays the same.

#### System Integration

Combining separate features into one working device.

**Example:** The clock, audio, FFT, and agent run together.

#### Table Precomputation

Calculating values ahead of time and storing them for lookup.

**Example:** A sine table replaces repeated sine calculations.

#### Template Correlation

A similarity score between a stored template and incoming features.

**Example:** A higher correlation means the audio sounds more like the template.

#### Template Matching

Detecting a pattern by comparing input to a stored example.

**Example:** Live audio features are compared to the enrolled template.

#### TEST and DUE Prefixes

Title conventions that mark tests and due dates.

**Example:** `TEST: Algebra` and `DUE: Essay`.

#### Test Date Detection

Recognizing which events are tests.

**Example:** Titles starting with `TEST:` are tests.

#### Text Rendering

Drawing characters on the display as pixels.

**Example:** The agent's reply is rendered as text in the message region.

#### Text-to-Speech Service

A service that converts written text into spoken audio.

**Example:** The reply text becomes a WAV file for the speaker.

#### Thonny IDE

A beginner-friendly editor for writing, running, and saving MicroPython programs on a Pico.

**Example:** Click Run in Thonny to execute a script on the Pico.

#### Threat Model

A list of what could go wrong, who might cause it, and what is protected.

**Example:** It names classroom eavesdropping and stolen tokens.

#### Threshold Trade-Off

The balance in which lowering the threshold lowers false rejects but raises false accepts.

**Example:** A lower threshold wakes the device more often but also by accident.

#### Time Domain

A view of a signal as values over time.

**Example:** A waveform plot shows the time domain.

#### Time Zones

Regions that share a standard clock time.

**Example:** An event at 9:00 in one zone is a different hour in another.

#### Timeouts

Limits on how long to wait for a response.

**Example:** A five-second timeout ends a stalled request.

#### Timer

A hardware counter that triggers actions at regular intervals.

**Example:** A timer fires every 50 ms to check the buttons.

#### Timing Verification

Measuring that code finishes within its allowed time.

**Example:** The FFT must finish in under 32 ms.

#### TLS Encryption

A method that scrambles network data so others cannot read it.

**Example:** TLS protects a password in transit.

#### Tone Generation

Creating samples that produce a pure sound at a chosen frequency.

**Example:** The device plays a 1,000 Hz beep.

#### Topic

A named channel used to route MQTT messages.

**Example:** `school/room12/alerts`

#### Topic Naming Scheme

A consistent pattern for naming topics.

**Example:** `school/classroom/device/status`

#### Topic Wildcards

Symbols that let a subscription match several topics.

**Example:** `school/+/alerts` matches every classroom.

#### Trained Keyword Spotting

Detecting words using a model trained on many recordings.

**Example:** A neural network trained on thousands of voices recognizes "Hey Pico."

#### Transcript Handling

Rules for storing, sharing, and deleting text of what was said.

**Example:** Transcripts are kept only on the school server.

#### Twiddle Factors

Precomputed sine and cosine constants used by the FFT.

**Example:** A table of twiddle factors avoids recalculating trigonometry.

#### Typed Arrays

Arrays whose elements all share one fixed number type.

**Example:** `array('h')` stores 16-bit signed integers.

#### umqtt Library

The MicroPython library for MQTT clients.

**Example:** `umqtt.simple` connects the Pico to a broker.

#### Unit Normalization

Scaling a vector so its length equals one.

**Example:** Normalized templates give scores between -1 and 1.

#### Up Button

The button that raises a value or moves up in a menu.

**Example:** Up increases the speaker volume.

#### Upcoming Events Query

A request for events within a coming time span.

**Example:** "What is due this week?"

#### Update Bandwidth

The amount of data per second that can be sent to the display.

**Example:** Low update bandwidth limits how often a full frame can be redrawn.

#### USB Power

Electrical power supplied through a USB cable.

**Example:** A phone charger supplies USB power to the device.

#### User Feedback

Visible or audible responses that tell the user what the device is doing.

**Example:** A beep confirms the wake phrase was heard.

#### User Testing

Observing real users to learn what works and what confuses them.

**Example:** Classmates try the button scheme and report problems.

#### Utterance Boundaries

The start and end points of a spoken phrase within audio.

**Example:** Silence marks the end of the utterance.

#### Viper Code

MicroPython code compiled with the `@micropython.viper` decorator for faster integer and pointer operations.

**Example:** A viper inner loop runs several times faster than plain Python.

#### Voice Activity Detection

Deciding whether an audio frame contains speech.

**Example:** The device stops recording after the voice activity detection reports silence.

#### Voice and Prompts

The speech style and spoken messages the device uses.

**Example:** A cheerful greeting each morning.

#### Volume Control

Adjusting how loud the speaker output is.

**Example:** Up and Down change volume in steps.

#### Volume Meter

A display element that shows how loud the sound is.

**Example:** A bar fills as RMS loudness rises.

#### Wake Confirmation Beep

A short sound that signals the device heard the wake word.

**Example:** A rising two-tone beep plays after detection.

#### Wake Cooldown

A short delay after a detection during which new detections are ignored.

**Example:** A two-second cooldown prevents repeated triggers.

#### Wake Word

A spoken phrase that signals the device to start listening.

**Example:** "Hey Pico" starts a request.

#### Wake-Word Enrollment

Recording samples of the wake phrase to build a detection template.

**Example:** The student says "Hey Pico" five times during enrollment.

#### WAV File Format

A common audio file format that stores raw samples with a header.

**Example:** A recorded utterance is saved as a WAV file.

#### WebSocket

A persistent two-way network connection between client and server.

**Example:** Always-on mode streams audio over a WebSocket.

#### Wi-Fi Connection

A wireless link between the device and a local network.

**Example:** The Pico joins the classroom network with a name and password.

#### Wi-Fi Radio

The wireless hardware that connects the Pico 2 W to a local network.

**Example:** The Wi-Fi radio lets the device reach the buddy server.

#### Window Fill Percentage

How much of the rolling window has been filled with data.

**Example:** Scoring begins when the window is fully filled.

#### Windowing

Multiplying a frame by a smooth shape that tapers its edges before the FFT.

**Example:** A window reduces leakage from abrupt frame edges.

#### Wiring Verification

Confirming that each part is connected to the correct pins.

**Example:** Compare wires to the pin assignment table.

#### Word Select

The I2S signal that marks the start of each sample and which channel it belongs to.

**Example:** Word select toggles between left and right channels.

