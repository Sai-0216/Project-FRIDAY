class ActionPlanning:
    STATUSES = ("ready", "active", "completed", "blocked")

    def __init__(self):
        self.name = "action_planning"

    def create(self, goal, actions):
        if not isinstance(goal, str) or not goal.strip():
            return None
        if not isinstance(actions, list) or not actions:
            return None
        normalized = []
        for index, action in enumerate(actions, 1):
            if not isinstance(action, str) or not action.strip():
                continue
            normalized.append({"id": index, "action": action.strip(), "completed": False})
        if not normalized:
            return None
        return {"goal": goal.strip(), "actions": normalized, "status": "ready"}

    def complete(self, plan, action_id):
        if not isinstance(plan, dict):
            return None
        for action in plan.get("actions", []):
            if action.get("id") == action_id:
                action["completed"] = True
                if all(item.get("completed") for item in plan.get("actions", [])):
                    plan["status"] = "completed"
                else:
                    plan["status"] = "active"
                return plan
        return None

    def remaining(self, plan):
        if not isinstance(plan, dict):
            return []
        return [action for action in plan.get("actions", []) if not action.get("completed", False)]

    def validate(self, plan):
        if not isinstance(plan, dict):
            return False
        if not isinstance(plan.get("goal"), str) or not plan["goal"].strip():
            return False
        if not isinstance(plan.get("actions"), list) or not plan["actions"]:
            return False
        if plan.get("status") not in self.STATUSES:
            return False
        for action in plan["actions"]:
            if not isinstance(action, dict):
                return False
            if not isinstance(action.get("id"), int):
                return False
            if not isinstance(action.get("action"), str) or not action["action"].strip():
                return False
            if not isinstance(action.get("completed"), bool):
                return False
        return True


action_planning = ActionPlanning()
