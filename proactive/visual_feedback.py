class VisualFeedback:
    TYPES = ("SUCCESS", "FAILURE", "CHANGED", "UNCHANGED")

    def __init__(self):
        self.name = "visual_feedback"

    def observe(self, before, after):
        before = before if isinstance(before, dict) else {}
        after = after if isinstance(after, dict) else {}
        changed = before != after
        status = "CHANGED" if changed else "UNCHANGED"
        return {
            "before": before,
            "after": after,
            "changed": changed,
            "status": status,
        }

    def assess(self, feedback, expected_change=True):
        feedback = feedback if isinstance(feedback, dict) else {}
        changed = bool(feedback.get("changed", False))
        success = changed == bool(expected_change)
        return {
            "success": success,
            "status": "SUCCESS" if success else "FAILURE",
            "expected_change": bool(expected_change),
            "observed_change": changed,
        }

    def create(self, action, before, after, expected_change=True):
        feedback = self.observe(before, after)
        assessment = self.assess(feedback, expected_change)
        return {
            "action": action if isinstance(action, dict) else {},
            "feedback": feedback,
            "assessment": assessment,
            "valid": True,
        }

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("action"), dict):
            return False
        if not isinstance(result.get("feedback"), dict):
            return False
        if not isinstance(result.get("assessment"), dict):
            return False
        return bool(result.get("valid", False))


visual_feedback = VisualFeedback()
