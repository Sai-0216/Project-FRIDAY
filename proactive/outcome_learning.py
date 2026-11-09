class OutcomeLearning:

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"

    TYPES = {
        SUCCESS,
        FAILURE,
        ACCEPTED,
        REJECTED,
        UNKNOWN,
    }

    @classmethod
    def is_valid(cls, outcome_type):
        return outcome_type in cls.TYPES

    @classmethod
    def create(cls, outcome_type, action=None, result=None):
        if not cls.is_valid(outcome_type):
            return None
        return {
            "type": outcome_type,
            "action": action,
            "result": result,
        }

    @classmethod
    def classify(cls, outcome):
        if outcome is None:
            return cls.UNKNOWN
        value = str(outcome).strip().lower()
        if value in {"completed", "complete", "success", "succeeded", "successful"}:
            return cls.SUCCESS
        if value in {"failed", "failure", "error", "errored", "unsuccessful"}:
            return cls.FAILURE
        if value in {"accepted", "accept"}:
            return cls.ACCEPTED
        if value in {"rejected", "reject", "declined", "decline"}:
            return cls.REJECTED
        if value == "unknown":
            return cls.UNKNOWN
        return cls.UNKNOWN

    @classmethod
    def extract_learning(cls, outcome_type, action=None, result=None):
        if not cls.is_valid(outcome_type):
            return None
        if not isinstance(action, str) or not action.strip():
            return None
        action = action.strip()
        if outcome_type == cls.SUCCESS:
            statement = f"{action} has previously produced a successful outcome."
        elif outcome_type == cls.FAILURE:
            statement = f"{action} has previously produced a failed outcome."
        elif outcome_type == cls.ACCEPTED:
            statement = f"{action} has previously been accepted."
        elif outcome_type == cls.REJECTED:
            statement = f"{action} has previously been rejected."
        else:
            statement = f"{action} has a previously observed outcome."
        return {
            "learning": statement,
            "outcome_type": outcome_type,
            "action": action,
            "result": result,
        }

    @classmethod
    def persist_learning(cls, outcome_type, action=None, result=None, confidence="MEDIUM"):
        from proactive.semantic_memory import semantic_memory
        learning = cls.extract_learning(outcome_type, action, result)
        if learning is None:
            return None
        return semantic_memory.record(learning["learning"], "outcome_learning", confidence)

    @classmethod
    def learning_confidence(cls, outcome_type):
        if outcome_type in (cls.SUCCESS, cls.ACCEPTED):
            return "HIGH"
        if outcome_type in (cls.FAILURE, cls.REJECTED):
            return "MEDIUM"
        if outcome_type == cls.UNKNOWN:
            return "LOW"
        return None
