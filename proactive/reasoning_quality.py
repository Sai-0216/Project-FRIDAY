class ReasoningQuality:

    MIN_SCORE=0.0
    MAX_SCORE=1.0

    FACTORS=("completeness","consistency","outcome_alignment","safety")

    def __init__(self, completeness=0.0, consistency=0.0, outcome_alignment=0.0, safety=0.0):
        self.completeness=self._clamp(completeness)
        self.consistency=self._clamp(consistency)
        self.outcome_alignment=self._clamp(outcome_alignment)
        self.safety=self._clamp(safety)

    @classmethod
    def create(cls, completeness=0.0, consistency=0.0, outcome_alignment=0.0, safety=0.0):
        values=[completeness,consistency,outcome_alignment,safety]
        if any(not isinstance(value,(int,float)) or isinstance(value,bool) for value in values):
            return None
        if any(value < cls.MIN_SCORE or value > cls.MAX_SCORE for value in values):
            return None
        return cls(completeness,consistency,outcome_alignment,safety)

    @staticmethod
    def _clamp(value):
        if not isinstance(value,(int,float)) or isinstance(value,bool):
            return 0.0
        return max(0.0,min(1.0,float(value)))

    def score(self):
        return round((self.completeness+self.consistency+self.outcome_alignment+self.safety)/4.0,4)

    def level(self):
        score=self.score()
        if score >= 0.80:
            return "HIGH"
        if score >= 0.50:
            return "MEDIUM"
        return "LOW"

    def to_dict(self):
        return {
            "completeness":self.completeness,
            "consistency":self.consistency,
            "outcome_alignment":self.outcome_alignment,
            "safety":self.safety,
            "score":self.score(),
            "level":self.level(),
        }

    @classmethod
    def from_reasoning(cls, reasoning):
        if not isinstance(reasoning, dict):
            return None
        action=reasoning.get("action")
        reason=reasoning.get("reason")
        outcome=reasoning.get("outcome")
        safety=reasoning.get("safety")
        completeness=1.0 if action is not None and reason is not None else 0.5 if action is not None or reason is not None else 0.0
        consistency=1.0 if reason is not None else 0.5 if action is not None else 0.0
        outcome_alignment=1.0 if outcome is not None else 0.5
        safety_score=1.0 if isinstance(safety, dict) and safety.get("allowed") is True else 0.5 if safety is not None else 0.0
        return cls.create(completeness,consistency,outcome_alignment,safety_score)

    def factor_scores(self):
        return {
            "completeness": self.completeness,
            "consistency": self.consistency,
            "outcome_alignment": self.outcome_alignment,
            "safety": self.safety,
        }

    def weak_factors(self, threshold=0.50):
        if not isinstance(threshold,(int,float)) or isinstance(threshold,bool):
            return []
        if threshold < self.MIN_SCORE or threshold > self.MAX_SCORE:
            return []
        return [name for name,score in self.factor_scores().items() if score < threshold]

    def improvement_signals(self, threshold=0.50):
        weak=self.weak_factors(threshold)
        mapping={
            "completeness":"IMPROVE_COMPLETENESS",
            "consistency":"IMPROVE_CONSISTENCY",
            "outcome_alignment":"IMPROVE_OUTCOME_ALIGNMENT",
            "safety":"IMPROVE_SAFETY",
        }
        return [mapping[factor] for factor in weak if factor in mapping]

    def assessment(self, threshold=0.50):
        result=self.to_dict()
        result["weak_factors"]=self.weak_factors(threshold)
        result["improvement_signals"]=self.improvement_signals(threshold)
        return result
