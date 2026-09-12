class ExecutionRecovery:

    STATES = ("completed", "retry", "replan", "blocked", "escalate")

    def __init__(self):
        self.name = "execution_recovery"

    def recover(self, execution_result, attempt_count=1, max_retries=2):
        if not isinstance(execution_result, dict):
            return None
        action_id = execution_result.get("action_id")
        action = execution_result.get("action")
        success = execution_result.get("success")
        if not isinstance(action_id, int) or not isinstance(action, str) or not action.strip():
            return None
        if not isinstance(success, bool):
            return None
        if not isinstance(attempt_count, int) or attempt_count < 1:
            return None
        if not isinstance(max_retries, int) or max_retries < 0:
            return None
        if success:
            return {"action_id": action_id, "action": action.strip(), "state": "completed", "attempt": attempt_count, "reason": "execution completed successfully"}
        if attempt_count <= max_retries:
            return {"action_id": action_id, "action": action.strip(), "state": "retry", "attempt": attempt_count, "reason": "execution failed and retry limit has not been reached"}
        return {"action_id": action_id, "action": action.strip(), "state": "replan", "attempt": attempt_count, "reason": "execution failed after retry limit; replanning is required"}

    def escalate(self, recovery):
        if not isinstance(recovery, dict):
            return None
        if recovery.get("state") not in {"blocked", "replan", "retry"}:
            return recovery
        result = dict(recovery)
        result["state"] = "escalate"
        result["reason"] = "execution recovery requires escalation"
        return result

    def validate(self, recovery):
        if not isinstance(recovery, dict):
            return False
        required = ("action_id", "action", "state", "attempt", "reason")
        if any(key not in recovery for key in required):
            return False
        if not isinstance(recovery["action_id"], int):
            return False
        if not isinstance(recovery["action"], str) or not recovery["action"].strip():
            return False
        if recovery["state"] not in self.STATES:
            return False
        if not isinstance(recovery["attempt"], int) or recovery["attempt"] < 1:
            return False
        if not isinstance(recovery["reason"], str) or not recovery["reason"].strip():
            return False
        return True


execution_recovery = ExecutionRecovery()
