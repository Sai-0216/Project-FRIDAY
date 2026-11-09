class ActionReinforcement:

    def __init__(self, action, score=0.0, successes=0):
        self.action = action
        self.score = score
        self.successes = successes

    def to_dict(self):
        return {
            "action": self.action,
            "score": self.score,
            "successes": self.successes,
        }

    @classmethod
    def create(cls, action, score=0.0, successes=0):
        if not isinstance(action, str) or not action.strip():
            return None
        try:
            score = float(score)
            successes = int(successes)
        except (TypeError, ValueError):
            return None
        score = max(0.0, min(1.0, score))
        successes = max(0, successes)
        return cls(action.strip(), score, successes)

    @classmethod
    def successful_actions(cls, records):
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
            if outcome not in {"success", "completed", "succeeded", "accepted"}:
                continue
            action = action.strip()
            results[action] = results.get(action, 0) + 1
        return results

    @classmethod
    def score_actions(cls, records):
        if not isinstance(records, list):
            return {}
        stats = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            action = record.get("action")
            outcome = str(record.get("outcome", "")).strip().lower()
            if not isinstance(action, str) or not action.strip():
                continue
            if outcome not in {"success", "completed", "succeeded", "accepted", "failed", "failure", "error", "rejected"}:
                continue
            action = action.strip()
            if action not in stats:
                stats[action] = {"success": 0, "total": 0}
            stats[action]["total"] += 1
            if outcome in {"success", "completed", "succeeded", "accepted"}:
                stats[action]["success"] += 1
        return {
            action: {
                "score": data["success"] / data["total"] if data["total"] else 0.0,
                "successes": data["success"],
                "total": data["total"],
            }
            for action, data in stats.items()
        }

    @classmethod
    def strengthen(cls, successes):
        try:
            successes = int(successes)
        except (TypeError, ValueError):
            return 0.0
        successes = max(0, successes)
        if successes == 0:
            return 0.0
        return min(1.0, 0.4 + (successes * 0.1))


import json
from pathlib import Path

REINFORCEMENT_FILE = Path(__file__).resolve().parent.parent / "data" / "action_reinforcement.json"


def save_reinforcement(reinforcement, file=None):
    target = Path(file) if file else REINFORCEMENT_FILE
    if not isinstance(reinforcement, ActionReinforcement):
        return False
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(reinforcement.to_dict(), f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_reinforcement(file=None):
    target = Path(file) if file else REINFORCEMENT_FILE
    try:
        if not target.exists():
            return None
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return ActionReinforcement.create(data.get("action"), data.get("score", 0.0), data.get("successes", 0))
    except Exception:
        return None
