# demo_kit.py -- the parts every demo in 20-demo-template.py shares.
#
#   Kit             the display and the three buttons, handed to each mode
#   settle()        wait for every button to be let go, then forget it
#   centered()      one line of text, centered
#   put()           one line of text, centered and padded to a fixed width
#                   so it covers whatever was there before
#   wrap_in_circle  word-wrap a paragraph so every line fits the ROUND glass
#   text_block()    wrap a paragraph, picking the biggest font that fits
#   menu_hint()     the small "hold MODE: menu" reminder
#   Speaker         tones (sine, square, triangle, sawtooth) and WAV files
#                   on the MAX98357A amplifier
#
# None of this is new: the text helpers grew out of test 04 and test 06,
# and the Speaker is test 05's make_tone() made faster with a look-up
# table, plus test 07's I2S set-up.

import math
import struct
import time
from array import array

from machine import I2S, Pin

import config

BLACK = config.BLACK
WHITE = config.WHITE
DIM = config.color565(150, 150, 150)
FAINT = config.color565(70, 70, 70)
TRACK = config.color565(40, 40, 40)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

CX = config.CENTER_X
CY = config.CENTER_Y

# The reminder that a long MODE press goes back to the showcase. Each mode
# draws it wherever its layout has room (see menu_hint()).
MENU_HINT = "hold MODE: menu"


# ---------------------------------------------------------------------
# The kit
# ---------------------------------------------------------------------
class Kit:
    """What every mode is handed: the display and the three Buttons
    (watchparts.Button objects).

    The MODE button belongs to 20-demo-template.py while a live demo is
    running: a long press goes back to the showcase, and a short press is
    passed to the mode's on_mode(). UP and DOWN belong to the mode."""

    def __init__(self, display, mode, up, down):
        self.display = display
        self.mode = mode
        self.up = up
        self.down = down
        self.buttons = (mode, up, down)


def settle(buttons, quiet_ms=60):
    """Wait until every button is let go, then make each Button forget
    the press it was in the middle of.

    Needed when one mode hands over to another while a button is still
    held: the long press that launched a demo would otherwise reach the new
    mode as a press -- or, with hold-to-repeat, as a stream of them."""
    while True:
        while any(b.pin.value() == 0 for b in buttons):
            time.sleep_ms(10)
        time.sleep_ms(quiet_ms)              # let the contacts stop bouncing
        if all(b.pin.value() == 1 for b in buttons):
            break
    now = time.ticks_ms()
    for b in buttons:
        b.held = False
        b.long_sent = False
        b.tapped_at = None
        b.release_pending = False
        b.changed_at = now


def any_pressed(kit, now):
    """True once if UP or DOWN went down. (MODE is the template's.)"""
    up = kit.up.pressed(now)
    down = kit.down.pressed(now)
    return up or down


# ---------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------
def centered(display, font, text, y, color=WHITE, background=BLACK):
    """Draw text centered left-to-right at row y."""
    config.centered_text(display, font, text, y, color, background)


def put(display, font, text, y, color, width, background=BLACK):
    """Draw text centered, padded with spaces to `width` characters, so a
    short new line completely covers a longer old one."""
    text = text[:width]
    pad = width - len(text)
    text = " " * (pad // 2) + text + " " * (pad - pad // 2)
    config.centered_text(display, font, text, y, color, background)


def menu_hint(display, y, background=BLACK):
    centered(display, SMALL, MENU_HINT, y, FAINT, background)


def row_chars(font, y, margin=8, radius=config.SAFE_RADIUS):
    """How many characters of `font` fit across the round glass on a line
    whose top is at row y. A line is only as wide as its narrowest edge:
    above the middle that is its top, below the middle its bottom."""
    dy = max(abs(y - CY), abs(y + font.HEIGHT - CY))
    if dy >= radius:
        return 0
    half = math.sqrt(radius * radius - dy * dy) - margin
    return max(0, int(2 * half) // font.WIDTH)


def wrap_in_circle(text, font, center_y=CY, line_gap=4, max_lines=9,
                   radius=config.SAFE_RADIUS):
    """Word-wrap text so the block is centered on center_y and every line
    fits inside the circle. Returns (top, lines), or None if it will not
    fit in max_lines.

    Tries one line, then two, then three...: each extra line moves the top
    of the block up and the bottom down, where the circle is narrower, so
    the widths have to be worked out again for every try."""
    words = text.split()
    pitch = font.HEIGHT + line_gap
    for count in range(1, max_lines + 1):
        top = center_y - (count * pitch - line_gap) // 2
        lines = []
        i = 0
        fits = True
        for row in range(count):
            width = row_chars(font, top + row * pitch, radius=radius)
            line = ""
            while i < len(words):
                candidate = words[i] if not line else line + " " + words[i]
                if len(candidate) > width:
                    break
                line = candidate
                i += 1
            if not line and i < len(words):
                fits = False                 # one word wider than the row
                break
            lines.append(line)
        if fits and i == len(words):
            return top, lines
    return None


def draw_lines(display, font, top, lines, color, background=BLACK,
               line_gap=4):
    for row, line in enumerate(lines):
        centered(display, font, line, top + row * (font.HEIGHT + line_gap),
                 color, background)


def text_block(display, text, center_y, color, background=BLACK,
               fonts=None, max_lines=6, line_gap=4, radius=config.SAFE_RADIUS):
    """Wrap text into the circle in the first font that fits (big first),
    draw it, and return (top, bottom) of what was drawn.

    Each entry in fonts is a font, or (font, most lines) to give that
    font its own limit -- ((BIG, 2), (SMALL, 4)) means "big if it fits on
    two lines, otherwise small"."""
    for entry in fonts or (BIG, SMALL):
        font, lines_allowed = (entry if isinstance(entry, tuple)
                               else (entry, max_lines))
        fit = wrap_in_circle(text, font, center_y, line_gap, lines_allowed,
                             radius)
        if fit is not None:
            top, lines = fit
            draw_lines(display, font, top, lines, color, background, line_gap)
            return top, top + len(lines) * (font.HEIGHT + line_gap)
    # Too long even in the small font: draw what fits.
    top, lines = wrap_in_circle(text[:120], SMALL, center_y, line_gap, 12,
                                radius) or (center_y, [text[:30]])
    draw_lines(display, SMALL, top, lines, color, background, line_gap)
    return top, top + len(lines) * (SMALL.HEIGHT + line_gap)


# ---------------------------------------------------------------------
# Sound
# ---------------------------------------------------------------------
SINE = "sine"
SQUARE = "square"
TRIANGLE = "triangle"
SAWTOOTH = "sawtooth"
WAVES = (SINE, SQUARE, TRIANGLE, SAWTOOTH)

# The same loudness does not SOUND the same for every wave: a square wave
# carries much more energy than a sine at the same peak. These even them
# out so stepping through the waves is not a jump in volume.
_WAVE_LEVEL = {SINE: 1.0, SQUARE: 0.45, TRIANGLE: 0.9, SAWTOOTH: 0.55}

_TABLE_BITS = 8
_TABLE_SIZE = 1 << _TABLE_BITS                 # 256 points per cycle
_PHASE_BITS = 16                               # fixed-point fraction
_PHASE_MASK = (1 << (_TABLE_BITS + _PHASE_BITS)) - 1


class Speaker:
    """The MAX98357A amplifier, open on I2S block 0 at one sample rate.

    THE SPEED TRICK. Test 05 calls math.sin() for every sample. That is
    fine for a beep but slow for a tune. Here one cycle of each wave is
    worked out once, 256 points, into a table. A note is then just
    stepping through the table at the right speed: the "phase" counts how
    far through the cycle we are, in 1/65536ths of a table step, so even a
    note whose cycle is not a whole number of samples comes out at the
    right pitch.

    write() returns as soon as the sound is in the I2S buffer (ibuf bytes,
    256 ms at 16000 Hz), so a short beep does not stop the program. Call
    wait() to stand still until everything written has finished."""

    def __init__(self, rate=16000, ibuf=8192, volume=None):
        self.rate = rate
        self.ibuf = ibuf
        self.volume = config.VOLUME if volume is None else volume
        self.fade = rate // 100                # 10 ms fade, so notes don't click
        self._tables = {}
        self._ends_at = time.ticks_ms()
        self.audio = I2S(config.I2S_SPEAKER_ID,
                         sck=Pin(config.I2S_BCLK_PIN),
                         ws=Pin(config.I2S_LRC_PIN),
                         sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                         format=I2S.MONO, rate=rate, ibuf=ibuf)

    def _table(self, wave, volume):
        key = (wave, volume)
        table = self._tables.get(key)
        if table is None:
            peak = 32767 * volume / 100 * _WAVE_LEVEL[wave]
            table = array('h', bytes(_TABLE_SIZE * 2))
            for i in range(_TABLE_SIZE):
                p = i / _TABLE_SIZE
                if wave == SINE:
                    v = math.sin(2 * math.pi * p)
                elif wave == SQUARE:
                    v = 1.0 if p < 0.5 else -1.0
                elif wave == TRIANGLE:
                    v = 4 * p - 1 if p < 0.5 else 3 - 4 * p
                else:                          # sawtooth
                    v = 2 * p - 1
                table[i] = int(peak * v)
            self._tables[key] = table
        return table

    def tone(self, freq, ms, wave=SINE, volume=None):
        """Returns the samples of one note (an array of 16-bit numbers).
        freq 0 is a rest: silence of the same length."""
        count = self.rate * ms // 1000
        out = array('h', bytes(count * 2))
        if freq <= 0 or count == 0:
            return out
        table = self._table(wave, self.volume if volume is None else volume)
        step = int(freq * _TABLE_SIZE * (1 << _PHASE_BITS) / self.rate)
        phase = 0
        shift = _PHASE_BITS
        mask = _TABLE_SIZE - 1
        wrap = _PHASE_MASK
        for i in range(count):
            out[i] = table[(phase >> shift) & mask]
            phase = (phase + step) & wrap
        # Fade the first and last 10 ms in and out, so the speaker cone
        # does not jump (which you would hear as a click).
        fade = min(self.fade, count // 2)
        for i in range(fade):
            out[i] = out[i] * i // fade
            out[count - 1 - i] = out[count - 1 - i] * i // fade
        return out

    def write(self, samples, count=None):
        """Queue samples (16-bit) to play. Returns once they are in the
        buffer; a sound longer than the buffer waits for room.

        count is how many samples that is. Leave it out for an array('h')
        (or a memoryview of one), bytes, or a bytearray; pass it for a
        memoryview of bytes, whose length counts bytes, not samples."""
        if count is None:
            count = len(samples)
            if isinstance(samples, (bytes, bytearray)):
                count //= 2
        ms = count * 1000 // self.rate
        now = time.ticks_ms()
        if time.ticks_diff(self._ends_at, now) < 0:
            self._ends_at = now
        self._ends_at = time.ticks_add(self._ends_at, ms)
        self.audio.write(samples)

    def play(self, freq, ms, wave=SINE, volume=None):
        self.write(self.tone(freq, ms, wave, volume))

    def rest(self, ms):
        self.write(array('h', bytes(self.rate * ms // 1000 * 2)))

    def busy(self):
        return time.ticks_diff(self._ends_at, time.ticks_ms()) > 0

    def wait(self):
        """Stand still until everything written has played."""
        left = time.ticks_diff(self._ends_at, time.ticks_ms())
        if left > 0:
            time.sleep_ms(left + 30)

    def play_wav(self, path, volume=None):
        """Play a 16-bit mono WAV file recorded at this speaker's rate.
        Streams it from flash 1024 samples at a time, so a long file needs
        no more RAM than a short one. Raises OSError if the file is
        missing and ValueError if it is the wrong kind of WAV.

        A WAV file is a list of "chunks", each an ID and a size. "fmt "
        says the rate, channels, and bits; "data" is the sound. Others
        (macOS adds a padding chunk called "FLLR") are skipped."""
        volume = self.volume if volume is None else volume
        with open(path, "rb") as f:
            head = f.read(12)
            if head[0:4] != b"RIFF" or head[8:12] != b"WAVE":
                raise ValueError("not a WAV file")
            rate = channels = bits = None
            while True:
                chunk = f.read(8)
                if len(chunk) < 8:
                    raise ValueError("no data chunk")
                size = struct.unpack("<I", chunk[4:8])[0]
                if chunk[0:4] == b"data":
                    break
                body = f.read(size + (size & 1))
                if chunk[0:4] == b"fmt ":
                    channels, rate = struct.unpack_from("<HI", body, 2)
                    bits = struct.unpack_from("<H", body, 14)[0]
            if (rate, channels, bits) != (self.rate, 1, 16):
                raise ValueError("want 16-bit mono at {} Hz, got {} bit, "
                                 "{} ch, {} Hz".format(self.rate, bits,
                                                       channels, rate))
            block = array('h', bytes(2048))
            view = memoryview(block)
            left = size // 2
            while left > 0:
                want = min(left, len(block))
                got = f.readinto(view[:want]) // 2
                if got <= 0:
                    break
                for i in range(got):
                    block[i] = block[i] * volume // 100
                self.write(view[:got])
                left -= got

    def deinit(self):
        """Let the last sound finish, then free I2S block 0."""
        self.wait()
        self.audio.deinit()


class Looper:
    """Plays one sound over and over WITHOUT stopping the program -- an
    alarm that rings while the screen flashes and the buttons still work.

    Writing a long sound in one go would make write() wait until most of
    it had gone into the I2S buffer. So update() writes one small chunk
    at a time, only when less than AHEAD_MS of sound is left queued.
    Call update() on every pass of the loop."""

    AHEAD_MS = 150
    CHUNK = 1024                               # samples per write: 64 ms

    def __init__(self, speaker, samples):
        self.speaker = speaker
        self.view = memoryview(samples)
        self.position = 0

    def update(self):
        speaker = self.speaker
        if time.ticks_diff(speaker._ends_at, time.ticks_ms()) > self.AHEAD_MS:
            return
        end = min(self.position + self.CHUNK, len(self.view))
        speaker.write(self.view[self.position:end])
        self.position = 0 if end >= len(self.view) else end


def make_speaker(rate=16000, ibuf=8192):
    """A Speaker, or None if the amplifier cannot be started -- so a demo
    can still show its screen on a kit with no speaker wired."""
    try:
        return Speaker(rate, ibuf)
    except (OSError, ValueError) as error:
        print("No speaker:", error)
        return None
