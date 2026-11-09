"""
Project FRIDAY
Phase 16.14

Proactive Event Manager

Responsibilities:
    - Receive events
    - Store events
    - Notify listeners
    - Prevent duplicate events within cooldown
    - Protect shared state from background-thread races
    - Maintain events in priority order
"""

import threading
from datetime import datetime

from .event import Event


class EventManager:

    def __init__(self, deduplication_cooldown=60):
        self.events = []
        self.listeners = []

        self.deduplication_cooldown = deduplication_cooldown
        self.recent_events = {}

        # Protect shared state because proactive
        # sources run in background threads.
        self.lock = threading.RLock()

    # --------------------------------------------------------
    # LISTENER MANAGEMENT
    # --------------------------------------------------------

    def register_listener(self, listener):
        with self.lock:
            if listener not in self.listeners:
                self.listeners.append(listener)

    # --------------------------------------------------------
    # EVENT FINGERPRINT
    # --------------------------------------------------------

    def _fingerprint(self, event):

        data = event.data or {}

        relevant_data = tuple(
            sorted(
                (
                    str(key),
                    str(value),
                )
                for key, value in data.items()
                if key not in (
                    "created_at",
                    "timestamp",
                )
            )
        )

        return (
            event.event_type,
            event.source,
            event.priority,
            relevant_data,
        )

    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    def _is_duplicate(self, event):

        now = datetime.now()
        fingerprint = self._fingerprint(event)

        previous_time = self.recent_events.get(
            fingerprint
        )

        if previous_time is None:
            self.recent_events[fingerprint] = now
            return False

        elapsed = (
            now - previous_time
        ).total_seconds()

        if elapsed < self.deduplication_cooldown:
            print(
                "[EventManager] Duplicate event suppressed: "
                f"{event}"
            )
            return True

        self.recent_events[fingerprint] = now

        return False

    # --------------------------------------------------------
    # EVENT PRIORITY
    # --------------------------------------------------------

    def _priority_key(self, event):
        """
        Higher-priority events come first.

        If two events have the same priority,
        newer events come first.
        """

        return (
            event.priority,
            event.created_at.timestamp()
        )

    # --------------------------------------------------------
    # EMIT EVENT
    # --------------------------------------------------------

    def emit(self, event):

        if not isinstance(event, Event):
            raise TypeError(
                "event must be an Event object"
            )

        with self.lock:

            if self._is_duplicate(event):
                return False

            self.events.append(event)

            # Keep event history ordered by priority.
            #
            # Higher priority = processed/displayed first
            # when retrieving recent events.
            self.events.sort(
                key=self._priority_key,
                reverse=True
            )

            print(
                f"[EventManager] Event received: {event}"
            )

            listeners = list(self.listeners)

        # Notify listeners outside the lock.
        #
        # This prevents slow reasoning/TTS operations
        # from blocking other event sources.
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                print(
                    "[EventManager] Listener error: "
                    + str(e)
                )

        return True

    # --------------------------------------------------------
    # EVENT HISTORY
    # --------------------------------------------------------

    def get_recent_events(self, limit=10):

        with self.lock:
            return self.events[:limit]

    def clear_events(self):

        with self.lock:
            self.events.clear()

    # --------------------------------------------------------
    # DEDUPLICATION CACHE
    # --------------------------------------------------------

    def clear_deduplication_cache(self):

        with self.lock:
            self.recent_events.clear()


event_manager = EventManager()