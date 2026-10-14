"""
Project FRIDAY
Phase 19.3.1
Episodic Memory Storage
"""

import json
import threading
from datetime import datetime
from pathlib import Path


class EpisodicMemory:

    MAX_RECORDS = 500

    def __init__(self, file=None):
        self.file = Path(file) if file else Path(__file__).resolve().parent.parent / "data" / "episodic_memory.json"
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
            print(f"[EPISODIC MEMORY] Load error: {e}")
            return []

    def _save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[EPISODIC MEMORY] Save error: {e}")
            return False

    def record(self, event, context=None, outcome=None):
        if not isinstance(event, str) or not event.strip():
            return None
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event.strip(),
            "context": context if isinstance(context, dict) else {},
            "outcome": outcome,
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

    def search(self, query, limit=20):
        if not isinstance(query, str) or not query.strip():
            return []

        query = query.strip().lower()

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []

        if limit <= 0:
            return []

        with self.lock:
            matches = [
                dict(record)
                for record in self.records
                if query in str(record.get("event", "")).lower()
            ]

        return matches[-limit:]

    def search_context(self, key, value, limit=20):
        if not isinstance(key, str) or not key.strip():
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []

        if limit <= 0:
            return []

        key = key.strip()

        with self.lock:
            matches = [
                dict(record)
                for record in self.records
                if isinstance(record.get("context"), dict)
                and record["context"].get(key) == value
            ]

        return matches[-limit:]

    def search_outcome(self, outcome, limit=20):
        if outcome is None:
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []

        if limit <= 0:
            return []

        with self.lock:
            matches = [
                dict(record)
                for record in self.records
                if record.get("outcome") == outcome
            ]

        return matches[-limit:]

    def count(self):
        with self.lock:
            return len(self.records)


episodic_memory = EpisodicMemory()
