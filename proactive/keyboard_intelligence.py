"""FRIDAY V3 - Phase 24.5 Keyboard Intelligence."""


class KeyboardIntelligence:

    ACTIONS = {
        "type": "type_text",
        "press": "press_key",
        "hotkey": "press_hotkey",
    }

    @classmethod
    def create_action(cls, action, value=""):
        action = str(action).lower()
        command = cls.ACTIONS.get(action)

        return {
            "action": action,
            "command": command,
            "value": value if isinstance(value, str) else str(value),
            "valid": command is not None,
        }

    @classmethod
    def type_text(cls, text):
        return cls.create_action("type", text)

    @classmethod
    def press_key(cls, key):
        return cls.create_action("press", key)

    @classmethod
    def hotkey(cls, *keys):
        if not keys:
            return cls.create_action("hotkey", "")
        return cls.create_action("hotkey", "+".join(str(key) for key in keys))

    @classmethod
    def validate_action(cls, action):
        if not isinstance(action, dict):
            return False
        if not isinstance(action.get("action"), str):
            return False
        if not isinstance(action.get("command"), (str, type(None))):
            return False
        if not isinstance(action.get("value"), str):
            return False
        if not isinstance(action.get("valid"), bool):
            return False
        return True

    @classmethod
    def available_actions(cls):
        return list(cls.ACTIONS.keys())


keyboard_intelligence = KeyboardIntelligence()
