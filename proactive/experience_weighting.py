class ExperienceWeighting:
    """Assign influence weights to learned execution experiences."""

    OUTCOME_WEIGHTS = {
        "success": 1.0,
        "failure": 0.0,
        "partial": 0.5,
        "unknown": 0.0,
    }

    LEARNING_STATES = ("reinforce", "correct", "observe")

    def weight(self, learning):
        if not self.validate_learning(learning):
            return None

        outcome_state = learning["outcome_state"]
        weight = self.OUTCOME_WEIGHTS[outcome_state]

        if outcome_state == "success":
            rationale = "successful experience provides strong evidence for future learning"
        elif outcome_state == "failure":
            rationale = "failed experience provides strong evidence for corrective learning"
        elif outcome_state == "partial":
            rationale = "partial experience provides moderate evidence for future learning"
        else:
            rationale = "unknown experience provides no reliable evidence for learning"

        result = {
            "action_id": learning["action_id"],
            "action": learning["action"],
            "outcome_state": outcome_state,
            "learning_state": learning["learning_state"],
            "weight": weight,
            "rationale": rationale,
        }

        return result if self.validate(result) else None

    def validate_learning(self, learning):
        if not isinstance(learning, dict):
            return False
        if not isinstance(learning.get("action_id"), int):
            return False
        if not isinstance(learning.get("action"), str) or not learning["action"].strip():
            return False
        if learning.get("outcome_state") not in self.OUTCOME_WEIGHTS:
            return False
        if learning.get("learning_state") not in self.LEARNING_STATES:
            return False
        return True

    def validate(self, weighted):
        if not isinstance(weighted, dict):
            return False
        if not isinstance(weighted.get("action_id"), int):
            return False
        if not isinstance(weighted.get("action"), str) or not weighted["action"].strip():
            return False
        if weighted.get("outcome_state") not in self.OUTCOME_WEIGHTS:
            return False
        if weighted.get("learning_state") not in self.LEARNING_STATES:
            return False
        weight = weighted.get("weight")
        if not isinstance(weight, (int, float)) or not 0.0 <= weight <= 1.0:
            return False
        if not isinstance(weighted.get("rationale"), str) or not weighted["rationale"].strip():
            return False
        return True


experience_weighting = ExperienceWeighting()
