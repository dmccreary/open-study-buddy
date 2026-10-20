# vad.py -- voice activity detection by counting frames (Chapter 11)
#
# Pure Python, no hardware. Feed it one loudness reading per 40 ms frame with
# update(); it answers None, "start", or "end".
#
# The states (the diagram in the chapter):
#   SILENCE   the level gate is closed; nothing is happening
#   STARTING  the gate opened; counting loud frames in a row (need start_frames)
#   SPEECH    enough loud frames in a row: an utterance has started
#   ENDING    the gate closed during speech; counting quiet frames in a row
#             (need end_frames); one loud frame sends it back to SPEECH
#
# Two counts do the work, and the level gate (levels.LevelGate) supplies the
# loud/quiet decision for each frame:
#   start_frames  consecutive loud frames to call it speech (a click is 1 frame)
#   end_frames    consecutive quiet frames to call it over (a pause between
#                 words is shorter than this)
#
# After "start", .start_index is the index of the FIRST loud frame of the run.
# After "end", .end_index is the index of the LAST loud frame. Frame indexes
# count from 0 at reset().
#
# boundaries() turns those two indexes into the frames to keep: a few frames of
# pre-roll before the start (soft first sounds that were below the gate) and a
# few of hang-over after the end (soft last sounds).

SILENCE, STARTING, SPEECH, ENDING = range(4)
NAMES = ("SILENCE", "STARTING", "SPEECH", "ENDING")

START_FRAMES = 3        # 120 ms of loud sound to start
END_FRAMES = 15         # 600 ms of quiet to end
PRE_ROLL_FRAMES = 4     # keep 160 ms before the first loud frame
HANG_OVER_FRAMES = 5    # keep 200 ms after the last loud frame


class VAD:
    def __init__(self, gate, start_frames=START_FRAMES, end_frames=END_FRAMES):
        self.gate = gate
        self.start_frames = start_frames
        self.end_frames = end_frames
        self.reset()

    def reset(self):
        self.gate.is_open = False
        self.state = SILENCE
        self.index = -1              # index of the frame being processed
        self.loud_run = 0
        self.quiet_run = 0
        self.start_index = None
        self.end_index = None
        self.last_loud = None

    def update(self, bits):
        """Process one frame's loudness. Returns None, "start" or "end"."""
        self.index += 1
        loud = self.gate.update(bits)
        if loud:
            self.last_loud = self.index

        if self.state == SILENCE:
            if loud:
                self.loud_run = 1
                self.state = STARTING
                return self._check_start()
        elif self.state == STARTING:
            if loud:
                self.loud_run += 1
                return self._check_start()
            self.loud_run = 0
            self.state = SILENCE
        elif self.state == SPEECH:
            if not loud:
                self.quiet_run = 1
                self.state = ENDING
                return self._check_end()
        elif self.state == ENDING:
            if loud:
                self.quiet_run = 0
                self.state = SPEECH
            else:
                self.quiet_run += 1
                return self._check_end()
        return None

    def _check_start(self):
        if self.loud_run >= self.start_frames:
            self.start_index = self.index - self.loud_run + 1
            self.state = SPEECH
            return "start"
        return None

    def _check_end(self):
        if self.quiet_run >= self.end_frames:
            self.end_index = self.last_loud
            self.state = SILENCE
            self.loud_run = 0
            self.quiet_run = 0
            return "end"
        return None


def boundaries(start_index, end_index, total_frames,
               pre_roll=PRE_ROLL_FRAMES, hang_over=HANG_OVER_FRAMES):
    """The frames to keep, as (first, stop): first is the first frame kept
    and stop is one past the last, so frames first..stop-1 are the utterance.
    The result never leaves the range 0..total_frames."""
    first = max(0, start_index - pre_roll)
    stop = min(total_frames, end_index + 1 + hang_over)
    return first, stop
