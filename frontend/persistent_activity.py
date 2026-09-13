import json
from pathlib import Path

DEFAULT_PATH = Path("data/frontend_activity.json")


class PersistentActivityStore:
    def __init__(self, path=DEFAULT_PATH, limit=100):
        self.path = Path(path)
        self.limit = max(1, int(limit))

    def _load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def save(self, items):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        trimmed = list(items)[-self.limit:]
        self.path.write_text(json.dumps(trimmed, ensure_ascii=False, indent=2), encoding="utf-8")
        return trimmed

    def add(self, device_id, command, result=None):
        items = self._load()
        items.append({
            "device_id": str(device_id),
            "command": str(command),
            "result": result or {},
        })
        return self.save(items)

    def recent(self, device_id=None, limit=10):
        items = self._load()
        if device_id is not None:
            items = [item for item in items if item.get("device_id") == str(device_id)]
        return items[-max(1, int(limit)):]

    def clear(self):
        self.save([])

if __name__ == "__main__":
    test_path = Path("data/frontend_activity_test.json")
    store = PersistentActivityStore(test_path, limit=5)
    store.clear()
    store.add("saicharan", "open calculator", {"outcome": "completed"})
    store.add("saicharan", "open notepad", {"outcome": "completed"})
    first = store.recent("saicharan")
    second = PersistentActivityStore(test_path, limit=5).recent("saicharan")
    print("FIRST:", first)
    print("RELOADED:", second)
    print("PERSISTED:", first == second)
    test_path.unlink(missing_ok=True)
