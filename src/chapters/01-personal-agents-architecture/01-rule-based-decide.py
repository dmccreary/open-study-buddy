# Chapter 1, Test 01: A rule-based agent in a few lines
# Runs on your COMPUTER (python3 01-rule-based-decide.py) or on the Pico. It
# needs no hardware. It is the `decide()` function from the chapter, plus a
# tiny stand-in for the school calendar so you can try the two questions in
# the "Rule-Based Agents" worked example.
#
# PASS: the first question gets a real answer, the second falls through to the
# apology (the gap that an LLM-backed brain closes), and the last line says PASS.

NAME = "01-rule-based-decide.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))


class Event:
    def __init__(self, title, day):
        self.title = title
        self.day = day


EVENTS = [
    Event("DUE: Lab report", "Thursday"),
    Event("TEST: Biology", "Friday"),
    Event("TEST: Algebra", "next Tuesday"),
]


def next_event_with_prefix(events, prefix):
    """Chapter 16 builds the real one. This returns the first match, with the
    prefix removed from the title."""
    for event in events:
        if event.title.startswith(prefix):
            return Event(event.title[len(prefix):].strip(), event.day)
    return None


def decide(text, events):
    words = text.lower()
    if "test" in words:
        event = next_event_with_prefix(events, "TEST:")
        return f"Your next test is {event.title} on {event.day}."
    if "due" in words:
        event = next_event_with_prefix(events, "DUE:")
        return f"{event.title} is due on {event.day}."
    return "Sorry, I only know about tests and due dates."


questions = (
    "When is my next test?",
    "What is due this week?",
    "Do I have anything big coming up this week?",
)
answers = []
for question in questions:
    answer = decide(question, EVENTS)
    answers.append(answer)
    print()
    print("Student:", question)
    print("Buddy  :", answer)

print()
if (answers[0] == "Your next test is Biology on Friday."
        and answers[1] == "Lab report is due on Thursday."
        and answers[2].startswith("Sorry")):
    print("PASS: rules answered what they anticipated and apologized for the rest.")
else:
    print("CHECK: an answer is not what the chapter shows.")

# Try This
#   1. Add a rule for the word "homework". What does the agent say about the
#      question "Is there homework tonight?" before and after?
#   2. Reword the first question: "Any exams soon?" Why does it fall through?
