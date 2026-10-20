#!/usr/bin/env bash
# Make a self-signed certificate for a LAB DEMO of HTTPS (test 07).
#
#   ./make-cert.sh 192.168.1.50        # the address or name the Pico connects to
#
# Writes server.pem + server.key (for buddy_server.py / ws_server.py --tls) and
# ca.der (the same certificate in DER form: copy THAT to the Pico with
#   mpremote fs cp ca.der :ca.der
# so the Pico can check it). The certificate is valid for 365 days and lists the
# address in its subjectAltName, which is what a client checks. server.key is a
# secret: it never leaves the server and is never committed.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then echo "usage: $0 SERVER_IP_OR_NAME [OUTPUT_FOLDER]" >&2; exit 1; fi
HOST="$1"
OUT="${2:-$(dirname "${BASH_SOURCE[0]}")}"
mkdir -p "$OUT"
cd "$OUT"
if [[ "$HOST" =~ ^[0-9.]+$ ]]; then SAN="IP:$HOST"; else SAN="DNS:$HOST"; fi
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -keyout server.key -out server.pem -days 365 -subj "/CN=$HOST" \
    -addext "subjectAltName=$SAN" -addext "basicConstraints=critical,CA:TRUE"
openssl x509 -in server.pem -outform DER -out ca.der
chmod 600 server.key
echo "wrote server.pem, server.key, ca.der  (ca.der is $(wc -c < ca.der | tr -d ' ') bytes)"
