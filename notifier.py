"""
Cross-platform desktop notifications.
"""

import logging
import platform
import subprocess

log = logging.getLogger("herald.notifier")


def notify(title: str, message: str) -> None:
    """Send a desktop notification."""
    system = platform.system()
    log.info("Notification: %s — %s", title, message.replace("\n", " | "))

    try:
        if system == "Darwin":
            _notify_macos(title, message)
        elif system == "Linux":
            _notify_linux(title, message)
        elif system == "Windows":
            _notify_windows(title, message)
        else:
            log.warning("Notifications not supported on %s", system)
    except Exception as e:
        log.warning("Notification failed: %s", e)


def _notify_macos(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script], check=True)


def _notify_linux(title: str, message: str) -> None:
    subprocess.run(["notify-send", title, message], check=True)


def _notify_windows(title: str, message: str) -> None:
    ps_script = f"""
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $template = @"
    <toast>
        <visual><binding template="ToastGeneric">
            <text>{title}</text>
            <text>{message}</text>
        </binding></visual>
    </toast>
"@
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml($template)
    $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("BBC Meeting Herald")
    $notifier.Show([Windows.UI.Notifications.ToastNotification]::new($xml))
    """
    subprocess.run(
        ["powershell", "-Command", ps_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
