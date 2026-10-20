# backoff.py -- wait longer after each failure, and add randomness
#
# delay_ms(attempt) is the wait before retry number attempt+1:
#     ceiling = min(cap, base * 2 ** attempt)
#     delay   = a random number from 0 to ceiling      ("full jitter")
# retry(fn, ...) calls fn() until it works, the error is not worth retrying, or
# the attempts run out. Pure Python: it runs on a computer exactly as on the Pico.

import time

try:
    import random
except ImportError:          # a very small build; fall back to no jitter
    random = None


def ceiling_ms(attempt, base_ms=500, cap_ms=8000):
    return min(cap_ms, base_ms * (2 ** attempt))


def delay_ms(attempt, base_ms=500, cap_ms=8000, jitter=True):
    top = ceiling_ms(attempt, base_ms, cap_ms)
    if jitter and random is not None:
        return random.randint(0, top)
    return top


def retry(fn, attempts=4, base_ms=500, cap_ms=8000, on_wait=None, sleep_ms=None):
    """Call fn() up to attempts times. An exception with .retryable == False
    (a wrong token, a malformed request) is raised at once: retrying cannot help.
    on_wait(attempt_number, attempts, delay, error) is called before each wait."""
    sleep_ms = sleep_ms or time.sleep_ms
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = attempt == attempts - 1
            if last or not getattr(e, "retryable", False):
                raise
            wait = delay_ms(attempt, base_ms, cap_ms)
            if on_wait:
                on_wait(attempt + 1, attempts, wait, e)
            sleep_ms(wait)
