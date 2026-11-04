# Test 08: SDO Read-Back Probe (experiment)
# Can the Pico read anything back from the GC9B72 through its SDO pin?
#
# The driver in lib/gc9b72.py only ever WRITES to the display. GalaxyCore
# has not published a GC9B72 datasheet, so nobody has documented how (or
# whether) its read-back works. This test does not assume anything -- it
# tries every reasonable way a GalaxyCore / MIPI-DCS display chip is known
# to answer, and reports what came back.
#
# It only touches the display's own pins, GP2-GP8 in config.py:
#   SCK GP2, SDA GP3, RST GP4, DC GP5, CS GP6, BL GP7, SDO GP8.
# The amp, microphone and buttons are never touched.
#
# What we know from sister chips (GC9A01, GC9306, GC9307) and the MIPI
# Display Command Set every one of them follows:
#
#   - Read commands are the MIPI ones: 04h display ID, 09h status,
#     0Ah power mode, 0Bh MADCTL, 0Ch pixel format, 0Dh image mode,
#     45h scanline, 2Eh memory read, DAh/DBh/DCh ID bytes.
#   - After a read command the chip waits for the clock, then shifts data
#     out MSB first. Multi-byte reads usually start with ONE dummy clock
#     (one junk bit); memory read starts with a whole dummy byte. So the
#     answer may be shifted by a few bits -- every test searches bit
#     offsets 0..16 instead of assuming one.
#   - The chip changes SDO on the FALLING clock edge (SPI mode 0), but a
#     few designs change on the rising edge, so both are sampled.
#   - Some modules put the chip in "3-wire" mode where SDA itself turns
#     around and carries the answer, and SDO stays silent. Tested too.
#   - Register F6h ("interface control" on sister chips) sets how the
#     serial port behaves. The init sequence writes C0h there. One test
#     flips each bit of it in turn in case one of them turns SDO on.
#
# WHY NOT HARDWARE SPI? The Pico's SPI0 block (which owns SCK GP2 and SDA
# GP3) can only receive on GP0, GP4, GP16 or GP20 -- GP8 belongs to SPI1.
# So the fast-clock tests use a PIO state machine instead: a tiny SPI
# controller written in PIO assembly that can use ANY three pins.
#
# Strategies, in order:
#   1. Idle check     is anything driving SDO (or SDA) with CS high/low?
#   2. Is SDO driven? bit-bang read commands with the pull-down, then the
#                     pull-up -- data that comes out the same both ways
#                     is being driven by the display
#   3. Command scan   every MIPI read command, every way of listening:
#                     bit-banged (both clock edges, DC low/high), SDA
#                     turn-around, PIO SPI at 1, 5 and 15 MHz
#   4. Proof tests    change a setting, read it back, change it back.
#                     Random noise cannot pass these: MADCTL, pixel format,
#                     inversion, display on/off, sleep in/out
#   5. Memory read    draw 4 known pixels, read them back with 2Eh
#   6. Scanline       45h should return a line number that keeps changing
#   7. FE/EF unlock   repeat the ID reads with GalaxyCore's "inter
#                     register enable" commands sent first
#   8. Reset state    read IDs straight after a hardware reset, no init
#   9. F6h sweep      flip each bit of the interface-control register
#
# The screen flickers (inversion, display off, sleep) while it runs --
# that is the tests working. When it finishes, the display is reset,
# re-initialized, and shows the verdict. Nothing is written to flash.

import gc
import time
import machine
from machine import Pin
import rp2
import config

NAME = "08-sdo-probe-test.py"
VERSION = "1.1"

SDO = getattr(config, "SDO_PIN", 8)
SDA = config.MOSI_PIN
SCK = config.SCK_PIN

# Set False to skip strategy 9 (the slowest, and the most experimental).
RUN_INTERFACE_SWEEP = True

OFFSETS = range(0, 17)       # dummy bits to search past
EXTRA_BITS = 16              # read this many bits past the answer

# The RP2040 and RP2350 both have a register that shows the level of
# every GPIO at once, so SDO and SDA are sampled in the same instant.
SIO_GPIO_IN = 0xD0000004

READ_COMMANDS = (
    (0x04, "RDDID     display ID", 24),
    (0x09, "RDDST     status", 32),
    (0x0A, "RDDPM     power mode", 8),
    (0x0B, "RDDMADCTL memory access", 8),
    (0x0C, "RDDCOLMOD pixel format", 8),
    (0x0D, "RDDIM     image mode", 8),
    (0x0E, "RDDSM     signal mode", 8),
    (0x0F, "RDDSDR    self-diagnostic", 8),
    (0x45, "GETSCAN   scanline", 16),
    (0x52, "RDDISBV   brightness", 8),
    (0x54, "RDCTRLD   control", 8),
    (0xDA, "RDID1     maker", 8),
    (0xDB, "RDID2     version", 8),
    (0xDC, "RDID3     module", 8),
)

findings = []


def note(message):
    """Record a finding for the summary at the end, and print it now."""
    findings.append(message)
    print("  >>", message)


def heading(title):
    gc.collect()
    print()
    print("=" * 64)
    print(title)
    print("=" * 64)


# ---------------------------------------------------------------------
# Bit helpers. Bit streams are bytearrays (one byte per bit): a list
# would cost 4 bytes per bit, more than a Pico W's heap can spare.
# ---------------------------------------------------------------------
def gpio_in():
    return machine.mem32[SIO_GPIO_IN] & 0x3FFFFFFF


def bits_of(words, pin):
    bits = bytearray(len(words))
    for i in range(len(words)):
        bits[i] = (words[i] >> pin) & 1
    return bits


def bytes_to_bits(buf):
    bits = bytearray(8 * len(buf))
    n = 0
    for byte in buf:
        for i in range(7, -1, -1):
            bits[n] = (byte >> i) & 1
            n += 1
    return bits


def value_at(bits, offset, width=8):
    """The width-bit number starting at bit `offset`, or None."""
    if offset + width > len(bits):
        return None
    v = 0
    for b in bits[offset:offset + width]:
        v = (v << 1) | b
    return v


def hex_bits(bits, offset=0):
    out = []
    i = offset
    while i + 8 <= len(bits):
        out.append("{:02X}".format(value_at(bits, i)))
        i += 8
    return " ".join(out)


def is_flat(bits):
    """True if every bit is the same -- no information in it."""
    return not bits or all(b == bits[0] for b in bits)


def pack16(*values):
    out = bytearray()
    for v in values:
        out.append(v >> 8)
        out.append(v & 0xFF)
    return bytes(out)


# ---------------------------------------------------------------------
# Control pins shared by every strategy
# ---------------------------------------------------------------------
cs = Pin(config.CS_PIN, Pin.OUT, value=1)
dc = Pin(config.DC_PIN, Pin.OUT, value=1)
rst = Pin(config.RST_PIN, Pin.OUT, value=1)
sck = None
mosi = None


def sdo_pull(pull):
    Pin(SDO, Pin.IN, pull)


def bb_open():
    """Take SCK and SDA back as plain GPIOs."""
    global sck, mosi
    sck = Pin(SCK, Pin.OUT, value=0)
    mosi = Pin(SDA, Pin.OUT, value=0)
    cs.on()


def bb_send(byte, leave_high=False):
    """Clock out one byte, MSB first, SPI mode 0."""
    for i in range(7, -1, -1):
        mosi.value((byte >> i) & 1)
        sck.on()
        if i or not leave_high:
            sck.off()


def bb_write(command, data=None):
    cs.off()
    dc.off()
    bb_send(command)
    if data:
        dc.on()
        for byte in data:
            bb_send(byte)
    cs.on()


def bb_read_raw(command, nbits, dc_read=0, sda_read=False,
                sda_pull=Pin.PULL_DOWN):
    """Send a read command, then clock nbits more while sampling the pins
    twice per clock: just after the falling edge (where a mode-0 chip has
    put the new bit out) and just after the rising edge.
    Returns (falling_samples, rising_samples)."""
    falling = [0] * nbits           # sized up front: no allocation mid-read
    rising = [0] * nbits
    cs.off()
    dc.off()
    bb_send(command, leave_high=True)       # SCK is high after bit 0
    if sda_read:
        mosi.init(Pin.IN, sda_pull)         # let the chip drive SDA
    else:
        mosi.off()                          # clock out 0x00 = NOP
    dc.value(dc_read)
    for i in range(nbits):
        sck.off()
        falling[i] = gpio_in()
        sck.on()
        rising[i] = gpio_in()
    sck.off()
    cs.on()
    if sda_read:
        mosi.init(Pin.OUT, value=0)
    return falling, rising


def hard_reset():
    rst.on()
    time.sleep_ms(10)
    rst.off()
    time.sleep_ms(20)
    rst.on()
    time.sleep_ms(150)


# ---------------------------------------------------------------------
# PIO SPI. Four PIO cycles per bit, so the state machine runs at 4x the
# SCK rate. Side-set drives SCK; OUT drives SDA; IN samples SDO.
#
#   sample_rise:  read SDO at the instant SCK rises (true SPI mode 0)
#   sample_late:  read SDO at the end of the high half, just before SCK
#                 falls -- catches a chip that changes on the rising edge
# ---------------------------------------------------------------------
@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_LEFT, in_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=8, autopush=True, push_thresh=8,
             sideset_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW)
def sample_rise():
    out(pins, 1).side(0)[1]
    in_(pins, 1).side(1)[1]


@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_LEFT, in_shiftdir=rp2.PIO.SHIFT_LEFT,
             autopull=True, pull_thresh=8, autopush=True, push_thresh=8,
             sideset_init=rp2.PIO.OUT_LOW, out_init=rp2.PIO.OUT_LOW)
def sample_late():
    out(pins, 1).side(0)[1]
    nop().side(1)
    in_(pins, 1).side(1)


# ---------------------------------------------------------------------
# The ways of listening ("buses"). Each one can write a command and read
# one back as bits. Only one is open at a time.
# ---------------------------------------------------------------------
_open_bus = None


def use(bus):
    global _open_bus
    if _open_bus is not None and _open_bus is not bus:
        _open_bus.close()
    bus.open()
    _open_bus = bus
    return bus


class BitBangBus:
    def __init__(self, edge, dc_read, sda=False):
        self.pin = SDA if sda else SDO
        self.edge = edge                # 0 = falling, 1 = rising
        self.dc_read = dc_read
        self.sda = sda
        self.label = "bitbang {} {} DC={}".format(
            "SDA/GP{}".format(SDA) if sda else "SDO/GP{}".format(SDO),
            "rise" if edge else "fall", dc_read)

    def open(self):
        bb_open()
        sdo_pull(Pin.PULL_DOWN)

    def close(self):
        pass

    def write(self, command, data=None):
        bb_write(command, data)

    def read(self, command, nbits):
        falling, rising = bb_read_raw(command, nbits, self.dc_read, self.sda)
        return bits_of(rising if self.edge else falling, self.pin)


class PioBus:
    def __init__(self, baudrate, late, dc_read):
        self.baudrate = baudrate
        self.late = late
        self.dc_read = dc_read
        self.sm = None
        self.label = "PIO {}MHz {} DC={}".format(
            baudrate // 1_000_000, "late" if late else "rise", dc_read)

    def open(self):
        sdo_pull(Pin.PULL_DOWN)
        self.sm = rp2.StateMachine(
            0, sample_late if self.late else sample_rise,
            freq=4 * self.baudrate, sideset_base=Pin(SCK),
            out_base=Pin(SDA), in_base=Pin(SDO))
        self.sm.active(1)
        cs.on()

    def close(self):
        if self.sm is not None:
            self.sm.active(0)
            self.sm = None

    def _xfer(self, byte):
        self.sm.put(byte << 24)          # shifts out from bit 31
        return self.sm.get() & 0xFF

    def write(self, command, data=None):
        cs.off()
        dc.off()
        self._xfer(command)
        if data:
            dc.on()
            for byte in data:
                self._xfer(byte)
        cs.on()

    def read(self, command, nbits):
        buf = bytearray((nbits + 7) // 8)
        cs.off()
        dc.off()
        self._xfer(command)
        dc.value(self.dc_read)
        for i in range(len(buf)):
            buf[i] = self._xfer(0x00)
        cs.on()
        return bytes_to_bits(buf)[:nbits]


def reinit_display():
    """Reset and re-run the full driver init. Hands SCK/SDA back to SPI."""
    global _open_bus
    if _open_bus is not None:
        _open_bus.close()
        _open_bus = None
    return config.init_display()


# ---------------------------------------------------------------------
print("{} v{}".format(NAME, VERSION))
print("SDO is on GP{}. Only GP2-GP8 are used.".format(SDO))
print("Starting the display with the normal driver first, so it is in a")
print("known state ...")
display = reinit_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "SDO probe", 120, config.CYAN)
config.centered_text(display, config.SMALL_FONT, "running -- see the shell", 170)
config.centered_text(display, config.SMALL_FONT, "flicker is expected", 190)

# ---------------------------------------------------------------------
heading("1. Idle check: is anything driving SDO?")
# ---------------------------------------------------------------------
# With CS high the chip should let SDO float, so it follows whichever
# pull resistor the Pico turns on. If it ignores the pull, something is
# driving it.
bb_open()
for cs_level in (1, 0):
    cs.value(cs_level)
    seen = {}
    for name, pull in (("down", Pin.PULL_DOWN), ("up", Pin.PULL_UP)):
        sdo_pull(pull)
        time.sleep_us(500)
        seen[name] = (gpio_in() >> SDO) & 1
    state = ("floating (follows the pull)" if seen["down"] != seen["up"]
             else "HELD at {}".format(seen["up"]))
    print("CS {}: SDO/GP{} is {}".format(
        "high" if cs_level else "low ", SDO, state))
cs.on()
sdo_pull(Pin.PULL_DOWN)

# SDA's own idle level, with SDA let go (as an input).
seen = {}
for name, pull in (("down", Pin.PULL_DOWN), ("up", Pin.PULL_UP)):
    mosi.init(Pin.IN, pull)
    time.sleep_us(500)
    seen[name] = mosi.value()
mosi.init(Pin.OUT, value=0)
print("SDA/GP{} let go: {}".format(
    SDA, "floating" if seen["down"] != seen["up"]
    else "HELD at {} (a resistor on the module?)".format(seen["up"])))

# ---------------------------------------------------------------------
heading("2. Is SDO driven during a read?")
# ---------------------------------------------------------------------
LOCATE_COMMANDS = (0x04, 0x09, 0x0A, 0x0C, 0xDA)


def listen(commands, title):
    """Bit-bang each command with SDO pulled down, then up, and listen on
    SDO and SDA. Returns how many reads were the same under both pulls
    and not flat -- i.e. really driven data -- per pin."""
    got = {}
    for name, pull in (("down", Pin.PULL_DOWN), ("up", Pin.PULL_UP)):
        sdo_pull(pull)
        for command in commands:
            falling, _ = bb_read_raw(command, 40)
            sda_falling, _ = bb_read_raw(command, 40, sda_read=True,
                                         sda_pull=pull)
            got[(name, command, SDO)] = bits_of(falling, SDO)
            got[(name, command, SDA)] = bits_of(sda_falling, SDA)
    sdo_pull(Pin.PULL_DOWN)
    driven = {SDO: 0, SDA: 0}
    for pin, pin_name in ((SDO, "SDO"), (SDA, "SDA")):
        for command in commands:
            down = got[("down", command, pin)]
            up = got[("up", command, pin)]
            if down == up and not is_flat(down):
                driven[pin] += 1
                print("  {} {} {:02X}h -> {}  (+1 bit: {})".format(
                    title, pin_name, command, hex_bits(down),
                    hex_bits(down, 1)))
            elif not is_flat(down) or not is_flat(up):
                print("  {} {} {:02X}h changes under one pull only:"
                      " down {} / up {}".format(title, pin_name, command,
                                                hex_bits(down), hex_bits(up)))
    return driven


driven = listen(LOCATE_COMMANDS, "read")
print("SDO answered {} of {} reads; SDA answered {}".format(
    driven[SDO], len(LOCATE_COMMANDS), driven[SDA]))
if driven[SDO]:
    note("the display drives SDO/GP{} during reads".format(SDO))
else:
    note("SDO/GP{} floats during every read -- nothing drives it".format(SDO))
if driven[SDA]:
    note("the display answers on SDA itself (3-wire turn-around mode)")

buses = [BitBangBus(edge, dc_read) for dc_read in (0, 1) for edge in (0, 1)]
buses += [BitBangBus(edge, 0, sda=True) for edge in (0, 1)]
buses += [PioBus(baudrate, late, dc_read)
          for baudrate in (1_000_000, 5_000_000, 15_000_000)
          for late in (False, True)
          for dc_read in (0, 1)]

# ---------------------------------------------------------------------
heading("3. Command scan: every read command, every way of listening")
# ---------------------------------------------------------------------
scan = {}           # bus label -> {command: bits}
for bus in buses:
    use(bus)
    results = {}
    lines = []
    for command, label, width in READ_COMMANDS:
        bits = bus.read(command, width + EXTRA_BITS)
        results[command] = bits
        if not is_flat(bits):
            lines.append("  {:02X}h {:<26} {}  (+1: {})".format(
                command, label, hex_bits(bits), hex_bits(bits, 1)))
    scan[bus.label] = results
    print("{:<26} {} of {} commands returned data".format(
        bus.label + ":", len(lines), len(READ_COMMANDS)))
    for line in lines:
        print(line)

# ---------------------------------------------------------------------
heading("4. Proof tests: change a setting, read it back")
# ---------------------------------------------------------------------
# Each test reads a register in state A, state B, then A again. It passes
# at bit offset k when A and A-again agree and A XOR B is exactly the bit
# that setting is supposed to flip. A stuck or noisy line cannot do that.
SLEEP_WAIT = 130
TESTS = (
    ("MADCTL 00h vs C0h", 0x0B,
     ((0x36, b"\x00", 0),), ((0x36, b"\xC0", 0),), (0xC0,), 0xC0),
    ("MADCTL 00h vs 28h", 0x0B,
     ((0x36, b"\x00", 0),), ((0x36, b"\x28", 0),), (0x28,), 0x28),
    ("pixel format 16 vs 18 bit", 0x0C,
     ((0x3A, b"\x05", 0),), ((0x3A, b"\x06", 0),), (0x03, 0x33), None),
    ("inversion off vs on", 0x0D,
     ((0x20, None, 0),), ((0x21, None, 0),), (0x20,), None),
    ("display on vs off", 0x0A,
     ((0x29, None, 0),), ((0x28, None, 0),), (0x04,), None),
    ("sleep out vs in", 0x0A,
     ((0x11, None, SLEEP_WAIT),), ((0x10, None, SLEEP_WAIT),),
     (0x10, 0x14), None),
)
# Puts every setting the tests touch back the way the driver left it.
RESTORE = ((0x36, b"\x00", 0), (0x3A, b"\x05", 0), (0x20, None, 0),
           (0x11, None, SLEEP_WAIT), (0x29, None, 0))


def apply(bus, steps):
    for command, data, wait in steps:
        bus.write(command, data)
        if wait:
            time.sleep_ms(wait)


def proof_test(bus, test):
    name, command, state_a, state_b, masks, exact_b = test
    nbits = 8 + EXTRA_BITS + 8
    apply(bus, state_a)
    a1 = bus.read(command, nbits)
    apply(bus, state_b)
    b = bus.read(command, nbits)
    apply(bus, state_a)
    a2 = bus.read(command, nbits)
    passes = []
    for k in OFFSETS:
        va1, vb, va2 = value_at(a1, k), value_at(b, k), value_at(a2, k)
        if va1 is None or vb is None:
            continue
        if va1 == va2 and (va1 ^ vb) in masks:
            exact = exact_b is not None and vb == exact_b
            passes.append((k, va1, vb, exact))
    return passes


proof = {}          # bus label -> list of (test name, offset)
for bus in buses:
    use(bus)
    passed = []
    for test in TESTS:
        for k, va, vb, exact in proof_test(bus, test):
            passed.append((test[0], k))
            print("{}: PASS {} at bit offset {} (A={:02X}h B={:02X}h{})".format(
                bus.label, test[0], k, va, vb,
                ", exact value" if exact else ""))
    apply(bus, RESTORE)
    proof[bus.label] = passed
    if not passed:
        print("{:<26} no test passed".format(bus.label + ":"))

for label, passed in proof.items():
    if passed:
        offsets = sorted(set(k for _, k in passed))
        note("READ-BACK WORKS via {} -- {} proof test(s), bit offset(s) {}"
             .format(label, len(passed), offsets))

# The bus that passed the most tests (or the first one) is used for the
# next three strategies.
best = max(buses, key=lambda b: len(proof.get(b.label, ())))
print()
print("Using '{}' for strategies 5-7.".format(best.label))

# ---------------------------------------------------------------------
heading("5. Memory read (2Eh): draw 4 pixels, read them back")
# ---------------------------------------------------------------------
# Four pixels at the very center: red, green, blue, white. A display
# that reads its memory back sends one dummy byte first, then each pixel
# as 2 bytes (RGB565) or, on most GalaxyCore/ILI-style chips, 3 bytes
# (RGB666, even when it was written as RGB565).
PIXELS = (config.RED, config.GREEN, config.BLUE, config.WHITE)
EXPECT_565 = bytes_to_bits(pack16(*PIXELS))
EXPECT_666 = bytes((0xF8, 0, 0, 0, 0xFC, 0, 0, 0, 0xF8, 0xF8, 0xFC, 0xF8))
MASK_666 = bytes((0xF8, 0xFC, 0xF8) * 4)


def ram_test(bus):
    x, y = config.CENTER_X - 2, config.CENTER_Y
    bus.write(0x2A, pack16(x, x + 3))
    bus.write(0x2B, pack16(y, y))
    bus.write(0x2C, pack16(*PIXELS))
    bus.write(0x2A, pack16(x, x + 3))
    bus.write(0x2B, pack16(y, y))
    bits = bus.read(0x2E, 8 * 16 + EXTRA_BITS)
    print("  raw: {}".format(hex_bits(bits)))
    found = []
    for k in range(0, 25):
        if bits[k:k + len(EXPECT_565)] == EXPECT_565:
            found.append("RGB565 at bit offset {}".format(k))
        got = [value_at(bits, k + 8 * i) for i in range(12)]
        if None not in got and all(
                (g & m) == (e & m)
                for g, e, m in zip(got, EXPECT_666, MASK_666)):
            found.append("RGB666 at bit offset {}".format(k))
    return found


use(best)
found = ram_test(best)
for f in found:
    note("memory read-back works via {}: {}".format(best.label, f))
if not found:
    print("  the 4 pixels were not found in the reply")

# ---------------------------------------------------------------------
heading("6. Scanline (45h): a number that should keep changing")
# ---------------------------------------------------------------------
# 45h returns the line the panel is refreshing right now -- 0 to about
# 370, sweeping 50-60 times a second. Ten reads a few ms apart should all
# be small numbers, and mostly different.
reads = []
for i in range(10):
    reads.append(best.read(0x45, 16 + EXTRA_BITS))
    time.sleep_ms(3 + i)
for k in OFFSETS:
    values = [value_at(bits, k, 16) for bits in reads]
    if None in values:
        continue
    if all(v < 0x400 for v in values) and len(set(values)) >= 4:
        note("scanline is alive via {} at bit offset {}: {}".format(
            best.label, k, values))
        break
else:
    print("  no offset gave a changing line number; raw first read:",
          hex_bits(reads[0]))

# ---------------------------------------------------------------------
heading("7. FE/EF 'inter register enable', then the ID reads again")
# ---------------------------------------------------------------------
# GalaxyCore chips hide their vendor registers until FEh then EFh are
# sent -- the init sequence starts that way, and ends with FEh EEh. If
# the ID registers live behind that door, this is where they show up.
best.write(0xFE)
best.write(0xEF)
for command, label, width in READ_COMMANDS:
    if command in (0x04, 0x09, 0xDA, 0xDB, 0xDC):
        bits = best.read(command, width + EXTRA_BITS)
        print("  {:02X}h {:<26} {}".format(
            command, label, "flat" if is_flat(bits) else hex_bits(bits)))
        if not is_flat(bits) and bits != scan[best.label][command]:
            note("{:02X}h answers differently after FE/EF: {}".format(
                command, hex_bits(bits)))
best.write(0xFE)
best.write(0xEE)

# ---------------------------------------------------------------------
heading("8. Straight after a hardware reset, before any init")
# ---------------------------------------------------------------------
reinit_display()            # releases the PIO, puts the pins in a known state
bb_open()
hard_reset()
heard = listen((0x04, 0x09, 0x0A, 0xDA), "reset")
if heard[SDO] or heard[SDA]:
    note("the chip answers right after reset (before init)")
else:
    print("  silent")
bb_write(0x11)              # sleep out alone, then try again
time.sleep_ms(SLEEP_WAIT)
heard = listen((0x04, 0x09, 0x0A, 0xDA), "slpout")
if heard[SDO] or heard[SDA]:
    note("the chip answers after reset + sleep-out")
else:
    print("  still silent after sleep-out")

# ---------------------------------------------------------------------
if RUN_INTERFACE_SWEEP:
    heading("9. F6h interface-control sweep (experimental)")
    # -----------------------------------------------------------------
    # The init writes C0h to F6h. Flip one bit at a time; after each try
    # the display gets a hardware reset and a full init, so a value that
    # breaks the serial port does no lasting harm.
    for bit in range(8):
        value = 0xC0 ^ (1 << bit)
        reinit_display()
        bb_open()
        bb_write(0xFE)
        bb_write(0xEF)
        bb_write(0xF6, bytes([value]))
        heard = listen((0x04, 0x09, 0x0A, 0x0C), "F6={:02X}".format(value))
        if heard[SDO] or heard[SDA]:
            note("F6h = {:02X}h makes the chip answer".format(value))
        else:
            print("F6h = {:02X}h (bit {} flipped): silent".format(value, bit))

# ---------------------------------------------------------------------
heading("Summary")
# ---------------------------------------------------------------------
works = any(proof.values())
any_data = any(not is_flat(bits) for results in scan.values()
               for bits in results.values())
if works:
    verdict, color = "Read-back WORKS", config.GREEN
elif any_data:
    verdict, color = "Data, not proven", config.YELLOW
else:
    verdict, color = "SDO is silent", config.RED

print(verdict)
for message in findings:
    print("  -", message)
if not works:
    print()
    print("If SDO floated the whole time, the likely causes are, in order:")
    print("  - the SDO pad is not connected to the chip on this module")
    print("    (check for continuity from the pad to the flex cable)")
    print("  - the chip's interface is strapped to a mode with no SDO")
    print("  - a loose or broken SDO wire -- check it with a meter")

rp2.PIO(0).remove_program()
display = reinit_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "SDO probe", 100, config.CYAN)
config.centered_text(display, config.BIG_FONT, verdict, 160, color)
config.centered_text(display, config.SMALL_FONT,
                     "SDO on GP{}".format(SDO), 215)
config.centered_text(display, config.SMALL_FONT,
                     "details in the shell", 235)
