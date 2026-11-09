class MetaReasoning:

    HIGH="HIGH"
    MEDIUM="MEDIUM"
    LOW="LOW"
    UNKNOWN="UNKNOWN"

    def __init__(self, reasoning=None, assessment=None, quality=None, improvement=None):
        self.reasoning = reasoning if isinstance(reasoning, dict) else {}
        self.assessment = assessment if isinstance(assessment, dict) else {}
        self.quality = quality if isinstance(quality, dict) else {}
        self.improvement = improvement if isinstance(improvement, dict) else {}

    def to_dict(self):
        return {
            "reasoning": self.reasoning,
            "assessment": self.assessment,
            "quality": self.quality,
            "improvement": self.improvement,
        }

    @classmethod
    def create(cls, reasoning=None, assessment=None, quality=None, improvement=None):
        if reasoning is not None and not isinstance(reasoning, dict):
            return None
        if assessment is not None and not isinstance(assessment, dict):
            return None
        if quality is not None and not isinstance(quality, dict):
            return None
        if improvement is not None and not isinstance(improvement, dict):
            return None
        return cls(reasoning, assessment, quality, improvement)

    @classmethod
    def from_reasoning(cls, reasoning):
        if not isinstance(reasoning, dict):
            return None
        return cls(reasoning=reasoning)

    def is_valid(self):
        return bool(self.reasoning or self.assessment or self.quality or self.improvement)

    @staticmethod
    def validate_assessment(assessment):
        if not isinstance(assessment, dict):
            return False
        allowed={"status","quality","improvement","reason"}
        return all(key in allowed for key in assessment.keys())

    @staticmethod
    def validate_quality(quality):
        if not isinstance(quality, dict):
            return False
        score=quality.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            return False
        if score < 0.0 or score > 1.0:
            return False
        level=quality.get("level")
        if level is not None and level not in {MetaReasoning.HIGH, MetaReasoning.MEDIUM, MetaReasoning.LOW, MetaReasoning.UNKNOWN}:
            return False
        return True

    @staticmethod
    def quality_level(score):
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            return MetaReasoning.UNKNOWN
        if score < 0.0 or score > 1.0:
            return MetaReasoning.UNKNOWN
        if score >= 0.80:
            return MetaReasoning.HIGH
        if score >= 0.50:
            return MetaReasoning.MEDIUM
        return MetaReasoning.LOW

    @classmethod
    def create_quality(cls, score):
        level=cls.quality_level(score)
        if level == cls.UNKNOWN:
            return None
        return {"score": float(score), "level": level}

    @classmethod
    def create_assessment(cls, score, status="ASSESSED", reason=None, improvement=None):
        quality=cls.create_quality(score)
        if quality is None:
            return None
        assessment={"status": status, "quality": quality}
        if reason is not None:
            assessment["reason"] = str(reason)
        if improvement is not None:
            assessment["improvement"] = improvement if isinstance(improvement, dict) else {"needed": bool(improvement)}
        if not cls.validate_assessment(assessment):
            return None
        return assessment

    @classmethod
    def build(cls, reasoning, score, reason=None, improvement=None):
        if not isinstance(reasoning, dict):
            return None
        assessment=cls.create_assessment(score, reason=reason, improvement=improvement)
        if assessment is None:
            return None
        quality=assessment.get("quality", {})
        return cls(reasoning=reasoning, assessment=assessment, quality=quality, improvement=improvement if isinstance(improvement, dict) else {})
