class KnowledgeRetention:
    """Retain validated consolidated lessons for future use."""

    RETENTION_STATES = ("retain", "review", "observe")
    LESSON_TYPES = ("reinforce", "warning", "improve", "observe")

    def retain(self, lesson):
        if not self._valid_input(lesson):
            return None

        lesson_type = lesson["lesson_type"]
        if lesson_type in ("reinforce", "warning", "improve"):
            retention_state = "retain"
        else:
            retention_state = "observe"

        result = {
            "sample_size": lesson["sample_size"],
            "outcome_states": list(lesson["outcome_states"]),
            "lesson_type": lesson_type,
            "lesson": lesson["lesson"],
            "retention_state": retention_state,
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("sample_size"), int) or value["sample_size"] <= 0:
            return False
        if not isinstance(value.get("outcome_states"), list) or not value["outcome_states"]:
            return False
        if any(state not in ("success", "failure", "partial", "unknown") for state in value["outcome_states"]):
            return False
        if value.get("lesson_type") not in self.LESSON_TYPES:
            return False
        return isinstance(value.get("lesson"), str) and bool(value["lesson"])

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = (
            "sample_size", "outcome_states", "lesson_type",
            "lesson", "retention_state"
        )
        if any(key not in result for key in required):
            return False
        return (
            isinstance(result["sample_size"], int)
            and result["sample_size"] > 0
            and isinstance(result["outcome_states"], list)
            and bool(result["outcome_states"])
            and all(state in ("success", "failure", "partial", "unknown") for state in result["outcome_states"])
            and result["lesson_type"] in self.LESSON_TYPES
            and isinstance(result["lesson"], str)
            and bool(result["lesson"])
            and result["retention_state"] in self.RETENTION_STATES
        )


knowledge_retention = KnowledgeRetention()
