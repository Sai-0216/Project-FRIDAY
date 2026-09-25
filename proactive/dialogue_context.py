"""
Project FRIDAY
Dialogue Context
Phase 35.2
"""

from conversation import conversation


class DialogueContext:
    """Tracks the subject currently being discussed."""

    def __init__(self):
        self.clear()

    def clear(self):
        self.current_topic = None
        self.previous_topic = None
        self.topic_confidence = 0.0
        self.topic_source = None

    def update_topic(
        self,
        topic,
        confidence=1.0,
        source="explicit",
    ):
        if not topic:
            return self.current_topic

        topic = str(topic).strip()

        if not topic:
            return self.current_topic

        if topic == self.current_topic:
            self.topic_confidence = float(confidence)
            self.topic_source = source
            return self.current_topic

        self.previous_topic = self.current_topic
        self.current_topic = topic
        self.topic_confidence = float(confidence)
        self.topic_source = source

        return self.current_topic

    def get_topic(self):
        return self.current_topic

    def get_previous_topic(self):
        return self.previous_topic

    def is_continuation(self, message):
        if not self.current_topic:
            return False

        text = str(message).strip().lower()

        if not text:
            return False

        continuation_phrases = (
            "what about",
            "what are its",
            "what are the",
            "what is its",
            "what is the",
            "what next",
            "then what",
            "why",
            "how",
            "and then",
            "continue",
            "go on",
            "tell me more",
            "explain it",
            "explain that",
        )

        return (
            text in continuation_phrases
            or any(
                text.startswith(phrase + " ")
                for phrase in continuation_phrases
            )
        )

    def recent_user_messages(self):
        messages = conversation.get_messages()

        return [
            message.get("content", "")
            for message in messages
            if message.get("role") == "user"
        ]

    def snapshot(self):
        return {
            "current_topic": self.current_topic,
            "previous_topic": self.previous_topic,
            "topic_confidence": self.topic_confidence,
            "topic_source": self.topic_source,
            "recent_user_messages": self.recent_user_messages(),
        }


dialogue_context = DialogueContext()

