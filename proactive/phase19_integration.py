from pathlib import Path
import json

from proactive.adaptive_reasoning import AdaptiveReasoning
from proactive.learning_safety import LearningSafety


class Phase19Integration:

    def __init__(self, context=None, memories=None, outcomes=None, patterns=None, preferences=None, safety=None):
        self.context = context if isinstance(context, dict) else {}
        self.memories = memories if isinstance(memories, list) else []
        self.outcomes = outcomes if isinstance(outcomes, dict) else {}
        self.patterns = patterns if isinstance(patterns, list) else []
        self.preferences = preferences if isinstance(preferences, dict) else {}
        self.safety = safety if isinstance(safety, dict) else {}

    def to_dict(self):
        return {
            "context": self.context,
            "memories": self.memories,
            "outcomes": self.outcomes,
            "patterns": self.patterns,
            "preferences": self.preferences,
            "safety": self.safety,
        }

    @classmethod
    def create(cls, context=None, memories=None, outcomes=None, patterns=None, preferences=None, safety=None):
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
        if safety is not None and not isinstance(safety, dict):
            return None
        return cls(context, memories, outcomes, patterns, preferences, safety)

    @classmethod
    def assemble(cls, context, memories=None, outcomes=None, patterns=None, preferences=None, safety=None):
        if not isinstance(context, dict):
            return None
        return cls(context=context, memories=memories, outcomes=outcomes, patterns=patterns, preferences=preferences, safety=safety)

    def adaptive_reasoning(self):
        reasoning = AdaptiveReasoning.create(self.context, self.memories, self.outcomes, self.patterns, self.preferences)
        if reasoning is None:
            return None
        return reasoning

    def safety_gate(self, learning):
        return LearningSafety.enforce(learning)

    def final_output(self, learning=None):
        safety = self.safety_gate(learning) if learning is not None else self.safety
        if not isinstance(safety, dict):
            safety = {"status": LearningSafety.BLOCKED, "allowed": False}
        if safety.get("status") != LearningSafety.SAFE or safety.get("allowed") is not True:
            return {"status": safety.get("status", LearningSafety.BLOCKED), "allowed": False, "reasoning": None}
        reasoning = self.adaptive_reasoning()
        if reasoning is None:
            return {"status": LearningSafety.BLOCKED, "allowed": False, "reasoning": None}
        return {"status": LearningSafety.SAFE, "allowed": True, "reasoning": reasoning.to_dict()}


INTEGRATION_FILE = Path(__file__).resolve().parent.parent / "data" / "phase19_integration.json"


def save_integration(integration, file=None):
    target = Path(file) if file else INTEGRATION_FILE
    if not isinstance(integration, Phase19Integration):
        return False
    data = integration.to_dict()
    if isinstance(data.get("safety"), dict):
        data["safety"] = {
            "status": data["safety"].get("status"),
            "allowed": data["safety"].get("allowed") is True,
        }
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_integration(file=None):
    target = Path(file) if file else INTEGRATION_FILE
    try:
        if not target.exists():
            return None
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None
        return Phase19Integration.create(data.get("context"), data.get("memories"), data.get("outcomes"), data.get("patterns"), data.get("preferences"), data.get("safety"))
    except Exception:
        return None
