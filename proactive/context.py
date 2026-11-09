"""
Project FRIDAY
Proactive Context

Provides lightweight environmental context
for proactive decision making.
"""

from datetime import datetime


class ProactiveContext:

    def __init__(self):
        self.enabled = True

    def get_context(self, event=None):
        """
        Build the current context used by
        FRIDAY's proactive intelligence.
        """

        now = datetime.now()

        context = {
            "hour": now.hour,
            "minute": now.minute,
            "time": now.strftime("%H:%M"),
            "is_night": self._is_night(now.hour),
            "is_quiet_hours": self._is_quiet_hours(now.hour),
            "event_priority": (
                event.priority
                if event is not None
                else 0
            ),
        }

        # Read optional environment information
        # supplied by the event itself.

        if event is not None:
            data = event.data or {}

            if "battery" in data:
                context["battery"] = data["battery"]

            if "charging" in data:
                context["charging"] = data["charging"]

        return context

    @staticmethod
    def _is_night(hour):
        """
        Night period:
        00:00 - 06:59
        22:00 - 23:59
        """

        return hour >= 22 or hour < 7

    @staticmethod
    def _is_quiet_hours(hour):
        """
        Quiet hours:
        23:00 - 06:59
        """

        return hour >= 23 or hour < 7


proactive_context = ProactiveContext()