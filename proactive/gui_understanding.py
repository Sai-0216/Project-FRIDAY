"""FRIDAY V3 - Phase 24.2 GUI Understanding."""


class GUIUnderstanding:

    TYPES = {
        "button": "clickable",
        "text": "readable",
        "input": "typeable",
        "link": "navigable",
        "image": "visual",
        "checkbox": "toggleable",
        "menu": "expandable",
    }

    @classmethod
    def understand_element(cls, element):
        if not isinstance(element, dict):
            return None

        element_type = str(element.get("type", "unknown")).lower()
        label = element.get("label", "")
        capability = cls.TYPES.get(element_type, "unknown")

        return {
            "type": element_type,
            "label": label,
            "capability": capability,
            "understood": capability != "unknown",
        }

    @classmethod
    def understand(cls, state):
        if not isinstance(state, dict):
            return {
                "elements": [],
                "understood_count": 0,
                "understood": False,
            }

        raw_elements = state.get("elements", [])
        if not isinstance(raw_elements, list):
            raw_elements = []

        elements = []
        for element in raw_elements:
            understood = cls.understand_element(element)
            if understood is not None:
                elements.append(understood)

        return {
            "elements": elements,
            "understood_count": sum(1 for item in elements if item["understood"]),
            "understood": bool(elements),
        }

    @classmethod
    def validate(cls, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("elements"), list):
            return False
        if not isinstance(result.get("understood_count"), int):
            return False
        if not isinstance(result.get("understood"), bool):
            return False
        return True


gui_understanding = GUIUnderstanding()
