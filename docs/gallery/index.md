---
title: Sample Gallery
description: Every sample program for the Open Study Buddy in one place - the labs, the finished demos, sixteen smart clock faces, and ideas for future samples - each with a screenshot and a difficulty level.
image: /gallery/img/demo-showcase.png
og:image: /gallery/img/demo-showcase.png
hide:
    toc
---

# Sample Gallery

Every program you can run on the Study Buddy, with a picture of what it puts
on the round screen. Use it to find a sample to try, a program to take apart,
or an idea for your own project.

**76 samples in all:** 47 that run today and 29 ideas waiting to be built.

| Section | Samples |
|---|---:|
| [The Labs](#the-labs) | 19 |
| [The Demos](#the-demos) | 12 |
| [Smart Clock Faces](#smart-clock-faces) | 16 |
| [Future Clock Faces](#future-clock-faces) | 16 |
| [Future Study Tools](#future-study-tools) | 13 |
| **Total** | **76** |

Each card has a difficulty level:

<span class="osb-level osb-beginner">Beginner</span> short programs, one
idea, nothing to change before you run them.<br/>
<span class="osb-level osb-intermediate">Intermediate</span> several ideas
together: timing, state machines, sound, or the network.<br/>
<span class="osb-level osb-advanced">Advanced</span> programs that manage
memory, signal processing, or many modes at once.<br/>
<span class="osb-level osb-idea">Idea</span> a sample nobody has written
yet. Its picture is concept art, not a screenshot.

The screenshots of the labs, demos, and clock faces come from their real
MicroPython code, run through a desktop simulator of the GC9B72 display.
[`scripts/render-gallery-images.py`](https://github.com/dmccreary/open-study-buddy/blob/main/scripts/render-gallery-images.py)
makes every image on this page again after a program changes.

## The Labs

Nineteen short programs in [`src/kits/study-buddy-base`](https://github.com/dmccreary/open-study-buddy/tree/main/src/kits/study-buddy-base). Labs 01 to 07 check each part as you wire it; labs 08 to 19 teach one idea each. Every card links to the lab's page.

<div class="grid cards" markdown>

-   **[Lab 01: Blink the Onboard LED](../kits/study-buddy-base/01-blink.md)**

    ![The Pico 2 W on the kit's breadboard, wired to the display, buttons, and audio boards](img/lab-01-blink.png){ .osb-screen }

    Make the Pico's own LED blink. The first proof that your board, cable, and MicroPython all work.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 02: The Hardware Probe](../kits/study-buddy-base/02-probe.md)**

    ![The shell output of the hardware probe: board, RAM, and flash reports](img/lab-02-probe.png){ .osb-screen }

    A checkup that reports the board, memory, flash, and every wire it can test, and warns about the ones that look wrong.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 03: Buttons on the Console](../kits/study-buddy-base/03-buttons.md)**

    ![The shell showing MODE, UP, and DOWN press and release messages, then PASS](img/lab-03-buttons.png){ .osb-screen }

    Press MODE, UP, and DOWN and watch each press and release appear in the shell.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 04: Hello World on the Display](../kits/study-buddy-base/04-hello-world.md)**

    ![Hello World in yellow inside a cyan ring on the round display](img/lab-04-hello-world.png){ .osb-screen }

    The smallest program that lights up the round 360 x 360 screen.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 05: Speaker Tones](../kits/study-buddy-base/05-speaker-tones.md)**

    ![The shell listing a beep, a C major scale, and three volume levels](img/lab-05-speaker-tones.png){ .osb-screen }

    A beep, a musical scale, and three volumes from the I2S amplifier and speaker.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 06: Listen with the Microphone](../kits/study-buddy-base/06-listen-meter.md)**

    ![A green level meter under the words Say Hey Pico, with I hear you below](img/lab-06-listen-meter.png){ .osb-screen }

    A live loudness meter that measures the quiet room first, then reacts when you talk.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 07: Hold to Record, Release to Play Back](../kits/study-buddy-base/07-record-playback.md)**

    ![RECORDING in red with a progress bar filling](img/lab-07-record-playback.png){ .osb-screen }

    Hold MODE and talk; let go and hear yourself. The first program that uses every part of the kit.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 08: How the Display Mixes Color](../kits/study-buddy-base/08-color-mixing.md)**

    ![A rainbow ring around red, green, and blue bars labeled with their bit counts](img/lab-08-color-mixing.png){ .osb-screen }

    RGB565 explained on the glass: 5 bits of red, 6 of green, 5 of blue.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Lab 09: Angles to Pixels](../kits/study-buddy-base/09-angles-to-pixels.md)**

    ![A clock face with 60 tick marks and a red hand, with its angle and x, y shown](img/lab-09-angles-to-pixels.png){ .osb-screen }

    Use sine and cosine to turn an angle into a point. The math behind every analog clock face.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 10: Flicker-Free Text](../kits/study-buddy-base/10-flicker-free-text.md)**

    ![Three counters comparing erase-then-draw, overwrite, and only-what-changed](img/lab-10-flicker-free-text.png){ .osb-screen }

    Three ways to update a number, raced side by side, so you can see why sending less is faster.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 11: What a Button Press Really Looks Like](../kits/study-buddy-base/11-button-bounce.md)**

    ![Counts of changes, naive presses, and real presses for each of the three buttons](img/lab-11-button-bounce.png){ .osb-screen }

    Count the extra presses a bouncing contact makes, then fix them with debouncing.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 12: One Loop, Many Jobs](../kits/study-buddy-base/12-one-loop-many-jobs.md)**

    ![A seconds counter, loops per second, and a moving dot](img/lab-12-one-loop-many-jobs.png){ .osb-screen }

    Blink, count, animate, and read buttons at once by checking the clock instead of sleeping.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 13: Modes as a State Machine](../kits/study-buddy-base/13-modes-state-machine.md)**

    ![A COLOR, COUNT, and DICE mode bar above a big orange circle](img/lab-13-modes-state-machine.png){ .osb-screen }

    MODE steps through three modes held in a table of states, the pattern every demo uses.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 14: Samples Make Sound](../kits/study-buddy-base/14-samples-make-sound.md)**

    ![A dotted 440 Hz sine wave with 36.4 samples per cycle](img/lab-14-samples-make-sound.png){ .osb-screen }

    Build a sine wave one number at a time and hear what sample rate and aliasing do.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 15: Envelopes](../kits/study-buddy-base/15-sound-envelopes.md)**

    ![The PLUCK envelope: a curve that falls quickly over 500 ms](img/lab-15-sound-envelopes.png){ .osb-screen }

    Play the same notes as a pluck, an organ, and more, and see each envelope's shape.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 16: A Microphone Oscilloscope](../kits/study-buddy-base/16-mic-oscilloscope.md)**

    ![A green sound wave on a scope grid with offset, peak, zoom, and trigger readouts](img/lab-16-mic-oscilloscope.png){ .osb-screen }

    Watch the sound the microphone hears as a live wave, with DC offset, gain, and a trigger.

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Lab 17: A Whistle Tuner](../kits/study-buddy-base/17-whistle-tuner.md)**

    ![880 Hz and the note A5 above a flat-to-sharp needle that is centered](img/lab-17-whistle-tuner.png){ .osb-screen }

    Whistle a note and see its frequency, its name, and how many cents sharp or flat you are.

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Lab 18: From Radio Waves to the Weather](../kits/study-buddy-base/18-network-layers.md)**

    ![Five network layers, each marked OK, ending with 64 F and wind 7 mph](img/lab-18-network-layers.png){ .osb-screen }

    WiFi, an IP address, NTP time, HTTP, and JSON, checked off one layer at a time.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Lab 19: Pattern Memory Game](../kits/study-buddy-base/19-pattern-game.md)**

    ![Red, green, and blue wedges around READY, press a button](img/lab-19-pattern-game.png){ .osb-screen }

    Repeat a growing pattern of colored wedges and notes. A game that uses everything before it.

    <span class="osb-level osb-advanced">Advanced</span>

</div>

## The Demos

Eleven demos and the showcase that ties them together. Copy `main.py` to the Pico and they run at power-up. See [The Finished Demo](../kits/study-buddy-base/intro.md#the-finished-demo) for the buttons.

<div class="grid cards" markdown>

-   **[The Showcase](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![The welcome screen listing the Pico 2 W, display, buttons, speaker, and microphone](img/demo-showcase.png){ .osb-screen }

    The power-up screen. It steps through every demo; hold any button to try one. Each demo loads only while it is on screen.

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Clock and Weather](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![10:09 AM with today's and tomorrow's forecast icons and temperatures](img/demo-clock.png){ .osb-screen }

    Sets its own time over WiFi and shows a two-day forecast with weather icons.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Alarm Clock](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![The alarm clock: 10:09 now, alarm at 10:10 AM, ON, rings in 1 min](img/demo-alarm.png){ .osb-screen }

    Set the alarm with three buttons. It rings from any demo when it is due.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Countdown Timer](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![A timer running at 00:10 in big red digits, with a cyan tick ring](img/demo-timer.png){ .osb-screen }

    Presets, a tick ring that counts down, and an alarm that keeps going after you leave.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Stopwatch](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![A running stopwatch at 00:06.74 with two laps, the best lap, and the average](img/demo-stopwatch.png){ .osb-screen }

    Start, stop, and laps, with the best and average lap times.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[School Calendar](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![Owl Buddy with the owl mascot and this week's school events](img/demo-school.png){ .osb-screen }

    A school mascot and this week's events. The school-generator skill makes one for your school.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Sound Lab](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![SQUARE 440 Hz with a square wave drawn below](img/demo-tones.png){ .osb-screen }

    Hear sine, square, triangle, and sawtooth waves, octaves, and a tune.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Sound Meter](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![A curved VU meter with green bars lit and 75 dB in the middle](img/demo-listen.png){ .osb-screen }

    A curved VU meter with peak hold that responds to talking, clapping, and whistling.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Record and Play](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![Press UP, then talk for 3 seconds](img/demo-record.png){ .osb-screen }

    Record three seconds and play them back. The recording buffer alone needs 150 KB.

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Quote of the Day](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![Quote of the day: Small steps, tested often, build big programs](img/demo-quote.png){ .osb-screen }

    A new quote each day, word-wrapped to fit the round glass.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Spanish Quiz](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![Spanish quiz choices red, sun, green, house, with red highlighted](img/demo-spanish.png){ .osb-screen }

    Hear a Spanish word through the speaker and pick its meaning.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Vocabulary Flash Cards](../kits/study-buddy-base/intro.md#the-finished-demo)**

    ![A flash card showing the word algorithm and a question mark](img/demo-vocab.png){ .osb-screen }

    See a word, think of its meaning, then press MODE to flip the card.

    <span class="osb-level osb-beginner">Beginner</span>

</div>

## Smart Clock Faces

These faces come from the [Clocks and Watches](https://dmccreary.github.io/clocks-and-watches/)
book, from three kits that use the same 2.1-inch round GC9B72 display: the
Chrono Smart Clock, the Big Round Speaker Clock, and the Railway Clock. Each
card links to the lab that builds it.

!!! note "Moving a face to the Study Buddy"
    All three clock kits wire the display to the same pins as the Study
    Buddy (GP2 to GP7), but their buttons are on GP13 to GP15, and the Study
    Buddy's are on GP16 to GP18. Run a face with the Study Buddy's own
    `config.py`, not the clock kit's. If the face reads a setting this kit's
    `config.py` does not have, copy that one line across. These faces have
    not yet been run on Study Buddy hardware.

<div class="grid cards" markdown>

-   **[Digital Clock](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/03-digital-clock/)**

    ![A large digital time and date](img/clock-digital.png){ .osb-screen }

    The time, the day of the week, and the date, updated every second.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Analog Watch Face](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/05-analog-watch-face/)**

    ![An analog watch face with hour, minute, and second hands](img/clock-analog.png){ .osb-screen }

    Sixty tick marks, the numbers 1 to 12, and moving hour, minute, and second hands.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Set the Time](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/07-set-time/)**

    ![A time-setting screen with the hour highlighted](img/clock-set-time.png){ .osb-screen }

    Set the hours and minutes with the buttons when there is no WiFi.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Digital Watch Face](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/08-digital-watch-face/)**

    ![A digital watch face with a ring of second ticks](img/clock-digital-watch.png){ .osb-screen }

    Digits 114 pixels tall inside a ring of 60 ticks that fills as the seconds pass.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Weather Clock](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/09-weather-clock/)**

    ![The time with today's and tomorrow's weather icons](img/clock-weather.png){ .osb-screen }

    The time plus today's and tomorrow's forecast from Open-Meteo, a free service with no account.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Stopwatch Face](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/10-stopwatch/)**

    ![A stopwatch face showing elapsed time and laps](img/clock-stopwatch.png){ .osb-screen }

    Minutes, seconds, and hundredths, with a lap time each time you press a button.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Countdown Face](https://dmccreary.github.io/clocks-and-watches/kits/sw-gc9b72/11-countdown-timer/)**

    ![A countdown timer face running down](img/clock-countdown.png){ .osb-screen }

    Set the minutes and seconds, then watch a ring around the edge count down to the alarm.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Big Clock](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![Giant digits filling the round screen](img/clock-big.png){ .osb-screen }

    The biggest digits that fit on the glass, readable across a room.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Time and Temperature](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![The time with the outside temperature](img/clock-temperature.png){ .osb-screen }

    The time with the temperature outside, refreshed every 30 minutes.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Time and Forecast](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![The time, 64 F partly cloudy, and highs and lows for two days](img/clock-forecast.png){ .osb-screen }

    Adds today's and tomorrow's highs, lows, and weather.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Alarm Face](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![An alarm clock face with the alarm time and on/off state](img/clock-alarm.png){ .osb-screen }

    An alarm with a choice of tones and an hourly chime.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Phrase of the Day](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![The time above a proverb about planting trees](img/clock-phrase.png){ .osb-screen }

    The time above a daily phrase that is the same for everyone on the same day.

    <span class="osb-level osb-intermediate">Intermediate</span>

-   **[Holiday Calendar](https://dmccreary.github.io/clocks-and-watches/kits/big-round-speaker-clock/09-ten-modes/)**

    ![A September 2026 calendar with Labor Day in red and today boxed](img/clock-holidays.png){ .osb-screen }

    A month calendar that works out holidays from rules like "the fourth Thursday in November".

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Swiss Railway Clock](https://dmccreary.github.io/clocks-and-watches/kits/mondaine/15-mondaine-clock/)**

    ![A white railway clock face with black hands and a red second hand](img/clock-railway.png){ .osb-screen }

    The station clock whose red second hand pauses at 12 until the minute hand jumps.

    <span class="osb-level osb-advanced">Advanced</span>

-   **[Railway Dial](https://dmccreary.github.io/clocks-and-watches/kits/mondaine/04-minute-markers/)**

    ![A white dial with bold hour bars and thin minute marks](img/clock-railway-dial.png){ .osb-screen }

    Just the dial: hour bars and minute marks placed with sine and cosine.

    <span class="osb-level osb-beginner">Beginner</span>

-   **[Smooth Sweep](https://dmccreary.github.io/clocks-and-watches/kits/mondaine/10-smooth-sweep/)**

    ![The railway clock with a smoothly sweeping second hand](img/clock-railway-sweep.png){ .osb-screen }

    A second hand that glides instead of ticking, redrawn many times a second.

    <span class="osb-level osb-intermediate">Intermediate</span>

</div>

## Future Clock Faces

Ideas for watch faces nobody has written yet. The pictures are concept art, drawn to show the idea, not screenshots of working code. Pick one and build it.

<div class="grid cards" markdown>

-   **Binary Clock**

    ![Rows of lit and dark dots for hours, minutes, and seconds](img/concept-binary-clock.png){ .osb-screen }

    Hours, minutes, and seconds as rows of lit dots. A direct way to practice binary.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Word Clock**

    ![A grid of letters with IT IS TEN PAST TEN lit in yellow](img/concept-word-clock.png){ .osb-screen }

    "IT IS TEN PAST TEN" lit on a grid of letters. The rules for saying the time become a table.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Fibonacci Clock**

    ![Colored squares of sizes 1, 1, 2, 3, and 5](img/concept-fibonacci-clock.png){ .osb-screen }

    Colored squares of size 1, 1, 2, 3, and 5 that add up to the hour and minutes.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Sun and Moon Dial**

    ![A 24-hour dial with a gold daylight arc and a sun marker](img/concept-sun-moon-dial.png){ .osb-screen }

    A 24-hour dial with daylight as a gold arc, using sunrise and sunset from Open-Meteo.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **World Clock**

    ![Three small analog dials for St. Paul, London, and Tokyo](img/concept-world-clock.png){ .osb-screen }

    Small dials for several cities, using the time-zone math in wifi_time.py.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Moon Phase**

    ![A waxing gibbous moon, 78% lit](img/concept-moon-phase.png){ .osb-screen }

    Today's moon phase, computed on the Pico with no web service.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Ring Clock**

    ![Three nested progress rings for hours, minutes, and seconds](img/concept-ring-clock.png){ .osb-screen }

    Three nested arcs fill as the hour, minute, and second go by.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Roman Numeral Face**

    ![A cream-colored analog face with Roman numerals](img/concept-roman-face.png){ .osb-screen }

    A classic cream dial with Roman numerals and a thin red seconds hand.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Nixie Tube Style**

    ![Glowing orange digits inside four glass tube outlines](img/concept-nixie.png){ .osb-screen }

    Orange digits glowing in drawn glass tubes, like a 1960s lab instrument.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Next Test Countdown**

    ![NEXT TEST: Biology in 2 d 4 h, with a magenta progress ring](img/concept-exam-countdown.png){ .osb-screen }

    Counts down to your next quiz or test and chimes a day before, whatever is on screen.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Bell Schedule**

    ![Colored arcs for class periods with Period 3, Algebra, 31 min left](img/concept-bell-schedule.png){ .osb-screen }

    Your class periods as colored arcs, with minutes left in this class and where you go next.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Pomodoro Focus Ring**

    ![FOCUS 18:42 inside a red ring that is three-quarters full](img/concept-pomodoro.png){ .osb-screen }

    A 25-minute focus timer with a 5-minute break and a dot for each session.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Minimal Dots**

    ![A navy face with twelve pastel dots and two thin hands](img/concept-minimal-dots.png){ .osb-screen }

    Twelve dots and two hands on navy. Shows how much a face can leave out.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Orbit Clock**

    ![A sun with a blue planet, a gray moon, and a red comet on three orbits](img/concept-orbit-clock.png){ .osb-screen }

    The hour is a planet, the minute a moon, and the second a comet on three orbits.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Day Progress**

    ![Progress bars for today, this week, the semester, and the year](img/concept-day-progress.png){ .osb-screen }

    How much of today, the week, the semester, and the year is already done.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Retro LCD Watch**

    ![Dark seven-segment digits on a green-gray LCD background](img/concept-retro-lcd.png){ .osb-screen }

    Seven-segment digits on a gray-green background, like a 1980s digital watch.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

</div>

## Future Study Tools

Ideas for samples that help with studying, several taken from the book's later chapters (FFT, wake words, MQTT, and the school agent). These are concept art too.

<div class="grid cards" markdown>

-   **Flash Quiz**

    ![A multiple-choice question: capital of Minnesota, with St. Paul highlighted](img/concept-flash-quiz.png){ .osb-screen }

    Multiple-choice decks, such as state capitals, that bring back the ones you miss.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Math Facts**

    ![7 x 8 = ? with three answer choices and a streak count](img/concept-math-facts.png){ .osb-screen }

    Times-table drills generated on the Pico, so no deck is needed.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Homework Checklist**

    ![Tonight's homework list with two of four items checked](img/concept-homework.png){ .osb-screen }

    Tonight's assignments, checked off with the buttons.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Mode Library**

    ![A list of installable modes with checkboxes](img/concept-mode-library.png){ .osb-screen }

    Browse and install new modes and quiz decks from a list your teacher publishes.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Push Alerts**

    ![A notification card: library book due tomorrow, from the media center](img/concept-push-alert.png){ .osb-screen }

    Reminders pushed from the school over MQTT, such as a library book due.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Hey Pico Wake Word**

    ![Hey Pico inside glowing cyan rings, heard you, ask away](img/concept-wake-word.png){ .osb-screen }

    Wakes up when it hears "Hey Pico" by matching sound features against a template of your voice.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Ask Your Buddy**

    ![A question about the science fair and the answer: Thursday at 6 PM in the gym](img/concept-ask-agent.png){ .osb-screen }

    Hold MODE, ask a question, and hear the school agent's answer.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Spectrum Analyzer**

    ![Colored frequency bars from 100 Hz to 8 kHz](img/concept-spectrum.png){ .osb-screen }

    Live frequency bars from the microphone, computed with an FFT.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-advanced">Advanced</span>

-   **Ear Trainer**

    ![A note on a staff and the choices C, E, and G](img/concept-note-trainer.png){ .osb-screen }

    Hear a note and name it. Practice for music class.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Metronome**

    ![A metronome with its pendulum swinging at 96 BPM](img/concept-metronome.png){ .osb-screen }

    A steady click with a swinging pendulum and adjustable beats per minute.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Breathing Coach**

    ![Breathe in 3 inside soft blue circles, round 2 of 5](img/concept-breathing.png){ .osb-screen }

    A circle that grows and shrinks to pace slow breathing before a test.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

-   **Library Voice Meter**

    ![A traffic light on yellow: a little loud, 62 dB](img/concept-noise-monitor.png){ .osb-screen }

    A traffic light that turns yellow and red when a study room gets loud.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-intermediate">Intermediate</span>

-   **Dice and Picker**

    ![A white die showing five, you rolled 5](img/concept-dice.png){ .osb-screen }

    Roll one or two dice, or pick who goes first.

    <span class="osb-level osb-idea">Idea</span><span class="osb-level osb-beginner">Beginner</span>

</div>

## Add Your Own

Built something new? A sample belongs in this gallery when it runs on the
base kit and has a picture of its screen. Add a line for it to
`scripts/render-gallery-images.py`, run the script, and add a card to this
page. If your program is one of the ideas above, replace its concept art with
the real screenshot and drop the Idea badge.
