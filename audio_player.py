"""
Cross-platform audio playback using pygame.mixer.
Falls back to system commands if pygame is unavailable.
"""

import logging
import platform
import subprocess
import time

log = logging.getLogger("herald.audio")

_USE_PYGAME = True
try:
    import pygame

    pygame.mixer.init()
except ImportError:
    _USE_PYGAME = False
    log.warning("pygame not installed. Falling back to system audio commands.")


def play_audio(path: str, volume: float = 1.0, duration: float = 15.0) -> None:
    """
    Play an audio file for up to `duration` seconds at the given volume.
    Supports MP3, WAV, OGG.
    """
    log.info("Playing: %s (%.0f%% vol, %.0fs)", path, volume * 100, duration)

    if _USE_PYGAME:
        _play_pygame(path, volume, duration)
    else:
        _play_system(path, duration)


def _play_pygame(path: str, volume: float, duration: float) -> None:
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        pygame.mixer.music.play()
        time.sleep(duration)
        pygame.mixer.music.fadeout(1500)
        time.sleep(1.5)
    except Exception as e:
        log.error("pygame playback failed: %s", e)
        _play_system(path, duration)


def _play_system(path: str, duration: float) -> None:
    """OS-level fallback using afplay (macOS), aplay/ffplay (Linux), or PowerShell (Windows)."""
    system = platform.system()
    try:
        if system == "Darwin":
            proc = subprocess.Popen(["afplay", path])
            time.sleep(duration)
            proc.terminate()
        elif system == "Linux":
            # Try ffplay first, then aplay
            for cmd in [["ffplay", "-nodisp", "-autoexit", "-t", str(duration), path],
                        ["aplay", path]]:
                try:
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    proc.wait(timeout=duration + 2)
                    return
                except FileNotFoundError:
                    continue
            log.error("No audio player found. Install ffmpeg or pygame.")
        elif system == "Windows":
            # Use PowerShell + Windows Media Player COM
            ps_cmd = (
                f'$p = New-Object Media.SoundPlayer "{path}"; '
                f"$p.PlaySync()"
            )
            proc = subprocess.Popen(
                ["powershell", "-Command", ps_cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(duration)
            proc.terminate()
        else:
            log.error("Unsupported OS: %s", system)
    except Exception as e:
        log.error("System playback failed: %s", e)
