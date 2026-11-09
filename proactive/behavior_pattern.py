from pathlib import Path
import json


class BehaviorPattern:

    MIN_OCCURRENCES = 2

    def __init__(self, pattern_type, action=None, occurrences=0, confidence="MEDIUM"):
        self.pattern_type = pattern_type
        self.action = action
        self.occurrences = occurrences
        self.confidence = confidence

    def to_dict(self):
        return {
            "pattern_type": self.pattern_type,
            "action": self.action,
            "occurrences": self.occurrences,
            "confidence": self.confidence,
        }

    @classmethod
    def create(cls, pattern_type, action=None, occurrences=0, confidence="MEDIUM"):
        if not isinstance(pattern_type, str) or not pattern_type.strip():
            return None
        try:
            occurrences = int(occurrences)
        except (TypeError, ValueError):
            return None
        if occurrences < 0:
            return None
        if confidence not in {"HIGH", "MEDIUM", "LOW"}:
            return None
        action_value = action.strip() if isinstance(action, str) and action.strip() else None
        return cls(pattern_type.strip(), action_value, occurrences, confidence)

    @classmethod
    def detect_repeated_actions(cls, records):
        if not isinstance(records, list):
            return {}
        counts = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            action = record.get("action")
            if not isinstance(action, str) or not action.strip():
                continue
            action = action.strip()
            counts[action] = counts.get(action, 0) + 1
        return {
            action: count
            for action, count in counts.items()
            if count >= cls.MIN_OCCURRENCES
        }

    @classmethod
    def frequency(cls, records):
        if not isinstance(records, list):
            return {}
        counts = {}
        total = 0
        for record in records:
            if not isinstance(record, dict):
                continue
            action = record.get("action")
            if not isinstance(action, str) or not action.strip():
                continue
            action = action.strip()
            counts[action] = counts.get(action, 0) + 1
            total += 1
        if total == 0:
            return {}
        return {
            action: {
                "occurrences": count,
                "total": total,
                "frequency": count / total,
            }
            for action, count in counts.items()
        }

    @classmethod
    def confidence(cls, occurrences):
        try:
            occurrences = int(occurrences)
        except (TypeError, ValueError):
            return "LOW"
        if occurrences >= 4:
            return "HIGH"
        if occurrences >= 2:
            return "MEDIUM"
        return "LOW"


PATTERN_FILE = Path(__file__).resolve().parent.parent / "data" / "behavior_patterns.json"


def save_pattern(pattern, file=None):
    target = Path(file) if file else PATTERN_FILE
    if not isinstance(pattern, BehaviorPattern):
        return False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(pattern.to_dict(), f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_pattern(file=None):
    target = Path(file) if file else PATTERN_FILE
    try:
        if not target.exists():
            return None
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return BehaviorPattern.create(data.get("pattern_type"), data.get("action"), data.get("occurrences", 0), data.get("confidence", "LOW"))
    except Exception:
        return None
