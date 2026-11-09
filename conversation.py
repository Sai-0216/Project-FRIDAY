"""
Project FRIDAY
Conversation Memory
"""

from collections import deque


class Conversation:

    def __init__(self, max_messages=4):

        self.messages = deque(
            maxlen=max_messages
        )

    # ----------------------------------------
    # Add user message
    # ----------------------------------------

    def add_user(self, message):

        self.messages.append({
            "role": "user",
            "content": message
        })

    # ----------------------------------------
    # Add FRIDAY response
    # ----------------------------------------

    def add_assistant(self, message):

        self.messages.append({
            "role": "assistant",
            "content": message
        })

    # ----------------------------------------
    # Get conversation
    # ----------------------------------------

    def get_messages(self):

        return list(
            self.messages
        )

    # ----------------------------------------
    # Get last user message
    # ----------------------------------------

    def get_last_user_message(self):

        for message in reversed(
            self.messages
        ):

            if message.get("role") == "user":

                return message.get(
                    "content",
                    ""
                )

        return None

    # ----------------------------------------
    # Get last assistant message
    # ----------------------------------------

    def get_last_assistant_message(self):

        for message in reversed(
            self.messages
        ):

            if message.get("role") == "assistant":

                return message.get(
                    "content",
                    ""
                )

        return None

    # ----------------------------------------
    # Clear conversation
    # ----------------------------------------

    def clear(self):

        self.messages.clear()


# ========================================
# GLOBAL CONVERSATION INSTANCE
# ========================================

conversation = Conversation(
    max_messages=4
)