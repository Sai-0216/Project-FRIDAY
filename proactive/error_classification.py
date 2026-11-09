class ErrorClassification:

    INCOMPLETE="INCOMPLETE"
    INCONSISTENT="INCONSISTENT"
    WRONG_OUTCOME="WRONG_OUTCOME"
    UNSAFE="UNSAFE"
    REPEATED_FAILURE="REPEATED_FAILURE"
    UNKNOWN="UNKNOWN"

    TYPES={INCOMPLETE,INCONSISTENT,WRONG_OUTCOME,UNSAFE,REPEATED_FAILURE,UNKNOWN}

    @classmethod
    def is_valid(cls,error_type):
        return error_type in cls.TYPES

    @classmethod
    def create(cls,error_type,reason=None,evidence=None):
        if not cls.is_valid(error_type):
            return None
        return {
            "type":error_type,
            "reason":str(reason) if reason is not None else None,
            "evidence":evidence if isinstance(evidence,dict) else {},
        }

    @classmethod
    def classify(cls,decision=None,reasoning=None):
        if not isinstance(decision,dict) and not isinstance(reasoning,dict):
            return cls.UNKNOWN
        if isinstance(reasoning,dict):
            signals=reasoning.get("improvement_signals",[])
            if "IMPROVE_SAFETY" in signals:
                return cls.UNSAFE
            if "IMPROVE_COMPLETENESS" in signals:
                return cls.INCOMPLETE
            if "IMPROVE_CONSISTENCY" in signals:
                return cls.INCONSISTENT
        if isinstance(decision,dict):
            expected=decision.get("expected")
            actual=decision.get("actual")
            if isinstance(expected,str) and isinstance(actual,str) and expected.strip() and actual.strip() and expected.strip().lower()!=actual.strip().lower():
                return cls.WRONG_OUTCOME
        return cls.UNKNOWN

    LOW="LOW"
    MEDIUM="MEDIUM"
    HIGH="HIGH"
    CRITICAL="CRITICAL"

    @classmethod
    def severity(cls,error_type,occurrences=1):
        if not cls.is_valid(error_type):
            return cls.UNKNOWN
        if not isinstance(occurrences,int) or isinstance(occurrences,bool) or occurrences < 1:
            return cls.UNKNOWN
        if error_type == cls.UNSAFE:
            return cls.CRITICAL
        if error_type == cls.REPEATED_FAILURE:
            return cls.CRITICAL
        if occurrences >= 3:
            return cls.HIGH
        if occurrences == 2:
            return cls.MEDIUM
        if error_type == cls.WRONG_OUTCOME:
            return cls.MEDIUM
        return cls.LOW

    @classmethod
    def assess(cls,error_type,reason=None,evidence=None,occurrences=1):
        if not cls.is_valid(error_type):
            return None
        severity=cls.severity(error_type,occurrences)
        if severity == cls.UNKNOWN:
            return None
        result=cls.create(error_type,reason,evidence)
        if result is None:
            return None
        result["severity"]=severity
        result["occurrences"]=occurrences
        return result

    @classmethod
    def classify_assessments(cls, reasoning_assessment=None, decision_assessment=None):
        if isinstance(reasoning_assessment,dict):
            signals=reasoning_assessment.get("improvement_signals",[])
            if "IMPROVE_SAFETY" in signals:
                return cls.UNSAFE
            if "IMPROVE_COMPLETENESS" in signals:
                return cls.INCOMPLETE
            if "IMPROVE_CONSISTENCY" in signals:
                return cls.INCONSISTENT
        if isinstance(decision_assessment,dict):
            expected=decision_assessment.get("expected")
            actual=decision_assessment.get("actual")
            if isinstance(expected,str) and isinstance(actual,str) and expected.strip() and actual.strip() and expected.strip().lower()!=actual.strip().lower():
                return cls.WRONG_OUTCOME
        return cls.UNKNOWN

    @classmethod
    def repeated_failure_count(cls, records, action):
        if not isinstance(records,list) or not isinstance(action,str) or not action.strip():
            return 0
        target=action.strip().lower()
        failures={"failed","failure","error","errored","rejected","reject"}
        count=0
        for record in records:
            if not isinstance(record,dict):
                continue
            record_action=record.get("action")
            outcome=record.get("outcome")
            if not isinstance(record_action,str) or not isinstance(outcome,str):
                continue
            if record_action.strip().lower()==target and outcome.strip().lower() in failures:
                count += 1
        return count

    @classmethod
    def detect_repeated_failure(cls, records, action):
        count=cls.repeated_failure_count(records,action)
        if count >= 2:
            return cls.REPEATED_FAILURE
        return cls.UNKNOWN

    @classmethod
    def assess_from_context(cls, reasoning_assessment=None, decision_assessment=None, records=None, action=None):
        repeated_count=cls.repeated_failure_count(records, action) if isinstance(records,list) and isinstance(action,str) else 0
        if repeated_count >= 2:
            return cls.assess(cls.REPEATED_FAILURE, "Action has repeatedly failed.", {"action":action,"failure_count":repeated_count}, repeated_count)
        error_type=cls.classify_assessments(reasoning_assessment, decision_assessment)
        if error_type == cls.UNKNOWN:
            return cls.assess(cls.UNKNOWN, "No clear error signal was identified.", {}, 1)
        reason=None
        evidence={}
        if isinstance(reasoning_assessment,dict):
            signals=reasoning_assessment.get("improvement_signals",[])
            evidence["reasoning_signals"]=signals
        if isinstance(decision_assessment,dict):
            evidence["decision"]=decision_assessment
        return cls.assess(error_type, reason, evidence, 1)
