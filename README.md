# Meeting announcement

A macOS daemon that monitors your Apple Calendar and plays your favourite theme (or any audio) before every meeting.

![Python](https://img.shields.io/badge/python-3.9+-blue)
![macOS](https://img.shields.io/badge/macOS-only-black)
![License](https://img.shields.io/badge/license-MIT-green)
![Vibes](https://img.shields.io/badge/vibes-dramatic-red)

## How It Works

1. Reads directly from Apple Calendar via macOS EventKit (same data store as Calendar.app)
2. Sees **all** your calendars — Google, iCloud, Exchange, whatever you've synced
3. Detects meetings starting in the next N seconds (default: 60)
4. Plays your chosen audio file
5. Shows a desktop notification with the meeting title

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/bbc-meeting-herald.git
cd bbc-meeting-herald

# Install dependencies
pip install -r requirements.txt

# Add your audio file
cp /path/to/bbc-news-theme.mp3 audio/theme.mp3

# Test setup (will ask for calendar permission on first run)
python setup_credentials.py

# Run the herald
python herald.py
```

On first run, macOS will ask for calendar access. Click **Allow**. If you miss it, grant access in **System Settings → Privacy & Security → Calendars**.

## Getting the Audio

Use any MP3 or WAV file you like.

Place your file at `audio/theme.mp3`, or update the path in `config.yaml`.

## Configuration

```yaml
# config.yaml
audio_file: "audio/theme.mp3"      # Path to your audio file
lead_time_seconds: 60               # Seconds before meeting to play
volume: 1.0                         # 0.0 to 1.0 (1.0 = full blast)
poll_interval_seconds: 30           # How often to check calendar
auto_open_meeting_link: true        # Auto-open Zoom/Meet/Teams links
play_duration_seconds: 15           # Seconds of audio to play
desktop_notification: true          # Show macOS notification
```

## Features

- **Native macOS**: Reads from EventKit — sees all calendars synced to Calendar.app
- **Zero config auth**: No API keys, no OAuth, just a one-time macOS permission
- **Smart dedup**: Won't play twice for the same meeting
- **Meeting link detection**: Extracts and auto-opens Zoom, Google Meet, and Teams links from event URL, notes, or location
- **Desktop notifications**: Native macOS notifications with meeting title + time
- **Graceful**: Skips all-day events and declined meetings

## Project Structure

```
bbc-meeting-herald/
├── herald.py              # Main daemon
├── calendar_client.py     # Apple Calendar (EventKit) client
├── audio_player.py        # Audio playback (pygame + afplay fallback)
├── notifier.py            # macOS desktop notifications
├── config.yaml            # User configuration
├── requirements.txt       # Dependencies
├── setup_credentials.py   # Setup checker + permission test
├── audio/                 # Place your audio file here
│   └── .gitkeep
├── LICENSE
└── README.md
```

## Running on Login

To have the herald start automatically when you log in:

```bash
# Copy the launch agent
cp dev/com.bbc-herald.plist ~/Library/LaunchAgents/

# Load it
launchctl load ~/Library/LaunchAgents/com.bbc-herald.plist

# To stop
launchctl unload ~/Library/LaunchAgents/com.bbc-herald.plist
```

## Why

Because every meeting should feel like breaking news.

## License

MIT
