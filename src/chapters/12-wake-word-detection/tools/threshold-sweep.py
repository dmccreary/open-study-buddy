# Run this on your COMPUTER, not on the Pico.
#
#   python3 threshold-sweep.py results.txt
#   python3 threshold-sweep.py results.txt --seconds 90
#
# Reads the RESULT lines that ../08-threshold-sweep.py prints (copy them from
# the Thonny shell or from `mpremote run` into a text file; several runs can be
# in the same file, and other lines are ignored):
#
#   RESULT,wake,0.874,me,normal
#   RESULT,other,0.312,me,normal
#
# and prints, for each speaker and pace and for everything together, how many
# "Hey Pico" attempts would be missed (false rejects) and how many other
# attempts would be accepted (false accepts) at thresholds from 0.50 to 0.95.
# With --seconds N (the total seconds of non-wake audio you tested) it also
# turns false accepts into an hourly rate, with a warning about how rough that is.

import sys

THRESHOLDS = [round(0.50 + 0.05 * i, 2) for i in range(10)]


def read(path):
    rows = []
    for line in open(path):
        parts = line.strip().split(",")
        if len(parts) >= 3 and parts[0] == "RESULT":
            rows.append((parts[1], float(parts[2]),
                         parts[3] if len(parts) > 3 else "?", parts[4] if len(parts) > 4 else "?"))
    return rows


def table(title, rows, seconds):
    wake = [s for kind, s, _, _ in rows if kind == "wake"]
    other = [s for kind, s, _, _ in rows if kind == "other"]
    print()
    print("{}: {} wake attempts, {} other attempts".format(title, len(wake), len(other)))
    if not wake or not other:
        print("  (need both kinds to compute a table)")
        return
    print("{:>9} {:>16} {:>16} {:>14}".format("threshold", "false rejects", "false accepts", "FA per hour*"))
    for t in THRESHOLDS:
        fr = sum([1 for s in wake if s < t])
        fa = sum([1 for s in other if s >= t])
        per_hour = "{:.0f}".format(fa / (seconds / 3600)) if seconds else "-"
        print("{:>9.2f} {:>6} ({:>5.1f}%) {:>6} ({:>5.1f}%) {:>14}".format(
            t, fr, 100 * fr / len(wake), fa, 100 * fa / len(other), per_hour))
    if seconds:
        print("* from {:.0f} s of other audio that was held-button speech, not a quiet room or a"
              " classroom; a rough upper bound at best, not a field rate.".format(seconds))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 threshold-sweep.py results.txt [--seconds N]")
    seconds = 0.0
    if "--seconds" in sys.argv:
        seconds = float(sys.argv[sys.argv.index("--seconds") + 1])
    rows = read(sys.argv[1])
    if not rows:
        sys.exit("no RESULT lines found")
    table("All results", rows, seconds)
    groups = sorted(set([(r[2], r[3]) for r in rows]))
    if len(groups) > 1:
        for speaker, pace in groups:
            table("Speaker {}, pace {}".format(speaker, pace),
                  [r for r in rows if r[2] == speaker and r[3] == pace], 0)


if __name__ == "__main__":
    main()
