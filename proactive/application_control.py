"""FRIDAY V3 - Phase 24.6 Application Control."""


class ApplicationControl:

    ACTIONS = {
        "open": "launch_application",
        "close": "close_application",
        "focus": "focus_application",
        "switch": "switch_application",
    }

    @classmethod
    def create_action(cls, action, application):
        action = str(action).lower()
        command = cls.ACTIONS.get(action)
        application = application if isinstance(application, str) else str(application)

        return {
            "action": action,
            "command": command,
            "application": application,
            "valid": command is not None and bool(application.strip()),
        }

    @classmethod
    def open(cls, application):
        return cls.create_action("open", application)

    @classmethod
    def close(cls, application):
        return cls.create_action("close", application)

    @classmethod
    def focus(cls, application):
        return cls.create_action("focus", application)

    @classmethod
    def switch(cls, application):
        return cls.create_action("switch", application)

    @classmethod
    def validate_action(cls, action):
        if not isinstance(action, dict):
            return False
        if not isinstance(action.get("action"), str):
            return False
        if not isinstance(action.get("command"), (str, type(None))):
            return False
        if not isinstance(action.get("application"), str):
            return False
        if not isinstance(action.get("valid"), bool):
            return False
        return True

    @classmethod
    def available_actions(cls):
        return list(cls.ACTIONS.keys())


application_control = ApplicationControl()
