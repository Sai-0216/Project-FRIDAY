class AutonomousExecution:

    STATES = ("ready", "blocked", "completed", "retry", "replan", "escalate")

    def __init__(self):
        self.name = "autonomous_execution"

    def integrate(self, selection, readiness, risk, safety, recovery=None):
        if not all(isinstance(value, dict) for value in (selection, readiness, risk, safety)):
            return None
        action_id = selection.get("action_id")
        if not isinstance(action_id, int):
            return None
        if readiness.get("action_id") != action_id or risk.get("action_id") != action_id or safety.get("action_id") != action_id:
            return None
        if not selection.get("action") or not readiness.get("action") or not risk.get("action") or not safety.get("action"):
            return None
        if not readiness.get("ready", False):
            state = "blocked"
            reason = "action is not execution-ready"
        elif not safety.get("allowed", False):
            state = "blocked"
            reason = safety.get("reason", "safe execution gate blocked the action")
        elif recovery is not None and isinstance(recovery, dict):
            recovery_state = recovery.get("state")
            if recovery_state in {"retry", "replan", "escalate", "completed"}:
                state = recovery_state
                reason = recovery.get("reason", "recovery state applied")
            else:
                state = "ready"
                reason = "action passed readiness and safety checks"
        else:
            state = "ready"
            reason = "action passed readiness and safety checks"
        return {"action_id": action_id, "action": selection["action"], "priority": selection.get("priority"), "risk": risk.get("risk"), "allowed": safety.get("allowed", False), "state": state, "reason": reason}

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = ("action_id", "action", "priority", "risk", "allowed", "state", "reason")
        if any(key not in result for key in required):
            return False
        if not isinstance(result["action_id"], int):
            return False
        if not isinstance(result["action"], str) or not result["action"].strip():
            return False
        if result["priority"] not in {"low", "medium", "high", "critical"}:
            return False
        if result["risk"] not in {"low", "medium", "high", "critical"}:
            return False
        if not isinstance(result["allowed"], bool):
            return False
        if result["state"] not in self.STATES:
            return False
        if not isinstance(result["reason"], str) or not result["reason"].strip():
            return False
        return True


autonomous_execution = AutonomousExecution()
