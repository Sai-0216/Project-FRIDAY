class ActionPrioritization:
    PRIORITIES = ("low", "medium", "high", "critical")

    def __init__(self):
        self.name = "action_prioritization"

    def create(self, action_plan, dependency_plan=None):
        if not isinstance(action_plan, dict):
            return None
        actions = action_plan.get("actions")
        if not isinstance(actions, list) or not actions:
            return None
        ready_ids = None
        if isinstance(dependency_plan, dict):
            ready_ids = {task.get("id") for task in dependency_plan.get("tasks", []) if task.get("ready") and not task.get("completed")}
        prioritized = []
        for index, action in enumerate(actions, 1):
            if not isinstance(action, dict):
                continue
            if action.get("completed", False):
                continue
            action_id = action.get("id", index)
            if ready_ids is not None and action_id not in ready_ids:
                continue
            prioritized.append({"id": action_id, "action": action.get("action", ""), "priority": "medium", "order": len(prioritized) + 1})
        if not prioritized:
            return {"goal": action_plan.get("goal", ""), "actions": [], "status": "blocked"}
        return {"goal": action_plan.get("goal", ""), "actions": prioritized, "status": "ready"}

    def set_priority(self, prioritized_plan, action_id, priority):
        if not isinstance(prioritized_plan, dict):
            return False
        if priority not in self.PRIORITIES:
            return False
        for action in prioritized_plan.get("actions", []):
            if action.get("id") == action_id:
                action["priority"] = priority
                return True
        return False

    def ordered_actions(self, prioritized_plan):
        if not isinstance(prioritized_plan, dict):
            return []
        ranking = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions = [action for action in prioritized_plan.get("actions", []) if isinstance(action, dict)]
        return sorted(actions, key=lambda item: (ranking.get(item.get("priority"), 99), item.get("order", 0)))

    def validate(self, prioritized_plan):
        if not isinstance(prioritized_plan, dict):
            return False
        if not isinstance(prioritized_plan.get("goal"), str):
            return False
        actions = prioritized_plan.get("actions")
        if not isinstance(actions, list):
            return False
        if prioritized_plan.get("status") not in ("ready", "blocked", "completed"):
            return False
        for action in actions:
            if not isinstance(action, dict):
                return False
            if not isinstance(action.get("id"), int):
                return False
            if not isinstance(action.get("action"), str) or not action["action"].strip():
                return False
            if action.get("priority") not in self.PRIORITIES:
                return False
            if not isinstance(action.get("order"), int):
                return False
        return True


action_prioritization = ActionPrioritization()
