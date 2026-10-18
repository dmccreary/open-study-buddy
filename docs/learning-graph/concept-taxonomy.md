---
title: Concept Taxonomy
description: The fifteen concept categories used to color the Open Study Buddy learning graph.
---

# Concept Taxonomy

The 326 concepts in the learning graph are grouped into 15 categories. Each concept
belongs to exactly one category. The TaxonomyID is the 3-5 letter code used in
`learning-graph.csv`. Categories are ordered from foundational material to the
capstone projects.

## Personal Agents and Architecture (FND)

**TaxonomyID:** FND  
**Concepts:** 22

What a personal agent is, open versus cloud agents, the Open Study Buddy architecture, and the swappable-brain progression from a rule-based buddy server to open-source agent frameworks.

## MicroPython Review (MPY)

**TaxonomyID:** MPY  
**Concepts:** 20

The MicroPython skills the book assumes from the prerequisite course: REPL, modules, the machine library, interrupts, timers, memory limits and garbage collection.

## Pico Kit Hardware (HWK)

**TaxonomyID:** HWK  
**Concepts:** 22

The kit parts and their wiring: Pico 2 W, RP2350, round display, INMP441 microphone, MAX98357A amplifier, speaker, buttons and breadboard.

## Round Display Graphics (DISP)

**TaxonomyID:** DISP  
**Concepts:** 26

Driving the 360 x 360 round display over SPI: RGB565, frame size, why full-frame updates are too slow, direct region writes, clock faces, icons and the school mascot.

## Buttons and Device Modes (BTN)

**TaxonomyID:** BTN  
**Concepts:** 16

Mode, Up and Down buttons, debouncing, edge detection, menus, state machines, device modes and non-blocking event loops.

## Digital Audio and I2S (AUD)

**TaxonomyID:** AUD  
**Concepts:** 30

Sound, sampling, the Nyquist limit, the I2S bus, machine.I2S, audio buffers and frames, tone and stored-audio playback, and the self-hearing problem.

## Signal Processing and FFT (DSP)

**TaxonomyID:** DSP  
**Concepts:** 26

Time and frequency domains, the DFT and FFT, bins, windowing, magnitude spectra, band energies, loudness and spectrum displays.

## High-Performance MicroPython (PERF)

**TaxonomyID:** PERF  
**Concepts:** 20

Making MicroPython fast enough for real time: viper, inline assembly, the assembly FFT, typed arrays, allocation-free code, cycle counting and benchmarking.

## Mic Calibration and Push-to-Talk (CAL)

**TaxonomyID:** CAL  
**Concepts:** 14

Measuring the noise floor and speech level, signal-to-noise ratio, level gates, push-to-talk recording and utterance boundaries.

## Wake-Word Detection (WAKE)

**TaxonomyID:** WAKE  
**Concepts:** 24

Detecting 'Hey Pico': enrollment, feature extraction, template correlation, thresholds, false accepts and rejects, limits, and comparison with trained models.

## Networking and Agent Link (NET)

**TaxonomyID:** NET  
**Concepts:** 26

Wi-Fi, HTTP and JSON on the school LAN, chunked audio upload, speech services, WebSocket streaming, HTTPS, and handling network failure.

## MQTT and Push Alerts (MQTT)

**TaxonomyID:** MQTT  
**Concepts:** 22

Publish/subscribe messaging: brokers, topics, QoS, retained messages, last-will, umqtt, non-blocking check_msg, and connecting to Home Assistant.

## School Agent and Calendar (SCH)

**TaxonomyID:** SCH  
**Concepts:** 24

Connecting the agent to a school calendar via JSON then iCalendar feeds, test and due-date events, briefings, reminders and per-school customization.

## Privacy and Responsible Listening (PRIV)

**TaxonomyID:** PRIV  
**Concepts:** 18

Consent, parent and school approval, data minimization and retention, local versus cloud processing, threat models, mute and indicators.

## Testing, Integration and Capstones (TEST)

**TaxonomyID:** TEST  
**Concepts:** 16

Probe and self-test programs, wiring checks, logging, diagnosing silent microphones and blank displays, system integration and capstone projects.

## Pedagogical Flow

The order above is the suggested teaching order. Personal-agent ideas, the MicroPython
review and the hardware come first. Display, buttons and audio follow, then signal
processing and performance. Calibration and wake-word detection build on audio and the FFT.
Networking comes next, and MQTT builds on it. The school-agent, privacy and
integration categories bring the pieces together.
