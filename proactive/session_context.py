from datetime import datetime
import json
import threading
import uuid
from pathlib import Path


class SessionContext:

    MAX_RECORDS = 100

    def __init__(self, file=None):
        self.file = Path(file) if file else Path(__file__).resolve().parent.parent / "data" / "session_context.json"
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.records = self._load()

    def _load(self):
        try:
            if not self.file.exists():
                return []
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"[SESSION CONTEXT] Load error: {e}")
            return []

    def _save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[SESSION CONTEXT] Save error: {e}")
            return False

    def create(self, context=None):
        record = {
            "session_id": str(uuid.uuid4()),
            "started_at": datetime.now().isoformat(),
            "context": context if isinstance(context, dict) else {},
        }
        with self.lock:
            self.records.append(record)
            self.records = self.records[-self.MAX_RECORDS:]
            if not self._save():
                self.records.pop()
                return None
        return dict(record)

    def recent(self, limit=20):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []
        if limit <= 0:
            return []
        with self.lock:
            return [dict(record) for record in self.records[-limit:]]

    def get(self, session_id):
        if not isinstance(session_id, str) or not session_id.strip():
            return None

        with self.lock:
            for record in self.records:
                if record.get("session_id") == session_id:
                    return dict(record)
        return None

    def latest(self):
        with self.lock:
            if not self.records:
                return None
            return dict(self.records[-1])

    def search_context(self, query_context, limit=20):
        if not isinstance(query_context, dict) or not query_context:
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []

        if limit <= 0:
            return []

        with self.lock:
            matches = []
            for record in self.records:
                context = record.get("context", {})
                if not isinstance(context, dict):
                    continue
                if all(context.get(key) == value for key, value in query_context.items()):
                    matches.append(dict(record))

        return matches[-limit:]

    SESSION_RETENTION_DAYS = 30

    def age_seconds(self, timestamp, now=None):
        from datetime import datetime
        try:
            created = datetime.fromisoformat(timestamp)
            current = now if isinstance(now, datetime) else datetime.now()
            return max(0.0, (current - created).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None

    def is_expired(self, record, now=None):
        if not isinstance(record, dict):
            return False
        age = self.age_seconds(record.get("started_at"), now)
        if age is None:
            return False
        return age >= self.SESSION_RETENTION_DAYS * 86400

    def count(self):
        with self.lock:
            return len(self.records)


session_context = SessionContext()
