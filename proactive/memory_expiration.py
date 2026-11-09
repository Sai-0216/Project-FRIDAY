class MemoryExpiration:

    POLICIES = {
        "EPISODIC": 30,
        "SEMANTIC": 180,
        "PREFERENCE": 365,
        "OUTCOME": 90,
        "TASK_STATE": 30,
        "ENVIRONMENT": 7,
        "FACT": None,
        "LEARNED_PATTERN": 180,
    }

    @classmethod
    def days_for(cls, memory_type):
        return cls.POLICIES.get(memory_type)

    @classmethod
    def never_expires(cls, memory_type):
        return cls.days_for(memory_type) is None

    @classmethod
    def is_supported(cls, memory_type):
        return memory_type in cls.POLICIES

    @classmethod
    def age_seconds(cls, timestamp, now=None):
        from datetime import datetime
        try:
            created = datetime.fromisoformat(timestamp)
            current = now if isinstance(now, datetime) else datetime.now()
            return max(0.0, (current - created).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None

    @classmethod
    def is_expired(cls, memory_type, timestamp, now=None):
        if not cls.is_supported(memory_type):
            return False
        days = cls.days_for(memory_type)
        if days is None:
            return False
        age = cls.age_seconds(timestamp, now)
        if age is None:
            return False
        return age >= days * 86400

    @classmethod
    def expiration_info(cls, memory_type, timestamp, now=None):
        days = cls.days_for(memory_type)
        age = cls.age_seconds(timestamp, now)
        return {
            "memory_type": memory_type,
            "retention_days": days,
            "age_seconds": age,
            "expired": cls.is_expired(memory_type, timestamp, now),
        }

    @classmethod
    def should_forget(cls, memory_type, timestamp, confidence=None, now=None):
        if not cls.is_supported(memory_type):
            return False
        if cls.never_expires(memory_type):
            return False
        if confidence == "HIGH":
            return False
        return cls.is_expired(memory_type, timestamp, now)

    @classmethod
    def is_protected(cls, memory_type, confidence=None):
        if not cls.is_supported(memory_type):
            return True
        if cls.never_expires(memory_type):
            return True
        return confidence == "HIGH"
