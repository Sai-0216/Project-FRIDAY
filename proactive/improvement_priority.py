class ImprovementPriority:

    HIGH="HIGH"
    MEDIUM="MEDIUM"
    LOW="LOW"
    UNKNOWN="UNKNOWN"

    MIN_SCORE=0.0
    MAX_SCORE=1.0

    def __init__(self,severity=0.0,frequency=0.0,confidence=0.0,recency=0.0):
        self.severity=self._clamp(severity)
        self.frequency=self._clamp(frequency)
        self.confidence=self._clamp(confidence)
        self.recency=self._clamp(recency)

    @classmethod
    def create(cls,severity=0.0,frequency=0.0,confidence=0.0,recency=0.0):
        values=[severity,frequency,confidence,recency]
        if any(not isinstance(value,(int,float)) or isinstance(value,bool) for value in values):
            return None
        if any(value < cls.MIN_SCORE or value > cls.MAX_SCORE for value in values):
            return None
        return cls(severity,frequency,confidence,recency)

    @staticmethod
    def _clamp(value):
        if not isinstance(value,(int,float)) or isinstance(value,bool):
            return 0.0
        return max(0.0,min(1.0,float(value)))

    def score(self):
        return round((self.severity*0.40)+(self.frequency*0.25)+(self.confidence*0.20)+(self.recency*0.15),4)

    def level(self):
        score=self.score()
        if score >= 0.80:
            return self.HIGH
        if score >= 0.50:
            return self.MEDIUM
        if score > 0.0:
            return self.LOW
        return self.UNKNOWN

    def to_dict(self):
        return {
            "severity":self.severity,
            "frequency":self.frequency,
            "confidence":self.confidence,
            "recency":self.recency,
            "score":self.score(),
            "level":self.level(),
        }

    @staticmethod
    def priority_value(priority):
        mapping={"HIGH":1.0,"MEDIUM":0.6,"LOW":0.3,"UNKNOWN":0.0}
        return mapping.get(priority,0.0)

    @classmethod
    def from_candidate(cls,candidate,frequency=0.0,confidence=0.0,recency=0.0):
        if not isinstance(candidate,dict):
            return None
        severity=cls.priority_value(candidate.get("priority"))
        if candidate.get("priority") not in {"HIGH","MEDIUM","LOW","UNKNOWN"}:
            return None
        return cls.create(severity,frequency,confidence,recency)

    @staticmethod
    def normalize_frequency(occurrences, reference=5):
        if not isinstance(occurrences,int) or isinstance(occurrences,bool) or occurrences < 0:
            return 0.0
        if not isinstance(reference,int) or isinstance(reference,bool) or reference <= 0:
            return 0.0
        return min(1.0,float(occurrences)/float(reference))

    @staticmethod
    def normalize_confidence(confidence):
        mapping={"HIGH":1.0,"MEDIUM":0.67,"LOW":0.33,"UNKNOWN":0.0}
        if not isinstance(confidence,str):
            return 0.0
        return mapping.get(confidence.strip().upper(),0.0)

    @staticmethod
    def normalize_recency(age_seconds):
        if not isinstance(age_seconds,(int,float)) or isinstance(age_seconds,bool):
            return 0.0
        if age_seconds < 0:
            age_seconds=0.0
        age_hours=float(age_seconds)/3600.0
        return round(1.0/(1.0+age_hours),4)

    @classmethod
    def profile(cls,candidate):
        if not isinstance(candidate,dict):
            return None
        priority=candidate.get("priority")
        severity=cls.priority_value(priority)
        if priority not in {"HIGH","MEDIUM","LOW","UNKNOWN"}:
            return None
        evidence=candidate.get("evidence") if isinstance(candidate.get("evidence"),dict) else {}
        occurrences=evidence.get("failure_count",evidence.get("occurrences",1))
        frequency=cls.normalize_frequency(occurrences)
        confidence=evidence.get("confidence",candidate.get("confidence","UNKNOWN"))
        confidence_score=cls.normalize_confidence(confidence)
        age_seconds=evidence.get("age_seconds")
        recency=cls.normalize_recency(age_seconds) if age_seconds is not None else 0.0
        result=cls.create(severity,frequency,confidence_score,recency)
        if result is None:
            return None
        data=result.to_dict()
        data["candidate"]=candidate
        return data

    def explanation(self):
        level=self.level()
        if level == self.HIGH:
            return "High priority because the improvement has strong severity, frequency, confidence, or recency signals."
        if level == self.MEDIUM:
            return "Medium priority because the improvement has meaningful but not consistently strong evidence."
        if level == self.LOW:
            return "Low priority because the improvement currently has limited evidence or impact."
        return "Priority is unknown because there is insufficient evidence."

    def assessment(self):
        result=self.to_dict()
        result["explanation"]=self.explanation()
        return result
