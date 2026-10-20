# scheduler.py -- Chapter 18: a cooperative scheduler with time budgets
#
# The main loop of the finished device:
#
#     sched = Scheduler(frame_us=40000)
#     sched.add("audio",   do_audio,   period_ms=40,   budget_ms=12)
#     sched.add("buttons", do_buttons, period_ms=40,   budget_ms=1)
#     sched.add("spectrum", draw_spec, period_ms=40,   budget_ms=9)
#     sched.add("status",  draw_status, period_ms=200, budget_ms=4)
#     while True:
#         mic.readinto(buf)      # blocks until a frame is ready: a pass starts here
#         sched.run_pass()       # runs every task that is due and fits
#
# COOPERATIVE means nothing can interrupt a task. Each task must return on its
# own, so a task's budget is a promise, not a limit the scheduler can enforce.
# What the scheduler CAN do:
#   - run tasks in the order they were added (earlier = more important)
#   - skip (defer) a due task whose budget does not fit in the time left in this
#     frame, for at most max_defer passes, so it cannot starve forever
#   - measure every run, and count a task that took longer than its budget
#   - count passes longer than a frame (the frame overrun counter, per pass)
#   - run SLICED tasks: a generator that does one small slice of a big job per
#     pass (a full-screen redraw in strips) and yields between slices
#
# Nothing here imports hardware, so it runs on a computer too.

import time


class Task:
    def __init__(self, name, fn, period_ms, budget_ms, sliced):
        self.name = name
        self.fn = fn
        self.period_us = int(period_ms * 1000)
        self.budget_us = int(budget_ms * 1000)
        self.sliced = sliced
        self.gen = None
        self.due = 0
        self.runs = 0
        self.total_us = 0
        self.worst_us = 0
        self.overruns = 0          # runs longer than budget
        self.deferred = 0          # consecutive deferrals right now
        self.defer_total = 0


class Scheduler:
    def __init__(self, frame_us=40000, max_defer=3):
        self.frame_us = frame_us
        self.max_defer = max_defer
        self.tasks = []
        self.passes = 0
        self.pass_overruns = 0     # passes whose work took longer than a frame
        self.worst_pass_us = 0
        self.last = []             # (name, us) of the tasks run in the last pass

    def add(self, name, fn, period_ms, budget_ms):
        self.tasks.append(Task(name, fn, period_ms, budget_ms, False))

    def add_sliced(self, name, make_job, period_ms, budget_ms):
        """make_job() returns a generator; each next() does one slice."""
        self.tasks.append(Task(name, make_job, period_ms, budget_ms, True))

    def run_pass(self):
        start = time.ticks_us()
        used = 0
        self.last = []
        for t in self.tasks:
            if time.ticks_diff(start, t.due) < 0:
                continue                                   # not due yet
            if t.budget_us > self.frame_us - used and t.deferred < self.max_defer:
                t.deferred += 1                            # does not fit this frame
                t.defer_total += 1
                continue
            t.deferred = 0
            t0 = time.ticks_us()
            finished = True
            if t.sliced:
                if t.gen is None:
                    t.gen = t.fn()
                try:
                    next(t.gen)
                    finished = False
                except StopIteration:
                    t.gen = None
            else:
                t.fn()
            dt = time.ticks_diff(time.ticks_us(), t0)
            used += dt
            t.runs += 1
            t.total_us += dt
            if dt > t.worst_us:
                t.worst_us = dt
            if dt > t.budget_us:
                t.overruns += 1
            if finished:
                t.due = time.ticks_add(t.due, t.period_us)
                if time.ticks_diff(start, t.due) > t.period_us:   # far behind: do not catch up
                    t.due = time.ticks_add(start, t.period_us)
            else:
                t.due = start                                    # run again next pass
            self.last.append((t.name, dt))
        self.passes += 1
        self.worst_pass_us = max(self.worst_pass_us, used)
        if used > self.frame_us:
            self.pass_overruns += 1
        return used

    def report(self):
        rows = []
        for t in self.tasks:
            rows.append((t.name, t.runs, t.total_us / max(1, t.runs) / 1000,
                         t.worst_us / 1000, t.budget_us / 1000, t.overruns, t.defer_total))
        return rows

    def print_report(self):
        print("{:<10} {:>5} {:>8} {:>8} {:>8} {:>8} {:>9}".format(
            "task", "runs", "avg ms", "worst ms", "budget", "over", "deferred"))
        for name, runs, avg, worst, budget, over, deferred in self.report():
            print("{:<10} {:>5} {:>8.1f} {:>8.1f} {:>8.1f} {:>8} {:>9}".format(
                name, runs, avg, worst, budget, over, deferred))
        print("passes {}, passes over one frame {}, worst pass {:.1f} ms".format(
            self.passes, self.pass_overruns, self.worst_pass_us / 1000))
