class LessonConsolidation:
    """Consolidate extracted knowledge into reusable lessons."""

    LESSON_TYPES = ("reinforce", "warning", "improve", "observe")

    def consolidate(self, knowledge_items):
        if not self._valid_input(knowledge_items):
            return None

        states = [item["outcome_state"] for item in knowledge_items]
        if "failure" in states:
            lesson_type = "warning"
            lesson = "repeated failure patterns should guide future decisions away from unsuccessful behavior"
        elif "partial" in states:
            lesson_type = "improve"
            lesson = "partial success patterns should guide targeted improvements in future behavior"
        elif "success" in states:
            lesson_type = "reinforce"
            lesson = "successful patterns should be reinforced and reused in future decisions"
        else:
            lesson_type = "observe"
            lesson = "insufficient evidence should be observed before forming a reusable lesson"

        result = {
            "sample_size": len(knowledge_items),
            "outcome_states": states,
            "lesson_type": lesson_type,
            "lesson": lesson,
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, list) or not value:
            return False
        for item in value:
            if not isinstance(item, dict):
                return False
            if item.get("outcome_state") not in ("success", "failure", "partial", "unknown"):
                return False
            if item.get("knowledge_type") not in ("success_pattern", "failure_pattern", "partial_pattern", "insufficient_evidence"):
                return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("sample_size"), int) or result["sample_size"] <= 0:
            return False
        if not isinstance(result.get("outcome_states"), list) or not result["outcome_states"]:
            return False
        if any(state not in ("success", "failure", "partial", "unknown") for state in result["outcome_states"]):
            return False
        return (
            result.get("lesson_type") in self.LESSON_TYPES
            and isinstance(result.get("lesson"), str)
            and bool(result["lesson"])
        )


lesson_consolidation = LessonConsolidation()
