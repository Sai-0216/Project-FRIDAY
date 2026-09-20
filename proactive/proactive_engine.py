"""
Project FRIDAY
Phase 16.18-B

Proactive Intelligence Engine

Receives events, gathers current context,
analyzes urgency, calculates event age,
applies urgency decay when appropriate,
analyzes relevance,
calculates combined attention,
and sends the complete reasoning context
to the DecisionPolicy.

The engine does NOT execute actions.

Phase 16.18-B:
    - Attach event metadata to decisions so
      proactive outcomes can be tracked later.
"""

from .event import Event
from .context import proactive_context
from .urgency import urgency_analyzer
from .urgency_decay import urgency_decay
from .relevance import relevance_analyzer
from .attention import attention_analyzer
from .decision_policy import decision_policy
from .event_intelligence import event_intelligence


class ProactiveEngine:

    def __init__(self):
        self.enabled = True

    def process_event(
        self,
        event
    ):

        if not isinstance(
            event,
            Event
        ):

            raise TypeError(
                "event must be an Event object"
            )

        if not self.enabled:

            return None

        print(
            f"[ProactiveEngine] "
            f"Processing event: {event}"
        )

        # =====================================================
        # CONTEXT
        # =====================================================

        context = proactive_context.get_context(
            event
        )

        # =====================================================
        # EVENT INTELLIGENCE
        # =====================================================

        event_intelligence_context = (
            event_intelligence.proactive_analysis(
                event
            )
        )

        context["event_intelligence"] = (
            event_intelligence_context
        )

        if event.event_type in (
            "ENVIRONMENT_WARNING",
            "ENVIRONMENT_CRITICAL",
        ):
            event_memory = (event.data or {}).get(
                "memory_insight"
            )

            if isinstance(event_memory, dict):
                context["environment_memory"] = event_memory
            else:
                try:
                    from proactive.environment_memory_insight import environment_memory_insight
                    context["environment_memory"] = (
                        environment_memory_insight.interpret()
                    )
                except Exception:
                    context["environment_memory"] = {
                        "samples": 0,
                        "has_history": False,
                        "status": "UNAVAILABLE",
                        "notable_trends": [],
                    }

        print(
            f"[ProactiveEngine] "
            f"Context: {context}"
        )

        # =====================================================
        # URGENCY
        # =====================================================

        urgency = urgency_analyzer.analyze(
            event
        )

        print(
            "[ProactiveEngine] "
            f"Initial urgency: {urgency}"
        )

        # Battery urgency should not decay because
        # battery conditions remain important even
        # when the event has existed for some time.

        decay_allowed = (
            event.event_type
            not in (
                "BATTERY_LOW",
            )
        )

        effective_urgency = urgency_decay.decay_event(
            event,
            urgency,
            decay_allowed=decay_allowed
        )

        print(
            "[ProactiveEngine] "
            f"Effective urgency: {effective_urgency}"
        )

        context["urgency"] = (
            effective_urgency
        )

        context["urgency_age"] = {
            "age_seconds": effective_urgency.get(
                "age_seconds",
                0
            ),
            "decay_applied": effective_urgency.get(
                "decay_applied",
                False
            ),
        }

        # =====================================================
        # RELEVANCE
        # =====================================================

        relevance = relevance_analyzer.analyze(
            event,
            context
        )

        print(
            "[ProactiveEngine] "
            f"Relevance: {relevance}"
        )

        context["relevance"] = relevance

        # =====================================================
        # ATTENTION
        # =====================================================

        attention = attention_analyzer.analyze(
            context
        )

        print(
            "[ProactiveEngine] "
            f"Attention: {attention}"
        )

        context["attention"] = attention

        # =====================================================
        # DECISION
        # =====================================================

        decision = decision_policy.decide(
            event,
            context
        )

        # -----------------------------------------------------
        # ATTACH EVENT METADATA
        #
        # The decision will eventually travel through
        # NotificationManager -> Brain.
        #
        # Keeping event_type on the decision allows
        # OutcomeMemory to know which event produced
        # the confirmation.
        # -----------------------------------------------------

        if decision is not None:

            decision["event_type"] = (
                event.event_type
            )

        if decision is None:

            print(
                "[ProactiveEngine] "
                "No decision generated."
            )

            return None

        # =====================================================
        # ATTACH COMPLETE CONTEXT
        # =====================================================

        decision["context"] = context

        print(
            "[ProactiveEngine] "
            f"Decision: {decision}"
        )

        return decision


proactive_engine = ProactiveEngine()