# secrets-template.py -- your WiFi network name and password.
#
# Copy this file to secrets.py and type in your own network:
#
#     cp secrets-template.py secrets.py
#
# (Or, in Thonny, open this file on the Pico, edit it, and use
# File > Save as... to save it on the Pico as secrets.py.)
#
# secrets.py is listed in the repository's .gitignore, so your password
# stays on your computer and your Pico -- it is never committed to GitHub.
# upload-code.sh sends both files to the Pico: this template, which has
# no real password in it, and secrets.py if you have made one.
#
# The demos that use WiFi (the clock and weather demo in
# 20-demo-template.py, wifi_time.py, forecast.py) import secrets.py. They
# show "No secrets.py on the Pico" and carry on without WiFi if it is
# missing.
#
# The Pico 2 W only connects to 2.4 GHz networks, not 5 GHz ones.

wifi_ssid = "your-network-name"
wifi_pass = "your-network-password"
