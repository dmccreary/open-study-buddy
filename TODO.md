# TODO: Hardware tests and measurements still needed

Chapters 9 to 18 were written on 2026-10-18 without access to the kit, a school
network, a Mosquitto broker, or classmates. Everything in them that depends on
a run is labelled **expected**, **estimate**, **synthetic**, or **illustrative**,
or is left as a "to be measured" blank. **After the tests and benchmarks below
have been run, the chapter content must be updated with the results.** The last
part of each item names what to change. Tick a box only after the chapter text,
table, or MicroSim specification has been updated.

Item format: `Ch | script | what to run or measure | what to update afterwards`.
Script names are relative to `src/chapters/<chapter folder>/` unless a full path is given.

## Do these first (other chapters depend on them)

- [ ] Ch 10 | `01-cycle-counter.py`, then `02`, `04`, `05`, `06` | Run the whole benchmark set; it fills in the Chapter 10 results table and settles whether the viper path fits the 40 ms frame | Ch 10 results table; Ch 9 "a guess of 100 to 300 ms" sentences; Ch 12 "expected to be several times over budget"; Ch 18 "plain-Python loudness is about 10 ms" budget assumption
- [ ] Ch 12 / Ch 10 | `src/chapters/12-wake-word-detection/features.py` | Ch 12's `Extractor(spectrum_fn=fast)` hook expects `fast(re, im, power)` on floats, but Ch 10's `fft_viper.py` works on Q15 integer arrays with a different API. Write and test a small adapter (or change the hook), then re-time `03-feature-timing.py` with it | Ch 12 "The Frame Budget" paragraph; Ch 10 text if it mentions the wake-word detector
- [ ] Ch 2 / 4 / 5 / 6 / 14 / 17 | `{:,}` in `str.format` | Chapters 11 and 12 removed the `{:,}` thousands separator from their scripts because MicroPython support was unconfirmed (the Ch 10 agent saw it ignored for floats), but earlier scripts still use it: `02/01-memory-report.py`, `02/05-bytes-struct-memoryview.py`, `02/07-heap-fragmentation.py`, `04/04-display-visible-area.py`, `05/05-frame-size-calc.py`, `06/01-pixel-vs-fillrect.py`, `14/01-chunk-arithmetic.py`, `14/04-upload-voice.py`. Run them on the Pico; if they fail or drop the commas, change the format | The listed scripts and any chapter output blocks that show comma-grouped numbers
- [ ] Ch 15 / Ch 18 | `15/04-check-msg-cost.py` | Measure `check_msg()` cost; Ch 18's scheduler demo assumes `network` 2.0 ms and `buttons` 0.5 ms | Ch 18 "The Time Budget in Numbers" (19.0, 21.0, 27.8 ms) and the scheduler timeline spec

## Chapter 9 (Signal Processing and the FFT)

- [ ] Ch 09 | src/chapters/09-signal-processing-fft/05-mic-spectrum-text.py and 07-spectrum-display.py | Run on the kit; record "work ms" per analyzed frame and frames skipped | Ch 9 "Whole Pipeline" section says FFT is "a guess of 100-300 ms, 3-8 frames, not a measurement"; Ch 10 table rows 1-3; Ch 10 "Chapter 9 guessed 100 to 300 ms" sentence
- [ ] Ch 09 | 05-mic-spectrum-text.py | Record dBFS in a quiet room and with a tone | Ch 9 Decibels section: quiet room about -58 dBFS (modelled from Ch 8's 13.1 bits); Ch 10 sim and meter ranges
- [ ] Ch 09 | 06-volume-meter.py | Check the meter scale (-70 to -20 dBFS) and the number reading in a quiet room (README says about -55 to -60) | Ch 9 Volume Meter section scale; PASS text in README
- [ ] Ch 09 | 07-spectrum-display.py | Check bar scale (-90 to -30 dBFS) and `PEAK_GATE_DBFS` (-50) on the real room | Ch 9 Spectrum Display table "Level scale"; Peak Frequency Detection gate sentence
- [ ] Ch 09 | 07-spectrum-display.py | Check `dsp.latest_frame()` really skips stale frames on the Pico (4 ms "instant" threshold) | Ch 9 Pipeline section and the `latest_frame` docstring

## Chapter 10 (High-Performance MicroPython)

- [ ] Ch 10 | 01-cycle-counter.py | Does the DWT cycle counter exist and count on the RP2350 via mem32 (0xE000EDFC / 0xE0001000 / 0xE0001004)? Record cycles/us, cost of one read, and whether `ticks_cpu` equals `ticks_us`. A bad access might reset the board; the script checks bit 25 and falls back to microseconds | Ch 10 "Cycle Counter and DWT Timer" section ("unverified"), key-takeaways bullet, `bench.py` header comment
- [ ] Ch 10 | 02-fft-pure-python-bench.py | Time `dsp.fft` (lists and `array('f')`, 128/256/512), microseconds per butterfly, and pipeline total | Ch 10 results table rows 1-3; "Baseline: Pure Python FFT" cycles-per-butterfly table; Ch 9 guess
- [ ] Ch 10 | 03-allocation-and-floats.py | Confirm the 12 expected yes/no allocation answers (especially "integer above 2**30" on a 32-bit chip); record int vs float loop times, list vs array times and bytes | Ch 10 allocation table; `allocation-classifier` spec table; Typed Arrays memory table (derived: 10,240 / 2,048 / 2,048 / 1,024)
- [ ] Ch 10 | 04-window-kernels.py | Window and sum times for list/array/viper/asm and cycles per sample; confirm the Pico assembler accepts `kernels_asm.py` (only checked in an emulator) | Ch 10 results table rows 4-7; "Speed estimate" paragraph (15-25 cycles/sample, 51-85 us); any assembler error
- [ ] Ch 10 | 05-fft-viper-bench.py | Time `fft_q15`, the whole viper pipeline and each stage; confirm 0 bytes allocated; band error. Note: unix port zero-extends ptr32 loads where the Pico sign-extends, so Q15 FFT was only checked in a CPython model | Ch 10 rows 8-9; accuracy table claims (0.20 dB worst error is modelled); "Using the viper FFT" text
- [ ] Ch 10 | 06-frame-loop-budget.py | Mic loop: both VERDICT lines, worst pass, overrun counts | Ch 10 rows 11-12; any Ch 10/11 statement that the pure path fails and the viper path passes
- [ ] Ch 10 | 07-dual-core.py | Record ratios A-D (core-0 rate % and worker time %); check I2S IRQs, GC stalls, flash lockout behaviour | Ch 10 row 13; "Using the Second Core" expectation (C near 100%, D slower)
- [ ] Ch 10 | bench | Optional: write an asm FFT (stretch) and time it | Ch 10 row 10 and the 0.92 ms paper estimate (assumes 60 cycles per butterfly)
- [ ] Ch 10 | src/chapters/10-high-performance-micropython/README.md | Confirm facts read from MicroPython source: float implementation (single precision, boxed; FPU use not verified), `ticks_cpu` = `time_us_32` on ARM, two-thread model, asm opcodes on M33 | Ch 10 text on those points

## Chapter 11 (Microphone Calibration and Push-to-Talk)

- [ ] Ch 11 | src/chapters/11-mic-calibration-push-to-talk/02-noise-floor.py | Run in a quiet room, and again with a fan or in a harder room; record floor, ceiling, spread, DC offset range | "Noise Floor" section (expected 12.5-13.1 bits; the 10-frame table is illustrative), "Room Acoustics" qualitative claims, "What Has and Has Not Been Measured" table
- [ ] Ch 11 | .../03-speech-level.py | At 30 cm: speech level, SNR in bits/dB, biggest sample, clipped frames | "Speech Level" section (illustrative 10-frame table, comment on the 17.0-bit speaker tone), SNR worked example (13.0/17.0, illustrative), MIN_SNR_BITS = 2.0 rationale, status table
- [ ] Ch 11 | .../06-distance-test.py | Measure at 10, 20 and 40 cm and compare with the 1 bit per doubling model | "Microphone Distance Effect" worked example (illustrative 18/17/16/15 bits, 80 cm limit) and the model-fit statement
- [ ] Ch 11 | .../04-calibrate.py | Full run on the device, UP to save; read back `calibration.json`; check `speech_floor`, `gate_close`, `record_shift` are sensible and that GATE_FRACTION 0.4, GATE_MARGIN 1.0, HYSTERESIS 0.5 work for real voices | `calibration.json` example (illustrative), speech-floor formula constants, synthetic calibration table (12.97/13.20/17.43/14.75/14.25), defaults in `calibration.py`
- [ ] Ch 11 | .../05-gate-meter.py | Record gate flips vs single-threshold flips on real speech | "Level Gate" text and the Level Gate Hysteresis Explorer spec (traces are synthetic)
- [ ] Ch 11 | .../07-ptt-record.py | Record work ms avg/max per frame (loudness + 16-bit conversion + bar), overruns, the free-heap line; confirm the 153,600-byte buffer allocates; check SKIP_FRAMES = 3 (120 ms) is enough start-up settling | "Recording an Utterance" (per-frame budget is a prediction), buffer-fits statement, "What Has and Has Not Been Measured" table
- [ ] Ch 11 | .../08-vad-record.py | Kept vs recorded length for a phrase; effect of whisper, cough, tap, fan; AUTO_STOP; tune VAD constants if needed | VAD reasoning for 3/15/4/5 frames (design choices, untested), VAD limits paragraph, VAD Boundary Finder spec
- [ ] Ch 11 | bench | Shout at about 5 cm; see whether samples reach CLIP_LEVEL (95% of full scale), whether the clipped flag triggers, whether the recording `limited` flag triggers | "Clipping Detection" section (95%, 2 samples), the `record_shift` explanation
- [ ] Ch 11 | bench | Run `01-bits-and-db.py` and `09-calibration-selftest.py` on the Pico; confirm JSON write, `os.remove`+`os.rename` swap, `struct.pack_into` with 512 star-args | Flash-write caution text and the "also runs on the Pico" claims in READMEs and script headers

## Chapter 12 (Wake-Word Detection)

- [ ] Ch 12 | src/chapters/12-wake-word-detection/03-feature-timing.py | ms per feature step with the plain-Python FFT, then with Chapter 10's fast transform via `Extractor(spectrum_fn=...)` | "The Frame Budget" paragraph ("expected to be several times over budget"; 17.4 us per butterfly is arithmetic), status table
- [ ] Ch 12 | .../02-band-table.py | Run on the Pico; compare the measured heap line with the 13,593-byte arithmetic and read free heap | "The Rolling Window" memory table
- [ ] Ch 12 | .../05-enroll.py | Five enrollments of your own "Hey Pico"; record the consistency numbers and on-screen feature time | "Enrolling the Phrase" (synthetic consistency 0.847/0.686/0.879/0.858/0.705; OUTLIER_BELOW 0.5 is a starting value)
- [ ] Ch 12 | .../06-self-test.py | Real template: shifted-window scores for -3 to +3 frames, room-noise score, ms per frame vs 40 ms | "Testing the Detector" (synthetic shifts 0.891/0.617/0.292), the "at least as fussy" statement
- [ ] Ch 12 | .../07-score-trace.py | Best score for 5 "Hey Pico", 5 other phrases, a cough, a clap; paste the CSV | "Deciding" section (THRESHOLD = 0.70 is an unvalidated placeholder), template-matching claims
- [ ] Ch 12 | .../08-threshold-sweep.py (+ tools/threshold-sweep.py) | False rejects/accepts at 0.50-0.95 for yourself, a classmate, fast pace, slow pace, noisy room; save the RESULT lines | FA/FR table and Threshold Trade-Off Explorer data (synthetic), synthetic pipeline numbers (7.5% FR and 18.1% FA at 0.70; speaker 100%/5% rejected; pace table), "Single-Speaker Limits", "Speaking Pace Sensitivity", honest-limits section, and the `THRESHOLD` constant in `detector.py`
- [ ] Ch 12 | .../09-live-detector.py | With a fast transform; always-on only after Chapter 17 approval: frame time, overruns, false accepts per hour over a long ordinary session, detection latency | "False Accepts" worked example (300 segments/hour is an assumption), status table
- [ ] Ch 12 | bench | After a detection, check the mic is quiet again before the cooldown ends; check the 2 s cooldown and 120 ms beep are sensible | "Deciding" section (50 frames, 880 Hz, 120 ms, 3,072 bytes)
- [ ] Ch 12 | .../01-detector-math-test.py | Run on the Pico (slow but possible); confirm `array('f', array)` copies, `f.readinto(array)`, `struct` "4s" header all work | PASS claims in the README, the 1,608-byte template file claim

## Chapter 13 (Wi-Fi, HTTP, Agent Link)

- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/01-wifi-connect.py | Run on the Pico with a real 2.4 GHz school network; record ms from "joining" to "connected" | Ch13 "Joining the Network" (the chapter gives no number, only says to measure)
- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/01-wifi-connect.py | Confirm `wlan.status()` returns 0/1/2/3/-1/-2/-3 and that `status("rssi")` and `network.hostname()` work on the Pico 2 W; try a wrong password and a 5 GHz-only SSID | Ch13 status table, the "-80 dBm rule of thumb" tip, the `wifi_link.py` REASONS dict
- [ ] Ch 13 | all 13-*.py | Compile and run every script on the Pico to catch MicroPython incompatibilities (`{:,}` in `str.format`, `str.partition`, `bytes.partition`, `socket.read`/`recv` return behavior) | Any statement about "runs on the Pico"; README "not checked" list
- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/05-socket-post.py | Record connect ms, round-trip ms, heap before/after against a LAN server | Ch13 "Reading the Reply Safely" (currently only says the messages are tiny) and the by-hand versus `requests` table
- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/06-requests-post.py | Record which `requests` version `mip` installs on the kit's firmware (chapter says 1.1.1 at time of writing), whether `timeout=` works, whether `requests` is already frozen into the Pico 2 W firmware; run the "Try This" loop without `close()` to find how many calls until sockets run out | Ch13 "The requests Library" (install paragraph and the HTTPS/CERT_NONE remark), "Reading the Reply Safely" socket-limit wording
- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/08-mdns-check.py | Run with `sys.version`; does `<server>.local` resolve on the Pico? Does the Pico answer to `study-buddy-07.local`? | Ch13 mDNS table (both rows are "unconfirmed") and the mDNS section's conclusion
- [ ] Ch 13 | src/chapters/13-wifi-http-agent-link/07-ask-buddy-display.py | With the server stopped, time from "asking..." to "error"; check no text spills the 15-character status or 30-character message regions | Ch13 "Showing the Link on the Display"

## Chapter 14 (Streaming, Security, Resilience)

- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/03-record-utterance.py | Record worst_us and average per 20 ms read, peak and rms, heap before/after the 128,000-byte buffer | Ch14 "Recording an Utterance" (the claim that the live conversion fits 20,000 us is an expectation based on ch8's ~10 ms per 512 samples); if over budget the chapter must say to use the test-07 record-then-convert method with a 3 s limit
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/01-chunk-arithmetic.py | Run on the Pico; record the free heap and which recordings fit (3 s and 5 s at 16 and 32 bit, 10 s at 16 bit) | Ch14 recording-size table, Chunk-Size and Heap Explorer spec (its F values and 40,000-byte reserve are labelled illustrative)
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/04-upload-voice.py | With the HTTP server, 1 s and 5 s holds: record ms, upload+server ms, first-audio ms, heap; press MODE mid-answer and note how fast it stops | Ch14 barge-in estimate (~80 ms stop is arithmetic only), Chunked Audio Upload worked example, any latency claim
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/04-upload-voice.py | Try `UPLOAD_CHUNK_BYTES` 512, 1024, 2048, 4096, 8192 and compare upload times | Ch14 "Audio Chunk Size" table (the TCP-segment column assumes a 1,460-byte MSS and was not measured) and the defaults 2,048 and 1,024
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/05-timeouts-and-failures.py | Record ms for each of the six cases on the school network; check whether an unreachable address times out or fails immediately | Ch14 Timeouts table (the 10,000, 50,000 and 200,000 bytes/s upload speeds are assumptions) and TOTAL_TIMEOUT_S=20 reasoning
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/05-timeouts-and-failures.py | Confirm the errno values MicroPython raises for refused, timeout and unreachable (`buddy_http.classify` relies on `errno.ETIMEDOUT/ECONNREFUSED/EHOSTUNREACH/ECONNRESET`) | Ch14 Failure Kinds table
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/06-retry-fallback.py | Stop the server and time MODE-to-OFFLINE; compare with the 35.5 s worst case; check `events_cache.json` is not rewritten when unchanged | Ch14 Retry and Backoff worst-case discussion, Offline Fallback section
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/07-tls-probe.py | Record connect ms and heap used for plain HTTP, HTTPS with CERT_NONE, and HTTPS with `ca.der`; check the damaged cert is refused; check whether `CERT_REQUIRED` accepts a certificate whose SAN is an IP address; check the date check with and without NTP/`mpremote rtc --set` | Ch14 TLS cost paragraph (only the 20,480-byte buffer floor, 16,384 in + 4,096 out, is given, from the master-branch mbedTLS config), Certificate Handling table and "What Is Untested" list
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/07-tls-probe.py | Verify the firmware's actual `ssl` behavior (TLS 1.2 only? `load_verify_locations(cadata=DER bytes)` ok?) against the firmware version in use | Ch14 TLS paragraph ("TLS 1.2 and earlier, no TLS 1.3"), `buddy_http._wrap`
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/08-websocket-stream.py | Run from the Pico against `server/ws_server.py`: does `wsclient.py` connect, does the big-integer mask in `_xor_mask` work and run fast, does the `hashlib.sha1`/`binascii` handshake pass, "slowest frame" us | Ch14 "Streaming Over a WebSocket" (whole section is untested on the device); also re-check that MicroPython's built-in `websocket` still does not mask client frames on the firmware in use
- [ ] Ch 14 | src/chapters/14-streaming-security-resilience/08-websocket-stream.py | Measure the slowest `send_binary` during recording versus the ring buffer's ~0.4 s limit; test a stall | Ch14 WebSocket paragraph about lost audio
- [ ] Ch 14 | bench | Install a real STT and TTS provider (school-approved), measure server-side latency for a 3 s utterance and the returned audio format; fill in `service_transcribe`/`service_synthesize` | Ch14 STT/TTS sections (everything about services is stub-based; no real recognition was tested)
- [ ] Ch 14 | bench | Reverse proxy (Caddy or nginx) with a real certificate in front of `buddy_server.py` and the Pico trusting its CA | Ch14 "What the Book Recommends" paragraph (described, not built or tested)
- [ ] Ch 13/14 | bench | Check Pico 2 W firmware (MicroPython 1.2x) for `mip.install("requests")` size/heap, and re-verify version-specific facts read from master docs (`requests` 1.1.1 calls `CERT_NONE` for HTTPS; ssl docs; `network_cyw43` status mapping) against the firmware release you ship | Ch13 requests section; Ch14 TLS section

## Chapter 15 (MQTT and Push Alerts)

- [ ] Ch 15 | src/chapters/15-mqtt-push-alerts/04-check-msg-cost.py | Run on the board with a real broker; record idle `check_msg()` average and slowest, and the slowest delivery pass (us) | "The Frame Budget" ends with an unmeasured expectation that both are small next to 40 ms; replace it with the numbers (Ch 18's scheduler demo also assumes 2.0 ms for `network`)
- [ ] Ch 15 | .../06-alert-audio-loop.py | Record "worst work" in the second an alert arrives, any overruns, and (Try This 1) how long a failed connect froze the loop with the broker stopped | Connect-timeout table and "Frame Budget" points 4 and 5 (model based on Ch 8's 9.77-frame ring), the test 06 worked example, and the 290 ms deaf-time arithmetic
- [ ] Ch 15 | .../08-echo-rtt.py (with server/echo_responder.py) | Measure fastest, median and slowest round trip on the school Wi-Fi | Delivery table's "one trip through the broker" row and the sentence saying the push speed is not known
- [ ] Ch 15 | .../07-status-heartbeat.py | Unplug the Pico and time how long until Mosquitto publishes `offline` | "Last Will and Keep-Alive" section, the status table row "about 45 s", and the 1.7 s toy-broker figure
- [ ] Ch 15 | .../02-mqtt-hello.py | Run with `SEND_PINGS = False` against Mosquitto and confirm a drop at about 45 s | Keep-alive worked example (toy-broker-only evidence)
- [ ] Ch 15 | bench: school Raspberry Pi | Install Mosquitto with `server/mosquitto.conf` and `study-buddy.acl`, then check: password file permissions, `%u` ACL patterns, `message_size_limit` behaviour, LAN-only listener, persistence default on Pi OS, `ufw` rule | The whole "Mosquitto on a School Raspberry Pi" section, the status-table persistence row, and the README caveats
- [ ] Ch 15 | bench: Mosquitto plus paho-mqtt 2.x | Run `publish_alert.py`, `watch.py`, `echo_responder.py` and `ha_discovery.py` against the real broker (retain, `--clear`, ACL denials) | Claims that these tools work (today verified only against a toy broker)
- [ ] Ch 15 | server/home-assistant.yaml and server/ha_discovery.py | Try the sensors, discovery payloads and the `mqtt.publish` automation in a real Home Assistant | Home Assistant section, including the "broker must support MQTT 5" note and the ghost-entity caveat
- [ ] Ch 15 | bench: Pico plus real firmware | Confirm `mpremote mip install umqtt.simple`, that `connect(timeout=)` exists in the installed version, and `json.loads(bytes.decode())` behaviour | Install paragraph and the umqtt API table
- [ ] Ch 15 | .../03-link-listener.py | Kill Wi-Fi silently (router off) and confirm the 45 s dead-link detection and Wi-Fi recovery on the real board | "Last Will and Keep-Alive" silent-drop paragraph and the Reconnecting paragraph

## Chapter 16 (Configuring the School Agent and Calendar)

- [ ] Ch 16 | src/chapters/16-school-agent-calendar/02-edition-splash.py and 01-show-school-mascot.py | Run on the glass; record draw time and whether name, slogan and mascot are clipped | Splash printout (fake layer only) and the 38.4 ms wire-time statement
- [ ] Ch 16 | .../03-briefing-display.py with server/push_daily.py --send | Run end to end over the real broker; check page timing and readability, and that a repeated briefing id is dropped | Briefing paging description and the "ignored second run" claim
- [ ] Ch 16 | bench: real feeds (Google secret iCal address, Outlook, Apple) | Run `check_config.py` against real feeds; check Windows zone names, RRULE, folding, and whether the feed sends ETag or Last-Modified | Parser limitations list, polling section, and the "Your Feed Is Not Cedar Ridge's" warning
- [ ] Ch 16 | bench: Ch 12 and the board | After Ch 12 is final, enroll a non-default phrase (for example "Hey Gale") and measure false accepts | Custom wake phrase section (assumes Ch 12's template matcher, enrollment, threshold, window length, single-speaker limits) and the syllable-count hint
- [ ] Ch 16 | server/calendar_brain.py with Ch 14's final server | Re-run the drop-in with the final Ch 14 server, including the WebSocket path and the Pico's offline cache | "Asking the Calendar" paragraph describing the drop-in
- [ ] Ch 16 | bench: Ch 14 text-to-speech | Speak a 300-character briefing and time it | Briefing paragraph on the 300-character limit and the Try This in script 03

## Chapter 17 (Privacy, Safety, and Responsible Listening)

- [ ] Ch 17 | src/chapters/17-privacy-responsible-listening/01-mute-switch.py | Wire a two-pole slide switch (one pole in microphone VDD, one pole GP9 to GND). Record the `spread` printed while microphone power is cut, and check VDD reads about 0 V on a multimeter | Ch 17 "The Hardware Mute Switch" and the warning box (no number is claimed yet); the VDD-cut and unpowered-clock-pin caveat; README
- [ ] Ch 17 | .../02-indicator-demo.py | Press and release MODE 20 times, note any moment the LED and status bar disagree with the button, and check the 120x20 "LISTENING" bar is readable from about 3 m | Ch 17 "The Listening Indicator" (visibility is unverified); README
- [ ] Ch 17 | .../04-wipe-buffers.py | Record "wipe ms" for the 150 KB buffer on the Pico | Ch 17 "Audio Not Stored" (text says only "takes a moment")
- [ ] Ch 17 | bench (network monitor) | Confirm no audio leaves the device before a MODE press (push-to-talk), and before the wake word (always-on) | Ch 17 always-on checklist step 5; data-flow table hops 1 and 2
- [ ] Ch 17 | bench (server) | Check the real Ch 13, 14, 15, 16 server defaults for logging, speech-service retention and retained MQTT messages | Ch 17 "Tracing One Question" table and the Data Flow Explorer spec (a recommended design, not measurements)
- [ ] Ch 17 | school privacy officer or counsel | Review the plan template and the Cedar Ridge example. Confirm the FERPA, COPPA, SOPIPA, BIPA and GDPR wording. FERPA was checked only against secondary university pages. SOPIPA and BIPA were written from memory with no web check. COPPA voice-as-personal-information and the 2023 Amazon Alexa settlement were web-verified | Ch 17 "Student Privacy Law" and "Transcript Handling"
- [ ] Ch 17 | classmates and teacher | Argue with the threat likelihood, impact and effort ratings (they are labelled judgments) and adjust them | Ch 17 threat table, the Threat Model Sorter spec ("Fix position" column), `tools/threat_model.py`

## Chapter 18 (Testing, Integration, and Capstone Projects)

- [ ] Ch 18 | src/chapters/18-testing-integration-capstones/selftest.py | Run on the full kit and record each check's "ms". Check the speaker-to-microphone loopback passes at `MIN_RISE_BITS` 2.0 (half of the ch 8 figure of 3.9 bits, measured at volume 40; the probe now plays at most 30%) | Ch 18 self-test table and speaker-check paragraph; README
- [ ] Ch 18 | .../02-display-probe.py | Record the three fill times (ch 5 measured 129 ms) and how long `shapes.ring()` takes for the self-test pattern | Ch 18 probe table; self-test display step
- [ ] Ch 18 | .../08-scheduler-demo.py | Replace the two assumed costs, `buttons` 0.5 ms and `network` 2.0 ms (ch 15's `04-check-msg-cost.py` measures `check_msg`), and re-run the four scenarios | Ch 18 "The Time Budget in Numbers": 19.0, 21.0 and 27.8 ms, the scenario table, and the Frame Budget Scheduler Timeline spec costs and totals
- [ ] Ch 18 | .../10-clap-detector.py | Record the distance at which claps stop counting (0.5, 1, 2, 4 m), the real peak above the floor in bits, and whether the 2.0-bit jump is right | Ch 18 "Clap Detector" (the sensitivity table is synthetic)
- [ ] Ch 18 | .../11-noise-monitor.py | Record the floor and the smoothed level during silent work, group work and a loud moment | Ch 18 "Classroom Noise Monitor" (the +2.0 and +4.0 bit band limits are starting values)
- [ ] Ch 18 | .../12-study-timer.py | Time a 5-minute focus period with a stopwatch, and check that the blocking beep (about 0.57 s) does not drop button presses | Ch 18 "Study Timer Buddy"
- [ ] Ch 18 | .../13-homework-reminder.py | Copy the trimmed `events.json` to the Pico and confirm it parses and fits in memory | Ch 18 "Homework Reminder Buddy" (file sizes were measured on a computer)
- [ ] Ch 18 | 10-clap-detector.py and 11-noise-monitor.py on the Pico | Run each for 60 s and record the `OverrunCounter` summary | Ch 18 reliability claims and the "plain-Python loudness is about 10 ms" assumption in the budget table
- [ ] Ch 18 | .../user-test-sheet.md | Run the protocol with three classmates on one capstone | Ch 18 "User Testing" (its worked example is labelled invented)

