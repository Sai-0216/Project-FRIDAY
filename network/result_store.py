from collections import defaultdict
from threading import RLock

MAX_RESULTS = 50

class DeviceResultStore:
    def __init__(self):
        self._results = defaultdict(list)
        self._lock = RLock()

    def record(self, device_id, result):
        if not isinstance(device_id, str) or not device_id.strip():
            return False
        if not isinstance(result, dict):
            return False
        with self._lock:
            bucket = self._results[device_id.strip()]
            bucket.append(dict(result))
            del bucket[:-MAX_RESULTS]
        return True

    def recent(self, device_id, limit=20):
        if not isinstance(device_id, str) or not device_id.strip():
            return []
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            return []
        with self._lock:
            return list(self._results.get(device_id.strip(), [])[-limit:])

    def latest(self, device_id):
        results = self.recent(device_id, 1)
        return results[0] if results else None

result_store = DeviceResultStore()
