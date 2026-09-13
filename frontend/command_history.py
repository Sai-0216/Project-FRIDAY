from collections import defaultdict, deque


class CommandHistory:
    def __init__(self, limit=30):
        self.limit = max(1, int(limit))
        self._history = defaultdict(lambda: deque(maxlen=self.limit))

    def add(self, device_id, command, result=None):
        entry = {
            "device_id": str(device_id),
            "command": str(command),
            "result": result or {},
        }
        self._history[str(device_id)].append(entry)
        return entry

    def recent(self, device_id, limit=10):
        items = list(self._history.get(str(device_id), []))
        return items[-max(1, int(limit)):]

    def latest(self, device_id):
        items = self.recent(device_id, 1)
        return items[0] if items else None

    def clear(self, device_id=None):
        if device_id is None:
            self._history.clear()
        else:
            self._history.pop(str(device_id), None)


history = CommandHistory()


if __name__ == "__main__":
    history.add("saicharan", "open calculator", {"outcome": "completed"})
    history.add("saicharan", "open notepad", {"outcome": "completed"})
    print("RECENT:", history.recent("saicharan"))
    print("LATEST:", history.latest("saicharan"))
