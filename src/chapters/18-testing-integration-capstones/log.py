# log.py -- Chapter 18: a small logger for a small computer
#
#   from log import Log, DEBUG, INFO, WARN, ERROR
#   log = Log(level=INFO, ring=40, path="log.txt", max_bytes=8192)
#   log.info("mic opened at %d Hz", 12800)
#   log.warn("frame overrun: %d us", 52000)
#   log.dump()              # print the last lines kept in RAM
#
# Three places a line can go, each with a different cost:
#   serial  : printed when its level >= level (what you see in Thonny)
#   RAM ring: EVERY line is kept in a ring of the last `ring` lines (cheap, and
#             lost when the power goes), so after something strange you can ask
#             "what just happened?" with dump()
#   flash   : lines at file_level (WARN by default) or above are appended to
#             `path`. Flash wears out and is slow (Chapter 2), so only the
#             rare, important lines go there, and the file is capped: when it
#             would pass max_bytes it is renamed to path + ".1" (replacing the
#             old .1) and a fresh file starts. Worst case: 2 x max_bytes of flash.
#
# Log levels, in plain words:
#   DEBUG  details you only want while hunting a bug
#   INFO   normal events worth knowing (started, connected)
#   WARN   something odd that the program recovered from
#   ERROR  something failed
#
# PRIVACY: never log audio or the words people said (Chapter 17). Log levels,
# counts, and codes.

import os
import time

DEBUG, INFO, WARN, ERROR = 10, 20, 30, 40
_NAMES = {10: "DBG", 20: "INF", 30: "WRN", 40: "ERR"}


def _ms():
    try:
        return time.ticks_ms()
    except AttributeError:                 # a computer, not a Pico
        return int(time.time() * 1000) & 0x3FFFFFFF


class Log:
    def __init__(self, level=INFO, ring=40, path=None, max_bytes=8192,
                 file_level=WARN, echo=True):
        self.level = level
        self.file_level = file_level
        self.path = path
        self.max_bytes = max_bytes
        self.echo = echo
        self._ring = [None] * ring
        self._next = 0                     # where the next line goes
        self.total = 0                     # lines ever logged
        self.file_errors = 0               # flash writes that failed
        self.counts = {DEBUG: 0, INFO: 0, WARN: 0, ERROR: 0}

    # ---- the four calls you use -------------------------------------
    def debug(self, msg, *args): self._log(DEBUG, msg, args)
    def info(self, msg, *args): self._log(INFO, msg, args)
    def warn(self, msg, *args): self._log(WARN, msg, args)
    def error(self, msg, *args): self._log(ERROR, msg, args)

    def _log(self, level, msg, args):
        if args:
            msg = msg % args
        line = "{:>9} {} {}".format(_ms(), _NAMES[level], msg)
        self.counts[level] += 1
        self.total += 1
        self._ring[self._next] = line
        self._next = (self._next + 1) % len(self._ring)
        if self.echo and level >= self.level:
            print(line)
        if self.path and level >= self.file_level:
            self._to_file(line)

    # ---- flash, with a size cap ---------------------------------------
    def _size(self):
        try:
            return os.stat(self.path)[6]
        except OSError:
            return 0

    def _to_file(self, line):
        try:
            if self._size() + len(line) + 1 > self.max_bytes:
                try:
                    os.remove(self.path + ".1")
                except OSError:
                    pass
                os.rename(self.path, self.path + ".1")
            with open(self.path, "a") as f:
                f.write(line + "\n")
        except OSError:
            self.file_errors += 1          # never let logging crash the program

    # ---- looking back ---------------------------------------------------
    def lines(self):
        """The lines still in the ring, oldest first."""
        n = len(self._ring)
        out = []
        for i in range(n):
            line = self._ring[(self._next + i) % n]
            if line is not None:
                out.append(line)
        return out

    def dump(self):
        for line in self.lines():
            print(line)
