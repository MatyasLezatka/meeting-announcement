#!/usr/bin/env python3
"""
BBC Meeting Herald — Your meetings deserve a proper introduction.
Monitors Apple Calendar and plays dramatic audio before every meeting.
"""

import time
import logging
import signal
import sys
import webbrowser
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from calendar_client import CalendarClient
from audio_player import play_audio
from notifier import notify

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("herald")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
DEFAULT_CONFIG = {
    "audio_file": "audio/theme.mp3",
    "lead_time_seconds": 60,
    "volume": 1.0,
    "poll_interval_seconds": 30,
    "auto_open_meeting_link": True,
    "play_duration_seconds": 15,
    "desktop_notification": True,
}

# Meetings we already announced — keyed by event ID
announced: set[str] = set()


def load_config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user = yaml.safe_load(f) or {}
        cfg.update(user)
    return cfg


def extract_meeting_link(event: dict) -> str | None:
    """Pull Zoom / Meet / Teams link from event URL, notes, or location."""
    # Check the event URL first (Calendar.app stores conference links here)
    url = event.get("url", "")
    if url and any(domain in url for domain in ["zoom.us", "meet.google", "teams.microsoft"]):
        return url

    # Fallback: regex the notes and location
    text = event.get("notes", "") + " " + event.get("location", "")
    patterns = [
        r"https?://[\w.-]*zoom\.us/j/\S+",
        r"https?://meet\.google\.com/\S+",
        r"https?://teams\.microsoft\.com/l/meetup-join/\S+",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def herald_loop(cfg: dict, cal: CalendarClient) -> None:
    lead = cfg["lead_time_seconds"]
    poll = cfg["poll_interval_seconds"]
    audio = Path(cfg["audio_file"])

    if not audio.exists():
        log.error("Audio file not found: %s", audio)
        log.error("Place your audio file there or update config.yaml")
        sys.exit(1)

    log.info("Herald active. Polling every %ds, announcing %ds before meetings.", poll, lead)
    log.info("Audio: %s | Volume: %.0f%%", audio, cfg["volume"] * 100)

    while True:
        try:
            events = cal.upcoming_events(minutes_ahead=5)

            for ev in events:
                eid = ev["id"]
                if eid in announced:
                    continue

                now = datetime.now(timezone.utc)
                delta = (ev["start_dt"] - now).total_seconds()

                if 0 < delta <= lead:
                    title = ev["summary"]
                    cal_name = ev.get("calendar_name", "")
                    label = f"{title} [{cal_name}]" if cal_name else title

                    log.info("🔴 BREAKING: \"%s\" in %d seconds", label, int(delta))

                    # Play the theme
                    play_audio(
                        str(audio),
                        volume=cfg["volume"],
                        duration=cfg["play_duration_seconds"],
                    )

                    # Desktop notification
                    if cfg["desktop_notification"]:
                        notify(
                            title="📺 Meeting Starting",
                            message=f"{title}\nStarting in {int(delta)} seconds",
                        )

                    # Auto-open meeting link
                    if cfg["auto_open_meeting_link"]:
                        link = extract_meeting_link(ev)
                        if link:
                            log.info("Opening meeting link: %s", link)
                            webbrowser.open(link)

                    announced.add(eid)

        except Exception as e:
            log.warning("Poll error: %s", e)

        time.sleep(poll)


def cleanup(*_):
    log.info("Herald signing off. Good night.")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    cfg = load_config()
    cal = CalendarClient()
    herald_loop(cfg, cal)


if __name__ == "__main__":
    main()
