class OutcomeAnalysis:

    STATES = ("success", "failure", "partial", "unknown")

    def __init__(self):
        self.name = "outcome_analysis"

    def analyze(self, outcome):
        if not isinstance(outcome, dict):
            return None
        action_id = outcome.get("action_id")
        action = outcome.get("action")
        success = outcome.get("success")
        if not isinstance(action_id, int):
            return None
        if not isinstance(action, str) or not action.strip():
            return None
        if success is True:
            state = "success"
            score = 1.0
            reasons = ["execution reported success"]
        elif success is False:
            state = "failure"
            score = 0.0
            reasons = ["execution reported failure"]
        elif isinstance(outcome.get("completed_steps"), int) and isinstance(outcome.get("total_steps"), int) and outcome.get("total_steps", 0) > 0:
            completed = max(0, min(outcome["completed_steps"], outcome["total_steps"]))
            score = completed / outcome["total_steps"]
            if score >= 1.0:
                state = "success"
                reasons = ["all reported steps completed"]
            elif score > 0.0:
                state = "partial"
                reasons = ["some reported steps completed"]
            else:
                state = "failure"
                reasons = ["no reported steps completed"]
        else:
            state = "unknown"
            score = 0.0
            reasons = ["execution outcome is insufficient to determine result"]
        return {"action_id": action_id, "action": action.strip(), "state": state, "score": round(score, 3), "reasons": reasons}

    def validate(self, analysis):
        if not isinstance(analysis, dict):
            return False
        required = ("action_id", "action", "state", "score", "reasons")
        if any(key not in analysis for key in required):
            return False
        if not isinstance(analysis["action_id"], int):
            return False
        if not isinstance(analysis["action"], str) or not analysis["action"].strip():
            return False
        if analysis["state"] not in self.STATES:
            return False
        if not isinstance(analysis["score"], (int, float)) or not 0.0 <= analysis["score"] <= 1.0:
            return False
        if not isinstance(analysis["reasons"], list):
            return False
        return True


outcome_analysis = OutcomeAnalysis()
