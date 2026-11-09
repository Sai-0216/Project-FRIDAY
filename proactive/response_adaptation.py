from pathlib import Path
import json


class ResponseAdaptation:

    @classmethod
    def signals(cls, preferences):
        if not isinstance(preferences, list):
            return {}
        signals = {}
        for preference in preferences:
            if not isinstance(preference, dict):
                continue
            text = preference.get("preference")
            category = preference.get("category")
            confidence = preference.get("confidence")
            if not isinstance(text, str) or not text.strip():
                continue
            if confidence not in {"HIGH", "MEDIUM"}:
                continue
            category = category or "general"
            signals.setdefault(category, []).append(text.strip())
        return signals

    @classmethod
    def rules(cls, signals):
        if not isinstance(signals, dict):
            return {}
        rules = {}
        interaction = signals.get("interaction", [])
        response = signals.get("response", [])
        workflow = signals.get("workflow", [])
        for text in interaction:
            value = text.lower()
            if "step-by-step" in value or "step by step" in value:
                rules["interaction_style"] = "STEP_BY_STEP"
        for text in response:
            value = text.lower()
            if "concise" in value:
                rules["response_style"] = "CONCISE"
            elif "detailed" in value:
                rules["response_style"] = "DETAILED"
        for text in workflow:
            value = text.lower()
            if "confirmation" in value or "confirm" in value:
                rules["workflow_style"] = "CONFIRMATION_REQUIRED"
        return rules

    @classmethod
    def personalize(cls, preferences):
        signals = cls.signals(preferences)
        rules = cls.rules(signals)
        return {"signals": signals, "rules": rules}

    @classmethod
    def safe_rules(cls, profile):
        if not isinstance(profile, dict):
            return {}
        rules = profile.get("rules", {})
        if not isinstance(rules, dict):
            return {}
        allowed = {"interaction_style", "response_style", "workflow_style"}
        return {key: value for key, value in rules.items() if key in allowed}


ADAPTATION_FILE = Path(__file__).resolve().parent.parent / "data" / "response_adaptation.json"


def save_profile(profile, file=None):
    target = Path(file) if file else ADAPTATION_FILE
    safe = ResponseAdaptation.safe_rules(profile)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump({"rules": safe}, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_profile(file=None):
    target = Path(file) if file else ADAPTATION_FILE
    try:
        if not target.exists():
            return {}
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"rules": ResponseAdaptation.safe_rules(data)}
    except Exception:
        return {}
