class DecisionConfidence:
    """Estimate confidence in a strategic decision."""

    def assess(self, decision_result, context_result=None):
        if not self._valid_decision(decision_result):
            return None
        if context_result is not None and not self._valid_context(context_result):
            return None

        score = float(decision_result["preferred_score"])
        tradeoff = float(decision_result["tradeoff_score"])
        context_quality = 1.0 if context_result is None else float(context_result["context_quality"])

        uncertainty = 1.0 - context_quality
        confidence = (score * 0.5) + (tradeoff * 0.25) + (context_quality * 0.25)
        confidence -= uncertainty * 0.1
        confidence = round(max(0.0, min(1.0, confidence)), 3)

        if confidence >= 0.75:
            level = "high"
            reason = "the selected option has strong evidence and sufficient decision context"
        elif confidence >= 0.5:
            level = "moderate"
            reason = "the selected option is reasonably supported but has some uncertainty"
        else:
            level = "low"
            reason = "the decision has limited evidence or substantial uncertainty"

        result = {
            "goal": decision_result["goal"],
            "preferred_option_id": decision_result["preferred_option_id"],
            "confidence": confidence,
            "confidence_level": level,
            "reason": reason,
        }
        return result if self.validate(result) else None

    def _valid_decision(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        for key in ("preferred_score", "tradeoff_score"):
            number = value.get(key)
            if not isinstance(number, (int, float)) or isinstance(number, bool):
                return False
            if not 0.0 <= float(number) <= 1.0:
                return False
        return True

    def _valid_context(self, value):
        if not isinstance(value, dict):
            return False
        quality = value.get("context_quality")
        if not isinstance(quality, (int, float)) or isinstance(quality, bool):
            return False
        return 0.0 <= float(quality) <= 1.0

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        option_id = result.get("preferred_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if not isinstance(result.get("confidence"), float) or not 0.0 <= result["confidence"] <= 1.0:
            return False
        if result.get("confidence_level") not in ("high", "moderate", "low"):
            return False
        if not isinstance(result.get("reason"), str) or not result["reason"].strip():
            return False
        return True

decision_confidence = DecisionConfidence()
