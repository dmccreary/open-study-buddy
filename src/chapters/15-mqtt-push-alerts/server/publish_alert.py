#!/usr/bin/env python3
"""Publish one alert to the school broker (Chapter 15).

Runs on your COMPUTER or on the school Pi. Needs:  pip install paho-mqtt
The broker address and account come from environment variables, never from
the command line or a file in the repository:

    export MQTT_HOST=192.168.1.50 MQTT_USER=buddy-server MQTT_PASSWORD=...

Examples
    python3 publish_alert.py --room 214 --type test --title "Algebra II test" \
        --when "Tomorrow 8:00 AM" --text "Algebra II test tomorrow at 8 AM."
    python3 publish_alert.py --all --type notice --title "Early dismissal" \
        --when "Friday 12:00 PM" --text "School ends at noon on Friday." --retain
    python3 publish_alert.py --all --clear           # remove the retained alert
    python3 publish_alert.py --room 214 --type test --title T --when W --text X --dry-run

--dry-run prints the topic and payload and connects to nothing.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import alerts      # noqa: E402  (shared with the Pico)
import topics      # noqa: E402


def build(args):
    """Returns (topic, payload text). payload is '' for --clear."""
    school = topics.slug(args.school)
    if args.all:
        topic = topics.school_alert(school)
    else:
        topic = topics.room_alert(school, topics.slug(args.room))
    if args.clear:
        return topic, ""
    alert_id = args.id or time.strftime("%Y%m%d-%H%M%S")
    alert = alerts.make_alert(alert_id, args.type, args.title, args.when, args.text, args.at)
    return topic, alerts.encode_alert(alert)


def publish(topic, payload, retain, qos=1):
    import paho.mqtt.client as mqtt
    host = os.environ.get("MQTT_HOST")
    if not host:
        sys.exit("Set MQTT_HOST (and MQTT_USER / MQTT_PASSWORD) first, or use --dry-run.")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="publish-alert-%d" % os.getpid())
    if os.environ.get("MQTT_USER"):
        client.username_pw_set(os.environ["MQTT_USER"], os.environ.get("MQTT_PASSWORD", ""))
    client.connect(host, int(os.environ.get("MQTT_PORT", "1883")), keepalive=30)
    client.loop_start()
    try:
        info = client.publish(topic, payload, qos=qos, retain=retain)
        info.wait_for_publish(timeout=5)
        if not info.is_published():
            sys.exit("The broker did not acknowledge the message within 5 seconds.")
    finally:
        client.loop_stop()
        client.disconnect()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--school", default="crhs")
    where = p.add_mutually_exclusive_group(required=True)
    where.add_argument("--room", help="classroom, e.g. 214 or 'Lab 130'")
    where.add_argument("--all", action="store_true", help="school-wide alert")
    p.add_argument("--type", default="notice", choices=alerts.TYPES)
    p.add_argument("--title", default="")
    p.add_argument("--when", default="")
    p.add_argument("--text", default="")
    p.add_argument("--at", help="UTC time for dashboards, e.g. 2026-10-20T13:00Z")
    p.add_argument("--id", help="alert id (default: the current date and time)")
    p.add_argument("--retain", action="store_true", help="keep it for devices that connect later")
    p.add_argument("--clear", action="store_true", help="delete the retained alert on the topic")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    try:
        topic, payload = build(args)
    except ValueError as error:
        sys.exit("Not a valid alert: %s" % error)
    retain = args.retain or args.clear
    print("topic  :", topic)
    print("payload: %s (%d bytes)%s" % (payload or "(empty)", len(payload.encode()),
                                        "  retained" if retain else ""))
    if args.dry_run:
        print("dry run: nothing was sent")
        return 0
    publish(topic, payload, retain)
    print("sent at QoS 1 and acknowledged by the broker")
    return 0


if __name__ == "__main__":
    sys.exit(main())
