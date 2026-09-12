class ActionSelection:

    def __init__(self):
        self.name = "action_selection"

    def select(self, prioritized_plan):
        if not isinstance(prioritized_plan, dict):
            return None
        actions = prioritized_plan.get("actions")
        if not isinstance(actions, list) or not actions:
            return None
        ranking = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        candidates = [action for action in actions if isinstance(action, dict) and not action.get("completed", False)]
        if not candidates:
            return None
        selected = min(candidates, key=lambda item: (ranking.get(item.get("priority"), 99), item.get("order", 0)))
        return {"action_id": selected.get("id"), "action": selected.get("action"), "priority": selected.get("priority"), "reason": "Highest-priority available action selected."}

    def validate(self, selection):
        if not isinstance(selection, dict):
            return False
        required = ("action_id", "action", "priority", "reason")
        if any(key not in selection for key in required):
            return False
        if not isinstance(selection["action_id"], int):
            return False
        if not isinstance(selection["action"], str) or not selection["action"].strip():
            return False
        if selection["priority"] not in {"low", "medium", "high", "critical"}:
            return False
        if not isinstance(selection["reason"], str) or not selection["reason"].strip():
            return False
        return True


action_selection = ActionSelection()
