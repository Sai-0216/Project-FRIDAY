"""
Project FRIDAY
Proactive Reminder Event Source

Converts due reminders into proactive events.

This module does NOT speak or execute actions.
It only detects due reminders and emits events.
"""

import threading
import time

from modules.reminders import reminders

from .event import Event


class ReminderSource:

    def __init__(self, event_manager):

        self.event_manager = event_manager

        self.running = False
        self.thread = None

    # ========================================
    # START
    # ========================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            name="FRIDAY-Proactive-Reminder-Source",
            daemon=True
        )

        self.thread.start()

        print(
            "[REMINDER SOURCE] "
            "Reminder event source started."
        )

    # ========================================
    # WORKER LOOP
    # ========================================

    def _run(self):

        while self.running:

            try:

                due_reminders = (
                    reminders.get_due()
                )

                for reminder in due_reminders:

                    text = reminder.get(
                        "text",
                        "your reminder"
                    )

                    event = Event(
                        event_type="REMINDER_EVENT",
                        source="reminder",
                        data={
                            "message": (
                                f"Sir, reminder. "
                                f"It's time to {text}."
                            ),
                            "reminder": reminder
                        },
                        priority=2
                    )

                    print(
                        "[REMINDER SOURCE] "
                        f"Creating event: {event}"
                    )

                    self.event_manager.emit(
                        event
                    )

            except Exception as e:

                print(
                    "[REMINDER SOURCE] "
                    f"Worker error: {e}"
                )

            time.sleep(10)

    # ========================================
    # STOP
    # ========================================

    def stop(self):

        self.running = False

        print(
            "[REMINDER SOURCE] "
            "Reminder event source stopped."
        )