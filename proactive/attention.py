"""
Project FRIDAY
Phase 16.17-G

Attention Calibration

Combines urgency and relevance into a calibrated
attention level.

Attention levels:

    0 = NONE
    1 = LOW
    2 = NORMAL
    3 = HIGH
    4 = CRITICAL

Design principle:

    High urgency + low relevance
        != automatically critical attention.

    Critical attention requires strong evidence
    from both urgency and relevance, except for
    explicitly critical situations.
"""


class AttentionAnalyzer:

    NONE = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

    def analyze(self, context=None):

        context = context or {}

        urgency = context.get(
            "urgency",
            {}
        )

        relevance = context.get(
            "relevance",
            {}
        )

        urgency_score = urgency.get(
            "score",
            0
        )

        relevance_score = relevance.get(
            "score",
            0
        )

        urgency_level = urgency.get(
            "level",
            "NONE"
        )

        relevance_level = relevance.get(
            "level",
            "IRRELEVANT"
        )

        relevant = relevance.get(
            "relevant",
            False
        )

        # --------------------------------------------------
        # NO ATTENTION
        # --------------------------------------------------

        if (
            urgency_score == 0
            and relevance_score == 0
        ):
            return {
                "score": self.NONE,
                "level": "NONE",
                "reason": (
                    "Event has no meaningful "
                    "urgency or relevance."
                ),
            }

        # --------------------------------------------------
        # CRITICAL
        #
        # Both signals must be critical.
        # --------------------------------------------------

        if (
            urgency_score >= 4
            and relevance_score >= 4
        ):
            return {
                "score": self.CRITICAL,
                "level": "CRITICAL",
                "reason": (
                    "Event is critically urgent "
                    "and critically relevant."
                ),
            }

        # --------------------------------------------------
        # HIGH
        #
        # Strong urgency + strong relevance
        # OR critical urgency + high relevance.
        # --------------------------------------------------

        if (
            urgency_score >= 3
            and relevance_score >= 3
        ):
            return {
                "score": self.HIGH,
                "level": "HIGH",
                "reason": (
                    "Event has high urgency "
                    "and high relevance."
                ),
            }

        if (
            urgency_score >= 4
            and relevance_score >= 2
        ):
            return {
                "score": self.HIGH,
                "level": "HIGH",
                "reason": (
                    "Event is critically urgent "
                    "and sufficiently relevant."
                ),
            }

        if (
            urgency_score >= 2
            and relevance_score >= 4
        ):
            return {
                "score": self.HIGH,
                "level": "HIGH",
                "reason": (
                    "Event has strong relevance "
                    "and meaningful urgency."
                ),
            }

        # --------------------------------------------------
        # NORMAL
        # --------------------------------------------------

        if (
            urgency_score >= 2
            and relevance_score >= 2
        ):
            return {
                "score": self.NORMAL,
                "level": "NORMAL",
                "reason": (
                    "Event has meaningful urgency "
                    "and relevance."
                ),
            }

        if (
            relevant
            and relevance_score >= 2
        ):
            return {
                "score": self.NORMAL,
                "level": "NORMAL",
                "reason": (
                    "Event is relevant to the "
                    "current situation."
                ),
            }

        if (
            urgency_score >= 2
            and relevance_score >= 1
        ):
            return {
                "score": self.NORMAL,
                "level": "NORMAL",
                "reason": (
                    "Event has meaningful urgency "
                    "despite limited relevance."
                ),
            }

        # --------------------------------------------------
        # LOW
        # --------------------------------------------------

        if (
            urgency_score >= 1
            or relevance_score >= 1
        ):
            return {
                "score": self.LOW,
                "level": "LOW",
                "reason": (
                    "Event has limited urgency "
                    "or relevance."
                ),
            }

        # --------------------------------------------------
        # FALLBACK
        # --------------------------------------------------

        return {
            "score": self.NONE,
            "level": "NONE",
            "reason": (
                "Event has no meaningful "
                "attention requirement."
            ),
        }


attention_analyzer = AttentionAnalyzer()