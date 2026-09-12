class ExecutionReadiness:
    STATES = ("ready", "blocked", "completed")

    def __init__(self):
        self.name = "execution_readiness"

    def assess(self, action, dependency_plan=None, workflow=None):
        if not isinstance(action, dict):
            return None
        action_id = action.get("id")
        action_name = action.get("action")
        if not isinstance(action_id, int) or not isinstance(action_name, str) or not action_name.strip():
            return None
        if action.get("completed", False):
            return {"action_id": action_id, "action": action_name, "ready": False, "state": "completed", "reasons": ["action already completed"]}
        reasons = []
        if action.get("priority") is not None and action.get("priority") not in {"low", "medium", "high", "critical"}:
            reasons.append("invalid priority")
        if isinstance(dependency_plan, dict):
            matching = next((task for task in dependency_plan.get("tasks", []) if task.get("id") == action_id), None)
            if matching is None:
                reasons.append("dependency task not found")
            elif not matching.get("ready", False):
                reasons.append("dependencies not satisfied")
        if isinstance(workflow, dict):
            if workflow.get("status") in {"blocked", "paused"}:
                reasons.append("workflow is blocked")
        ready = not reasons
        return {"action_id": action_id, "action": action_name.strip(), "ready": ready, "state": "ready" if ready else "blocked", "reasons": reasons}

    def is_ready(self, assessment):
        return isinstance(assessment, dict) and assessment.get("ready") is True and assessment.get("state") == "ready"

    def validate(self, assessment):
        if not isinstance(assessment, dict):
            return False
        required = ("action_id", "action", "ready", "state", "reasons")
        if any(key not in assessment for key in required):
            return False
        if not isinstance(assessment["action_id"], int):
            return False
        if not isinstance(assessment["action"], str) or not assessment["action"].strip():
            return False
        if not isinstance(assessment["ready"], bool):
            return False
        if assessment["state"] not in self.STATES:
            return False
        if not isinstance(assessment["reasons"], list):
            return False
        return True


execution_readiness = ExecutionReadiness()
