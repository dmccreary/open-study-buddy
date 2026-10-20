# overrun.py -- Chapter 18: count the frames your loop was too slow for
#
#   mic = OverrunCounter(config.init_microphone())     # wraps any object with readinto()
#   ... use mic.readinto(buf) exactly as before ...
#   print(mic.summary())
#
# readinto() blocks until the next 40 ms frame is ready (Chapter 8). So the
# time between two returns of readinto() is the length of one pass of your
# loop. If a pass takes longer than a frame, the microphone's ring buffer
# starts to fill up behind you. This wrapper measures every pass and counts:
#
#   overruns     passes longer than one frame plus jitter_us of timing noise
#   worst_us     the longest pass seen
#   backlog      Chapter 8's model: backlog grows by (pass / frame - 1) frames
#                on a slow pass and shrinks on a fast one (it never goes below 0)
#   lost_est     frames the model says were lost: backlog beyond the ring's depth
#
# The ring depth (9.77 frames, about 0.4 s) is what Chapter 8 measured on one
# board at one setting. The backlog and lost_est numbers are a MODEL, not a
# measurement of lost audio.

import time


class OverrunCounter:
    def __init__(self, mic, frame_us=40000, jitter_us=2000, ring_frames=9.77):
        self.mic = mic
        self.frame_us = frame_us
        self.jitter_us = jitter_us
        self.ring_frames = ring_frames
        self.reset()

    def reset(self):
        self._last = None
        self.passes = 0
        self.overruns = 0
        self.worst_us = 0
        self.backlog = 0.0
        self.max_backlog = 0.0
        self.lost_est = 0.0

    def readinto(self, buf):
        n = self.mic.readinto(buf)
        now = time.ticks_us()
        if self._last is not None:
            self._note(time.ticks_diff(now, self._last))
        self._last = now
        return n

    def _note(self, pass_us):
        self.passes += 1
        if pass_us > self.worst_us:
            self.worst_us = pass_us
        if pass_us > self.frame_us + self.jitter_us:
            self.overruns += 1
        self.backlog = max(0.0, self.backlog + pass_us / self.frame_us - 1.0)
        if self.backlog > self.ring_frames:
            self.lost_est += self.backlog - self.ring_frames
            self.backlog = self.ring_frames
        if self.backlog > self.max_backlog:
            self.max_backlog = self.backlog

    def deinit(self):
        self.mic.deinit()

    def summary(self):
        return ("{} passes, {} overruns, worst {:.1f} ms, max backlog {:.2f} frames, "
                "model-estimated lost {:.2f} frames").format(
                    self.passes, self.overruns, self.worst_us / 1000,
                    self.max_backlog, self.lost_est)
