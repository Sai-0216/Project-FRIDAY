class PolicyAdjustment:
    """Adjust decision policies from adapted action strategies."""

    ADJUSTMENTS = ("reinforce", "adjust", "retain")
    ADAPTATIONS = ("strengthen", "modify", "observe")

    def adjust(self, adaptation):
        if not self.validate_adaptation(adaptation):
            return None

        strategy = adaptation["adaptation"]

        if strategy == "strengthen":
            adjustment = "reinforce"
            recommendation = "reinforce the policy supporting the successful strategy"
        elif strategy == "modify":
            adjustment = "adjust"
            recommendation = "adjust the policy to improve future decision outcomes"
        else:
            adjustment = "retain"
            recommendation = "retain the current policy while gathering more evidence"

        result = {
            "action_id": adaptation["action_id"],
            "action": adaptation["action"],
            "adaptation": strategy,
            "adjustment": adjustment,
            "recommendation": recommendation,
        }

        return result if self.validate(result) else None

    def validate_adaptation(self, adaptation):
        if not isinstance(adaptation, dict):
            return False
        if not isinstance(adaptation.get("action_id"), int):
            return False
        if not isinstance(adaptation.get("action"), str) or not adaptation["action"].strip():
            return False
        if adaptation.get("adaptation") not in self.ADAPTATIONS:
            return False
        return True

    def validate(self, adjustment):
        if not isinstance(adjustment, dict):
            return False
        if not isinstance(adjustment.get("action_id"), int):
            return False
        if not isinstance(adjustment.get("action"), str) or not adjustment["action"].strip():
            return False
        if adjustment.get("adaptation") not in self.ADAPTATIONS:
            return False
        if adjustment.get("adjustment") not in self.ADJUSTMENTS:
            return False
        if not isinstance(adjustment.get("recommendation"), str) or not adjustment["recommendation"].strip():
            return False
        return True


policy_adjustment = PolicyAdjustment()
