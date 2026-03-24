"""
macOS Calendar client using EventKit via PyObjC.
Reads directly from the same calendar store as Apple Calendar.app.
Supports all synced accounts (Google, iCloud, Exchange, etc.).
"""

import logging
from datetime import datetime, timedelta, timezone

import objc
from EventKit import (
    EKEntityMaskEvent,
    EKEventStore,
    EKSpanThisEvent,
    EKAuthorizationStatusAuthorized,
    EKAuthorizationStatusNotDetermined,
)
from Foundation import NSDate, NSRunLoop, NSDefaultRunLoopMode

log = logging.getLogger("herald.calendar")


class CalendarClient:
    def __init__(self):
        self.store = EKEventStore.alloc().init()
        self._request_access()
        log.info("Calendar client ready. Reading from Apple Calendar.")

    def _request_access(self) -> None:
        """Request calendar access. macOS will show a permission dialog on first run."""
        status = EKEventStore.authorizationStatusForEntityType_(EKEntityMaskEvent)

        if status == EKAuthorizationStatusAuthorized:
            log.info("Calendar access already granted.")
            return

        if status == EKAuthorizationStatusNotDetermined:
            log.info("Requesting calendar access (check the system dialog)...")
            granted = [None]
            error = [None]

            def callback(g, e):
                granted[0] = g
                error[0] = e

            self.store.requestFullAccessToEventsWithCompletion_(callback)

            # Spin the run loop briefly to let the callback fire
            run_loop = NSRunLoop.currentRunLoop()
            deadline = datetime.now() + timedelta(seconds=30)
            while granted[0] is None and datetime.now() < deadline:
                run_loop.runMode_beforeDate_(
                    NSDefaultRunLoopMode,
                    NSDate.dateWithTimeIntervalSinceNow_(0.5),
                )

            if not granted[0]:
                raise PermissionError(
                    "Calendar access denied. Grant access in "
                    "System Settings → Privacy & Security → Calendars"
                )
            log.info("Calendar access granted.")
        else:
            raise PermissionError(
                "Calendar access denied. Grant access in "
                "System Settings → Privacy & Security → Calendars"
            )

    def upcoming_events(self, minutes_ahead: int = 5) -> list[dict]:
        """Fetch events starting within the next `minutes_ahead` minutes."""
        now = NSDate.date()
        end = NSDate.dateWithTimeIntervalSinceNow_(minutes_ahead * 60)

        predicate = self.store.predicateForEventsWithStartDate_endDate_calendars_(
            now, end, None  # None = all calendars
        )
        ek_events = self.store.eventsMatchingPredicate_(predicate)

        if not ek_events:
            return []

        events = []
        for ev in ek_events:
            # Skip all-day events
            if ev.isAllDay():
                continue

            # Skip declined events (status 3 = declined)
            if ev.status() == 3:
                continue

            start_ns = ev.startDate()
            start_ts = start_ns.timeIntervalSince1970()
            start_dt = datetime.fromtimestamp(start_ts, tz=timezone.utc)

            event_dict = {
                "id": ev.eventIdentifier(),
                "summary": ev.title() or "Untitled Meeting",
                "start_dt": start_dt,
                "location": ev.location() or "",
                "notes": ev.notes() or "",
                "url": ev.URL().absoluteString() if ev.URL() else "",
                "calendar_name": ev.calendar().title() if ev.calendar() else "",
            }
            events.append(event_dict)

        return events
