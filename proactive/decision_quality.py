class DecisionQuality:

    GOOD="GOOD"
    FAIR="FAIR"
    POOR="POOR"
    UNKNOWN="UNKNOWN"

    def __init__(self, action=None, expected=None, actual=None, score=0.0):
        self.action=action if isinstance(action,str) else None
        self.expected=expected if isinstance(expected,str) else None
        self.actual=actual if isinstance(actual,str) else None
        self.score=self._clamp(score)

    @classmethod
    def create(cls, action=None, expected=None, actual=None, score=0.0):
        if action is not None and not isinstance(action,str):
            return None
        if expected is not None and not isinstance(expected,str):
            return None
        if actual is not None and not isinstance(actual,str):
            return None
        if not isinstance(score,(int,float)) or isinstance(score,bool):
            return None
        if score < 0.0 or score > 1.0:
            return None
        return cls(action,expected,actual,score)

    @staticmethod
    def _clamp(value):
        if not isinstance(value,(int,float)) or isinstance(value,bool):
            return 0.0
        return max(0.0,min(1.0,float(value)))

    def level(self):
        if self.score >= 0.80:
            return self.GOOD
        if self.score >= 0.50:
            return self.FAIR
        if self.score > 0.0:
            return self.POOR
        return self.UNKNOWN

    def to_dict(self):
        return {
            "action":self.action,
            "expected":self.expected,
            "actual":self.actual,
            "score":self.score,
            "level":self.level(),
        }

    @staticmethod
    def outcome_score(expected, actual):
        if not isinstance(expected,str) or not isinstance(actual,str):
            return 0.0
        expected=expected.strip().lower()
        actual=actual.strip().lower()
        if not expected or not actual:
            return 0.0
        return 1.0 if expected == actual else 0.2

    @classmethod
    def from_outcome(cls, action, expected, actual):
        score=cls.outcome_score(expected,actual)
        return cls.create(action,expected,actual,score)

    def explanation(self):
        level=self.level()
        if level == self.GOOD:
            return "Expected and actual outcomes matched."
        if level == self.FAIR:
            return "Decision produced a partially satisfactory outcome."
        if level == self.POOR:
            return "Expected and actual outcomes did not align."
        return "Outcome information is insufficient."

    def factor_scores(self):
        outcome_available=1.0 if isinstance(self.expected,str) and isinstance(self.actual,str) and self.expected.strip() and self.actual.strip() else 0.0
        action_valid=1.0 if isinstance(self.action,str) and self.action.strip() else 0.0
        outcome_match=self.outcome_score(self.expected,self.actual)
        return {"outcome_match":outcome_match,"action_validity":action_valid,"outcome_availability":outcome_available}

    def weak_factors(self, threshold=0.50):
        if not isinstance(threshold,(int,float)) or isinstance(threshold,bool):
            return []
        if threshold < 0.0 or threshold > 1.0:
            return []
        return [name for name,score in self.factor_scores().items() if score < threshold]

    def assessment(self, threshold=0.50):
        result=self.to_dict()
        result["explanation"]=self.explanation()
        result["factor_scores"]=self.factor_scores()
        result["weak_factors"]=self.weak_factors(threshold)
        return result
