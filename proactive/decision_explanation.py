class DecisionExplanation:
    """Explain why a strategic decision was selected."""

    def explain(self, tradeoff_result, confidence_result, context_result=None):
        if not self._valid_tradeoff(tradeoff_result):
            return None
        if not self._valid_confidence(confidence_result):
            return None
        if context_result is not None and not self._valid_context(context_result):
            return None

        score = float(tradeoff_result["preferred_score"])
        tradeoff = float(tradeoff_result["tradeoff_score"])
        confidence = float(confidence_result["confidence"])
        context_quality = 1.0 if context_result is None else float(context_result["context_quality"])

        reasons = []
        if score >= 0.75:
            reasons.append("the selected option has a strong evaluation score")
        elif score >= 0.5:
            reasons.append("the selected option has a reasonable evaluation score")
        else:
            reasons.append("the selected option has a limited evaluation score")

        if tradeoff >= 0.5:
            reasons.append("it has a substantial advantage over alternatives")
        elif tradeoff >= 0.2:
            reasons.append("it has a meaningful advantage over alternatives")
        else:
            reasons.append("the leading options are closely matched")

        if confidence >= 0.75:
            reasons.append("overall decision confidence is high")
        elif confidence >= 0.5:
            reasons.append("overall decision confidence is moderate")
        else:
            reasons.append("overall decision confidence is low")

        if context_quality >= 0.75:
            reasons.append("the available decision context is strong")
        elif context_quality >= 0.5:
            reasons.append("the available decision context is adequate")
        else:
            reasons.append("the available decision context is limited")

        explanation = "The decision was selected because " + "; ".join(reasons) + "."

        result = {
            "goal": tradeoff_result["goal"],
            "preferred_option_id": tradeoff_result["preferred_option_id"],
            "confidence_level": confidence_result["confidence_level"],
            "tradeoff_type": tradeoff_result["tradeoff_type"],
            "context_quality": float(context_quality),
            "explanation": explanation,
            "reason_count": len(reasons),
        }
        return result if self.validate(result) else None

    def _valid_tradeoff(self, value):
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
        if value.get("tradeoff_type") not in ("none", "strong_preference", "moderate_preference", "close_choice"):
            return False
        return True

    def _valid_confidence(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        confidence = value.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            return False
        if not 0.0 <= float(confidence) <= 1.0:
            return False
        if value.get("confidence_level") not in ("high", "moderate", "low"):
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
        if result.get("confidence_level") not in ("high", "moderate", "low"):
            return False
        if result.get("tradeoff_type") not in ("none", "strong_preference", "moderate_preference", "close_choice"):
            return False
        if not isinstance(result.get("context_quality"), float) or not 0.0 <= result["context_quality"] <= 1.0:
            return False
        if not isinstance(result.get("explanation"), str) or not result["explanation"].strip():
            return False
        if not isinstance(result.get("reason_count"), int) or isinstance(result.get("reason_count"), bool) or result["reason_count"] <= 0:
            return False
        return True

decision_explanation = DecisionExplanation()
