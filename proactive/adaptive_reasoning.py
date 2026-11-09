class AdaptiveReasoning:

    def __init__(self, context=None, memories=None, outcomes=None, patterns=None, preferences=None):
        self.context = context if isinstance(context, dict) else {}
        self.memories = memories if isinstance(memories, list) else []
        self.outcomes = outcomes if isinstance(outcomes, dict) else {}
        self.patterns = patterns if isinstance(patterns, list) else []
        self.preferences = preferences if isinstance(preferences, dict) else {}

    def to_dict(self):
        return {
            "context": self.context,
            "memories": self.memories,
            "outcomes": self.outcomes,
            "patterns": self.patterns,
            "preferences": self.preferences,
        }

    @classmethod
    def create(cls, context=None, memories=None, outcomes=None, patterns=None, preferences=None):
        if context is not None and not isinstance(context, dict):
            return None
        if memories is not None and not isinstance(memories, list):
            return None
        if outcomes is not None and not isinstance(outcomes, dict):
            return None
        if patterns is not None and not isinstance(patterns, list):
            return None
        if preferences is not None and not isinstance(preferences, dict):
            return None
        return cls(context, memories, outcomes, patterns, preferences)

    @classmethod
    def memory_signals(cls, memories):
        if not isinstance(memories, list):
            return []
        signals = []
        for memory in memories:
            if not isinstance(memory, dict):
                continue
            knowledge = memory.get("knowledge")
            confidence = memory.get("confidence")
            score = memory.get("score", 0.0)
            if not isinstance(knowledge, str) or not knowledge.strip():
                continue
            if confidence not in {"HIGH", "MEDIUM"}:
                continue
            try:
                score = float(score)
            except (TypeError, ValueError):
                score = 0.0
            signals.append({"knowledge": knowledge.strip(), "confidence": confidence, "score": max(0.0, min(1.0, score))})
        return signals

    @classmethod
    def outcome_signals(cls, outcomes):
        if not isinstance(outcomes, dict):
            return {}
        signals = {}
        success_rate = outcomes.get("success_rate")
        try:
            success_rate = float(success_rate)
        except (TypeError, ValueError):
            signals["outcome_quality"] = "UNKNOWN"
            return signals
        if success_rate < 0.0 or success_rate > 1.0:
            signals["outcome_quality"] = "UNKNOWN"
        elif success_rate >= 0.80:
            signals["outcome_quality"] = "SUCCESS_PATTERN"
        elif success_rate < 0.50:
            signals["outcome_quality"] = "FAILURE_PATTERN"
        else:
            signals["outcome_quality"] = "MIXED_PATTERN"
        signals["success_rate"] = success_rate
        return signals

    @classmethod
    def behavior_signals(cls, patterns):
        if not isinstance(patterns, list):
            return []
        signals = []
        for pattern in patterns:
            if not isinstance(pattern, dict):
                continue
            if pattern.get("pattern_type") != "REPEATED_ACTION":
                continue
            action = pattern.get("action")
            confidence = pattern.get("confidence")
            occurrences = pattern.get("occurrences", 0)
            if not isinstance(action, str) or not action.strip():
                continue
            try:
                occurrences = int(occurrences)
            except (TypeError, ValueError):
                continue
            if occurrences < 2:
                continue
            if confidence == "HIGH":
                signal = "REINFORCE_ACTION"
            elif confidence == "MEDIUM":
                signal = "CONSIDER_ACTION_HISTORY"
            else:
                continue
            signals.append({"action": action.strip(), "signal": signal, "occurrences": occurrences, "confidence": confidence})
        return signals

    @classmethod
    def preference_signals(cls, preferences):
        if not isinstance(preferences, dict):
            return {}
        allowed = {"interaction_style", "response_style", "workflow_style"}
        return {key: value for key, value in preferences.items() if key in allowed}

    @classmethod
    def safe_signals(cls, reasoning):
        if not isinstance(reasoning, AdaptiveReasoning):
            return {}
        return {
            "memory_signals": cls.memory_signals(reasoning.memories),
            "outcome_signals": cls.outcome_signals(reasoning.outcomes),
            "behavior_signals": cls.behavior_signals(reasoning.patterns),
            "preference_signals": cls.preference_signals(reasoning.preferences),
        }
