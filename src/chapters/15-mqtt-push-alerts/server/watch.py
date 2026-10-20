#!/usr/bin/env python3
"""A tiny subscriber for testing (Chapter 15). Prints every message that
matches the filter(s), with a flag for retained messages.

    pip install paho-mqtt
    export MQTT_HOST=192.168.1.50 MQTT_USER=dashboard MQTT_PASSWORD=...
    python3 watch.py                         # everything about school "crhs"
    python3 watch.py 'school/crhs/device/+/status' --seconds 60

Stops after --seconds (default: until Ctrl-C).
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import topics   # noqa: E402


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("filters", nargs="*", default=["school/crhs/#"])
    p.add_argument("--seconds", type=float, default=0)
    args = p.parse_args(argv)
    for f in args.filters:
        if not topics.valid_filter(f):
            sys.exit("Not a valid subscription filter: %r" % f)
    host = os.environ.get("MQTT_HOST")
    if not host:
        sys.exit("Set MQTT_HOST (and MQTT_USER / MQTT_PASSWORD) first.")

    import paho.mqtt.client as mqtt
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="watch-%d" % os.getpid())
    if os.environ.get("MQTT_USER"):
        client.username_pw_set(os.environ["MQTT_USER"], os.environ.get("MQTT_PASSWORD", ""))

    def on_connect(client, userdata, flags, reason_code, properties):
        print("connected (%s); subscribing to %s" % (reason_code, ", ".join(args.filters)))
        for f in args.filters:
            client.subscribe(f, qos=1)

    def on_message(client, userdata, msg):
        flag = "R" if msg.retain else " "
        print("%s %s %-48s %s" % (time.strftime("%H:%M:%S"), flag, msg.topic,
                                  msg.payload.decode(errors="replace")))

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, int(os.environ.get("MQTT_PORT", "1883")), keepalive=30)
    client.loop_start()
    try:
        deadline = time.time() + args.seconds if args.seconds else None
        while deadline is None or time.time() < deadline:
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
