class SafeExecution:

    STATES = ("allowed", "blocked", "invalid")

    def __init__(self):
        self.name = "safe_execution"

    def assess(self, readiness, risk):
        if not isinstance(readiness, dict) or not isinstance(risk, dict):
            return None
        action_id = readiness.get("action_id")
        action = readiness.get("action")
        ready = readiness.get("ready")
        risk_level = risk.get("risk")
        if not isinstance(action_id, int) or not isinstance(action, str) or not action.strip():
            return None
        if not isinstance(ready, bool) or risk_level not in {"low", "medium", "high", "critical"}:
            return None
        if risk.get("action_id") != action_id:
            return None
        if not ready:
            return {"action_id": action_id, "action": action.strip(), "allowed": False, "state": "blocked", "reason": "action is not execution-ready"}
        if risk_level in {"high", "critical"}:
            return {"action_id": action_id, "action": action.strip(), "allowed": False, "state": "blocked", "reason": "elevated risk requires explicit approval"}
        return {"action_id": action_id, "action": action.strip(), "allowed": True, "state": "allowed", "reason": "action is ready and risk is within safe execution limits"}

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = ("action_id", "action", "allowed", "state", "reason")
        if any(key not in result for key in required):
            return False
        if not isinstance(result["action_id"], int):
            return False
        if not isinstance(result["action"], str) or not result["action"].strip():
            return False
        if not isinstance(result["allowed"], bool):
            return False
        if result["state"] not in self.STATES:
            return False
        if not isinstance(result["reason"], str) or not result["reason"].strip():
            return False
        return True


safe_execution = SafeExecution()
