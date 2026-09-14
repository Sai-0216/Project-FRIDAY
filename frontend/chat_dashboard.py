"""
Project FRIDAY
Frontend Chat Dashboard
"""

from conversation import conversation


def build_chat_dashboard():
    messages = conversation.get_messages()

    if not isinstance(messages, list):
        return []

    return list(messages)


def chat_message_count():
    return len(build_chat_dashboard())


def get_last_user_message():
    messages = build_chat_dashboard()

    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")

    return None


def get_last_assistant_message():
    messages = build_chat_dashboard()

    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content", "")

    return None


def format_chat_dashboard():
    messages = build_chat_dashboard()

    if not messages:
        return "Chat is empty."

    lines = []

    for message in messages:
        role = message.get("role", "unknown")
        content = message.get("content", "")

        lines.append("{}: {}".format(role, content))

    return chr(10).join(lines)
