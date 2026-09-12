class DynamicWorkflowAdaptation:
    """Adapt an execution workflow based on current task states."""

    def adapt(self, tracking_result):
        if not self._valid_input(tracking_result):
            return None

        states = [task["state"] for task in tracking_result["task_states"]]

        if "failed" in states:
            action = "adapt"
            reason = "one or more tasks failed"
        elif all(state == "completed" for state in states):
            action = "continue"
            reason = "all tasks completed"
        else:
            action = "continue"
            reason = "execution is still in progress"

        result = {
            "goal": tracking_result["goal"],
            "selected_option_id": tracking_result["selected_option_id"],
            "action": action,
            "reason": reason,
            "completed_count": states.count("completed"),
            "running_count": states.count("running"),
            "pending_count": states.count("pending"),
            "failed_count": states.count("failed"),
            "adaptation_status": "ready",
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
        if value.get("tracking_status") != "active":
            return False
        states = value.get("task_states")
        if not isinstance(states, list) or not states:
            return False
        ids = set()
        for task in states:
            if not isinstance(task, dict):
                return False
            task_id = task.get("task_id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
                return False
            if task_id in ids:
                return False
            ids.add(task_id)
            if not isinstance(task.get("dispatch_id"), int) or isinstance(task.get("dispatch_id"), bool) or task["dispatch_id"] <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            if task.get("state") not in ("pending", "running", "completed", "failed"):
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
        if result.get("action") not in ("continue", "adapt"):
            return False
        if not isinstance(result.get("reason"), str) or not result["reason"].strip():
            return False
        for key in ("completed_count", "running_count", "pending_count", "failed_count"):
            if not isinstance(result.get(key), int) or isinstance(result.get(key), bool) or result[key] < 0:
                return False
        if result.get("adaptation_status") != "ready":
            return False
        return True


dynamic_workflow_adaptation = DynamicWorkflowAdaptation()
