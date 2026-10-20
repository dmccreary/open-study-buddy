#!/usr/bin/env python3
"""The daily job (Chapter 16): compose the morning briefing and today's
reminders and push them to the devices over MQTT (Chapter 15).

    python3 push_daily.py --now 2026-10-19T07:30            # dry run: print only
    python3 push_daily.py --now 2026-10-19T07:30 --send     # publish (needs paho-mqtt and MQTT_HOST ...)

Run it once each school morning, for example from cron:
    30 7 * * 1-5  cd /path/to/server && python3 push_daily.py --send
It is safe to run twice: every alert id is built from the date, the event and
the lead time, so a device ignores the second copy.
"""
import argparse
import os
import sys
from datetime import datetime

import agent_config
import alerts
import compose
import topics
from load_calendar import load_calendar

HERE = os.path.dirname(os.path.abspath(__file__))


def plan(cal, now, cfg):
    """[(topic, alert dict)] for this morning."""
    school = cfg["school"]["id"]
    out = []
    if cfg["features"]["briefing"]:
        brief = compose.daily_briefing(cal, now, cfg)
        if brief:
            text = compose.fit_sentences(brief["sentences"], alerts.MAX_TEXT_BRIEFING)
            short = cfg["school"].get("short_name") or cfg["school"]["name"]
            alert = alerts.make_alert("%s-briefing" % now.strftime("%Y%m%d"), "briefing",
                                      compose.shorten("Good morning, " + short, alerts.MAX_TITLE),
                                      brief["show"], text)
            out.append((topics.school_alert(school), alert))
    if cfg["features"]["test_alerts"] or cfg["features"]["due_alerts"] or cfg["features"]["no_school_notices"]:
        for (kind, room), alert in compose.reminders(cal, now, cfg):
            if kind == "room" and cfg["mqtt"]["alert_topic_scope"] == "room":
                out.append((topics.room_alert(school, room), alert))
            else:
                out.append((topics.school_alert(school), alert))
    return out


def send(messages):
    import paho.mqtt.client as mqtt
    host = os.environ.get("MQTT_HOST")
    if not host:
        sys.exit("Set MQTT_HOST (and MQTT_USER / MQTT_PASSWORD) first, or leave off --send.")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="push-daily-%d" % os.getpid())
    if os.environ.get("MQTT_USER"):
        client.username_pw_set(os.environ["MQTT_USER"], os.environ.get("MQTT_PASSWORD", ""))
    client.connect(host, int(os.environ.get("MQTT_PORT", "1883")), keepalive=30)
    client.loop_start()
    try:
        for topic, alert in messages:
            info = client.publish(topic, alerts.encode_alert(alert), qos=1, retain=False)
            info.wait_for_publish(timeout=5)
            if not info.is_published():
                sys.exit("The broker did not acknowledge %s" % topic)
    finally:
        client.loop_stop()
        client.disconnect()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--config", default=os.path.join(HERE, "agent.toml"))
    p.add_argument("--now", help="school-local time, e.g. 2026-10-19T07:30 (default: now)")
    p.add_argument("--send", action="store_true", help="publish; without it, only print")
    args = p.parse_args(argv)
    cfg = agent_config.load(args.config)
    cal, status = load_calendar(cfg)
    now = datetime.fromisoformat(args.now).replace(tzinfo=cal.tz) if args.now else datetime.now(cal.tz)
    messages = plan(cal, now, cfg)
    print("%s (%s): %d message(s)" % (now.strftime("%a %Y-%m-%d %H:%M"), cal.tz.key, len(messages)))
    for topic, alert in messages:
        print("\n%s\n  %s  (%d bytes)" % (topic, alerts.encode_alert(alert), len(alerts.encode_alert(alert).encode())))
    if args.send:
        send(messages)
        print("\nsent %d message(s) at QoS 1" % len(messages))
    else:
        print("\ndry run: nothing was sent (add --send)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
