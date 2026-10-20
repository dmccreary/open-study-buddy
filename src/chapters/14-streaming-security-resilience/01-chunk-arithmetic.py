# Chapter 14, Test 01: How big should an audio chunk be? (arithmetic only)
# Works out, for a 3 s and a 5 s utterance of 16-bit mono audio at 12,800 Hz,
# how many bytes there are, how many chunks each chunk size makes, how much
# time each chunk covers, and what each framing method adds per chunk. On a
# Pico it also reports the free heap and whether the recordings fit. Runs on
# your COMPUTER (python3 01-chunk-arithmetic.py) or on the Pico; no network.
#
# PASS: the numbers match the chapter's table (a 5 s recording is 128,000
# bytes; 2,048-byte chunks make 63 chunks) and the last line says PASS.

NAME = "01-chunk-arithmetic.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc

RATE = 12800
BYTES_PER_SAMPLE = 2
MSS = 1460                    # a typical TCP segment payload on an Ethernet-style network


def recording_bytes(seconds, bytes_per_sample=BYTES_PER_SAMPLE):
    return seconds * RATE * bytes_per_sample


def chunks_needed(total, chunk):
    return (total + chunk - 1) // chunk


def ws_overhead(chunk):
    """WebSocket client frame: 2 header bytes + 4 mask bytes, +2 when length >= 126."""
    return 2 + 4 + (2 if chunk >= 126 else 0)


def http_chunk_overhead(chunk):
    """Transfer-Encoding: chunked adds '<hex length>\\r\\n' before and '\\r\\n' after."""
    return len("{:x}".format(chunk)) + 2 + 2


ok = True
print()
print("Recording sizes (16-bit mono, {} samples/s):".format(RATE))
for seconds in (3, 5):
    print("  {} s  = {:>7,} bytes   (as 32-bit microphone words: {:>7,})".format(
        seconds, recording_bytes(seconds), recording_bytes(seconds, 4)))
ok = ok and recording_bytes(5) == 128000 and recording_bytes(3) == 76800

print()
print("{:>6} {:>7} {:>9} {:>7} {:>14} {:>14}".format(
    "chunk", "chunks", "audio per", "TCP", "WebSocket", "HTTP chunked"))
print("{:>6} {:>7} {:>9} {:>7} {:>14} {:>14}".format(
    "bytes", "in 5 s", "chunk ms", "segs", "extra bytes/%", "extra bytes/%"))
for chunk in (256, 512, 1024, 2048, 4096, 8192):
    n = chunks_needed(recording_bytes(5), chunk)
    ms = chunk * 1000 // (RATE * BYTES_PER_SAMPLE)
    segments = (chunk + MSS - 1) // MSS
    ws = ws_overhead(chunk)
    ht = http_chunk_overhead(chunk)
    print("{:>6,} {:>7} {:>9} {:>7} {:>8} {:>5.2f}% {:>8} {:>5.2f}%".format(
        chunk, n, ms, segments, ws, 100 * ws / chunk, ht, 100 * ht / chunk))
ok = ok and chunks_needed(128000, 2048) == 63 and ws_overhead(1024) == 8

print()
print("Why not send head + body as one bytes object? It copies the recording:")
for seconds in (3, 5):
    one = recording_bytes(seconds)
    print("  {} s: recording {:>7,} B, plus a copy {:>7,} B = {:>7,} B in two blocks".format(
        seconds, one, one, 2 * one))

try:
    gc.collect()
    free = gc.mem_free()
    print()
    print("free heap now: {:,} bytes".format(free))
    for seconds, width in ((3, 4), (5, 4), (5, 2), (10, 2)):
        need = recording_bytes(seconds, width)
        try:
            block = bytearray(need)
            del block
            verdict = "fits"
        except MemoryError:
            verdict = "does NOT fit"
        gc.collect()
        print("  {:>2} s of {}-bit audio ({:>7,} bytes) : {}".format(
            seconds, width * 8, need, verdict))
except AttributeError:
    print()
    print("(gc.mem_free() only exists on the Pico: run this there to see which recordings fit)")

print()
print("PASS" if ok else "CHECK: a number differs from the chapter")

# Try This
#   1. Add 4096 to the Pico's list of chunk sizes you would use. What does one
#      lost chunk cost in audio (ms)?
#   2. At what chunk size does the WebSocket overhead fall under 0.5%?
