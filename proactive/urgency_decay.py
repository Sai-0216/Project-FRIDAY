"""
Project FRIDAY
Phase 16.16-E

Automatic Event Age Calculation

Calculates how old an Event is using its
created_at timestamp and applies urgency decay.

Important:
    Physical-state events such as BATTERY_LOW
    should not automatically decay.
"""

from datetime import datetime

from .event import Event


class UrgencyDecay:

    # --------------------------------------------------------
    # DEFAULT DECAY THRESHOLDS
    # --------------------------------------------------------

    def __init__(
        self,
        high_after=300,
        normal_after=900,
        low_after=1800
    ):
        """
        Time thresholds are measured in seconds.

        Default:

            0 - 5 minutes       → original urgency
            5 - 15 minutes      → HIGH at most
            15 - 30 minutes     → NORMAL at most
            30+ minutes         → LOW at most
        """

        self.high_after = high_after
        self.normal_after = normal_after
        self.low_after = low_after

    # ========================================================
    # EVENT AGE
    # ========================================================

    def get_age_seconds(self, event):

        if not isinstance(event, Event):
            raise TypeError(
                "event must be an Event object"
            )

        now = datetime.now()

        age_seconds = (
            now - event.created_at
        ).total_seconds()

        # Clock changes should never produce
        # a negative event age.

        if age_seconds < 0:
            age_seconds = 0

        return age_seconds

    # ========================================================
    # DECAY SCORE
    # ========================================================

    def decay_score(
        self,
        score,
        age_seconds
    ):
        """
        Return an urgency score adjusted for age.

        The score can only decrease.
        """

        if score <= 0:
            return 0

        if age_seconds < 0:
            age_seconds = 0

        if age_seconds >= self.low_after:
            return min(
                score,
                1
            )

        if age_seconds >= self.normal_after:
            return min(
                score,
                2
            )

        if age_seconds >= self.high_after:
            return min(
                score,
                3
            )

        return score

    # ========================================================
    # DECAY URGENCY
    # ========================================================

    def decay(
        self,
        urgency,
        age_seconds
    ):
        """
        Apply urgency decay using a supplied age.
        """

        if not urgency:

            return {
                "score": 0,
                "level": "NONE",
                "reason": "No urgency provided.",
            }

        original_score = urgency.get(
            "score",
            0
        )

        new_score = self.decay_score(
            original_score,
            age_seconds
        )

        return {
            "score": new_score,
            "level": self._score_to_level(
                new_score
            ),
            "reason": urgency.get(
                "reason",
                "Urgency adjusted for event age."
            ),
            "original_score": original_score,
            "age_seconds": age_seconds,
        }

    # ========================================================
    # EVENT-BASED DECAY
    # ========================================================

    def decay_event(
        self,
        event,
        urgency,
        decay_allowed=True
    ):
        """
        Calculate the real age of an event and apply
        urgency decay when allowed.

        decay_allowed=False is intended for physical-state
        events such as BATTERY_LOW.
        """

        if not isinstance(event, Event):
            raise TypeError(
                "event must be an Event object"
            )

        if not decay_allowed:

            return {
                "score": urgency.get(
                    "score",
                    0
                ),
                "level": urgency.get(
                    "level",
                    "NONE"
                ),
                "reason": urgency.get(
                    "reason",
                    "Urgency preserved."
                ),
                "original_score": urgency.get(
                    "score",
                    0
                ),
                "age_seconds": self.get_age_seconds(
                    event
                ),
                "decay_applied": False,
            }

        age_seconds = self.get_age_seconds(
            event
        )

        result = self.decay(
            urgency,
            age_seconds
        )

        result["decay_applied"] = True

        return result

    # ========================================================
    # SCORE → LEVEL
    # ========================================================

    @staticmethod
    def _score_to_level(score):

        if score >= 4:
            return "CRITICAL"

        if score == 3:
            return "HIGH"

        if score == 2:
            return "NORMAL"

        if score == 1:
            return "LOW"

        return "NONE"


urgency_decay = UrgencyDecay()