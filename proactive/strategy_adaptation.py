class StrategyAdaptation:
    """Adapt action strategies from learned execution outcomes."""

    ADAPTATIONS = ("strengthen", "modify", "observe")
    LEARNING_STATES = ("reinforce", "correct", "observe")

    def adapt(self, learning):
        if not self.validate_learning(learning):
            return None

        learning_state = learning["learning_state"]

        if learning_state == "reinforce":
            adaptation = "strengthen"
            recommendation = "strengthen the current strategy for future executions"
        elif learning_state == "correct":
            adaptation = "modify"
            recommendation = "modify the strategy to address the learned weakness"
        else:
            adaptation = "observe"
            recommendation = "keep the current strategy and gather more outcome evidence"

        result = {
            "action_id": learning["action_id"],
            "action": learning["action"],
            "learning_state": learning_state,
            "adaptation": adaptation,
            "recommendation": recommendation,
        }

        return result if self.validate(result) else None

    def validate_learning(self, learning):
        if not isinstance(learning, dict):
            return False
        if not isinstance(learning.get("action_id"), int):
            return False
        if not isinstance(learning.get("action"), str) or not learning["action"].strip():
            return False
        if learning.get("learning_state") not in self.LEARNING_STATES:
            return False
        return True

    def validate(self, adaptation):
        if not isinstance(adaptation, dict):
            return False
        if not isinstance(adaptation.get("action_id"), int):
            return False
        if not isinstance(adaptation.get("action"), str) or not adaptation["action"].strip():
            return False
        if adaptation.get("learning_state") not in self.LEARNING_STATES:
            return False
        if adaptation.get("adaptation") not in self.ADAPTATIONS:
            return False
        if not isinstance(adaptation.get("recommendation"), str) or not adaptation["recommendation"].strip():
            return False
        return True


strategy_adaptation = StrategyAdaptation()
