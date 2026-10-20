"""Build the Calendar that agent.toml describes (Chapter 16). Standard library only."""
import json
import os

import agent_config
import calendar_source


def load_calendar(cfg, clock=None):
    """Returns (Calendar, status). status says where the data came from:
    'file', or for a URL 'fetched', 'not-modified', 'recent', or 'stale'."""
    cal_cfg = cfg["calendar"]
    courses = [{"course": c["name"], "teacher": c.get("teacher"), "room": c.get("room")} for c in cfg["courses"]]
    school = cfg["school"]
    if cal_cfg["source"] == "json":
        with open(agent_config.resolve(cfg, cal_cfg["json_path"]), encoding="utf-8") as f:
            data = json.load(f)
        return calendar_source.from_json(data, courses_extra=courses), "file"
    url = os.environ.get("SCHOOL_ICS_URL") or cal_cfg["ics_url"]
    if url:
        cache_dir = agent_config.resolve(cfg, cal_cfg["cache_dir"])
        os.makedirs(cache_dir, exist_ok=True)
        kwargs = {"clock": clock} if clock else {}
        feed = calendar_source.FeedCache(
            url, os.path.join(cache_dir, "feed.ics"),
            min_interval_s=cal_cfg["poll_minutes"] * 60, **kwargs)
        text, status = feed.text()
        source = url
    else:
        path = agent_config.resolve(cfg, cal_cfg["ics_path"])
        with open(path, encoding="utf-8") as f:
            text = f.read()
        status, source = "file", path
    cal = calendar_source.from_ics(text, school["name"], school["timezone"], courses, source=source)
    return cal, status
