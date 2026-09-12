class ExecutionStateTracking:
    """Track the execution state of dispatched tasks."""

    VALID_STATES = ("pending", "running", "completed", "failed")

    def initialize(self, dispatch_result):
        if not self._valid_input(dispatch_result):
            return None

        states = []
        for task in dispatch_result["dispatched_tasks"]:
            states.append({
                "task_id": task["task_id"],
                "dispatch_id": task["dispatch_id"],
                "description": task["description"],
                "state": "pending",
            })

        result = {
            "goal": dispatch_result["goal"],
            "selected_option_id": dispatch_result["selected_option_id"],
            "task_states": states,
            "state_count": len(states),
            "tracking_status": "active",
        }
        return result if self.validate(result) else None

    def update(self, tracking_result, task_id, new_state):
        if not self.validate(tracking_result):
            return None
        if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
            return None
        if new_state not in self.VALID_STATES:
            return None

        updated = {
            "goal": tracking_result["goal"],
            "selected_option_id": tracking_result["selected_option_id"],
            "task_states": [dict(task) for task in tracking_result["task_states"]],
            "state_count": tracking_result["state_count"],
            "tracking_status": tracking_result["tracking_status"],
        }

        found = False
        for task in updated["task_states"]:
            if task["task_id"] == task_id:
                task["state"] = new_state
                found = True
                break

        if not found:
            return None
        return updated if self.validate(updated) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if value.get("dispatch_status") != "ready":
            return False
        tasks = value.get("dispatched_tasks")
        if not isinstance(tasks, list) or not tasks:
            return False
        for task in tasks:
            if not isinstance(task, dict):
                return False
            if not isinstance(task.get("task_id"), int) or isinstance(task.get("task_id"), bool) or task["task_id"] <= 0:
                return False
            if not isinstance(task.get("dispatch_id"), int) or isinstance(task.get("dispatch_id"), bool) or task["dispatch_id"] <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            if task.get("dispatch_status") != "dispatched":
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
        states = result.get("task_states")
        if not isinstance(states, list) or not states:
            return False
        ids = []
        dispatch_ids = []
        for task in states:
            if not isinstance(task, dict):
                return False
            task_id = task.get("task_id")
            dispatch_id = task.get("dispatch_id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
                return False
            if not isinstance(dispatch_id, int) or isinstance(dispatch_id, bool) or dispatch_id <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            if task.get("state") not in self.VALID_STATES:
                return False
            ids.append(task_id)
            dispatch_ids.append(dispatch_id)
        if len(set(ids)) != len(ids):
            return False
        if len(set(dispatch_ids)) != len(dispatch_ids):
            return False
        if not isinstance(result.get("state_count"), int) or isinstance(result.get("state_count"), bool):
            return False
        if result["state_count"] != len(states):
            return False
        if result.get("tracking_status") != "active":
            return False
        return True


execution_state_tracking = ExecutionStateTracking()
