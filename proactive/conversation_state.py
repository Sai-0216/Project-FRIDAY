"""
Project FRIDAY
Conversation State
Phase 35.1
"""

from datetime import datetime


class ConversationState:
    """Tracks the active state of the current conversation."""

    def __init__(self):
        self.clear()

    def clear(self):
        self.session_id = None
        self.status = "idle"
        self.turn_count = 0
        self.active_topic = None
        self.previous_topic = None
        self.last_user_message = None
        self.last_assistant_message = None
        self.last_intent = None
        self.last_parameters = {}
        self.last_resolved_command = None
        self.pending_slot_intent = None
        self.pending_slot_parameters = {}
        self.pending_slots = []
        self.updated_at = None
        self.error = None

    def _touch(self):
        self.updated_at = datetime.now().isoformat()

    def begin_turn(self, user_message, previous_user_message=None):
        self.status = "active"
        self.turn_count += 1
        self.last_user_message = user_message
        if previous_user_message is not None:
            self.last_user_message = user_message
        self.error = None
        self._touch()

    def update_topic(self, active_topic, previous_topic=None):
        self.previous_topic = (
            previous_topic
            if previous_topic is not None
            else self.active_topic
        )
        self.active_topic = active_topic
        self._touch()

    def update_intent(self, intent, parameters=None):
        self.last_intent = intent
        self.last_parameters = dict(parameters or {})
        self._touch()

    def update_resolved_command(self, command):
        self.last_resolved_command = command
        self._touch()

    def update_pending_slots(
        self,
        intent,
        parameters=None,
        missing_slots=None,
    ):
        self.pending_slot_intent = intent
        self.pending_slot_parameters = dict(
            parameters or {}
        )
        self.pending_slots = list(
            missing_slots or []
        )
        self._touch()

    def clear_pending_slots(self):
        self.pending_slot_intent = None
        self.pending_slot_parameters = {}
        self.pending_slots = []
        self._touch()

    def complete_turn(self, assistant_message=None):
        self.status = "completed"
        if assistant_message is not None:
            self.last_assistant_message = assistant_message
        self._touch()

    def fail(self, error):
        self.status = "error"
        self.error = str(error)
        self._touch()

    def snapshot(self):
        return {
            "session_id": self.session_id,
            "status": self.status,
            "turn_count": self.turn_count,
            "active_topic": self.active_topic,
            "previous_topic": self.previous_topic,
            "last_user_message": self.last_user_message,
            "last_assistant_message": self.last_assistant_message,
            "last_intent": self.last_intent,
            "last_parameters": dict(self.last_parameters),
            "last_resolved_command": self.last_resolved_command,
            "pending_slots": {
                "active": bool(
                    self.pending_slot_intent
                    and self.pending_slots
                ),
                "intent": self.pending_slot_intent,
                "parameters": dict(
                    self.pending_slot_parameters
                ),
                "missing": list(self.pending_slots),
            },
            "updated_at": self.updated_at,
            "error": self.error,
        }


conversation_state = ConversationState()
