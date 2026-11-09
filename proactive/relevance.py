"""
Project FRIDAY
Phase 16.17-A

Proactive Relevance Analyzer

Determines whether an event is relevant to FRIDAY's
current situation.

Relevance levels:

    0 = IRRELEVANT
    1 = LOW
    2 = RELEVANT
    3 = HIGH
    4 = CRITICAL
"""


class RelevanceAnalyzer:

    IRRELEVANT = 0
    LOW = 1
    RELEVANT = 2
    HIGH = 3
    CRITICAL = 4

    def analyze(self, event, context=None):

        if event is None:
            return {
                "score": self.IRRELEVANT,
                "level": "IRRELEVANT",
                "relevant": False,
                "reason": "No event provided.",
            }

        context = context or {}

        event_type = event.event_type
        data = event.data or {}

        is_quiet_hours = context.get(
            "is_quiet_hours",
            False
        )

        # ----------------------------------------------------
        # BATTERY
        # ----------------------------------------------------

        if event_type == "BATTERY_LOW":

            battery = data.get("battery")
            charging = data.get(
                "charging",
                False
            )

            if charging:
                return {
                    "score": self.IRRELEVANT,
                    "level": "IRRELEVANT",
                    "relevant": False,
                    "reason": (
                        "Battery is low but the "
                        "device is charging."
                    ),
                }

            if battery is not None:

                if battery <= 10:
                    return {
                        "score": self.CRITICAL,
                        "level": "CRITICAL",
                        "relevant": True,
                        "reason": (
                            "Critical battery condition "
                            "requires attention."
                        ),
                    }

                if battery <= 20:
                    return {
                        "score": self.HIGH,
                        "level": "HIGH",
                        "relevant": True,
                        "reason": (
                            "Low battery may require "
                            "user attention."
                        ),
                    }

            return {
                "score": self.RELEVANT,
                "level": "RELEVANT",
                "relevant": True,
                "reason": (
                    "Battery condition may require "
                    "attention."
                ),
            }
            
        # ----------------------------------------------------
        # ENVIRONMENT
        # ----------------------------------------------------

        if event_type == "ENVIRONMENT_CRITICAL":

            return {
                "score": self.CRITICAL,
                "level": "CRITICAL",
                "relevant": True,
                "reason": (
                    "Critical system/environment "
                    "condition requires attention."
                ),
            }

        if event_type == "ENVIRONMENT_WARNING":

            return {
                "score": self.HIGH,
                "level": "HIGH",
                "relevant": True,
                "reason": (
                    "Elevated system/environment "
                    "condition is relevant."
                ),
            }
            
        # ----------------------------------------------------
        # REMINDERS
        # ----------------------------------------------------

        if event_type == "REMINDER_EVENT":

            if is_quiet_hours:
                return {
                    "score": self.LOW,
                    "level": "LOW",
                    "relevant": False,
                    "reason": (
                        "Reminder occurred during "
                        "quiet hours."
                    ),
                }

            return {
                "score": self.RELEVANT,
                "level": "RELEVANT",
                "relevant": True,
                "reason": (
                    "A scheduled reminder is due."
                ),
            }

        # ----------------------------------------------------
        # TIME EVENTS
        # ----------------------------------------------------

        if event_type == "TIME_EVENT":

            priority = event.priority

            if priority >= 5:
                return {
                    "score": self.CRITICAL,
                    "level": "CRITICAL",
                    "relevant": True,
                    "reason": (
                        "High-priority scheduled event "
                        "requires attention."
                    ),
                }

            if priority >= 3:
                return {
                    "score": self.HIGH,
                    "level": "HIGH",
                    "relevant": True,
                    "reason": (
                        "Important scheduled event "
                        "is relevant."
                    ),
                }

            if is_quiet_hours:
                return {
                    "score": self.LOW,
                    "level": "LOW",
                    "relevant": False,
                    "reason": (
                        "Low-priority event occurred "
                        "during quiet hours."
                    ),
                }

            if priority >= 2:
                return {
                    "score": self.RELEVANT,
                    "level": "RELEVANT",
                    "relevant": True,
                    "reason": (
                        "Normal scheduled event "
                        "is relevant."
                    ),
                }

            return {
                "score": self.LOW,
                "level": "LOW",
                "relevant": False,
                "reason": (
                    "Low-priority scheduled event "
                    "has limited relevance."
                ),
            }

        # ----------------------------------------------------
        # UNKNOWN EVENT
        # ----------------------------------------------------

        return {
            "score": self.LOW,
            "level": "LOW",
            "relevant": False,
            "reason": (
                "Unknown event type has no established "
                "proactive relevance."
            ),
        }


relevance_analyzer = RelevanceAnalyzer()