class NotificationManager:
    def __init__(self):
        self._items = []

    def add(self, notification):
        if not notification:
            return None
        item = dict(notification)
        self._items.append(item)
        return item

    def dismiss(self, index):
        try:
            index = int(index)
        except (TypeError, ValueError):
            return None
        if index < 0 or index >= len(self._items):
            return None
        return self._items.pop(index)

    def clear(self):
        removed = list(self._items)
        self._items.clear()
        return removed

    def count(self):
        return len(self._items)

    def recent(self, limit=10):
        try:
            limit = max(0, int(limit))
        except (TypeError, ValueError):
            limit = 10
        return list(self._items[-limit:]) if limit else []


if __name__ == "__main__":
    manager = NotificationManager()
    manager.add({"type": "activity", "count": 1, "message": "1 new activity detected."})
    manager.add({"type": "activity", "count": 2, "message": "2 new activities detected."})
    print('COUNT:', manager.count())
    print('RECENT:', manager.recent())
    print('DISMISSED:', manager.dismiss(0))
    print('COUNT AFTER DISMISS:', manager.count())
    print('CLEARED:', manager.clear())
    print('FINAL COUNT:', manager.count())
