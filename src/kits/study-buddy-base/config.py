# Hardware configuration for the Study Buddy base kit: a Raspberry Pi Pico 2 W
# wired to a 2.1" 360x360 round GC9B72 SPI smartwatch display, three push
# buttons, a MAX98357A I2S amplifier driving a speaker, and an INMP441 I2S
# MEMS microphone.
#
# This started as a copy of the Chrono Smart Clock (study-buddy) kit's
# config.py from the clocks-and-watches repository. The display, buttons,
# speaker, and WiFi/time settings are unchanged. The microphone section is
# new: its pins and I2S settings come from the fft-lab-kit config.py in the
# fft-benchmarking repository, where the INMP441 was confirmed on real
# hardware.
#
# Every lab in this folder imports this file instead of repeating pin
# numbers, so the whole kit only needs to be described in one place.
#
# The display's silkscreen reads "Driver IC: GC9B72, Resolution: 360x360" --
# the 640x640 figure on some AliExpress listings for this panel is wrong.
#
# The driver (lib/gc9b72.py) and the fonts (lib/vga1_*.py) are copied from
# the study-buddy kit in clocks-and-watches. Upload them to the Pico's lib/
# folder along with this file.

from machine import Pin, SPI, I2S
import gc9b72
from gc9b72 import color565

WIDTH = 360
HEIGHT = 360

# Pico 2 W + bare GC9B72 module, on SPI0.
#
# The 10-pad breakout reads (left to right): GND VCC SCL SDA RST DC CS BL
# SDO TE. Only 8 of those are wired -- SDO (read-back) and TE (frame
# tearing sync) are not used by this driver and left unconnected.
#
#   Module pin   Pico pin   Wire color
#   ----------   --------   ----------
#   SCL / CLK    GP2        orange
#   SDA / MOSI   GP3        yellow
#   RST          GP4        green
#   DC           GP5        blue
#   CS           GP6        purple
#   BL           GP7        gray
#   VCC          3V3        red
#   GND          GND        black
SPI_ID = 0
SCK_PIN = 2
MOSI_PIN = 3
RST_PIN = 4
DC_PIN = 5
CS_PIN = 6
BL_PIN = 7

# On a Pico 2 W the onboard LED is NOT wired to GP25 the way it is on a
# plain Pico -- it hangs off the CYW43439 wireless chip. MicroPython hides
# that behind the pin name "LED", so always use Pin("LED"), never Pin(25).
#
# GP23, GP24, GP25 and GP29 belong to the wireless chip on this board.
# Don't wire anything to them.
LED_PIN = "LED"

# 24 MHz is what the robot-faces kit ships at, confirmed on a plain Pico
# with 20 cm ribbon cables and no speckling or tearing.
#
# THE NUMBER YOU ASK FOR IS NOT ALWAYS THE NUMBER YOU GET. MicroPython
# derives the SPI clock by dividing a 48 MHz peripheral clock, and rounds
# DOWN to the nearest rate it can make. Measured on a Pico 2 W running
# MicroPython 1.29 (the CPU runs at 150 MHz, but SPI does not care):
#
#     you ask for      you get
#     10_000_000        8_000_000
#     16_000_000       12_000_000
#     20_000_000       12_000_000
#     24_000_000       24_000_000   <- the ceiling
#     62_500_000       24_000_000
#
# Between 12 and 24 MHz there is NOTHING, and nothing above 24. Print the
# SPI object to see the rate you really got:
#
#     from machine import Pin, SPI
#     print(SPI(0, baudrate=24_000_000, sck=Pin(2), mosi=Pin(3)))
#
# If you see speckled pixels or torn frames on long or messy wiring,
# step down to 12_000_000.
BAUDRATE = 24_000_000

# Three push buttons, each with its other leg to GND. PULL_UP holds the
# pin at 1 until a press pulls it to 0, so "pressed" reads as 0.
#
#   Mode       GP13   step through what the up/down buttons change
#   Increment  GP14   the current setting goes up
#   Decrement  GP15   the current setting goes down
#
# Same pins and names as the other clock kits in this repository.
BUTTON_MODE_PIN = 13
BUTTON_INCREMENT_PIN = 14
BUTTON_DECREMENT_PIN = 15

# The speaker: a MAX98357A I2S amplifier board. It turns the Pico's digital
# audio into power for a small speaker, so there is no DAC to wire and no
# resistor to pick.
#
#   Amp pin   Pico pin   What it does
#   -------   --------   ------------
#   LRC       GP21       "left/right clock": says which channel a sample is
#   BCLK      GP20       "bit clock": one tick for every bit of audio
#   DIN       GP19       "data in": the audio itself
#   GAIN      GP18       how loud the amp makes it (see GAIN_DB below)
#
# THE ONE RULE: MicroPython's I2S on the Pico needs LRC on the pin right
# AFTER BCLK. Here BCLK is GP20 and LRC is GP21, so it works. Swap them
# and I2S() raises an error. (It is the MicroPython docs' rule for rp2:
# "The ws pin number must be one greater than the sck pin number" -- ws
# is the library's name for LRC, and sck is its name for BCLK.)
#
# Any four pins would do apart from that rule. These avoid the display
# (GP2-GP7), the buttons (GP13-GP15), the microphone (GP10-GP12), and the
# wireless chip's own pins (GP23, GP24, GP25, GP29).
I2S_LRC_PIN = 21
I2S_BCLK_PIN = 20
I2S_DIN_PIN = 19
I2S_GAIN_PIN = 18

# The speaker transmits on I2S block 0. The microphone below receives on
# block 1, so the kit can listen and talk at the same time.
I2S_SPEAKER_ID = 0

# The amplifier's GAIN pin has three settings, chosen by what it is wired
# to. Because it is wired to a Pico pin here, set_gain() can pick one in
# software:
#
#   GAIN_DB   GAIN pin does this     Pico pin is set to
#   -------   --------------------   -----------------------
#      6      tied to the amp's VIN   output, 1   (high)
#      9      left floating           input       (disconnected)
#     12      tied to GND             output, 0   (low)
#
# Numbers are from the board maker's documentation (Adafruit's MAX98357A
# breakout). 9 dB is what you get with no wire at all. The "6" setting
# only makes sense if the amp's VIN is 3.3 V, the same as a Pico pin's
# high level; if VIN is 5 V, use 9 or 12.
GAIN_DB = 9

# Default loudness for software volume, 0 (silent) to 100 (the loudest the
# amplifier is asked for). Keep it low while testing: a speaker an inch
# from your ear is louder than you expect.
VOLUME = 40

# The microphone: an INMP441 I2S MEMS microphone board. Like the amplifier,
# it talks I2S, but in the other direction -- it sends audio TO the Pico.
#
#   Mic pin   Pico pin   What it does
#   -------   --------   ------------
#   SCK       GP10       "serial clock": the Pico's bit clock for the mic
#   WS        GP11       "word select": says which channel a sample is
#   SD        GP12       "serial data": the audio itself, mic to Pico
#   L/R       GND        picks the LEFT channel (tie to 3V3 for right)
#   VDD       3V3        power -- the INMP441 is a 3.3 V part, never 5 V
#   GND       GND
#
# The same ws-is-sck-plus-one rule applies: SCK is GP10 and WS is GP11.
# These pins avoid the display (GP2-GP7), the buttons (GP13-GP15), the
# amplifier (GP18-GP21), and the wireless chip's own pins.
MIC_SCK_PIN = 10
MIC_WS_PIN = 11
MIC_SD_PIN = 12

# I2S block 1, so the microphone does not fight the speaker for block 0.
MIC_I2S_ID = 1

# The INMP441 sends 24 real bits of audio inside a 32-bit word, so we read
# 32-bit samples and shift right by 8 to recover the value.
MIC_SAMPLE_BITS = 32
MIC_SAMPLE_SHIFT = 8

# 12800 Hz is plenty for speech and keeps the FFT cheap. The highest pitch
# you can see is half the sample rate (the Nyquist limit), so 6400 Hz.
MIC_SAMPLE_RATE = 12800

# The I2S driver's internal ring buffer, in bytes. 40000 bytes holds
# 10000 32-bit samples, almost a second of audio at 12800 Hz, so a slow
# display update does not make the driver drop samples.
MIC_BUFFER_BYTES = 40000

# 512 samples at 12800 Hz is exactly 40 ms of sound per frame, which gives
# the FFT 25 Hz between bins (12800 / 512).
FFT_SIZE = 512

# RGB565: five bits of red, six of green, five of blue, packed into 16
# bits. color565(red, green, blue) builds any color from three ordinary
# 0-255 values, and it is re-exported above so labs can use config.color565().
BLACK = 0x0000
WHITE = 0xFFFF
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
YELLOW = 0xFFE0
CYAN = 0x07FF
MAGENTA = 0xF81F
GRAY = color565(110, 110, 110)

# Fill flags for shapes.ellipse() / shapes.poly() -- outline vs. solid.
NO_FILL = 0
FILL = 1

# The geometry of a round screen. The driver addresses a 360x360 square,
# but only the circle inscribed in it is visible -- draw in the corners
# and you're spending SPI bytes on pixels under the bezel that no one
# will ever see.
CENTER_X = WIDTH // 2       # 180
CENTER_Y = HEIGHT // 2      # 180
RADIUS = WIDTH // 2         # 180 -- the physical edge of the glass

# The largest circle you can see all of: the glass is 360 px across, but
# the bezel covers the outermost pixels. Confirmed on real hardware with
# a red ring at 168 that sits right at the visible edge. If a different
# panel cuts the ring off, make this smaller.
SAFE_RADIUS = 168

# Local time zone, used when setting the clock from the internet (see
# wifi_time.py). NTP servers only ever hand out UTC.
#   Eastern -5, Central -6, Mountain -7, Pacific -8
TIMEZONE_HOURS = -6
# True to apply US daylight saving time (second Sunday in March to the
# first Sunday in November). Set False for Arizona, Hawaii, or anywhere
# that does not change its clocks.
USE_US_DST = True

# Where to get the weather forecast for (see forecast.py). Latitude and
# longitude in degrees -- look up your town on a map site, or search for
# "<your town> latitude longitude". North and east are positive; the
# United States has a NEGATIVE longitude. This is Minneapolis.
LATITUDE = 44.98
LONGITUDE = -93.27
TEMPERATURE_UNIT = "fahrenheit"      # or "celsius"

# Fonts live in lib/ alongside the driver. The GC9B72 driver has no
# built-in font -- text() takes a font MODULE as its first argument.
import vga1_8x16 as SMALL_FONT       # 8 x 16 -- 45 characters across
import vga1_bold_16x32 as BIG_FONT   # 16 x 32 -- 22 characters across

_backlight = None


def init_display():
    """Start the SPI bus and the GC9B72. Returns the display object."""
    global _backlight

    spi = SPI(SPI_ID, baudrate=BAUDRATE,
              sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))

    _backlight = Pin(BL_PIN, Pin.OUT)

    return gc9b72.GC9B72(
        spi,
        dc=Pin(DC_PIN, Pin.OUT),
        cs=Pin(CS_PIN, Pin.OUT),
        reset=Pin(RST_PIN, Pin.OUT),
        backlight=_backlight,
        rotation=0)


def set_backlight(on):
    """Turn the backlight on or off."""
    _backlight.value(1 if on else 0)


def init_led():
    """Returns the onboard LED. Use the name "LED", not GPIO 25 (see above)."""
    return Pin(LED_PIN, Pin.OUT)


def init_buttons():
    """Set up the three buttons. Returns (mode, increment, decrement).

    Each pin idles at 1 and reads 0 while its button is held down, so
    the labs test for `button.value() == 0`."""
    mode = Pin(BUTTON_MODE_PIN, Pin.IN, Pin.PULL_UP)
    increment = Pin(BUTTON_INCREMENT_PIN, Pin.IN, Pin.PULL_UP)
    decrement = Pin(BUTTON_DECREMENT_PIN, Pin.IN, Pin.PULL_UP)
    return mode, increment, decrement


def set_gain(db=None):
    """Set the amplifier's gain pin for 6, 9, or 12 dB (default GAIN_DB).

    Returns the Pin."""
    db = GAIN_DB if db is None else db
    if db == 9:
        return Pin(I2S_GAIN_PIN, Pin.IN)             # floating
    if db == 12:
        return Pin(I2S_GAIN_PIN, Pin.OUT, value=0)   # tied to GND
    if db == 6:
        return Pin(I2S_GAIN_PIN, Pin.OUT, value=1)   # tied high
    raise ValueError("GAIN_DB must be 6, 9, or 12, not {}".format(db))


def init_microphone(rate=MIC_SAMPLE_RATE):
    """Start the INMP441 on I2S block 1. Returns the I2S object.

    Read 32-bit samples from it and shift each right by MIC_SAMPLE_SHIFT
    to get the 24-bit value. Call .deinit() when you are done with it."""
    return I2S(MIC_I2S_ID,
               sck=Pin(MIC_SCK_PIN), ws=Pin(MIC_WS_PIN), sd=Pin(MIC_SD_PIN),
               mode=I2S.RX, bits=MIC_SAMPLE_BITS, format=I2S.MONO,
               rate=rate, ibuf=MIC_BUFFER_BYTES)


def centered_text(display, font, text, y, color=WHITE, background=BLACK):
    """Draw text centered left-to-right on the screen at row y."""
    x = (WIDTH - len(text) * font.WIDTH) // 2
    display.text(font, text, x, y, color, background)
