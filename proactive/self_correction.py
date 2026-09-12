class SelfCorrection:
    STATES = ("on_track", "needs_correction", "corrected", "blocked")

    def __init__(self):
        self.name = "self_correction"

    def assess(self, expected_progress, actual_progress):
        try:
            expected = float(expected_progress)
            actual = float(actual_progress)
        except (TypeError, ValueError):
            return None
        gap = expected - actual
        needs_correction = gap > 0.1
        return {
            "expected_progress": expected,
            "actual_progress": actual,
            "gap": gap,
            "needs_correction": needs_correction,
            "state": "needs_correction" if needs_correction else "on_track",
        }

    def create_correction(self, assessment, correction):
        if not isinstance(assessment, dict) or not assessment.get("needs_correction"):
            return None
        if not isinstance(correction, str) or not correction.strip():
            return None
        return {
            "reason": "progress_below_expectation",
            "correction": correction.strip(),
            "state": "corrected",
        }

    def apply(self, plan, correction):
        if not isinstance(plan, dict) or not isinstance(correction, dict):
            return False
        plan["correction"] = correction.get("correction")
        plan["correction_state"] = correction.get("state", "corrected")
        return True

    def validate_assessment(self, assessment):
        if not isinstance(assessment, dict):
            return False
        required = ("expected_progress", "actual_progress", "gap", "needs_correction", "state")
        if any(key not in assessment for key in required):
            return False
        return assessment.get("state") in ("on_track", "needs_correction")

    def validate_correction(self, correction):
        if not isinstance(correction, dict):
            return False
        if not isinstance(correction.get("correction"), str) or not correction["correction"]:
            return False
        return correction.get("state") == "corrected"


self_correction = SelfCorrection()
