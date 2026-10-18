#!/usr/bin/env bash
# Upload one chapter's code to the Pico 2 W, and optionally run one file.
#
#   ./upload-chapter.sh 05                     upload kit + chapter 5 files
#   ./upload-chapter.sh 05 01-fill-timing.py   ...then run that file
#   ./upload-chapter.sh 05 --no-kit            chapter files only (the kit's
#                                              config.py and lib/ are already there)
#
# What is uploaded:
#   1. The kit's lib/ and config.py from ../kits/study-buddy-base/ (the tested
#      pin numbers, display driver, and fonts every chapter file imports).
#      Skipped with --no-kit.
#   2. Every top-level .py and .rgb565 file in the chapter folder. Files in
#      subfolders such as tools/ stay on your computer.
#
# Chapter 1 runs on your computer; see each
# chapter's README.md.
#
# IMPORTANT: Quit Thonny first. Only one program can use the Pico's serial
# port at a time. Override the port with:  PORT=/dev/cu.usbmodem14301 ./upload-chapter.sh 05

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$HERE/../kits/study-buddy-base"

if [[ $# -lt 1 ]]; then
    echo "usage: $0 CHAPTER_NUMBER [FILE_TO_RUN | --no-kit] [--no-kit]" >&2
    exit 1
fi

num="$(printf '%02d' "$((10#$1))")"
shift

no_kit=0
run_file=""
for arg in "$@"; do
    if [[ "$arg" == "--no-kit" ]]; then no_kit=1; else run_file="$arg"; fi
done

shopt -s nullglob
dirs=( "$HERE/$num"-*/ )
shopt -u nullglob
if (( ${#dirs[@]} != 1 )); then
    echo "Error: could not find exactly one folder named $num-* in $HERE" >&2
    exit 1
fi
CHAPTER="${dirs[0]%/}"

if ! command -v mpremote >/dev/null 2>&1; then
    echo "Error: mpremote is not installed. Install with: pip install mpremote" >&2
    exit 1
fi

if [[ -z "${PORT:-}" ]]; then
    shopt -s nullglob
    serial_devs=( /dev/cu.usbmodem* /dev/ttyACM* /dev/ttyUSB* )
    shopt -u nullglob
    if (( ${#serial_devs[@]} == 0 )); then
        echo "Error: No Pico detected. Plug it in and try again." >&2
        exit 1
    fi
    PORT="${serial_devs[0]}"
fi
echo "Using device: $PORT   (quit Thonny first!)"

upload() {
    echo "  -> ${2#:}"
    mpremote connect "$PORT" fs cp "$1" "$2" || {
        echo "Error: could not write to the Pico. Is Thonny still connected?" >&2
        exit 1
    }
}

mpremote connect "$PORT" soft-reset >/dev/null 2>&1 || true

if (( no_kit == 0 )); then
    echo "Uploading the kit (lib/ and config.py) ..."
    mpremote connect "$PORT" fs mkdir :lib >/dev/null 2>&1 || true
    for f in "$KIT"/lib/*.py; do upload "$f" ":lib/$(basename "$f")"; done
    upload "$KIT/config.py" :config.py
    if [[ -f "$KIT/secrets.py" ]]; then upload "$KIT/secrets.py" :secrets.py; fi
fi

echo "Uploading chapter $num files ..."
shopt -s nullglob
for f in "$CHAPTER"/*.py "$CHAPTER"/*.rgb565; do
    upload "$f" ":$(basename "$f")"
done
shopt -u nullglob

if [[ -n "$run_file" ]]; then
    echo
    echo "Running $run_file (Ctrl-C to stop) ..."
    mpremote connect "$PORT" run "$CHAPTER/$run_file"
else
    echo
    echo "Done. Run a file with:  mpremote connect $PORT run $CHAPTER/<file>.py"
fi
