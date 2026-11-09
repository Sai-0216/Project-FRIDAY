"""
Project FRIDAY
Background Reminder Worker

Compatibility wrapper for the Phase 16
Proactive Reminder System.

Reminder triggering is now handled by:

ReminderSource
    ↓
EventManager
    ↓
ProactiveEngine
    ↓
NotificationManager
"""

from proactive.proactive_system import proactive_system


class ReminderWorker:

    def __init__(self):

        self.running = False

    # ========================================
    # START
    # ========================================

    def start(self):

        if self.running:
            return

        self.running = True

        print(
            "[REMINDER] Reminder worker redirected "
            "to proactive system."
        )

    # ========================================
    # STOP
    # ========================================

    def stop(self):

        if not self.running:
            return

        self.running = False

        print(
            "[REMINDER] Reminder worker stopped."
        )


reminder_worker = ReminderWorker()