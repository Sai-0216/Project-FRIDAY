class PersistentPlans:
    STATUSES = ("active", "paused", "completed", "cancelled")

    def __init__(self):
        self.name = "persistent_plans"
        self._next_id = 1

    def create(self, name, goal, steps=None):
        if not isinstance(name, str) or not name.strip():
            return None
        if not isinstance(goal, str) or not goal.strip():
            return None
        items = []
        for index, step in enumerate(steps if isinstance(steps, list) else [], 1):
            if isinstance(step, str) and step.strip():
                items.append({"id": index, "step": step.strip(), "completed": False})
        plan = {
            "id": self._next_id,
            "name": name.strip(),
            "goal": goal.strip(),
            "steps": items,
            "step_count": len(items),
            "completed_count": 0,
            "status": "active",
            "progress": 0.0,
        }
        self._next_id += 1
        return plan

    def update(self, plan):
        if not isinstance(plan, dict):
            return None
        steps = plan.get("steps", [])
        completed = sum(1 for step in steps if step.get("completed"))
        plan["step_count"] = len(steps)
        plan["completed_count"] = completed
        plan["progress"] = completed / len(steps) if steps else 0.0
        if steps and completed == len(steps):
            plan["status"] = "completed"
        return plan

    def complete_step(self, plan, step_id):
        if not isinstance(plan, dict):
            return False
        for step in plan.get("steps", []):
            if step.get("id") == step_id:
                step["completed"] = True
                self.update(plan)
                return True
        return False

    def set_status(self, plan, status):
        if not isinstance(plan, dict) or status not in self.STATUSES:
            return False
        plan["status"] = status
        return True

    def validate(self, plan):
        if not isinstance(plan, dict):
            return False
        required = ("id", "name", "goal", "steps", "step_count", "completed_count", "status", "progress")
        if any(key not in plan for key in required):
            return False
        if not isinstance(plan["steps"], list):
            return False
        if plan["step_count"] != len(plan["steps"]):
            return False
        completed = sum(1 for step in plan["steps"] if step.get("completed"))
        if plan["completed_count"] != completed:
            return False
        expected = completed / len(plan["steps"]) if plan["steps"] else 0.0
        if abs(float(plan["progress"]) - expected) > 1e-9:
            return False
        return plan["status"] in self.STATUSES


persistent_plans = PersistentPlans()
