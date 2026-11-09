from datetime import datetime
import json
import threading
from pathlib import Path


class SemanticMemory:

    MAX_RECORDS = 500

    def __init__(self, file=None):
        self.file = Path(file) if file else Path(__file__).resolve().parent.parent / "data" / "semantic_memory.json"
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
            print(f"[SEMANTIC MEMORY] Load error: {e}")
            return []

    def _save(self):
        try:
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[SEMANTIC MEMORY] Save error: {e}")
            return False

    def record(self, knowledge, source=None, confidence="MEDIUM"):
        if not isinstance(knowledge, str) or not knowledge.strip():
            return None
        knowledge = knowledge.strip()
        with self.lock:
            if self.has_knowledge(knowledge):
                return None

            record = {
                "timestamp": datetime.now().isoformat(),
                "knowledge": knowledge,
                "source": source,
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
                if q in record.get("knowledge", "").lower()
            ]

        return matches[-limit:]

    def search_source(self, source, limit=20):
        if source is None:
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
                if record.get("source") == source
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

    def has_knowledge(self, knowledge):
        if not isinstance(knowledge, str) or not knowledge.strip():
            return False

        target = knowledge.strip().lower()
        with self.lock:
            return any(
                record.get("knowledge", "").strip().lower() == target
                for record in self.records
            )

    def search_min_confidence(self, minimum="MEDIUM", limit=20):
        from proactive.memory_confidence import MemoryConfidence

        if not MemoryConfidence.is_valid(minimum):
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
                if MemoryConfidence.at_least(record.get("confidence"), minimum)
            ]

        return matches[-limit:]

    def rank_by_relevance(self, query, limit=20):
        from proactive.memory_relevance import MemoryRelevance

        if not isinstance(query, str) or not query.strip():
            return []

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return []
        if limit <= 0:
            return []

        with self.lock:
            ranked = []
            for record in self.records:
                relevance = MemoryRelevance.text_match(query, record.get("knowledge", ""))
                score = MemoryRelevance.combined_score(relevance, record.get("confidence"))
                item = dict(record)
                item["relevance"] = relevance
                item["score"] = score
                ranked.append(item)

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    def count(self):
        with self.lock:
            return len(self.records)


semantic_memory = SemanticMemory()
