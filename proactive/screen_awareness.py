"""FRIDAY V3 - Phase 24.1 Screen Awareness."""


class ScreenAwareness:

    @staticmethod
    def _safe_value(value, default=None):
        return default if value is None else value

    @classmethod
    def capture(cls, width=0, height=0, applications=None, elements=None):
        applications = applications if isinstance(applications, list) else []
        elements = elements if isinstance(elements, list) else []

        return {
            "screen": {
                "width": int(width) if isinstance(width, (int, float)) else 0,
                "height": int(height) if isinstance(height, (int, float)) else 0,
            },
            "applications": applications,
            "elements": elements,
            "aware": True,
        }

    @classmethod
    def describe(cls, state):
        if not isinstance(state, dict):
            return {
                "screen": {},
                "applications": [],
                "elements": [],
                "aware": False,
            }

        return {
            "screen": state.get("screen", {}),
            "applications": state.get("applications", []),
            "elements": state.get("elements", []),
            "aware": bool(state.get("aware", False)),
        }

    @classmethod
    def validate(cls, state):
        if not isinstance(state, dict):
            return False
        if not isinstance(state.get("screen"), dict):
            return False
        if not isinstance(state.get("applications"), list):
            return False
        if not isinstance(state.get("elements"), list):
            return False
        if not isinstance(state.get("aware"), bool):
            return False
        return True


screen_awareness = ScreenAwareness()
