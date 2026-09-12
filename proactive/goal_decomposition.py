class GoalDecomposition:
    def __init__(self):
        self.name = "goal_decomposition"

    def create(self, goal, subgoals=None):
        if not isinstance(goal, str) or not goal.strip():
            return None
        items = subgoals if isinstance(subgoals, list) else []
        normalized = []
        for index, item in enumerate(items, 1):
            if isinstance(item, str) and item.strip():
                normalized.append({
                    "id": index,
                    "goal": item.strip(),
                    "completed": False,
                })
        return {
            "goal": goal.strip(),
            "subgoals": normalized,
            "count": len(normalized),
            "completed_count": 0,
            "status": "ready",
        }

    def complete(self, plan, subgoal_id):
        if not isinstance(plan, dict):
            return False
        for item in plan.get("subgoals", []):
            if item.get("id") == subgoal_id:
                item["completed"] = True
                plan["completed_count"] = sum(1 for x in plan["subgoals"] if x.get("completed"))
                plan["status"] = "completed" if plan["completed_count"] == plan["count"] and plan["count"] > 0 else "active"
                return True
        return False

    def remaining(self, plan):
        if not isinstance(plan, dict):
            return []
        return [item for item in plan.get("subgoals", []) if not item.get("completed")]

    def validate(self, plan):
        if not isinstance(plan, dict):
            return False
        if not isinstance(plan.get("goal"), str) or not plan["goal"]:
            return False
        if not isinstance(plan.get("subgoals"), list):
            return False
        if plan.get("count") != len(plan["subgoals"]):
            return False
        if plan.get("completed_count") != sum(1 for x in plan["subgoals"] if x.get("completed")):
            return False
        return plan.get("status") in ("ready", "active", "completed")


goal_decomposition = GoalDecomposition()
