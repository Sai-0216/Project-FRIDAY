class ActionFailure:

    def __init__(self, action, failures=0, total=0, rate=0.0):
        self.action = action
        self.failures = failures
        self.total = total
        self.rate = rate

    def to_dict(self):
        return {
            "action": self.action,
            "failures": self.failures,
            "total": self.total,
            "failure_rate": self.rate,
        }

    @classmethod
    def create(cls, action, failures=0, total=0, rate=0.0):
        if not isinstance(action, str) or not action.strip():
            return None
        try:
            failures = int(failures)
            total = int(total)
            rate = float(rate)
        except (TypeError, ValueError):
            return None
        failures = max(0, failures)
        total = max(0, total)
        rate = max(0.0, min(1.0, rate))
        return cls(action.strip(), failures, total, rate)




    @classmethod
    def failed_actions(cls, records):
        if not isinstance(records, list):
            return {}
        results = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            action = record.get("action")
            outcome = str(record.get("outcome", "")).strip().lower()
            if not isinstance(action, str) or not action.strip():
                continue
            if outcome not in {"failed", "failure", "error", "rejected"}:
                continue
            action = action.strip()
            results[action] = results.get(action, 0) + 1
        return results

    @classmethod
    def severity(cls, failure_rate):
        try:
            rate = float(failure_rate)
        except (TypeError, ValueError):
            return "UNKNOWN"
        if rate < 0.0 or rate > 1.0:
            return "UNKNOWN"
        if rate >= 0.75:
            return "CRITICAL"
        if rate >= 0.50:
            return "HIGH"
        if rate >= 0.25:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def extract_learning(cls, action, failures):
        if not isinstance(action, str) or not action.strip():
            return None
        try:
            failures = int(failures)
        except (TypeError, ValueError):
            return None
        if failures <= 0:
            return None
        action = action.strip()
        if failures == 1:
            statement = f"{action} has previously failed."
        else:
            statement = f"{action} has repeatedly failed."
        return {
            "learning": statement,
            "action": action,
            "failures": failures,
        }

    @classmethod
    def persist_learning(cls, action, failures, confidence="MEDIUM"):
        from proactive.semantic_memory import semantic_memory
        learning = cls.extract_learning(action, failures)
        if learning is None:
            return None
        return semantic_memory.record(learning["learning"], "action_failure", confidence)
