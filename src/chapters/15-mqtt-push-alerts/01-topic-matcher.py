# Chapter 15, Test 01: Which subscriptions does a topic reach?
# Runs on your COMPUTER (python3 01-topic-matcher.py) or on the Pico. It needs
# no hardware and no broker. It checks topics.py (the book's topic scheme and
# the "+" and "#" matcher) against the table in the chapter: eight topics
# against seven subscription filters, with the answers written by hand.
#
# PASS: every row matches its hand-written answer, the scheme's names print,
# and the last line says PASS.

NAME = "01-topic-matcher.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import topics

FILTERS = (
    "school/crhs/alert",                 # S1 school-wide alerts, one school
    "school/crhs/class/214/alert",       # S2 one classroom
    "school/crhs/class/+/alert",         # S3 any classroom
    "school/crhs/device/+/status",       # S4 every device's status
    "school/crhs/#",                     # S5 everything about one school
    "school/+/alert",                    # S6 school-wide alerts, any school
    "#",                                 # S7 everything
)

# topic -> numbers of the filters (1-7) that must select it. Written by hand
# from the matching rules, NOT produced by the code under test.
CASES = (
    ("school/crhs/alert", (1, 5, 6, 7)),
    ("school/crhs/class/214/alert", (2, 3, 5, 7)),
    ("school/crhs/class/lab-130/alert", (3, 5, 7)),
    ("school/crhs/device/desk-07/status", (4, 5, 7)),
    ("school/crhs/device/desk-07/telemetry", (5, 7)),
    ("school/trhs/alert", (6, 7)),
    ("school/crhs", (5, 7)),
    ("$SYS/broker/uptime", ()),
)

problems = []

print()
print("{:<38}".format("topic") + " ".join("S%d" % n for n in range(1, 8)))
for topic, expected in CASES:
    got = tuple(n for n, f in enumerate(FILTERS, 1) if topics.topic_matches(f, topic))
    row = " ".join(" x" if n in got else " ." for n in range(1, 8))
    flag = "" if got == expected else "   <-- expected {}".format(expected)
    print("{:<38}{}{}".format(topic, row, flag))
    if got != expected:
        problems.append(topic)

print()
print("Filters:")
for n, f in enumerate(FILTERS, 1):
    print("  S{} {}".format(n, f))

# Names built by the scheme, and the rules for one level of a topic
print()
print("Names for school 'crhs', room 'Lab 130', device 'desk-07':")
room = topics.slug("Lab 130")
print("  school alert  :", topics.school_alert("crhs"))
print("  room alert    :", topics.room_alert("crhs", room))
print("  device status :", topics.device_status("crhs", "desk-07"))
print("  telemetry     :", topics.device_telemetry("crhs", "desk-07"))
if room != "lab-130":
    problems.append("slug('Lab 130') gave " + room)

BAD_FILTERS = ("school/#/alert", "school/crh+/alert", "", "a/b#")
for f in BAD_FILTERS:
    if topics.valid_filter(f):
        problems.append("accepted bad filter " + repr(f))
for f in ("a/b", "a/+", "a/#", "#", "+/+/+"):
    if not topics.valid_filter(f):
        problems.append("rejected good filter " + repr(f))

print()
if problems:
    for p in problems:
        print("PROBLEM:", p)
    print("CHECK: the matcher disagrees with the chapter's table.")
else:
    print("PASS: the matcher agrees with all {} hand-written rows.".format(len(CASES)))

# Try This
#   1. Add the filter "school/+/class/+/alert". Which of the eight topics does
#      it select? Write your guess down before you run it.
#   2. Is "school/crhs/#" the same as "school/crhs/+"? Add a topic that tells
#      them apart.
#   3. Why does "#" not select "$SYS/broker/uptime"?
