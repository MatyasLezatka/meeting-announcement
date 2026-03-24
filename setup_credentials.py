#!/usr/bin/env python3
"""
Interactive helper to verify Apple Calendar access and test the herald setup.
Run this once before starting the herald.
"""

import sys
from pathlib import Path


def main():
    print("=" * 60)
    print("  BBC Meeting Herald — Setup Check")
    print("=" * 60)
    print()

    # Check audio file
    audio_path = Path(__file__).parent / "audio" / "theme.mp3"
    if audio_path.exists():
        print(f"[OK] Audio file found: {audio_path}")
    else:
        print(f"[MISSING] No audio file at {audio_path}")
        print("  Place your MP3/WAV file at audio/theme.mp3")
        print("  Or update the path in config.yaml")
        print()

    # Test calendar access
    print("\nTesting Apple Calendar access...")
    print("(macOS may show a permission dialog — click 'Allow')\n")

    try:
        from calendar_client import CalendarClient

        client = CalendarClient()
        events = client.upcoming_events(minutes_ahead=120)
        print(f"[SUCCESS] Connected. Found {len(events)} event(s) in the next 2 hours.")

        if events:
            print("\nUpcoming:")
            for ev in events:
                title = ev["summary"]
                cal = ev.get("calendar_name", "")
                start = ev["start_dt"].strftime("%H:%M")
                print(f"  • {start} — {title} [{cal}]")
        else:
            print("  (No events in the next 2 hours)")

        print("\nSetup complete. Run `python herald.py` to start the herald.")

    except PermissionError as e:
        print(f"\n[ERROR] {e}")
        print("\nFix: System Settings → Privacy & Security → Calendars → enable for Terminal/Python")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
