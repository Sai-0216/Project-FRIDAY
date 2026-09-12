"""FRIDAY V3 - Phase 24.3 UI Element Detection."""


class UIElementDetection:

    ACTIONABLE = {
        "button": "click",
        "input": "type",
        "link": "navigate",
        "checkbox": "toggle",
        "menu": "expand",
    }

    @classmethod
    def detect_element(cls, element):
        if not isinstance(element, dict):
            return None

        element_type = str(element.get("type", "unknown")).lower()
        label = element.get("label", "")
        action = cls.ACTIONABLE.get(element_type)

        return {
            "type": element_type,
            "label": label,
            "action": action,
            "actionable": action is not None,
        }

    @classmethod
    def detect(cls, gui_state):
        if not isinstance(gui_state, dict):
            return {
                "elements": [],
                "actionable_count": 0,
                "detected": False,
            }

        raw_elements = gui_state.get("elements", [])
        if not isinstance(raw_elements, list):
            raw_elements = []

        elements = []
        for element in raw_elements:
            detected = cls.detect_element(element)
            if detected is not None:
                elements.append(detected)

        return {
            "elements": elements,
            "actionable_count": sum(1 for item in elements if item["actionable"]),
            "detected": bool(elements),
        }

    @classmethod
    def actionable(cls, detection):
        if not isinstance(detection, dict):
            return []

        elements = detection.get("elements", [])
        if not isinstance(elements, list):
            return []

        return [element for element in elements if isinstance(element, dict) and element.get("actionable")]

    @classmethod
    def validate(cls, detection):
        if not isinstance(detection, dict):
            return False
        if not isinstance(detection.get("elements"), list):
            return False
        if not isinstance(detection.get("actionable_count"), int):
            return False
        if not isinstance(detection.get("detected"), bool):
            return False
        return True


ui_element_detection = UIElementDetection()
