# buddy_config.py -- where the buddy server is, and how patient to be
#
# Edit BUDDY_HOST to the address the server printed when it started
# ("put this in buddy_config.py on the Pico"). Wi-Fi name and password are NOT
# here: they stay in secrets.py (wifi_ssid, wifi_pass), which is never committed.

BUDDY_HOST = "192.168.1.50"     # CHANGE ME: your server's address on the classroom network
BUDDY_PORT = 8080
DEVICE_ID = "desk-07"           # who is asking; 1 to 32 characters
HOSTNAME = "study-buddy-07"     # the Pico's own name on the network

CONNECT_TIMEOUT_MS = 15000      # give up joining Wi-Fi after this long
REQUEST_TIMEOUT_S = 8           # every socket wait gives up after this long
MAX_REPLY_BYTES = 2048          # never read more than this from the server
