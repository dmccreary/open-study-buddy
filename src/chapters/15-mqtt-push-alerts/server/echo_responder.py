#!/usr/bin/env python3
"""Answers the device's round-trip test (Chapter 15, test 08).

The device publishes to  school/<school>/device/<id>/echo  and this program
publishes the same bytes back on  .../echo-reply .  Run it on the school Pi
or your computer:    pip install paho-mqtt ; python3 echo_responder.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import topics   # noqa: E402

FILTER = "school/+/device/+/echo"


def reply_topic(topic):
    """'school/crhs/device/desk-07/echo' -> '.../echo-reply'. None if it is not an echo topic."""
    if not topics.topic_matches(FILTER, topic):
        return None
    return topic + "-reply"


def main():
    host = os.environ.get("MQTT_HOST")
    if not host:
        sys.exit("Set MQTT_HOST (and MQTT_USER / MQTT_PASSWORD) first.")
    import paho.mqtt.client as mqtt
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="echo-responder")
    if os.environ.get("MQTT_USER"):
        client.username_pw_set(os.environ["MQTT_USER"], os.environ.get("MQTT_PASSWORD", ""))

    def on_connect(client, userdata, flags, reason_code, properties):
        client.subscribe(FILTER, qos=0)
        print("echoing", FILTER)

    def on_message(client, userdata, msg):
        target = reply_topic(msg.topic)
        if target:
            client.publish(target, msg.payload, qos=0)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, int(os.environ.get("MQTT_PORT", "1883")), keepalive=30)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(main())
