class ContextualDecisionAnalysis:
    """Analyze the context surrounding a potential decision."""

    def analyze(self, context):
        if not self._valid_input(context):
            return None

        result = {
            "goal": context["goal"],
            "constraints": list(context["constraints"]),
            "available_options": list(context["available_options"]),
            "priority": context["priority"],
            "uncertainty": context["uncertainty"],
            "context_quality": self._context_quality(context),
        }

        return result if self.validate(result) else None

    def _context_quality(self, context):
        score = 0.0
        score += 0.25
        if context["constraints"]:
            score += 0.25
        if context["available_options"]:
            score += 0.25
        if context["uncertainty"] <= 0.5:
            score += 0.25
        return score

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        if not isinstance(value.get("constraints"), list):
            return False
        if not isinstance(value.get("available_options"), list) or not value["available_options"]:
            return False
        if value.get("priority") not in ("low", "medium", "high", "critical"):
            return False
        if not isinstance(value.get("uncertainty"), (int, float)):
            return False
        if not 0.0 <= value["uncertainty"] <= 1.0:
            return False
        return all(isinstance(item, str) and item.strip() for item in value["constraints"] + value["available_options"])

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = (
            "goal",
            "constraints",
            "available_options",
            "priority",
            "uncertainty",
            "context_quality",
        )
        if any(key not in result for key in required):
            return False
        return (
            isinstance(result["goal"], str)
            and bool(result["goal"].strip())
            and isinstance(result["constraints"], list)
            and isinstance(result["available_options"], list)
            and bool(result["available_options"])
            and result["priority"] in ("low", "medium", "high", "critical")
            and isinstance(result["uncertainty"], (int, float))
            and 0.0 <= result["uncertainty"] <= 1.0
            and isinstance(result["context_quality"], float)
            and 0.0 <= result["context_quality"] <= 1.0
        )


contextual_decision_analysis = ContextualDecisionAnalysis()
