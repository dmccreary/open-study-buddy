#!/usr/bin/env python3
"""Home Assistant MQTT discovery messages for one Study Buddy (Chapter 15).

ILLUSTRATIVE: built from Home Assistant's MQTT discovery documentation and
checked only for valid JSON. It has NOT been tried against a real Home
Assistant. Discovery topics look like
    homeassistant/<component>/<object_id>/config
and the payload tells Home Assistant which topics to read.

    python3 ha_discovery.py --device desk-07            # print what would be sent
    python3 ha_discovery.py --device desk-07 --send     # publish (needs paho-mqtt, MQTT_HOST ...)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import topics   # noqa: E402


def messages(school, device):
    """[(config topic, payload dict), ...] for the device's two entities."""
    status = topics.device_status(school, device)
    telemetry = topics.device_telemetry(school, device)
    uid = "osb_%s_%s" % (school, device.replace("-", "_"))
    info = {"identifiers": [uid], "name": "Study Buddy %s" % device,
            "manufacturer": "Open Study Buddy", "model": "Pico 2 W kit"}
    online = {
        "name": "Online", "unique_id": uid + "_online",
        "state_topic": status, "payload_on": "online", "payload_off": "offline",
        "device_class": "connectivity", "device": info,
    }
    volume = {
        "name": "Volume", "unique_id": uid + "_volume",
        "state_topic": telemetry, "value_template": "{{ value_json.vol }}",
        "unit_of_measurement": "%",
        "availability_topic": status, "payload_available": "online",
        "payload_not_available": "offline", "device": info,
    }
    return [("homeassistant/binary_sensor/%s_online/config" % uid, online),
            ("homeassistant/sensor/%s_volume/config" % uid, volume)]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--school", default="crhs")
    p.add_argument("--device", required=True)
    p.add_argument("--send", action="store_true")
    args = p.parse_args(argv)
    msgs = messages(topics.slug(args.school), topics.slug(args.device))
    for topic, payload in msgs:
        print(topic)
        print(json.dumps(payload, indent=2))
    if args.send:
        host = os.environ.get("MQTT_HOST")
        if not host:
            sys.exit("Set MQTT_HOST (and MQTT_USER / MQTT_PASSWORD) first.")
        import paho.mqtt.client as mqtt
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ha-discovery")
        if os.environ.get("MQTT_USER"):
            client.username_pw_set(os.environ["MQTT_USER"], os.environ.get("MQTT_PASSWORD", ""))
        client.connect(host, int(os.environ.get("MQTT_PORT", "1883")), keepalive=30)
        client.loop_start()
        for topic, payload in msgs:
            client.publish(topic, json.dumps(payload), qos=1, retain=True).wait_for_publish(5)
        client.loop_stop()
        client.disconnect()
        print("sent (retained)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
