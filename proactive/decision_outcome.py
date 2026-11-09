class DecisionOutcome:

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"

    TYPES = {
        SUCCESS,
        FAILURE,
        UNKNOWN,
    }

    @classmethod
    def is_valid(cls, outcome_type):
        return outcome_type in cls.TYPES

    @classmethod
    def create(cls, action, outcome_type, reason=None, context=None):
        if not isinstance(action, str) or not action.strip():
            return None
        if not cls.is_valid(outcome_type):
            return None
        return {
            "action": action.strip(),
            "outcome": outcome_type,
            "reason": reason,
            "context": context if isinstance(context, dict) else {},
        }

    @classmethod
    def statistics(cls, records):
        if not isinstance(records, list):
            return {"total": 0, "success": 0, "failure": 0, "success_rate": 0.0, "failure_rate": 0.0}
        success = 0
        failure = 0
        for record in records:
            if not isinstance(record, dict):
                continue
            outcome = str(record.get("outcome", "")).strip().lower()
            if outcome in (cls.SUCCESS.lower(), "completed", "success", "succeeded", "accepted"):
                success += 1
            elif outcome in (cls.FAILURE.lower(), "failed", "failure", "error", "rejected"):
                failure += 1
        total = success + failure
        success_rate = success / total if total else 0.0
        failure_rate = failure / total if total else 0.0
        return {"total": total, "success": success, "failure": failure, "success_rate": success_rate, "failure_rate": failure_rate}

    @classmethod
    def action_statistics(cls, records):
        if not isinstance(records, list):
            return {}
        stats = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            action = record.get("action")
            if not isinstance(action, str) or not action.strip():
                continue
            action = action.strip()
            outcome = str(record.get("outcome", "")).strip().lower()
            if outcome in (cls.SUCCESS.lower(), "completed", "success", "succeeded", "accepted"):
                success = True
            elif outcome in (cls.FAILURE.lower(), "failed", "failure", "error", "rejected"):
                success = False
            else:
                continue
            if action not in stats:
                stats[action] = {"total": 0, "success": 0, "failure": 0, "success_rate": 0.0}
            stats[action]["total"] += 1
            if success:
                stats[action]["success"] += 1
            else:
                stats[action]["failure"] += 1
        for data in stats.values():
            data["success_rate"] = data["success"] / data["total"] if data["total"] else 0.0
        return stats

    @classmethod
    def action_failures(cls, records):
        stats = cls.action_statistics(records)
        return {
            action: {
                "failure": data["failure"],
                "total": data["total"],
                "failure_rate": data["failure"] / data["total"] if data["total"] else 0.0,
            }
            for action, data in stats.items()
            if data["failure"] > 0
        }

    @classmethod
    def quality(cls, success_rate):
        try:
            rate = float(success_rate)
        except (TypeError, ValueError):
            return "UNKNOWN"
        if rate < 0.0 or rate > 1.0:
            return "UNKNOWN"
        if rate >= 0.80:
            return "GOOD"
        if rate >= 0.50:
            return "FAIR"
        return "POOR"
