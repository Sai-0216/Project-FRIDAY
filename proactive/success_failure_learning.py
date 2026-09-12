class SuccessFailureLearning:

    STATES = ("reinforce", "correct", "observe")

    def __init__(self):
        self.name = "success_failure_learning"

    def learn(self, analysis):
        if not isinstance(analysis, dict):
            return None
        action_id = analysis.get("action_id")
        action = analysis.get("action")
        state = analysis.get("state")
        score = analysis.get("score")
        if not isinstance(action_id, int):
            return None
        if not isinstance(action, str) or not action.strip():
            return None
        if state not in {"success", "failure", "partial", "unknown"}:
            return None
        if not isinstance(score, (int, float)) or not 0.0 <= score <= 1.0:
            return None
        if state == "success":
            learning_state = "reinforce"
            lesson = "successful outcome should strengthen the associated action strategy"
        elif state == "failure":
            learning_state = "correct"
            lesson = "failed outcome should trigger corrective learning"
        elif state == "partial":
            learning_state = "correct"
            lesson = "partial outcome should identify improvements for future attempts"
        else:
            learning_state = "observe"
            lesson = "insufficient outcome evidence; gather more experience"
        return {"action_id": action_id, "action": action.strip(), "outcome_state": state, "score": round(float(score), 3), "learning_state": learning_state, "lesson": lesson}

    def validate(self, learning):
        if not isinstance(learning, dict):
            return False
        required = ("action_id", "action", "outcome_state", "score", "learning_state", "lesson")
        if any(key not in learning for key in required):
            return False
        if not isinstance(learning["action_id"], int):
            return False
        if not isinstance(learning["action"], str) or not learning["action"].strip():
            return False
        if learning["outcome_state"] not in {"success", "failure", "partial", "unknown"}:
            return False
        if not isinstance(learning["score"], (int, float)) or not 0.0 <= learning["score"] <= 1.0:
            return False
        if learning["learning_state"] not in self.STATES:
            return False
        if not isinstance(learning["lesson"], str) or not learning["lesson"].strip():
            return False
        return True


success_failure_learning = SuccessFailureLearning()
