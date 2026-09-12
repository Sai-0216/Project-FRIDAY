class AdaptiveDecisionImprovement:
    """Determine decision improvements from observed performance trends."""

    TRENDS = ("improving", "declining", "stable", "insufficient")
    IMPROVEMENTS = ("continue", "adjust", "optimize", "observe")

    def improve(self, trend):
        if not self.validate_trend(trend):
            return None

        trend_state = trend["trend"]

        if trend_state == "improving":
            improvement = "continue"
            recommendation = "continue the current decision strategy while preserving successful behavior"
        elif trend_state == "declining":
            improvement = "adjust"
            recommendation = "adjust future decisions to address the declining performance trend"
        elif trend_state == "stable":
            improvement = "optimize"
            recommendation = "optimize the current decision strategy for further improvement"
        else:
            improvement = "observe"
            recommendation = "gather more experience before changing future decision behavior"

        result = {
            "trend": trend_state,
            "improvement": improvement,
            "recommendation": recommendation,
            "sample_size": trend["sample_size"],
            "change": trend["change"],
        }

        return result if self.validate(result) else None

    def validate_trend(self, trend):
        if not isinstance(trend, dict):
            return False
        if trend.get("trend") not in self.TRENDS:
            return False
        if not isinstance(trend.get("sample_size"), int) or trend["sample_size"] < 0:
            return False
        if not isinstance(trend.get("change"), (int, float)):
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if result.get("trend") not in self.TRENDS:
            return False
        if result.get("improvement") not in self.IMPROVEMENTS:
            return False
        if not isinstance(result.get("recommendation"), str) or not result["recommendation"].strip():
            return False
        if not isinstance(result.get("sample_size"), int) or result["sample_size"] < 0:
            return False
        if not isinstance(result.get("change"), (int, float)):
            return False
        return True


adaptive_decision_improvement = AdaptiveDecisionImprovement()
