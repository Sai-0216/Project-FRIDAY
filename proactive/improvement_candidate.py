class ImprovementCandidate:

    HIGH="HIGH"
    MEDIUM="MEDIUM"
    LOW="LOW"
    UNKNOWN="UNKNOWN"

    TYPES={"REASONING","DECISION","ERROR","BEHAVIOR","STRATEGY"}

    def __init__(self,candidate_type=None,target=None,reason=None,evidence=None,priority="UNKNOWN"):
        self.candidate_type=candidate_type if isinstance(candidate_type,str) else None
        self.target=target if isinstance(target,str) else None
        self.reason=reason if isinstance(reason,str) else None
        self.evidence=evidence if isinstance(evidence,dict) else {}
        self.priority=priority if priority in {self.HIGH,self.MEDIUM,self.LOW,self.UNKNOWN} else self.UNKNOWN

    @classmethod
    def create(cls,candidate_type,target=None,reason=None,evidence=None,priority="UNKNOWN"):
        if candidate_type not in cls.TYPES:
            return None
        if target is not None and not isinstance(target,str):
            return None
        if reason is not None and not isinstance(reason,str):
            return None
        if evidence is not None and not isinstance(evidence,dict):
            return None
        if priority not in {cls.HIGH,cls.MEDIUM,cls.LOW,cls.UNKNOWN}:
            return None
        return cls(candidate_type,target,reason,evidence,priority)

    def to_dict(self):
        return {
            "type":self.candidate_type,
            "target":self.target,
            "reason":self.reason,
            "evidence":self.evidence,
            "priority":self.priority,
        }

    def is_valid(self):
        return self.candidate_type in self.TYPES

    @classmethod
    def from_error(cls,error):
        if not isinstance(error,dict):
            return None
        error_type=error.get("type")
        severity=error.get("severity",cls.UNKNOWN)
        if error_type in {None,"UNKNOWN"}:
            return None
        priority_map={"CRITICAL":cls.HIGH,"HIGH":cls.HIGH,"MEDIUM":cls.MEDIUM,"LOW":cls.LOW}
        priority=priority_map.get(severity,cls.UNKNOWN)
        if priority == cls.UNKNOWN:
            return None
        evidence=error.get("evidence") if isinstance(error.get("evidence"),dict) else {}
        target=evidence.get("action")
        if not isinstance(target,str) or not target.strip():
            decision=evidence.get("decision")
            if isinstance(decision,dict) and isinstance(decision.get("action"),str):
                target=decision.get("action")
        if not isinstance(target,str) or not target.strip():
            target=error_type
        reason=error.get("reason")
        if not isinstance(reason,str) or not reason.strip():
            reason="Improvement candidate identified from error evidence."
        return cls.create("ERROR",target,reason,evidence,priority)

    @classmethod
    def from_reasoning_assessment(cls,assessment):
        if not isinstance(assessment,dict):
            return None
        signals=assessment.get("improvement_signals")
        if not isinstance(signals,list) or not signals:
            return None
        priority_map={"IMPROVE_SAFETY":cls.HIGH,"IMPROVE_OUTCOME_ALIGNMENT":cls.MEDIUM,"IMPROVE_CONSISTENCY":cls.MEDIUM,"IMPROVE_COMPLETENESS":cls.LOW}
        for signal in signals:
            priority=priority_map.get(signal)
            if priority is not None:
                target=signal.replace("IMPROVE_","").lower()
                reason="Reasoning quality indicates an improvement opportunity."
                evidence={"signal":signal,"assessment":assessment}
                return cls.create("REASONING",target,reason,evidence,priority)
        return None

    @classmethod
    def from_decision_assessment(cls,assessment):
        if not isinstance(assessment,dict):
            return None
        level=assessment.get("level")
        priority_map={"POOR":cls.HIGH,"FAIR":cls.MEDIUM}
        priority=priority_map.get(level)
        if priority is None:
            return None
        action=assessment.get("action")
        if not isinstance(action,str) or not action.strip():
            return None
        reason=assessment.get("explanation")
        if not isinstance(reason,str) or not reason.strip():
            reason="Decision quality indicates an improvement opportunity."
        evidence={"assessment":assessment}
        return cls.create("DECISION",action,reason,evidence,priority)

    @classmethod
    def detect(cls,error=None,reasoning_assessment=None,decision_assessment=None):
        candidate=cls.from_error(error) if isinstance(error,dict) else None
        if candidate is not None:
            return candidate
        candidate=cls.from_reasoning_assessment(reasoning_assessment) if isinstance(reasoning_assessment,dict) else None
        if candidate is not None:
            return candidate
        candidate=cls.from_decision_assessment(decision_assessment) if isinstance(decision_assessment,dict) else None
        return candidate

    @staticmethod
    def identity(candidate):
        if isinstance(candidate,ImprovementCandidate):
            candidate=candidate.to_dict()
        if not isinstance(candidate,dict):
            return None
        candidate_type=candidate.get("type")
        target=candidate.get("target")
        if not isinstance(candidate_type,str) or not isinstance(target,str):
            return None
        return (candidate_type.strip().upper(),target.strip().lower())

    @classmethod
    def deduplicate(cls,candidates):
        if not isinstance(candidates,list):
            return []
        unique=[]
        seen=set()
        for candidate in candidates:
            identity=cls.identity(candidate)
            if identity is None or identity in seen:
                continue
            seen.add(identity)
            unique.append(candidate)
        return unique
