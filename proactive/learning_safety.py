class LearningSafety:

    SAFE = "SAFE"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"

    @classmethod
    def classify(cls, learning):
        if not isinstance(learning, dict):
            return cls.BLOCKED
        forbidden = {
            "autonomy_level",
            "execution_permissions",
            "trusted_actions",
            "authorization",
        }
        if any(key in learning for key in forbidden):
            return cls.BLOCKED
        if "confidence" in learning and learning.get("confidence") not in {"HIGH", "MEDIUM", "LOW"}:
            return cls.REVIEW
        return cls.SAFE

    @classmethod
    def validate_autonomy_boundary(cls, learning):
        if not isinstance(learning, dict):
            return False
        forbidden = {
            "autonomy_level",
            "execution_permissions",
            "trusted_actions",
            "authorization",
        }
        return not any(key in learning for key in forbidden)

    @classmethod
    def reject_unsafe(cls, learning):
        return cls.classify(learning) == cls.BLOCKED

    @classmethod
    def approve_safe(cls, learning):
        return cls.classify(learning) == cls.SAFE

    @classmethod
    def enforce(cls, learning):
        classification = cls.classify(learning)
        if classification == cls.SAFE:
            return {"status": cls.SAFE, "allowed": True}
        if classification == cls.REVIEW:
            return {"status": cls.REVIEW, "allowed": False}
        return {"status": cls.BLOCKED, "allowed": False}
