class StrategicDecisionIntegration:
    """Integrate the complete Phase 29 strategic decision pipeline."""

    def integrate(self, analysis_result, options_result, evaluation_result, tradeoff_result, confidence_result, explanation_result, selection_result):
        if not self._valid_analysis(analysis_result):
            return None
        if not self._valid_options(options_result):
            return None
        if not self._valid_evaluation(evaluation_result):
            return None
        if not self._valid_tradeoff(tradeoff_result):
            return None
        if not self._valid_confidence(confidence_result):
            return None
        if not self._valid_explanation(explanation_result):
            return None
        if not self._valid_selection(selection_result):
            return None

        goal = analysis_result["goal"]
        option_id = selection_result["selected_option_id"]

        sources = [options_result, evaluation_result, tradeoff_result, confidence_result, explanation_result, selection_result]
        if any(item.get("goal") != goal for item in sources):
            return None

        if evaluation_result["best_option_id"] != option_id:
            return None
        if tradeoff_result["preferred_option_id"] != option_id:
            return None
        if confidence_result["preferred_option_id"] != option_id:
            return None
        if explanation_result["preferred_option_id"] != option_id:
            return None

        result = {
            "goal": goal,
            "selected_option_id": option_id,
            "selected_score": float(selection_result["selected_score"]),
            "confidence": float(selection_result["confidence"]),
            "confidence_level": selection_result["confidence_level"],
            "tradeoff_type": selection_result["tradeoff_type"],
            "explanation": selection_result["explanation"],
            "decision_status": selection_result["decision_status"],
            "context_quality": float(analysis_result["context_quality"]),
            "option_count": int(options_result["option_count"]),
            "integration_status": "complete",
        }
        return result if self.validate(result) else None

    def _valid_analysis(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        quality = value.get("context_quality")
        return isinstance(quality, (int, float)) and not isinstance(quality, bool) and 0.0 <= float(quality) <= 1.0

    def _valid_options(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        if not isinstance(value.get("option_count"), int) or isinstance(value.get("option_count"), bool) or value["option_count"] <= 0:
            return False
        return True

    def _valid_evaluation(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("best_option_id")
        score = value.get("best_score")
        return (isinstance(option_id, int) and not isinstance(option_id, bool) and option_id > 0 and isinstance(score, (int, float)) and not isinstance(score, bool) and 0.0 <= float(score) <= 1.0)

    def _valid_tradeoff(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        return isinstance(option_id, int) and not isinstance(option_id, bool) and option_id > 0 and value.get("tradeoff_type") in ("none", "strong_preference", "moderate_preference", "close_choice")

    def _valid_confidence(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        confidence = value.get("confidence")
        return (isinstance(option_id, int) and not isinstance(option_id, bool) and option_id > 0 and isinstance(confidence, (int, float)) and not isinstance(confidence, bool) and 0.0 <= float(confidence) <= 1.0 and value.get("confidence_level") in ("high", "moderate", "low"))

    def _valid_explanation(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        return isinstance(option_id, int) and not isinstance(option_id, bool) and option_id > 0 and isinstance(value.get("explanation"), str) and bool(value["explanation"].strip())

    def _valid_selection(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("selected_option_id")
        return isinstance(option_id, int) and not isinstance(option_id, bool) and option_id > 0 and value.get("decision_status") == "selected"

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        option_id = result.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        for key in ("selected_score", "confidence", "context_quality"):
            if not isinstance(result.get(key), float) or not 0.0 <= result[key] <= 1.0:
                return False
        if result.get("confidence_level") not in ("high", "moderate", "low"):
            return False
        if result.get("tradeoff_type") not in ("none", "strong_preference", "moderate_preference", "close_choice"):
            return False
        if not isinstance(result.get("explanation"), str) or not result["explanation"].strip():
            return False
        if result.get("decision_status") != "selected":
            return False
        if not isinstance(result.get("option_count"), int) or isinstance(result.get("option_count"), bool) or result["option_count"] <= 0:
            return False
        if result.get("integration_status") != "complete":
            return False
        return True

strategic_decision_integration = StrategicDecisionIntegration()
