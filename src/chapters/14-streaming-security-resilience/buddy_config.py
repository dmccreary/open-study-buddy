# buddy_config.py -- Chapter 14 settings: where the server is and how patient to be
#
# Wi-Fi name and password stay in secrets.py (wifi_ssid, wifi_pass). So does the
# server token: add a line  buddy_token = "..."  to secrets.py. Never put a
# password or token in this file, because this file is the one you share.

BUDDY_HOST = "192.168.1.50"     # CHANGE ME: the address the server printed at start-up
BUDDY_PORT = 8080               # plain HTTP
BUDDY_WS_PORT = 8081            # WebSocket
BUDDY_TLS_PORT = 8443           # HTTPS (only if the server was started with --tls)
DEVICE_ID = "desk-07"
HOSTNAME = "study-buddy-07"

USE_TLS = False                 # True: talk HTTPS on BUDDY_TLS_PORT (see test 07 first)
CA_FILE = "ca.der"              # the certificate to trust when USE_TLS is True (DER file)

CONNECT_TIMEOUT_MS = 15000      # joining Wi-Fi
REQUEST_TIMEOUT_S = 8           # EVERY single socket wait (connect, send, receive)
TOTAL_TIMEOUT_S = 20            # a whole request, however slowly the bytes trickle
MAX_REPLY_BYTES = 2048          # never read more than this from a JSON reply

MAX_UTTERANCE_S = 5             # recording limit; 5 s x 12,800 x 2 bytes = 128,000 bytes
UPLOAD_CHUNK_BYTES = 2048       # one send() of the recording (80 ms of 16-bit audio)
STREAM_CHUNK_BYTES = 1024       # one WebSocket frame (one 40 ms audio frame)

RETRY_ATTEMPTS = 4              # 1 try + 3 retries
BACKOFF_BASE_MS = 500
BACKOFF_CAP_MS = 8000
