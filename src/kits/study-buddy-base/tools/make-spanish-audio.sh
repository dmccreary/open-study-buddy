#!/usr/bin/env bash
# Make the spoken words for the Spanish quiz (demo_spanish.py), one WAV
# file per word, in ../spanish/. Runs on a Mac, using the Spanish voice
# that comes with macOS -- no downloads, no accounts.
#
#   tools/make-spanish-audio.sh            # the default voice, Paulina
#   VOICE=Monica tools/make-spanish-audio.sh
#
# See which Spanish voices your Mac has with:  say -v '?' | grep es_
#
# Each file is 16-bit mono at 16000 Hz -- the format
# demo_kit.Speaker.play_wav() plays -- about 20 KB a word. upload-code.sh
# copies them to the Pico's spanish/ folder.
#
# The words must match the first word of each pair in WORDS in
# demo_spanish.py. Add one there, add it here, and run this again.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$SCRIPT_DIR/../spanish"
VOICE="${VOICE:-Paulina}"

WORDS=(hola gracias perro gato casa libro agua manzana escuela amigo
       rojo verde sol leche mesa ventana)

if ! command -v say >/dev/null 2>&1; then
    echo "Error: this needs the macOS 'say' command." >&2
    exit 1
fi

mkdir -p "$OUT"
for word in "${WORDS[@]}"; do
    say -v "$VOICE" -o "$OUT/$word.wav" \
        --file-format=WAVE --data-format=LEI16@16000 "$word"
    printf '  %-10s %6d bytes\n' "$word" "$(wc -c < "$OUT/$word.wav")"
done
echo "Made ${#WORDS[@]} words in $OUT with the voice $VOICE."
