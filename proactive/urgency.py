"""
Project FRIDAY
Phase 16.16-A

Urgency Analyzer

Converts event information into an urgency score
and explains why the event has that urgency.

Urgency levels:

    0 = NONE
    1 = LOW
    2 = NORMAL
    3 = HIGH
    4 = CRITICAL
"""


class UrgencyAnalyzer:

    NONE = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

    def analyze(self, event):

        if event is None:
            return {
                "score": self.NONE,
                "level": "NONE",
                "reason": "No event provided.",
            }

        event_type = event.event_type
        data = event.data or {}

        # ----------------------------------------------------
        # BATTERY
        # ----------------------------------------------------

        if event_type == "BATTERY_LOW":

            battery = data.get("battery")
            charging = data.get("charging", False)

            if charging:
                return {
                    "score": self.NONE,
                    "level": "NONE",
                    "reason": "Device is charging.",
                }

            if battery is not None:

                if battery <= 10:
                    return {
                        "score": self.CRITICAL,
                        "level": "CRITICAL",
                        "reason": "Battery is critically low.",
                    }

                if battery <= 20:
                    return {
                        "score": self.HIGH,
                        "level": "HIGH",
                        "reason": "Battery is low.",
                    }

            return {
                "score": self.NORMAL,
                "level": "NORMAL",
                "reason": "Battery requires attention.",
            }
            
        # ----------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------

        if event_type == "ENVIRONMENT_CRITICAL":

            return {
                "score": self.CRITICAL,
                "level": "CRITICAL",
                "reason": (
                    "Critical system/environment "
                    "condition detected."
                ),
            }

        if event_type == "ENVIRONMENT_WARNING":

            return {
                "score": self.HIGH,
                "level": "HIGH",
                "reason": (
                    "Elevated system/environment "
                    "condition detected."
                ),
            }

        # ----------------------------------------------------
        # REMINDERS
        # ----------------------------------------------------

        if event_type == "REMINDER_EVENT":

            return {
                "score": self.NORMAL,
                "level": "NORMAL",
                "reason": "A scheduled reminder is due.",
            }

        # ----------------------------------------------------
        # TIME EVENTS
        # ----------------------------------------------------

        if event_type == "TIME_EVENT":

            if event.priority >= 5:
                return {
                    "score": self.CRITICAL,
                    "level": "CRITICAL",
                    "reason": "High-priority scheduled event.",
                }

            if event.priority >= 3:
                return {
                    "score": self.HIGH,
                    "level": "HIGH",
                    "reason": "Important scheduled event.",
                }

            if event.priority >= 2:
                return {
                    "score": self.NORMAL,
                    "level": "NORMAL",
                    "reason": "Normal scheduled event.",
                }

            return {
                "score": self.LOW,
                "level": "LOW",
                "reason": "Low-priority scheduled event.",
            }

        # ----------------------------------------------------
        # UNKNOWN EVENT
        # ----------------------------------------------------

        return {
            "score": self.LOW,
            "level": "LOW",
            "reason": "Unknown event type.",
        }


urgency_analyzer = UrgencyAnalyzer()