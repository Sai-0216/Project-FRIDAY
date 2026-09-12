class OptionEvaluation:
    """Evaluate generated decision options using guidance and decision context."""

    def evaluate(self, option_result, context_result):
        if not self._valid_inputs(option_result, context_result):
            return None

        evaluated = []
        uncertainty = context_result["uncertainty"]
        priority = context_result["priority"]

        for item in option_result["options"]:
            recommendation = item["recommendation"]

            if recommendation == "preferred":
                score = 1.0
            elif recommendation == "consider":
                score = 0.7
            elif recommendation == "observe":
                score = 0.5
            else:
                score = 0.2

            score -= uncertainty * 0.2

            if priority == "critical":
                score -= 0.05
            elif priority == "high":
                score -= 0.02

            score = max(0.0, min(1.0, round(score, 3)))

            evaluated.append({
                "option_id": item["option_id"],
                "option": item["option"],
                "recommendation": recommendation,
                "score": score,
            })

        best = max(evaluated, key=lambda item: item["score"])

        result = {
            "goal": option_result["goal"],
            "evaluated_options": evaluated,
            "best_option_id": best["option_id"],
            "best_score": best["score"],
            "option_count": len(evaluated),
        }

        return result if self.validate(result) else None

    def _valid_inputs(self, option_result, context_result):
        if not isinstance(option_result, dict) or not isinstance(context_result, dict):
            return False
        if not isinstance(option_result.get("goal"), str) or not option_result["goal"].strip():
            return False
        if not isinstance(option_result.get("options"), list) or not option_result["options"]:
            return False
        if not isinstance(context_result.get("uncertainty"), (int, float)):
            return False
        if not 0.0 <= context_result["uncertainty"] <= 1.0:
            return False
        if context_result.get("priority") not in ("low", "medium", "high", "critical"):
            return False

        for item in option_result["options"]:
            if not isinstance(item, dict):
                return False
            if not isinstance(item.get("option_id"), int) or item["option_id"] <= 0:
                return False
            if not isinstance(item.get("option"), str) or not item["option"].strip():
                return False
            if item.get("recommendation") not in ("preferred", "avoid", "consider", "observe"):
                return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        options = result.get("evaluated_options")
        if not isinstance(options, list) or not options:
            return False
        if not isinstance(result.get("best_option_id"), int) or result["best_option_id"] <= 0:
            return False
        if not isinstance(result.get("best_score"), float) or not 0.0 <= result["best_score"] <= 1.0:
            return False
        if not isinstance(result.get("option_count"), int) or result["option_count"] != len(options):
            return False

        for item in options:
            if not isinstance(item, dict):
                return False
            if not isinstance(item.get("option_id"), int) or item["option_id"] <= 0:
                return False
            if not isinstance(item.get("option"), str) or not item["option"].strip():
                return False
            if item.get("recommendation") not in ("preferred", "avoid", "consider", "observe"):
                return False
            if not isinstance(item.get("score"), float) or not 0.0 <= item["score"] <= 1.0:
                return False

        ids = [item["option_id"] for item in options]
        if result["best_option_id"] not in ids:
            return False
        best_scores = [item["score"] for item in options if item["option_id"] == result["best_option_id"]]
        return bool(best_scores) and result["best_score"] == best_scores[0]


option_evaluation = OptionEvaluation()
