# Chapters

This textbook is organized into 18 chapters covering 326 concepts.

## Chapter Overview

1. [Personal Agents and the Open Study Buddy Architecture](01-personal-agents-architecture/index.md) - Defines personal agents, contrasts commercial cloud agents with open school-hosted agents, and introduces the Open Study Buddy device, buddy server, and the swappable-brain progression from rules to LLMs.
2. [MicroPython Review for Embedded Systems](02-micropython-review/index.md) - Refreshes the MicroPython skills used throughout the book: the REPL, modules, the machine library, GPIO, timers, interrupts, memory limits, and garbage collection on the Pico.
3. [Sound and Digital Audio Basics](03-sound-and-digital-audio/index.md) - Explains sound waves, frequency, amplitude, sampling, sample rate, bit depth, and the Nyquist limit, and introduces the time and frequency domains that later audio chapters build on.
4. [The Pico Kit Hardware and Wiring](04-pico-kit-hardware/index.md) - Introduces the Raspberry Pi Pico 2 W, round display, INMP441 microphone, MAX98357A amplifier, speaker, and buttons, with breadboard wiring, power, and the pin assignment table for the kit.
5. [Display Basics: Pixels, Color, and Frame Size](05-display-basics/index.md) - Covers driving the 360 by 360 round display over SPI, RGB565 color, frame buffers, clock-face geometry, and why updating the whole frame on every change is too slow.
6. [Drawing Directly to Display Regions](06-display-regions-and-drawing/index.md) - Teaches direct region writes, drawing windows, and dirty regions, then uses them for text, icons, sprites, animation, image loading, and displaying a school mascot on the round display.
7. [Buttons, State Machines, and Device Modes](07-buttons-and-device-modes/index.md) - Builds Mode, Up, and Down button handling with debouncing, long press, menus, state machines, non-blocking event loops, and on-screen feedback for each device mode.
8. [I2S Audio: Recording and Playing Sound](08-i2s-audio/index.md) - Shows how the I2S bus, machine.I2S, audio buffers, and audio frames capture microphone sound and play tones and stored audio while staying inside a fixed frame time budget.
9. [Signal Processing and the FFT](09-signal-processing-fft/index.md) - Teaches the Fourier transform, the FFT, frequency bins, windowing, magnitude spectra, loudness, and band energies, and uses them to build volume meters and spectrum displays.
10. [High-Performance MicroPython](10-high-performance-micropython/index.md) - Makes MicroPython fast enough for real-time audio using typed arrays, viper code, inline assembly, allocation-free loops, cycle counting, and benchmarking against the frame budget.
11. [Microphone Calibration and Push-to-Talk](11-mic-calibration-push-to-talk/index.md) - Measures the noise floor and speech level, sets level gates, and records an utterance on a button press, using voice activity detection to find where speech starts and stops.
12. [Wake-Word Detection](12-wake-word-detection/index.md) - Builds an on-device wake-word detector from audio features, rolling windows, and template correlation, and examines thresholds, enrollment, false accepts, and false rejects honestly.
13. [Wi-Fi, HTTP, and Connecting to the Agent](13-wifi-http-agent-link/index.md) - Connects the Pico to the school network using Wi-Fi, IP addresses, JSON, HTTP POST, and the requests library so it can send a request to the buddy server and read the reply.
14. [Streaming Speech, Security, and Network Resilience](14-streaming-security-resilience/index.md) - Covers sending speech to the agent in memory-safe chunks, speech-to-text and text-to-speech services, WebSockets, tokens, HTTPS, and handling timeouts, retries, and offline fallback.
15. [MQTT and Push Alerts](15-mqtt-push-alerts/index.md) - Introduces publish-subscribe messaging with brokers, topics, QoS levels, and retained messages, and receives school alerts with umqtt without blocking the real-time audio loop.
16. [Configuring the School Agent and Calendar](16-school-agent-calendar/index.md) - Connects the buddy to school events using JSON and iCalendar feeds, server-side parsing, TEST and DUE title conventions, daily briefings, reminders, and per-school personalization.
17. [Privacy, Safety, and Responsible Listening](17-privacy-responsible-listening/index.md) - Addresses consent, data minimization, retention, student-privacy concepts, threat models, a hardware mute switch, listening indicators, and the approval process for always-on listening.
18. [Testing, Integration, and Capstone Projects](18-testing-integration-capstones/index.md) - Combines probes, self-tests, logging, and diagnostics to integrate the display, audio, DSP, and agent features into one finished device and several capstone projects.

## How to Use This Textbook

Work through the chapters in order. Each chapter builds on the ones before it, so the dependencies between concepts are always respected: sound and hardware come before the display and audio code, and the network, school-agent, and privacy chapters build on the working device. The first two chapters are a refresher, so students who already know the Raspberry Pi Pico and MicroPython can move through them quickly.

---

**Note:** Each chapter includes a list of concepts covered. Make sure to complete prerequisites before moving to advanced chapters.
