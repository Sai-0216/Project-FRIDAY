"""
Project FRIDAY
Context Fusion
Phase 35.7
"""


class ContextFusion:
    """Combines existing conversation context sources into one snapshot."""

    def __init__(
        self,
        conversation_state=None,
        dialogue_context=None,
        intent_continuity=None,
        conversational_memory=None,
        conversation_context=None,
    ):
        self.conversation_state = conversation_state
        self.dialogue_context = dialogue_context
        self.intent_continuity = intent_continuity
        self.conversational_memory = conversational_memory
        self.conversation_context = conversation_context

    def _reference_snapshot(self, command=None):
        if not self.conversation_context or not command:
            return {
                "detected": False,
                "type": None,
                "target": None,
            }

        try:
            detected = (
                self.conversation_context.has_reference(
                    command
                )
                or self.conversation_context.is_previous_reference(
                    command
                )
            )

            if not detected:
                return {
                    "detected": False,
                    "type": None,
                    "target": None,
                }

            reference_type = (
                "previous_topic"
                if self.conversation_context.is_previous_reference(
                    command
                )
                else "current_topic"
            )

            target = (
                self.conversation_context.get_reference_target(
                    command
                )
            )

            return {
                "detected": True,
                "type": reference_type,
                "target": target,
            }

        except Exception as error:
            print(
                "[CONTEXT] Reference fusion failed:",
                repr(error),
            )

            return {
                "detected": False,
                "type": None,
                "target": None,
            }

    def build(self, command=None):
        state = (
            self.conversation_state.snapshot()
            if self.conversation_state
            else {}
        )

        dialogue = (
            self.dialogue_context.snapshot()
            if self.dialogue_context
            else {}
        )

        continuity = (
            self.intent_continuity.snapshot()
            if self.intent_continuity
            else {}
        )

        memory = (
            self.conversational_memory.recent()
            if self.conversational_memory
            else []
        )

        topic = (
            self.conversation_context.get_topic()
            if self.conversation_context
            else None
        )

        previous_topic = (
            self.conversation_context.get_previous_topic()
            if self.conversation_context
            else None
        )

        return {
            "turn": {
                "count": state.get("turn_count"),
                "status": state.get("status"),
                "user_message": state.get(
                    "last_user_message"
                ),
                "assistant_message": state.get(
                    "last_assistant_message"
                ),
            },
            "topic": {
                "current": (
                    state.get("active_topic")
                    or dialogue.get("current_topic")
                    or topic
                ),
                "previous": (
                    state.get("previous_topic")
                    or dialogue.get("previous_topic")
                    or previous_topic
                ),
                "confidence": dialogue.get(
                    "topic_confidence"
                ),
                "source": dialogue.get(
                    "topic_source"
                ),
            },
            "intent": {
                "current": state.get(
                    "last_intent"
                ),
                "parameters": dict(
                    state.get("last_parameters") or {}
                ),
                "previous": continuity.get(
                    "previous_intent"
                ),
                "previous_parameters": dict(
                    continuity.get(
                        "previous_parameters"
                    ) or {}
                ),
            },
            "slots": {
                "pending": bool(
                    (
                        state.get("pending_slots")
                        or {}
                    ).get("active")
                ),
                "intent": (
                    (
                        state.get("pending_slots")
                        or {}
                    ).get("intent")
                ),
                "parameters": dict(
                    (
                        state.get("pending_slots")
                        or {}
                    ).get("parameters")
                    or {}
                ),
                "missing": list(
                    (
                        state.get("pending_slots")
                        or {}
                    ).get("missing")
                    or []
                ),
            },
            "command": {
                "resolved": state.get(
                    "last_resolved_command"
                ),
            },
            "references": {
                "current_topic": topic,
                "previous_topic": previous_topic,
            },
            "reference": self._reference_snapshot(
                command
            ),
            "recent_turns": [
                dict(turn)
                for turn in memory
            ],
        }

    def snapshot(self):
        return self.build()


context_fusion = ContextFusion()
