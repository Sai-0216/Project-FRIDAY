"""
Project FRIDAY
Intent Continuity
Phase 35.5
"""


class IntentContinuity:
    """Determines whether a new command continues the previous intent."""

    def __init__(self):
        self.clear()

    def clear(self):
        self.previous_intent = None
        self.previous_parameters = {}
        self.previous_topic = None

    def update(
        self,
        intent,
        parameters=None,
        topic=None,
    ):
        self.previous_intent = intent
        self.previous_parameters = dict(parameters or {})
        self.previous_topic = topic

    def is_continuation(
        self,
        command,
        dialogue_context,
    ):
        if not self.previous_intent:
            return False

        if not dialogue_context:
            return False

        return dialogue_context.is_continuation(
            command
        )

    def resolve(
        self,
        command,
        current_intent,
        current_parameters=None,
        dialogue_context=None,
    ):
        parameters = dict(current_parameters or {})

        if not self.is_continuation(
            command,
            dialogue_context,
        ):
            return {
                "intent": current_intent,
                "parameters": parameters,
                "continued": False,
                "previous_intent": self.previous_intent,
            }

        has_current_intent = (
            current_intent
            and current_intent != "unknown"
        )

        effective_intent = (
            current_intent
            if has_current_intent
            else self.previous_intent
        )

        if not parameters:
            parameters = dict(
                self.previous_parameters
            )

        return {
            "intent": effective_intent,
            "parameters": parameters,
            "continued": True,
            "previous_intent": self.previous_intent,
        }
    def snapshot(self):
        return {
            "previous_intent": self.previous_intent,
            "previous_parameters": dict(
                self.previous_parameters
            ),
            "previous_topic": self.previous_topic,
        }


intent_continuity = IntentContinuity()
