class KnowledgeExtraction:
    """Extract reusable knowledge from adaptive learning results."""

    KNOWLEDGE_TYPES = ("success_pattern", "failure_pattern", "partial_pattern", "insufficient_evidence")

    def extract(self, learning_result):
        if not self._valid_input(learning_result):
            return None

        state = learning_result["outcome_state"]
        if state == "success":
            knowledge_type = "success_pattern"
            insight = "successful behavior should be retained as reusable knowledge"
        elif state == "failure":
            knowledge_type = "failure_pattern"
            insight = "failed behavior should be retained as a warning for future decisions"
        elif state == "partial":
            knowledge_type = "partial_pattern"
            insight = "partial behavior should be retained with its identified improvement opportunity"
        else:
            knowledge_type = "insufficient_evidence"
            insight = "insufficient evidence is available for reliable knowledge extraction"

        result = {
            "action_id": learning_result["action_id"],
            "action": learning_result["action"],
            "outcome_state": state,
            "learning_state": learning_result["learning_state"],
            "adaptation": learning_result["adaptation"],
            "adjustment": learning_result["adjustment"],
            "knowledge_type": knowledge_type,
            "insight": insight,
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        return (
            isinstance(value, dict)
            and isinstance(value.get("action_id"), int)
            and isinstance(value.get("action"), str)
            and bool(value.get("action"))
            and value.get("outcome_state") in ("success", "failure", "partial", "unknown")
            and value.get("learning_state") in ("reinforce", "correct", "observe")
            and value.get("adaptation") in ("strengthen", "modify", "observe")
            and value.get("adjustment") in ("reinforce", "adjust", "retain")
        )

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        required = (
            "action_id", "action", "outcome_state", "learning_state",
            "adaptation", "adjustment", "knowledge_type", "insight"
        )
        if any(key not in result for key in required):
            return False
        return (
            isinstance(result["action_id"], int)
            and isinstance(result["action"], str)
            and bool(result["action"])
            and result["outcome_state"] in ("success", "failure", "partial", "unknown")
            and result["learning_state"] in ("reinforce", "correct", "observe")
            and result["adaptation"] in ("strengthen", "modify", "observe")
            and result["adjustment"] in ("reinforce", "adjust", "retain")
            and result["knowledge_type"] in self.KNOWLEDGE_TYPES
            and isinstance(result["insight"], str)
            and bool(result["insight"])
        )


knowledge_extraction = KnowledgeExtraction()
