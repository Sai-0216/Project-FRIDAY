from datetime import datetime
import json
import threading
from pathlib import Path


class PreferenceMemory:

    MAX_RECORDS = 500

    def __init__(self, file=None):
        self.file = Path(file) if file else Path(__file__).resolve().parent.parent / "data" / "preference_memory.json"
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
            print(f"[PREFERENCE MEMORY] Load error: {e}")
            return []

    def _save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[PREFERENCE MEMORY] Save error: {e}")
            return False

    def record(self, preference, category=None, confidence="MEDIUM"):
        if not isinstance(preference, str) or not preference.strip():
            return None
        preference = preference.strip()
        with self.lock:
            if any(record.get("preference", "").strip().lower() == preference.lower() for record in self.records):
                return None
            record = {
                "timestamp": datetime.now().isoformat(),
                "preference": preference,
                "category": category,
                "confidence": confidence,
            }
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

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []

        if limit <= 0:
            return []

        q = query.strip().lower()
        with self.lock:
            matches = [
                dict(record)
                for record in self.records
                if q in record.get("preference", "").lower()
            ]

        return matches[-limit:]

    def search_category(self, category, limit=20):
        if category is None:
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
                if record.get("category") == category
            ]

        return matches[-limit:]

    def search_confidence(self, confidence, limit=20):
        if confidence is None:
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
                if record.get("confidence") == confidence
            ]

        return matches[-limit:]

    def update(self, preference, category=None, confidence="MEDIUM"):
        if not isinstance(preference, str) or not preference.strip():
            return None

        preference = preference.strip()
        with self.lock:
            matches = [
                i
                for i, record in enumerate(self.records)
                if category is not None and record.get("category") == category
            ]

            if not matches:
                return self.record(preference, category, confidence)

            index = matches[-1]
            record = {
                "timestamp": datetime.now().isoformat(),
                "preference": preference,
                "category": category,
                "confidence": confidence,
            }
            self.records[index] = record
            if not self._save():
                return None
        return dict(record)

    def replace(self, existing_preference, preference, category=None, confidence="MEDIUM"):
        if not isinstance(existing_preference, str) or not isinstance(preference, str) or not preference.strip():
            return None
        with self.lock:
            index = next((i for i, record in enumerate(self.records) if record.get("preference", "").strip().lower() == existing_preference.strip().lower()), None)
            if index is None:
                return self.record(preference, category, confidence)
            record = {"timestamp": datetime.now().isoformat(), "preference": preference.strip(), "category": category, "confidence": confidence}
            self.records[index] = record
            if not self._save():
                return None
            return dict(record)

    def count(self):
        with self.lock:
            return len(self.records)


preference_memory = PreferenceMemory()
