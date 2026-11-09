class MemoryConfidence:

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    LEVELS = {
        LOW: 1,
        MEDIUM: 2,
        HIGH: 3,
    }

    @classmethod
    def is_valid(cls, confidence):
        return confidence in cls.LEVELS

    @classmethod
    def score(cls, confidence):
        return cls.LEVELS.get(confidence, 0)

    @classmethod
    def at_least(cls, confidence, minimum):
        if not cls.is_valid(confidence) or not cls.is_valid(minimum):
            return False
        return cls.score(confidence) >= cls.score(minimum)
