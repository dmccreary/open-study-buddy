---
title: Course Description for Open Study Buddy
description: A detailed course description for Open Study Buddy including overview, topics covered and learning objectives in the format of the 2001 Bloom Taxonomy
quality_score: 99
---
# Open Study Buddy

**Title:** Open Study Buddy

**Target Audience:** High school students (grades 9–12) as the primary audience, with content accessible to motivated junior high students, college undergraduates, coding clubs, hobbyists, and the teachers and mentors who run school maker programs.

**Prerequisites:** The *Learning MicroPython and Physical Computing* course (or equivalent experience). Students should already be able to flash MicroPython onto a Raspberry Pi Pico, use Thonny and the REPL, write loops, functions, and modules, read a push button with debouncing, and drive a display. The first chapter reviews these basics briefly, but it is a refresher, not a first introduction. Basic arithmetic and the idea of a sine wave are helpful; no prior signal-processing, networking, or artificial-intelligence experience is assumed.

## Course Overview

Open Study Buddy is a hands-on course for building a **low-cost, fully open, personal AI agent device** from parts that cost a few tens of dollars. The device combines a Raspberry Pi Pico 2 W microcontroller, a large round 360 × 360 color display (the same display used in the Chrono Smart Clock kit), an I2S speaker amplifier (MAX98357A) with a small high-quality speaker, an INMP441 I2S digital microphone, and three momentary push buttons (**Mode**, **Up**, **Down**). Students write every line of MicroPython that runs on it. By the end, they own a desk companion that listens, shows what it heard, speaks answers aloud, and tells them what is due and when the next test is.

The course follows the fast-growing trend of **personal agents**: always-on AI software that carries out multi-step work on a person's behalf, such as checking calendars, summarizing information, and coming back when it needs a decision. Most commercial personal agents are closed, run on a vendor's cloud computer, and bill a monthly subscription. Open Study Buddy takes the opposite approach. The device is **totally open**. Each person, class, or school sets up and configures the agent behind it, chooses where that agent runs, and decides which data it may touch. A school can connect its agent to the school calendar to announce events, upcoming tests, and project due dates, and can give its device its own **school mascot** (for example, a griffin) that appears on the round display.

The device is capable because several technologies meet on one inexpensive board. The Pico 2's dual cores and DSP-friendly instructions run a real-time **FFT** on live microphone audio, which supports volume meters, spectrum displays, and **wake-word detection** ("Hey Pico"). The Wi-Fi radio on the Pico 2 W connects the device to the agent software, and to **MQTT**, the lightweight publish/subscribe protocol at the core of many open home-automation and alert systems, so that a school can push "test tomorrow" alerts to every device. The large round display, speaker, and buttons give the agent a face, a voice, and a physical interface. That display carries a lot of information for a microcontroller: 360 × 360 is 129,600 pixels, or about 259 KB per frame at 16 bits per pixel, so pushing a full frame buffer to the screen on every update is far too slow for a responsive device. Students therefore learn to **write directly to the display, one region at a time**, redrawing only the part of the screen that changed (the time digits, a spectrum bar, a status icon) instead of the whole frame. The default listening mode is **push-to-talk**; an always-on wake-word mode is an advanced option that requires explicit approval from a parent, teacher, or school before it is enabled.

The book is also a gentle, step-by-step tutorial on getting the most out of MicroPython. Each chapter adds one idea on top of the previous chapter and ends with a working device feature. Students learn the techniques that make real embedded systems work: I2S audio, direct-memory-access style buffering, assembly-accelerated inner loops, non-blocking event loops, timers, and talking to a network service. Students also learn the responsibilities that come with a listening device: privacy, consent, data minimization, and the difference between a device that stays local and one that sends data away.

## Main Topics Covered

- **Personal agents and the Open Study Buddy architecture** — what a personal agent is, how commercial cloud agents differ from open, self-hosted agents, and how a Pico-based terminal (listen, display, speak) connects to the agent software behind it
- **MicroPython review for embedded systems** — the REPL, Thonny, `mpremote`, modules and imports, the `machine` library, GPIO, interrupts, timers, memory limits, and garbage collection
- **The hardware kit** — Raspberry Pi Pico 2 W, the 360 × 360 round color display and its controller, the INMP441 microphone, the MAX98357A amplifier and speaker, push buttons, breadboard wiring, and power
- **Round display graphics** — SPI display drivers, color formats (RGB565), text and fonts, clock-face geometry, icons, animation, and displaying a school mascot image; why full-frame buffer updates are too slow on a 360 × 360 display, and how to use direct writes to set a drawing window and update only the changed region
- **Buttons and user-interface design** — Mode, Up, and Down button schemes, debouncing, long press, menu navigation, and a state machine for device modes
- **Digital audio fundamentals** — sound, sampling, sample rate, bit depth, Nyquist limit, the I2S bus (clock, word select, data), and reading and writing audio buffers with `machine.I2S`
- **Speaker output** — generating tones, playing stored audio, volume control, amplifier shutdown, and avoiding the device hearing its own voice
- **Digital signal processing on the Pico 2** — windowing, the FFT, frequency bins, magnitude spectra, log-spaced band energies, spectrum displays, and measuring speed with the cycle counter
- **High-performance MicroPython** — pure-Python versus `@micropython.viper` and assembly inner loops, `array` buffers passed by address, avoiding allocation in real-time code, and benchmarking against a real-time frame budget
- **Microphone calibration and push-to-talk** — measuring the noise floor and speech level, signal-to-noise ratio, level gates, clipping, and recording an utterance on a button press
- **Wake-word detection** — enrolling a phrase, feature extraction, template correlation, rolling windows, thresholds, false-accept and false-reject trade-offs, and the honest limits of template matching versus trained models
- **Networking and connecting to an agent** — Wi-Fi, HTTP clients and JSON on the school LAN, a swappable "brain" behind one small request contract, push-to-talk audio sent in chunks to stay inside the Pico's memory, WebSocket streaming for always-on mode, authentication, handling network failure, and why plain HTTP is acceptable only on a trusted classroom network (with an introduction to HTTPS)
- **MQTT and push alerts** — publish/subscribe versus request/response, brokers (running Mosquitto on a school Raspberry Pi), topics and topic naming per school and classroom, QoS levels, retained messages, last-will, `umqtt` on MicroPython, non-blocking `check_msg` inside the audio loop, authentication, keeping the broker off the public internet, and how MQTT connects the device to open home-automation dashboards such as Home Assistant
- **Configuring the school agent** — a progression from a small rule-based buddy server (about 100 lines, no LLM), to the same server with speech-to-text, text-to-speech and one LLM call, to an optional open-source self-hosted agent behind the same contract; reading school events from a hand-edited JSON file, then an iCalendar (.ics) feed (parsed on the server, never on the Pico), using `TEST:` and `DUE:` title conventions for tests and project due dates, daily briefings, reminders, and per-school customization
- **School mascots and personalization** — preparing mascot images for a round display, themes, voices, and wake-phrase choices
- **Privacy, safety, and responsible listening** — consent, parent and school approval for always-on listening, local versus cloud processing, data retention, student-privacy law concepts, a hardware mute, and visible "listening" indicators
- **Testing, debugging, and system integration** — probes and self-test programs, measuring frame overruns, logging, and combining the clock, audio, DSP, and agent features into one finished device

## Topics Not Covered

- Building or training large language models, neural-network keyword-spotting models, or speech-recognition models (the course uses template correlation for wake words and relies on a separate service for transcription)
- Installation and administration details of any single commercial personal-agent product (the course treats commercial agents only as context)
- Cloud server administration, container orchestration, and production-grade web hosting (running a single MQTT broker and buddy server on a school Raspberry Pi is covered; clustering and high availability are not)
- Printed-circuit-board design, soldering, surface-mount assembly, and custom enclosure design (the kit uses a breadboard and plug-in wires)
- The C/C++ Pico SDK, Arduino toolchain, and custom firmware builds (the course uses stock MicroPython only)
- Advanced DSP theory such as filter design mathematics, wavelets, and the derivation of the FFT algorithm
- Bluetooth audio, cellular connectivity, and battery power-management design
- Legal advice on student-privacy regulations (the course explains concepts and tells students to consult their school's policies)

## Learning Outcomes

After completing this course, students will be able to:

### Remember
*Retrieving, recognizing, and recalling relevant knowledge from long-term memory.*

- Define *personal agent*, *push-to-talk*, *wake word*, *sample rate*, *FFT*, *I2S*, and *noise floor*
- Name the five hardware parts of the Open Study Buddy kit and state the job of each
- State the pixel count and approximate byte size of a full 360 × 360 RGB565 frame
- Identify the Pico 2 W pins used for the display (SPI), the microphone (I2S RX), the amplifier (I2S TX), and the three buttons
- Define *publisher*, *subscriber*, *broker*, *topic*, *retained message*, and *QoS level* in MQTT
- Recall the three I2S signals (bit clock, word select, serial data) and what each carries
- List the Mode, Up, and Down button roles used in each device mode
- Recall the default wake phrase ("Hey Pico") and the steps needed to approve always-on listening
- State the audio frame size and sample rate used by the kit and the time that one frame represents

### Understand
*Constructing meaning from instructional messages, including oral, written, and graphic communication.*

- Explain how a personal agent differs from a chatbot and how an open, school-hosted agent differs from a vendor-hosted cloud agent
- Describe the data flow from a spoken question, through the microphone and Pico, to the agent, and back to the speaker and display
- Explain why a sampled signal needs a sample rate above twice its highest frequency (the Nyquist limit)
- Explain what an FFT bin represents and calculate the frequency of a given bin from the sample rate and FFT size
- Summarize why a real-time audio loop has a fixed time budget and what an overrun means
- Explain why updating the whole 360 × 360 display for every change is too slow, and how writing directly to a defined region avoids the cost
- Explain publish/subscribe messaging and how it differs from HTTP request/response, and why it suits alerts
- Explain how template correlation detects a wake word and why mean-subtraction is needed
- Describe why always-on listening raises privacy concerns that push-to-talk does not

### Apply
*Carrying out or using a procedure in a given situation.*

- Wire the display, microphone, amplifier, speaker, and three buttons to a Pico 2 W and verify each part with a self-test program
- Write MicroPython that draws text, a clock face, and a school mascot image on the round 360 × 360 display
- Update the display with direct region writes (set a window, then stream only the changed pixels) for clock digits, spectrum bars, and status icons
- Capture audio from the INMP441 with `machine.I2S` and compute its loudness in real time
- Play tones and recorded audio through the MAX98357A amplifier and control the volume with buttons
- Run the assembly-accelerated FFT on a live audio frame and draw a live spectrum on the display
- Calibrate the microphone, enroll the phrase "Hey Pico," and tune the detection threshold
- Connect the Pico 2 W to Wi-Fi and exchange JSON with a school-hosted buddy server over HTTP POST, then send push-to-talk audio to it in chunks
- Subscribe the Pico to an MQTT topic with `umqtt` and show incoming alerts on the display without blocking the audio loop
- Publish device status (online, last wake, volume) to an MQTT topic on a school broker
- Configure the buddy server to read events from a JSON file and then an iCalendar (.ics) feed, and announce events whose titles start with `TEST:` or `DUE:` on the device

### Analyze
*Breaking material into constituent parts and determining how the parts relate to one another and to an overall structure or purpose.*

- Break the device into subsystems (input, audio, DSP, display, network, agent) and trace how data moves between them
- Diagnose a silent microphone, a distorted speaker, or a blank display by isolating wiring, configuration, and software causes
- Measure and compare the time of a full-frame update with the time of region-only updates, and decide which regions of a screen layout should be redrawn independently
- Compare pure-Python, viper, and assembly FFT implementations by measured cycles and decide which fit inside the frame budget
- Analyze a spectrum to tell silence, steady noise, a tone, and speech apart
- Examine wake-word score traces and distinguish false accepts from false rejects and their likely causes
- Analyze where memory and CPU time go in a running program and find sources of garbage-collection pauses
- Compare HTTP polling, MQTT, and WebSocket for delivering a "test tomorrow" alert and for streaming audio, in terms of latency, memory use, and complexity
- Compare push-to-talk with always-on wake-word listening in terms of privacy, power use, reliability, and user experience

### Evaluate
*Making judgments based on criteria and standards through checking and critiquing.*

- Judge whether a wake-word detector is good enough using measured false-accept and false-reject rates at several thresholds
- Critique the limits of template correlation compared with a trained keyword-spotting model
- Evaluate the privacy and safety risks of a classroom listening device and decide which safeguards are required before it is turned on
- Choose MQTT QoS levels, retained messages, and last-will settings for classroom alerts and justify the choices
- Evaluate the risk of exposing an MQTT broker or agent to the internet and decide which authentication and encryption are required
- Assess the trade-offs of running the agent locally, on a school server, or in a vendor's cloud in terms of cost, control, latency, and data exposure
- Evaluate the answers an agent gives about school events for accuracy, and decide when the device should ask for confirmation
- Justify the design choices for the button scheme, display layout, and audio levels based on user testing with classmates

### Create
*Putting elements together to form a coherent or functional whole; reorganizing elements into a new pattern or structure.*

- Design and build a complete Open Study Buddy device that combines the clock display, push-to-talk, speaker responses, and spectrum visualization
- Create a personalized school edition with its own mascot, colors, wake phrase, and voice prompts
- Design a screen layout divided into independently updated regions (time, mascot, spectrum, agent message, status bar) that keeps the display responsive while audio is processed
- Build an alert pipeline in which a school server publishes upcoming tests and due dates to MQTT and several devices subscribe and display them
- Write a state machine that moves the device between clock, listening, thinking, speaking, and settings modes
- Design a configuration for a school agent that reports the next test, upcoming project due dates, and daily events from a school calendar
- Connect the device to an open home-automation dashboard, such as Home Assistant, through MQTT
- Develop a new DSP-based feature, such as a clap detector, a noise-level monitor for a classroom, or a tuner
- Capstone project ideas: a homework-reminder buddy for a class, a study-timer buddy that listens for questions, a classroom noise-meter buddy, or a school-event announcer with a custom mascot
- Produce a privacy and consent plan that a teacher or parent could review before a device is deployed
