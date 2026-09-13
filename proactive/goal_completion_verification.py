class GoalCompletionVerification:
    """Verify whether an execution workflow completed successfully."""

    VALID_STATES = ("pending", "running", "completed", "failed")

    def verify(self, tracking_result):
        if not self._valid_input(tracking_result):
            return None

        states = [task["state"] for task in tracking_result["task_states"]]

        if "failed" in states:
            status = "failed"
            reason = "one or more tasks failed"
        elif all(state == "completed" for state in states):
            status = "completed"
            reason = "all tasks completed successfully"
        else:
            status = "in_progress"
            reason = "one or more tasks are still in progress"

        result = {
            "goal": tracking_result["goal"],
            "selected_option_id": tracking_result["selected_option_id"],
            "verification_status": status,
            "reason": reason,
            "completed_count": states.count("completed"),
            "failed_count": states.count("failed"),
            "remaining_count": sum(1 for state in states if state != "completed"),
            "verification_state": "ready",
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

            dispatch_id = task.get("dispatch_id")
            if not isinstance(dispatch_id, int) or isinstance(dispatch_id, bool) or dispatch_id <= 0:
                return False

            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False

            if task.get("state") not in self.VALID_STATES:
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

        if result.get("verification_status") not in ("completed", "failed", "in_progress"):
            return False

        if not isinstance(result.get("reason"), str) or not result["reason"].strip():
            return False

        for key in ("completed_count", "failed_count", "remaining_count"):
            if not isinstance(result.get(key), int) or isinstance(result.get(key), bool) or result[key] < 0:
                return False

        if result.get("verification_state") != "ready":
            return False

        return True


goal_completion_verification = GoalCompletionVerification()
