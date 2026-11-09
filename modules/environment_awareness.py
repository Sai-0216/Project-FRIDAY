"""
Project FRIDAY
Environment Awareness
Phase 18.3.1
"""

from modules.device_state import device_state
from proactive.environment_trends import environment_trends
from modules.environment import environment
from proactive.event import Event


class EnvironmentAwareness:

    # ========================================
    # AWARENESS POLICY
    # ========================================

    REPORT_STATUSES = {
        "WARNING",
        "CRITICAL",
    }

    # ========================================
    # STATE
    # ========================================

    def __init__(self):

        self.last_reported_signature = None

    # ========================================
    # CONDITION SIGNATURE
    # ========================================

    def _condition_signature(
        self,
        analysis
    ):
        """
        Build a stable signature for the current
        environmental condition.

        Numeric fluctuations such as RAM moving
        from 92.0% to 92.5% do not create a new
        condition.
        """

        status = analysis.get(
            "status",
            "NORMAL"
        )

        reasons = analysis.get(
            "reasons",
            []
        )

        normalized_reasons = []

        for reason in reasons:

            reason = str(
                reason
            )

            # Remove live numeric values such as:
            # RAM usage is high (92.5%).
            normalized = reason.split(
                " (",
                1
            )[0].strip()

            normalized_reasons.append(
                normalized
            )

        return (
            status,
            tuple(
                sorted(
                    normalized_reasons
                )
            )
        )

    # ========================================
    # ANALYZE
    # ========================================

    def analyze(
        self,
        state=None
    ):
        """
        Analyze a device state and determine
        whether a new environmental condition
        deserves attention.
        """

        if state is None:

            state = device_state.snapshot()

        details = environment.status_details(
            state
        )

        status = details.get(
            "status",
            "NORMAL"
        )

        reasons = details.get(
            "reasons",
            []
        )

        should_report = (
            status in self.REPORT_STATUSES
        )

        history = []
        try:
            from proactive.environment_memory import environment_memory
            history = environment_memory.history()
        except Exception:
            history = []

        trends = environment_trends.analyze(history)

        try:
            from proactive.environment_memory_insight import environment_memory_insight
            memory_insight = environment_memory_insight.interpret(history=history)
        except Exception:
            memory_insight = {
                "samples": len(history),
                "has_history": bool(history),
                "status": "UNAVAILABLE",
                "notable_trends": [],
            }

        analysis = {
            "status": status,
            "should_report": should_report,
            "reasons": reasons,
            "trends": trends,
            "memory_insight": memory_insight,
        }

        # ----------------------------------------
        # DUPLICATE CONDITION
        # ----------------------------------------

        if should_report:

            signature = (
                self._condition_signature(
                    analysis
                )
            )

            if (
                signature
                == self.last_reported_signature
            ):

                analysis["should_report"] = False

            analysis["condition_changed"] = (
                signature
                != self.last_reported_signature
            )

        else:

            # ------------------------------------
            # NORMAL STATE
            #
            # Clear the previous reported
            # condition so a future warning
            # can be reported again.
            # ------------------------------------

            self.last_reported_signature = None

            analysis["condition_changed"] = False

        return analysis

    # ========================================
    # MARK REPORTED
    # ========================================

    def mark_reported(
        self,
        analysis
    ):
        """
        Mark the current condition as reported.
        """

        if not analysis:

            return

        if not analysis.get(
            "should_report"
        ):

            return

        signature = (
            self._condition_signature(
                analysis
            )
        )

        self.last_reported_signature = (
            signature
        )
    
    # ========================================
    # CREATE PROACTIVE EVENT
    # ========================================

    def create_event(
        self,
        state=None
    ):
        """
        Create a proactive environment event only
        when a new warning or critical condition
        is detected.

        The event contains structured environmental,
        correlation, and workload context.
        """

        if state is None:

            state = device_state.snapshot()

        analysis = self.analyze(
            state
        )

        if not analysis.get(
            "should_report"
        ):

            return None

        status = analysis.get(
            "status",
            "WARNING"
        )

        # ----------------------------------------
        # Structured correlations
        # ----------------------------------------

        correlations = (
            environment.correlations(
                state
            )
        )

        # ----------------------------------------
        # Workload context
        # ----------------------------------------

        workload = (
            environment.workload_context(
                state
            )
        )

        # ----------------------------------------
        # Event type
        # ----------------------------------------

        if status == "CRITICAL":

            event_type = (
                "ENVIRONMENT_CRITICAL"
            )

        else:

            event_type = (
                "ENVIRONMENT_WARNING"
            )

        # ----------------------------------------
        # Event priority
        # ----------------------------------------

        has_critical_correlation = any(
            finding.get("severity")
            == "CRITICAL"
            for finding in correlations
        )

        if (
            status == "CRITICAL"
            or has_critical_correlation
        ):

            priority = 4

        else:

            priority = 2

        # ----------------------------------------
        # Create event
        # ----------------------------------------

        event = Event(
            event_type=event_type,
            source="environment_awareness",
            data={
                "status": status,

                "reasons": analysis.get(
                    "reasons",
                    []
                ),

                "trends": analysis.get(
                    "trends",
                    {}
                ),

                "memory_insight": analysis.get(
                    "memory_insight",
                    {}
                ),

                "correlations": correlations,

                "workload_context": workload,

                "state": state,
            },

            priority=priority
        )

        # ----------------------------------------
        # Mark condition as reported
        # ----------------------------------------

        self.mark_reported(
            analysis
        )

        return event
    # ========================================
    # MESSAGE
    # ========================================

    def message(
        self,
        state=None
    ):
        """
        Return a message only for a new
        environmental condition.
        """

        if state is None:

            state = device_state.snapshot()

        analysis = self.analyze(
            state
        )

        if not analysis[
            "should_report"
        ]:

            return None

        status = analysis[
            "status"
        ]

        reasons = analysis[
            "reasons"
        ]

        if status == "CRITICAL":

            prefix = (
                "Sir, I detected a critical "
                "system condition."
            )

        else:

            prefix = (
                "Sir, I noticed something that "
                "may need your attention."
            )

        if reasons:

            message = (
                prefix
                + " "
                + " ".join(
                    reasons
                )
            )

        else:

            message = prefix

        # ----------------------------------------
        # Remember that FRIDAY reported it
        # ----------------------------------------

        self.mark_reported(
            analysis
        )

        return message


# ========================================
# ENVIRONMENT AWARENESS INSTANCE
# ========================================

environment_awareness = (
    EnvironmentAwareness()
)