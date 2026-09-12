class StrategicTradeoffAnalysis:
    """Analyze trade-offs between evaluated decision options."""

    def analyze(self, evaluation_result):
        if not self._valid_input(evaluation_result):
            return None
        options = evaluation_result["evaluated_options"]
        ranked = sorted(options, key=lambda item: float(item["score"]), reverse=True)
        best = ranked[0]
        alternatives = ranked[1:]
        preferred_score = float(best["score"])
        if not alternatives:
            tradeoff_type = "none"
            tradeoff_score = 0.0
            insight = "no competing option is available for trade-off analysis"
        else:
            second = alternatives[0]
            tradeoff_score = round(max(0.0, preferred_score - float(second["score"])), 3)
            if tradeoff_score >= 0.5:
                tradeoff_type = "strong_preference"
                insight = "the leading option has a substantial advantage over alternatives"
            elif tradeoff_score >= 0.2:
                tradeoff_type = "moderate_preference"
                insight = "the leading option has a meaningful advantage over alternatives"
            else:
                tradeoff_type = "close_choice"
                insight = "the leading options are closely matched and require careful consideration"
        result = {
            "goal": evaluation_result["goal"],
            "preferred_option_id": best["option_id"],
            "preferred_score": preferred_score,
            "tradeoff_type": tradeoff_type,
            "tradeoff_score": float(tradeoff_score),
            "insight": insight,
            "option_count": len(options),
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        options = value.get("evaluated_options")
        if not isinstance(options, list) or not options:
            return False
        for item in options:
            if not isinstance(item, dict):
                return False
            if not isinstance(item.get("option_id"), int) or isinstance(item.get("option_id"), bool) or item["option_id"] <= 0:
                return False
            if not isinstance(item.get("option"), str) or not item["option"].strip():
                return False
            if not isinstance(item.get("score"), (int, float)) or isinstance(item.get("score"), bool):
                return False
            if not 0.0 <= float(item["score"]) <= 1.0:
                return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        if not isinstance(result.get("preferred_option_id"), int) or isinstance(result.get("preferred_option_id"), bool) or result["preferred_option_id"] <= 0:
            return False
        if not isinstance(result.get("preferred_score"), float) or not 0.0 <= result["preferred_score"] <= 1.0:
            return False
        if result.get("tradeoff_type") not in ("none", "strong_preference", "moderate_preference", "close_choice"):
            return False
        if not isinstance(result.get("tradeoff_score"), float) or not 0.0 <= result["tradeoff_score"] <= 1.0:
            return False
        if not isinstance(result.get("insight"), str) or not result["insight"].strip():
            return False
        if not isinstance(result.get("option_count"), int) or isinstance(result.get("option_count"), bool) or result["option_count"] <= 0:
            return False
        return True

strategic_tradeoff_analysis = StrategicTradeoffAnalysis()
