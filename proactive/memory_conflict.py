class MemoryConflict:

    PREFERENCE_CONFLICT = "PREFERENCE_CONFLICT"
    FACT_CONFLICT = "FACT_CONFLICT"
    SEMANTIC_CONFLICT = "SEMANTIC_CONFLICT"

    TYPES = {
        PREFERENCE_CONFLICT,
        FACT_CONFLICT,
        SEMANTIC_CONFLICT,
    }

    @classmethod
    def is_valid_type(cls, conflict_type):
        return conflict_type in cls.TYPES

    @classmethod
    def create(cls, conflict_type, existing, incoming):
        if not cls.is_valid_type(conflict_type):
            return None
        return {
            "type": conflict_type,
            "existing": existing,
            "incoming": incoming,
            "resolved": False,
            "resolution": None,
        }

    @classmethod
    def detect_preference_conflict(cls, existing, incoming):
        if not isinstance(existing, dict) or not isinstance(incoming, dict):
            return False
        existing_category = existing.get("category")
        incoming_category = incoming.get("category")
        existing_preference = existing.get("preference")
        incoming_preference = incoming.get("preference")
        if not existing_category or not incoming_category:
            return False
        if existing_category != incoming_category:
            return False
        if not isinstance(existing_preference, str) or not isinstance(incoming_preference, str):
            return False
        return existing_preference.strip().lower() != incoming_preference.strip().lower()

    @classmethod
    def compare_confidence(cls, existing, incoming):
        from proactive.memory_confidence import MemoryConfidence
        if not isinstance(existing, dict) or not isinstance(incoming, dict):
            return None
        old = existing.get("confidence")
        new = incoming.get("confidence")
        if not MemoryConfidence.is_valid(old) or not MemoryConfidence.is_valid(new):
            return None
        old_score = MemoryConfidence.score(old)
        new_score = MemoryConfidence.score(new)
        if new_score > old_score:
            return "incoming"
        if old_score > new_score:
            return "existing"
        return "tie"

    @classmethod
    def compare_recency(cls, existing, incoming, now=None):
        from proactive.memory_expiration import MemoryExpiration
        from datetime import datetime
        current = now if isinstance(now, datetime) else datetime.now()
        if not isinstance(existing, dict) or not isinstance(incoming, dict):
            return None
        old_age = MemoryExpiration.age_seconds(existing.get("timestamp"), current)
        new_age = MemoryExpiration.age_seconds(incoming.get("timestamp"), current)
        if old_age is None or new_age is None:
            return None
        if new_age < old_age:
            return "incoming"
        if old_age < new_age:
            return "existing"
        return "tie"

    @classmethod
    def resolve(cls, existing, incoming, now=None):
        confidence_result = cls.compare_confidence(existing, incoming)
        if confidence_result in ("existing", "incoming"):
            return confidence_result
        if confidence_result == "tie":
            recency_result = cls.compare_recency(existing, incoming, now)
            if recency_result in ("existing", "incoming", "tie"):
                return recency_result
        return "manual_review"

    @classmethod
    def is_safe_resolution(cls, existing, incoming, resolution):
        if resolution not in ("existing", "incoming"):
            return False
        if not isinstance(existing, dict) or not isinstance(incoming, dict):
            return False
        winner = incoming if resolution == "incoming" else existing
        confidence = winner.get("confidence")
        return confidence in ("HIGH", "MEDIUM")
