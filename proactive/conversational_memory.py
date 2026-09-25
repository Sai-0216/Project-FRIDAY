"""
Project FRIDAY
Conversational Memory
Phase 35.4
"""

from datetime import datetime


class ConversationalMemory:
    """Stores structured memory for the active conversation."""

    def __init__(self, max_turns=12):
        self.max_turns = max_turns
        self.clear()

    def clear(self):
        self.turns = []

    def remember_turn(
        self,
        user_message,
        assistant_message=None,
        topic=None,
        intent=None,
        resolved_command=None,
    ):
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user_message": str(user_message).strip(),
            "assistant_message": (
                str(assistant_message).strip()
                if assistant_message is not None
                else None
            ),
            "topic": topic,
            "intent": intent,
            "resolved_command": resolved_command,
        }

        self.turns.append(turn)

        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

        return turn

    def recent(self, limit=5):
        if limit <= 0:
            return []

        return list(self.turns[-limit:])

    def latest(self):
        if not self.turns:
            return None

        return self.turns[-1]

    def find_by_topic(self, topic, limit=5):
        if not topic:
            return []

        normalized = str(topic).strip().lower()

        matches = [
            turn
            for turn in reversed(self.turns)
            if str(turn.get("topic") or "").strip().lower()
            == normalized
        ]

        return list(reversed(matches[-limit:]))

    def find_by_intent(self, intent, limit=5):
        if not intent:
            return []

        matches = [
            turn
            for turn in reversed(self.turns)
            if turn.get("intent") == intent
        ]

        return list(reversed(matches[-limit:]))

    def get_context(self, limit=5):
        return self.recent(limit)

    def snapshot(self):
        return {
            "max_turns": self.max_turns,
            "turn_count": len(self.turns),
            "turns": [dict(turn) for turn in self.turns],
        }


conversational_memory = ConversationalMemory()
