#!/usr/bin/env python3
"""Chapter 17: a teen-friendly threat model. Each threat gets a likelihood and
an impact from 1 (low) to 3 (high), and the risk score is likelihood x impact.

The 1-to-3 numbers are REASONED JUDGMENTS for a school classroom, written so
you can argue with them. They are not statistics. Change them to match your
school and see the order change.

Run:  python3 threat_model.py
"""

# id, short name, STRIDE-lite kind, asset, actor, surface, likelihood, impact, first defense, effort to fix (1 easy .. 3 hard)
THREATS = [
    ("T1", "Mic left open with no indicator", "Information disclosure",
     "what students say", "a bug in our own code", "microphone code path", 2, 3,
     "Listener owns the mic; 03-indicator-test.py", 2),
    ("T2", "Eavesdropping on plain HTTP", "Information disclosure",
     "audio and questions", "someone on the same Wi-Fi", "the school network", 2, 3,
     "HTTPS (Ch. 14); trusted network only", 2),
    ("T3", "Exposed MQTT broker", "Spoofing / tampering",
     "alerts, device status", "anyone on the internet", "broker port", 2, 3,
     "no public port; username and password (Ch. 15)", 1),
    ("T4", "secrets.py committed to git", "Information disclosure",
     "Wi-Fi password, tokens", "anyone who can read the repo", "git history", 2, 3,
     ".gitignore + check_secrets.py; rotate if leaked", 1),
    ("T5", "Prompt injection in a calendar title", "Tampering / elevation",
     "what the agent does", "anyone who can add an event", "calendar text", 2, 2,
     "text is data; allow-list; no send tools", 2),
    ("T6", "Server logs keep audio or transcripts", "Information disclosure",
     "recordings, transcripts", "an admin, or whoever gets the disk", "server log folder", 3, 2,
     "audio never written; retention sweep", 1),
    ("T7", "Always-on turned on without approval", "Repudiation / policy",
     "students' trust", "a well-meaning builder", "the settings menu", 1, 3,
     "approval checklist; default is push-to-talk", 1),
    ("T8", "Lost or stolen device", "Information disclosure",
     "stored secrets, settings", "whoever finds it", "the flash chip", 2, 2,
     "short-lived token; rotate on loss", 2),
    ("T9", "Cloud vendor keeps recordings", "Information disclosure",
     "audio, transcripts", "the vendor, its staff", "STT/LLM/TTS service", 2, 3,
     "choose local or school-hosted; read the terms", 3),
    ("T10", "Someone else's voice triggers the device", "Spoofing",
     "the device's actions", "a classmate", "wake-word detector", 3, 1,
     "push-to-talk; confirm side effects", 1),
]

def main():
    rows = []
    for t in THREATS:
        rows.append((t[6] * t[7], t[0], t[1], t[2], t[6], t[7], t[8], t[9]))
    # fix order: highest score first; among equals, the easiest fix first
    rows.sort(key=lambda r: (-r[0], r[7], int(r[1][1:])))
    print("{:<4} {:<42} {:>2} {:>2} {:>5} {:>6}  {}".format(
        "id", "threat", "L", "I", "score", "effort", "first defense"))
    for score, tid, name, kind, l, i, defense, effort in rows:
        print("{:<4} {:<42} {:>2} {:>2} {:>5} {:>6}  {}".format(
            tid, name, l, i, score, effort, defense))
    print()
    counts = {}
    for r in rows:
        counts[r[0]] = counts.get(r[0], 0) + 1
    print("score counts:", ", ".join("{}: {}".format(k, counts[k]) for k in sorted(counts, reverse=True)))
    print("Fix order = highest score first; among equal scores, the easiest fix first.")

if __name__ == "__main__":
    main()
