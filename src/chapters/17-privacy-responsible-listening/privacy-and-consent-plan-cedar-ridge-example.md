# Privacy and Consent Plan: Open Study Buddy (Cedar Ridge example)

> ILLUSTRATIVE ONLY. Cedar Ridge High School is a synthetic school, and every
> name, number, and policy reference below is invented to show how the template
> reads when it is filled in. It is not a real policy and not legal advice.
> Use your own school's policies and people.

## 1. Who and why

- **School and class:** Cedar Ridge High School, Physical Computing, Room 214
- **Plan owner:** Mr. Brandt, Physical Computing teacher
- **Date prepared:** 2026-10-19
- **Review date:** 2027-06-01
- **Purpose:** Ten desk devices let students ask about upcoming tests and due dates by pressing a button and speaking.
- **Who is near the microphone:** Students in grades 9 to 12 in Period 6 and Mr. Brandt.

## 2. Listening mode

- **Listening mode:** push-to-talk
- **Why this mode is needed:** The devices only need to hear a question after a student presses the Mode button.
- **Hardware mute and indicator:** Each device has a two-pole slide switch that cuts the microphone's 3V3 supply (true hardware mute) and reports the state to the program on GP9; the status bar shows LISTENING while the microphone is open and MIC OFF when muted.

## 3. Data

- **Data collected:** A few seconds of audio after each button press, its text, and the reply.
- **Audio stored:** no
- **Transcripts stored:** no
- **Retention days:** 0
- **Where processing happens:** school server in the library (a Raspberry Pi)
- **Outside services that receive data:** none; speech-to-text and text-to-speech run on the school server
- **Who can read transcripts or logs:** Mr. Brandt and the school IT administrator can read the server's error log, which contains no audio and no transcripts
- **Deletion process:** The IT administrator runs the retention sweep every night, which removes log files older than 7 days; the sweep's output is kept in the IT ticket queue

## 4. Safety

- **Agent permissions:** Read the school calendar and speak. No sending, no deleting, no web access.
- **Secrets handling:** Wi-Fi and server tokens live in secrets.py on each device and in environment variables on the server; secrets.py is in .gitignore and check_secrets.py passes before every commit
- **Network:** School Wi-Fi only; HTTPS between device and server; the MQTT broker accepts connections from the school network only, with a username and password
- **Incident contact:** Mr. Brandt, room 214, and the IT help desk

## 5. Notice and approval

- **Parent notice and opt-out:** A letter goes home before the unit starts. A student whose family opts out does not use a device and builds the project on a computer simulation instead, with no grade penalty.
- **Policies consulted:** Cedar Ridge Technology Use Policy and Student Data Policy (invented); reviewed by the school's privacy officer on 2026-10-12
- **School approval:** Assistant Principal Dr. Reyes, 2026-10-15
- **Parent consent record:** not required: push-to-talk only
- **Always-on approval:** not applicable
