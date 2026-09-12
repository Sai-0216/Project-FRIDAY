class MetaLearningIntegration:
    """Integrate the complete meta-learning pipeline into one validated result."""

    def integrate(self, retrieval_result, generalized_result, evaluation_result, guidance_result):
        if not self._valid_inputs(retrieval_result, generalized_result, evaluation_result, guidance_result):
            return None

        result = {
            "retrieved_lesson": retrieval_result["lesson"],
            "retrieved_lesson_type": retrieval_result["lesson_type"],
            "generalized_lesson_type": generalized_result["generalized_lesson_type"],
            "generalized_insight": generalized_result["generalized_insight"],
            "evaluation": evaluation_result["evaluation"],
            "consistency": evaluation_result["consistency"],
            "guidance": guidance_result["guidance"],
            "reason": guidance_result["reason"],
            "sample_size": generalized_result["sample_size"],
        }

        return result if self.validate(result) else None

    def _valid_inputs(self, retrieval, generalized, evaluation, guidance):
        if not isinstance(retrieval, dict):
            return False
        if not isinstance(generalized, dict):
            return False
        if not isinstance(evaluation, dict):
            return False
        if not isinstance(guidance, dict):
            return False

        if retrieval.get("lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        if not isinstance(retrieval.get("lesson"), str) or not retrieval["lesson"]:
            return False
        if generalized.get("generalized_lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        if not isinstance(generalized.get("generalized_insight"), str) or not generalized["generalized_insight"]:
            return False
        if evaluation.get("evaluation") not in ("strong", "moderate", "weak"):
            return False
        if not isinstance(evaluation.get("consistency"), (int, float)):
            return False
        if not 0.0 <= evaluation["consistency"] <= 1.0:
            return False
        if guidance.get("guidance") not in ("reinforce", "avoid", "improve", "consider", "observe"):
            return False
        if not isinstance(guidance.get("reason"), str) or not guidance["reason"]:
            return False
        if not isinstance(generalized.get("sample_size"), int) or generalized["sample_size"] < 2:
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False

        required = (
            "retrieved_lesson",
            "retrieved_lesson_type",
            "generalized_lesson_type",
            "generalized_insight",
            "evaluation",
            "consistency",
            "guidance",
            "reason",
            "sample_size",
        )
        if any(key not in result for key in required):
            return False

        return (
            isinstance(result["retrieved_lesson"], str)
            and bool(result["retrieved_lesson"])
            and result["retrieved_lesson_type"] in ("reinforce", "warning", "improve", "observe")
            and result["generalized_lesson_type"] in ("reinforce", "warning", "improve", "observe")
            and isinstance(result["generalized_insight"], str)
            and bool(result["generalized_insight"])
            and result["evaluation"] in ("strong", "moderate", "weak")
            and isinstance(result["consistency"], (int, float))
            and 0.0 <= result["consistency"] <= 1.0
            and result["guidance"] in ("reinforce", "avoid", "improve", "consider", "observe")
            and isinstance(result["reason"], str)
            and bool(result["reason"])
            and isinstance(result["sample_size"], int)
            and result["sample_size"] >= 2
        )


meta_learning_integration = MetaLearningIntegration()
