class MemoryRelevance:

    MIN_SCORE = 0.0
    MAX_SCORE = 1.0

    @classmethod
    def clamp(cls, score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            return cls.MIN_SCORE
        return max(cls.MIN_SCORE, min(cls.MAX_SCORE, score))

    @classmethod
    def text_match(cls, query, text):
        if not isinstance(query, str) or not isinstance(text, str):
            return 0.0
        query = query.strip().lower()
        text = text.strip().lower()
        if not query or not text:
            return 0.0
        if query == text:
            return 1.0
        if query in text or text in query:
            return 0.75
        query_words = set(query.split())
        text_words = set(text.split())
        if not query_words or not text_words:
            return 0.0
        overlap = len(query_words & text_words) / len(query_words)
        return cls.clamp(overlap)

    @classmethod
    def context_match(cls, query_context, memory_context):
        if not isinstance(query_context, dict) or not isinstance(memory_context, dict):
            return 0.0
        if not query_context or not memory_context:
            return 0.0
        matches = 0
        total = 0
        for key, value in query_context.items():
            total += 1
            if key in memory_context and memory_context.get(key) == value:
                matches += 1
        if total == 0:
            return 0.0
        return cls.clamp(matches / total)

    @classmethod
    def recency_score(cls, age_seconds):
        try:
            age_seconds = max(0.0, float(age_seconds))
        except (TypeError, ValueError):
            return 0.0
        age_hours = age_seconds / 3600.0
        return cls.clamp(1.0 / (1.0 + age_hours))


    @classmethod
    def confidence_score(cls, confidence):
        from proactive.memory_confidence import MemoryConfidence
        score = MemoryConfidence.score(confidence)
        if score <= 0:
            return 0.0
        return cls.clamp(score / 3.0)

    @classmethod
    def combined_score(cls, relevance, confidence):
        relevance = cls.clamp(relevance)
        confidence = cls.confidence_score(confidence)
        return cls.clamp((relevance * 0.7) + (confidence * 0.3))
