class StrategicDecisionSelection:
    """Select and validate the final strategic decision."""

    def select(self, evaluation_result, tradeoff_result, confidence_result, explanation_result):
        if not self._valid_evaluation(evaluation_result):
            return None
        if not self._valid_tradeoff(tradeoff_result):
            return None
        if not self._valid_confidence(confidence_result):
            return None
        if not self._valid_explanation(explanation_result):
            return None

        goal = evaluation_result["goal"]
        option_id = evaluation_result["best_option_id"]

        if tradeoff_result["goal"] != goal or confidence_result["goal"] != goal or explanation_result["goal"] != goal:
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
            "selected_score": float(evaluation_result["best_score"]),
            "confidence": float(confidence_result["confidence"]),
            "confidence_level": confidence_result["confidence_level"],
            "tradeoff_type": tradeoff_result["tradeoff_type"],
            "explanation": explanation_result["explanation"],
            "decision_status": "selected",
        }
        return result if self.validate(result) else None

    def _valid_evaluation(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("best_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        score = value.get("best_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            return False
        if not 0.0 <= float(score) <= 1.0:
            return False
        return True

    def _valid_tradeoff(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
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

    def _valid_explanation(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("preferred_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if not isinstance(value.get("explanation"), str) or not value["explanation"].strip():
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        option_id = result.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if not isinstance(result.get("selected_score"), float) or not 0.0 <= result["selected_score"] <= 1.0:
            return False
        if not isinstance(result.get("confidence"), float) or not 0.0 <= result["confidence"] <= 1.0:
            return False
        if result.get("confidence_level") not in ("high", "moderate", "low"):
            return False
        if result.get("tradeoff_type") not in ("none", "strong_preference", "moderate_preference", "close_choice"):
            return False
        if not isinstance(result.get("explanation"), str) or not result["explanation"].strip():
            return False
        if result.get("decision_status") != "selected":
            return False
        return True

strategic_decision_selection = StrategicDecisionSelection()
