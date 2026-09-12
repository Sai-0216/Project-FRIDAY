class CrossExperienceGeneralization:
    """Generalize recurring patterns across multiple retained experiences."""

    def generalize(self, knowledge_records):
        if not self._valid_input(knowledge_records):
            return None

        lesson_types = [record["lesson_type"] for record in knowledge_records]
        outcome_states = []
        for record in knowledge_records:
            outcome_states.extend(record["outcome_states"])

        counts = {}
        for lesson_type in lesson_types:
            counts[lesson_type] = counts.get(lesson_type, 0) + 1

        dominant_type = max(counts, key=counts.get)
        pattern_count = counts[dominant_type]

        if dominant_type == "reinforce":
            insight = "repeated successful patterns should be reinforced across future experiences"
        elif dominant_type == "warning":
            insight = "repeated failure patterns should guide future decisions away from unsuccessful behavior"
        elif dominant_type == "improve":
            insight = "repeated partial outcomes indicate an opportunity for targeted improvement"
        else:
            insight = "insufficiently consistent experience patterns should be observed before stronger conclusions"

        result = {
            "generalized_lesson_type": dominant_type,
            "generalized_insight": insight,
            "pattern_count": pattern_count,
            "sample_size": len(knowledge_records),
            "outcome_states": outcome_states,
        }

        return result if self.validate(result) else None

    def _valid_input(self, records):
        if not isinstance(records, list) or len(records) < 2:
            return False

        for record in records:
            if not isinstance(record, dict):
                return False
            if record.get("lesson_type") not in ("reinforce", "warning", "improve", "observe"):
                return False
            if record.get("retention_state") not in ("retain", "review", "observe"):
                return False
            if record.get("retention_state") != "retain":
                return False
            if not isinstance(record.get("lesson"), str) or not record["lesson"]:
                return False
            if not isinstance(record.get("sample_size"), int) or record["sample_size"] <= 0:
                return False
            if not isinstance(record.get("outcome_states"), list) or not record["outcome_states"]:
                return False

        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False

        required = (
            "generalized_lesson_type",
            "generalized_insight",
            "pattern_count",
            "sample_size",
            "outcome_states",
        )
        if any(key not in result for key in required):
            return False

        return (
            result["generalized_lesson_type"] in ("reinforce", "warning", "improve", "observe")
            and isinstance(result["generalized_insight"], str)
            and bool(result["generalized_insight"])
            and isinstance(result["pattern_count"], int)
            and result["pattern_count"] > 0
            and isinstance(result["sample_size"], int)
            and result["sample_size"] >= 2
            and isinstance(result["outcome_states"], list)
            and bool(result["outcome_states"])
        )


cross_experience_generalization = CrossExperienceGeneralization()
