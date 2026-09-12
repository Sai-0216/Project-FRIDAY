class MetaLearningEvaluation:
    """Evaluate the reliability of generalized knowledge."""

    def evaluate(self, generalized_result):
        if not self._valid_input(generalized_result):
            return None

        pattern_count = generalized_result["pattern_count"]
        sample_size = generalized_result["sample_size"]
        lesson_type = generalized_result["generalized_lesson_type"]

        consistency = pattern_count / sample_size

        if consistency >= 0.75 and pattern_count >= 3:
            evaluation = "strong"
        elif consistency >= 0.5 and pattern_count >= 2:
            evaluation = "moderate"
        else:
            evaluation = "weak"

        if lesson_type == "observe":
            evaluation = "weak"

        result = {
            "evaluation": evaluation,
            "consistency": consistency,
            "pattern_count": pattern_count,
            "sample_size": sample_size,
            "lesson_type": lesson_type,
        }

        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if value.get("generalized_lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        if not isinstance(value.get("pattern_count"), int) or value["pattern_count"] <= 0:
            return False
        if not isinstance(value.get("sample_size"), int) or value["sample_size"] < 2:
            return False
        if value["pattern_count"] > value["sample_size"]:
            return False
        if not isinstance(value.get("generalized_insight"), str) or not value["generalized_insight"]:
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False

        required = (
            "evaluation",
            "consistency",
            "pattern_count",
            "sample_size",
            "lesson_type",
        )
        if any(key not in result for key in required):
            return False

        return (
            result["evaluation"] in ("strong", "moderate", "weak")
            and isinstance(result["consistency"], float)
            and 0.0 <= result["consistency"] <= 1.0
            and isinstance(result["pattern_count"], int)
            and result["pattern_count"] > 0
            and isinstance(result["sample_size"], int)
            and result["sample_size"] >= 2
            and result["pattern_count"] <= result["sample_size"]
            and result["lesson_type"] in ("reinforce", "warning", "improve", "observe")
        )


meta_learning_evaluation = MetaLearningEvaluation()
