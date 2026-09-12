class GoalExecutionPlanning:
    """Convert a validated strategic decision into an execution plan."""

    def plan(self, decision_result):
        if not self._valid_input(decision_result):
            return None

        goal = decision_result["goal"]
        option_id = decision_result["selected_option_id"]
        score = float(decision_result["selected_score"])
        confidence = float(decision_result["confidence"])

        tasks = [
            {"task_id": 1, "description": "prepare execution for the selected strategy", "depends_on": []},
            {"task_id": 2, "description": "execute the selected strategy", "depends_on": [1]},
            {"task_id": 3, "description": "verify the execution outcome", "depends_on": [2]},
        ]

        result = {
            "goal": goal,
            "selected_option_id": option_id,
            "selected_score": score,
            "confidence": confidence,
            "tasks": tasks,
            "task_count": len(tasks),
            "plan_status": "ready",
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        for key in ("selected_score", "confidence"):
            number = value.get(key)
            if not isinstance(number, (int, float)) or isinstance(number, bool):
                return False
            if not 0.0 <= float(number) <= 1.0:
                return False
        if value.get("decision_status") != "selected":
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        option_id = result.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        for key in ("selected_score", "confidence"):
            if not isinstance(result.get(key), float) or not 0.0 <= result[key] <= 1.0:
                return False
        tasks = result.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            return False
        for task in tasks:
            if not isinstance(task, dict):
                return False
            task_id = task.get("task_id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            if not isinstance(task.get("depends_on"), list):
                return False
            for dependency in task["depends_on"]:
                if not isinstance(dependency, int) or isinstance(dependency, bool) or dependency <= 0:
                    return False
        if not isinstance(result.get("task_count"), int) or isinstance(result.get("task_count"), bool) or result["task_count"] != len(tasks):
            return False
        if result.get("plan_status") != "ready":
            return False
        return True

goal_execution_planning = GoalExecutionPlanning()
