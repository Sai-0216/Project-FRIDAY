"""
Project FRIDAY
Proactive Scheduler

Responsible for generating time-based events.

The scheduler does NOT execute actions.
It only creates and emits events.
"""

import threading
import time
from datetime import datetime, timedelta

from .event import Event


class Scheduler:

    def __init__(self, event_manager):

        self.event_manager = event_manager

        self.running = False
        self.thread = None

        self.tasks = []
        self.lock = threading.Lock()

    # ========================================
    # START
    # ========================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            name="FRIDAY-Proactive-Scheduler",
            daemon=True
        )

        self.thread.start()

        print(
            "[SCHEDULER] "
            "Proactive scheduler started."
        )

    # ========================================
    # SCHEDULE EVENT
    # ========================================

    def schedule_event(
        self,
        event,
        run_at
    ):

        if not isinstance(event, Event):

            raise TypeError(
                "event must be an Event object"
            )

        if not isinstance(
            run_at,
            datetime
        ):

            raise TypeError(
                "run_at must be a datetime object"
            )

        task = {
            "event": event,
            "run_at": run_at,
            "triggered": False
        }

        with self.lock:

            self.tasks.append(
                task
            )

        print(
            "[SCHEDULER] "
            f"Event scheduled for {run_at}: "
            f"{event}"
        )

    # ========================================
    # SCHEDULE AFTER DELAY
    # ========================================

    def schedule_after(
        self,
        event,
        seconds
    ):

        run_at = (
            datetime.now()
            + timedelta(seconds=seconds)
        )

        self.schedule_event(
            event,
            run_at
        )

    # ========================================
    # WORKER LOOP
    # ========================================

    def _run(self):

        while self.running:

            now = datetime.now()

            with self.lock:

                for task in self.tasks:

                    if task["triggered"]:
                        continue

                    if now >= task["run_at"]:

                        task["triggered"] = True

                        self._emit_event(
                            task["event"]
                        )

            time.sleep(0.5)

    # ========================================
    # EMIT EVENT
    # ========================================

    def _emit_event(
        self,
        event
    ):

        print(
            "[SCHEDULER] "
            f"Triggering event: {event}"
        )

        self.event_manager.emit(
            event
        )

    # ========================================
    # STOP
    # ========================================

    def stop(self):

        self.running = False

        print(
            "[SCHEDULER] "
            "Proactive scheduler stopped."
        )


# ============================================
# HELPER
# ============================================

def create_time_event(
    message,
    priority=2
):

    return Event(
        event_type="TIME_EVENT",
        source="scheduler",
        data={
            "message": message
        },
        priority=priority
    )