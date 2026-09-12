"""FRIDAY V3 - Phase 23.1 Parallel Reasoning."""

from proactive.reasoning_strategy import ReasoningStrategy
from proactive.reasoning_quality import ReasoningQuality


class ParallelReasoning:

    def __init__(self):
        self.strategies = tuple(ReasoningStrategy.TYPES)

    def available_strategies(self):
        return list(self.strategies)

    @staticmethod
    def _safe_context(context):
        return dict(context) if isinstance(context, dict) else {}

    @staticmethod
    def _build_path(strategy, context):
        return {
            "strategy": strategy,
            "context": dict(context),
            "reasoning_mode": strategy,
            "independent": True,
        }

    @classmethod
    def generate(cls, context):
        context = cls._safe_context(context)
        return [cls._build_path(strategy, context) for strategy in ReasoningStrategy.TYPES]

    @classmethod
    def assess_path(cls, path):
        if not isinstance(path, dict):
            return None
        strategy = path.get("strategy")
        context = path.get("context", {})
        if strategy not in ReasoningStrategy.TYPES or not isinstance(context, dict):
            return None
        quality = ReasoningQuality.create(
            completeness=1.0,
            consistency=1.0,
            outcome_alignment=0.5,
            safety=1.0 if strategy == ReasoningStrategy.CAUTIOUS else 0.5,
        )
        return {"strategy": strategy, "quality": quality.to_dict() if quality else None}

    @classmethod
    def generate_assessed(cls, context):
        return [{"path": path, "assessment": cls.assess_path(path)} for path in cls.generate(context)]

    @classmethod
    def validate_paths(cls, paths):
        if not isinstance(paths, list):
            return False
        for path in paths:
            if not isinstance(path, dict):
                return False
            if path.get("strategy") not in ReasoningStrategy.TYPES:
                return False
            if path.get("independent") is not True:
                return False
        return True


parallel_reasoning = ParallelReasoning()
