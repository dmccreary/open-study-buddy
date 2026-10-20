# Privacy and Consent Plan: Open Study Buddy

> This is a planning worksheet, not legal advice. It does not replace your
> school's own policies, your district's technology and student-data rules, or
> the advice of your school's counsel or privacy officer. Fill it in, then give
> it to the people named under "Review and approval" BEFORE any device is used.
> Keep every field short and concrete. Write "none" instead of leaving a blank.

Check it with: `python3 tools/check_plan.py privacy-and-consent-plan-template.md`

## 1. Who and why

- **School and class:** <school name, class, room>
- **Plan owner:** <teacher or club adviser responsible for the devices>
- **Date prepared:** <YYYY-MM-DD>
- **Review date:** <YYYY-MM-DD, at most one school year after the date prepared>
- **Purpose:** <one sentence: what the device is for, in plain words>
- **Who is near the microphone:** <for example: students in grades 9 to 12 and one teacher>

## 2. Listening mode

- **Listening mode:** <push-to-talk | wake word (always-on)>
- **Why this mode is needed:** <one sentence; push-to-talk is the default>
- **Hardware mute and indicator:** <describe the mute switch type (software-visible or true hardware) and the listening indicator>

## 3. Data

- **Data collected:** <what the microphone and the agent handle, in a few words>
- **Audio stored:** <no | yes, N days>
- **Transcripts stored:** <no | yes, N days>
- **Retention days:** <number of days, 0 if nothing is kept>
- **Where processing happens:** <on the device | school server | cloud service (name it)>
- **Outside services that receive data:** <none | list each service and what it receives>
- **Who can read transcripts or logs:** <named roles, not "staff">
- **Deletion process:** <who deletes, how, how often, and how you know it happened>

## 4. Safety

- **Agent permissions:** <the actions the agent may take; for example read-only calendar>
- **Secrets handling:** <where passwords and tokens live; confirm they are not in git>
- **Network:** <school Wi-Fi only | HTTPS used | MQTT broker not reachable from the internet>
- **Incident contact:** <a person and a way to reach them>

## 5. Notice and approval

- **Parent notice and opt-out:** <how families are told, and what happens if they say no>
- **Policies consulted:** <your school or district policy names or numbers, and who at the school reviewed this plan>
- **School approval:** <name, role, date>
- **Parent consent record:** <where signed forms are kept, or "not required: push-to-talk only">
- **Always-on approval:** <not applicable | completed: name, role, date of each approval in the Always-on checklist>
