class LearningIntegration:
    """Integrate the Phase 27 adaptive learning pipeline."""

    STATES = ("success", "failure", "partial", "unknown")
    LEARNING_STATES = ("reinforce", "correct", "observe")
    ADAPTATIONS = ("strengthen", "modify", "observe")
    ADJUSTMENTS = ("reinforce", "adjust", "retain")
    TRENDS = ("improving", "declining", "stable", "insufficient")
    IMPROVEMENTS = ("continue", "adjust", "optimize", "observe")

    def integrate(self, outcome, learning, adaptation, policy, experience, trend, improvement):
        if not self._valid_outcome(outcome):
            return None
        if not self._valid_learning(learning):
            return None
        if not self._valid_adaptation(adaptation):
            return None
        if not self._valid_policy(policy):
            return None
        if not self._valid_experience(experience):
            return None
        if not self._valid_trend(trend):
            return None
        if not self._valid_improvement(improvement):
            return None

        result = {
            "action_id": outcome["action_id"],
            "action": outcome["action"],
            "outcome_state": outcome["state"],
            "score": outcome["score"],
            "learning_state": learning["learning_state"],
            "adaptation": adaptation["adaptation"],
            "adjustment": policy["adjustment"],
            "weight": experience["weight"],
            "trend": trend["trend"],
            "improvement": improvement["improvement"],
            "recommendation": improvement["recommendation"],
        }
        return result if self.validate(result) else None

    def _valid_outcome(self, value):
        return (
            isinstance(value, dict)
            and isinstance(value.get("action_id"), int)
            and isinstance(value.get("action"), str)
            and bool(value.get("action"))
            and value.get("state") in self.STATES
            and isinstance(value.get("score"), (int, float))
            and 0.0 <= value["score"] <= 1.0
        )

    def _valid_learning(self, value):
        return (
            isinstance(value, dict)
            and value.get("learning_state") in self.LEARNING_STATES
            and value.get("action_id") == value.get("action_id")
        )

    def _valid_adaptation(self, value):
        return isinstance(value, dict) and value.get("adaptation") in self.ADAPTATIONS

    def _valid_policy(self, value):
        return isinstance(value, dict) and value.get("adjustment") in self.ADJUSTMENTS

    def _valid_experience(self, value):
        return (
            isinstance(value, dict)
            and isinstance(value.get("weight"), (int, float))
            and 0.0 <= value["weight"] <= 1.0
        )

    def _valid_trend(self, value):
        return (
            isinstance(value, dict)
            and value.get("trend") in self.TRENDS
            and isinstance(value.get("sample_size"), int)
            and value["sample_size"] >= 0
            and isinstance(value.get("change"), (int, float))
        )

    def _valid_improvement(self, value):
        return isinstance(value, dict) and value.get("improvement") in self.IMPROVEMENTS

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = (
            "action_id", "action", "outcome_state", "score", "learning_state",
            "adaptation", "adjustment", "weight", "trend", "improvement",
            "recommendation"
        )
        if any(key not in result for key in required):
            return False
        return (
            isinstance(result["action_id"], int)
            and isinstance(result["action"], str)
            and bool(result["action"])
            and result["outcome_state"] in self.STATES
            and isinstance(result["score"], (int, float))
            and 0.0 <= result["score"] <= 1.0
            and result["learning_state"] in self.LEARNING_STATES
            and result["adaptation"] in self.ADAPTATIONS
            and result["adjustment"] in self.ADJUSTMENTS
            and isinstance(result["weight"], (int, float))
            and 0.0 <= result["weight"] <= 1.0
            and result["trend"] in self.TRENDS
            and result["improvement"] in self.IMPROVEMENTS
            and isinstance(result["recommendation"], str)
            and bool(result["recommendation"])
        )


learning_integration = LearningIntegration()
