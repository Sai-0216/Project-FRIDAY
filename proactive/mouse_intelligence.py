"""FRIDAY V3 - Phase 24.4 Mouse Intelligence."""


class MouseIntelligence:

    ACTIONS = {
        "move": "move_cursor",
        "click": "left_click",
        "double_click": "double_click",
        "right_click": "right_click",
    }

    @classmethod
    def create_action(cls, action, x=0, y=0):
        action = str(action).lower()
        normalized = cls.ACTIONS.get(action)

        return {
            "action": action,
            "command": normalized,
            "x": int(x) if isinstance(x, (int, float)) else 0,
            "y": int(y) if isinstance(y, (int, float)) else 0,
            "valid": normalized is not None,
        }

    @classmethod
    def plan_click(cls, element):
        if not isinstance(element, dict):
            return cls.create_action("invalid")

        return cls.create_action(
            "click",
            element.get("x", 0),
            element.get("y", 0),
        )

    @classmethod
    def validate_action(cls, action):
        if not isinstance(action, dict):
            return False
        if not isinstance(action.get("action"), str):
            return False
        if not isinstance(action.get("command"), (str, type(None))):
            return False
        if not isinstance(action.get("x"), int):
            return False
        if not isinstance(action.get("y"), int):
            return False
        if not isinstance(action.get("valid"), bool):
            return False
        return True

    @classmethod
    def available_actions(cls):
        return list(cls.ACTIONS.keys())


mouse_intelligence = MouseIntelligence()
