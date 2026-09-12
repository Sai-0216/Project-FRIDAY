class RiskAssessment:

    LEVELS = ("low", "medium", "high", "critical")

    def __init__(self):
        self.name = "risk_assessment"

    def assess(self, action):
        if not isinstance(action, dict):
            return None
        if not isinstance(action.get("action_id"), int):
            return None
        text = action.get("action")
        priority = action.get("priority")
        if not isinstance(text, str) or not text.strip():
            return None
        if priority not in {"low", "medium", "high", "critical"}:
            return None

        reasons = []
        risk = "low"
        lowered = text.lower()

        high_terms = ("delete", "remove", "send", "publish", "install", "change", "modify")
        critical_terms = ("format", "shutdown", "terminate", "payment", "transfer", "password")

        if any(term in lowered for term in critical_terms):
            risk = "critical"
            reasons.append("action contains a potentially critical operation")
        elif any(term in lowered for term in high_terms):
            risk = "high"
            reasons.append("action contains an operation requiring caution")
        elif priority == "critical":
            risk = "high"
            reasons.append("critical priority increases execution risk")
        elif priority == "high":
            risk = "medium"
            reasons.append("high priority requires additional caution")
        else:
            reasons.append("no elevated risk indicators detected")

        return {"action_id": action["action_id"], "action": text.strip(), "risk": risk, "reasons": reasons}

    def validate(self, assessment):
        if not isinstance(assessment, dict):
            return False
        required = ("action_id", "action", "risk", "reasons")
        if any(key not in assessment for key in required):
            return False
        if not isinstance(assessment["action_id"], int):
            return False
        if not isinstance(assessment["action"], str) or not assessment["action"].strip():
            return False
        if assessment["risk"] not in self.LEVELS:
            return False
        if not isinstance(assessment["reasons"], list):
            return False
        return True


risk_assessment = RiskAssessment()
