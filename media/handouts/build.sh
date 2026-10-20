#!/usr/bin/env bash
# Generate one-pager.pdf (US Letter) from one-pager.html.
# Refreshes the embedded QR code first, then renders with installed Google Chrome.
#
# Requires: pip install segno playwright
# Usage:    media/handouts/build.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

python3 build-pdf.py

echo "Open: $(pwd)/one-pager.pdf"
