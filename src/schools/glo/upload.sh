#!/usr/bin/env bash
# Upload the GLO demo to the Pico 2 W and run it.
#
#   ./upload.sh                  kit files + demo, then run 01-glo-buddy.py
#   ./upload.sh --no-run         upload only
#
# The kit's config.py, display driver and fonts come from
# ../../kits/study-buddy-base/ so the pin numbers live in one place.
# Quit Thonny first. Override the port with:  PORT=/dev/cu.usbmodem14301 ./upload.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$HERE/../../kits/study-buddy-base"

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
mpremote connect "$PORT" fs mkdir :lib >/dev/null 2>&1 || true
for f in "$KIT"/lib/*.py; do upload "$f" ":lib/$(basename "$f")"; done
upload "$KIT/config.py" :config.py
upload "$HERE/griffin-140.rgb565" :griffin-140.rgb565
upload "$HERE/01-glo-buddy.py" :01-glo-buddy.py

if [[ "${1:-}" != "--no-run" ]]; then
    echo
    echo "Running 01-glo-buddy.py ..."
    mpremote connect "$PORT" run "$HERE/01-glo-buddy.py"
fi
