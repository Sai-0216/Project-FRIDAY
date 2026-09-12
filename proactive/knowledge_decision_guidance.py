class KnowledgeDecisionGuidance:
    """Convert evaluated knowledge into guidance for future decisions."""

    def guide(self, evaluation_result):
        if not self._valid_input(evaluation_result):
            return None

        evaluation = evaluation_result["evaluation"]
        lesson_type = evaluation_result["lesson_type"]

        if evaluation == "strong":
            if lesson_type == "reinforce":
                guidance = "reinforce"
                reason = "strong evidence supports repeating successful patterns"
            elif lesson_type == "warning":
                guidance = "avoid"
                reason = "strong evidence indicates repeated failure patterns should be avoided"
            elif lesson_type == "improve":
                guidance = "improve"
                reason = "strong evidence indicates targeted improvement is needed"
            else:
                guidance = "observe"
                reason = "strong evidence is unavailable for an observe-only pattern"
        elif evaluation == "moderate":
            guidance = "consider"
            reason = "moderate evidence should inform decisions without being treated as conclusive"
        else:
            guidance = "observe"
            reason = "weak evidence should be observed before influencing decisions strongly"

        result = {
            "guidance": guidance,
            "reason": reason,
            "evaluation": evaluation,
            "lesson_type": lesson_type,
            "consistency": evaluation_result["consistency"],
        }

        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if value.get("evaluation") not in ("strong", "moderate", "weak"):
            return False
        if value.get("lesson_type") not in ("reinforce", "warning", "improve", "observe"):
            return False
        if not isinstance(value.get("consistency"), (int, float)):
            return False
        if not 0.0 <= value["consistency"] <= 1.0:
            return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False

        required = (
            "guidance",
            "reason",
            "evaluation",
            "lesson_type",
            "consistency",
        )
        if any(key not in result for key in required):
            return False

        return (
            result["guidance"] in ("reinforce", "avoid", "improve", "consider", "observe")
            and isinstance(result["reason"], str)
            and bool(result["reason"])
            and result["evaluation"] in ("strong", "moderate", "weak")
            and result["lesson_type"] in ("reinforce", "warning", "improve", "observe")
            and isinstance(result["consistency"], (int, float))
            and 0.0 <= result["consistency"] <= 1.0
        )


knowledge_decision_guidance = KnowledgeDecisionGuidance()
