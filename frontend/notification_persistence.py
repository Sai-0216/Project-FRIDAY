import json
from pathlib import Path


class NotificationPersistence:
    def __init__(self, path='data/frontend_notifications.json'):
        self.path = Path(path)

    def save(self, items):
        items = list(items or [])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8')
        return self.path

    def load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def clear(self):
        try:
            if self.path.exists():
                self.path.unlink()
        except OSError:
            pass


if __name__ == '__main__':
    store = NotificationPersistence('data/test_frontend_notifications.json')
    sample = [
        {'type': 'activity', 'count': 1, 'message': '1 new activity detected.'},
        {'type': 'activity', 'count': 2, 'message': '2 new activities detected.'},
    ]
    print('SAVE:', store.save(sample))
    print('LOAD:', store.load())
    store.clear()
    print('AFTER CLEAR:', store.load())
