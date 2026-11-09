import json
from pathlib import Path
from threading import RLock


class SelfCorrection:
    STATES = ("on_track", "needs_correction", "corrected", "blocked")

    PREPARE = "PREPARE"
    VERIFY = "VERIFY"
    CHANGE_STRATEGY = "CHANGE_STRATEGY"
    MAINTAIN = "MAINTAIN"
    NONE = "NONE"

    ACTIONS = {PREPARE, VERIFY, CHANGE_STRATEGY, MAINTAIN, NONE}
    FORBIDDEN_KEYS = {
        "autonomy_level",
        "execution_permissions",
        "trusted_actions",
        "authorization",
    }

    def __init__(self, action=None, target=None, reason=None,
                 confidence="LOW", evidence=None):
        self.action = action if action in self.ACTIONS else None
        self.target = target if isinstance(target, str) else None
        self.reason = reason if isinstance(reason, str) else None
        self.confidence = (
            confidence if confidence in {"HIGH", "MEDIUM", "LOW"} else "LOW"
        )
        self.evidence = evidence if isinstance(evidence, dict) else {}
        self.name = "self_correction"

    # Existing progress-assessment API

    def assess(self, expected_progress, actual_progress):
        try:
            expected = float(expected_progress)
            actual = float(actual_progress)
        except (TypeError, ValueError):
            return None

        gap = expected - actual
        needs_correction = gap > 0.1

        return {
            "expected_progress": expected,
            "actual_progress": actual,
            "gap": gap,
            "needs_correction": needs_correction,
            "state": "needs_correction" if needs_correction else "on_track",
        }

    def create_correction(self, assessment, correction):
        if not isinstance(assessment, dict) or not assessment.get("needs_correction"):
            return None
        if not isinstance(correction, str) or not correction.strip():
            return None

        return {
            "reason": "progress_below_expectation",
            "correction": correction.strip(),
            "state": "corrected",
        }

    def apply(self, plan, correction):
        if not isinstance(plan, dict) or not isinstance(correction, dict):
            return False

        plan["correction"] = correction.get("correction")
        plan["correction_state"] = correction.get("state", "corrected")
        return True

    def validate_assessment(self, assessment):
        if not isinstance(assessment, dict):
            return False

        required = (
            "expected_progress",
            "actual_progress",
            "gap",
            "needs_correction",
            "state",
        )
        if any(key not in assessment for key in required):
            return False

        return assessment.get("state") in ("on_track", "needs_correction")

    def validate_correction(self, correction):
        if not isinstance(correction, dict):
            return False
        if not isinstance(correction.get("correction"), str):
            return False
        if not correction["correction"]:
            return False

        return correction.get("state") == "corrected"

    # Restored compatibility API

    @classmethod
    def create(cls, action, target=None, reason=None,
               confidence="LOW", evidence=None):
        if action not in cls.ACTIONS:
            return None
        if target is not None and not isinstance(target, str):
            return None
        if reason is not None and not isinstance(reason, str):
            return None
        if confidence not in {"HIGH", "MEDIUM", "LOW"}:
            return None
        if evidence is not None and not isinstance(evidence, dict):
            return None

        return cls(action, target, reason, confidence, evidence)

    def to_dict(self):
        return {
            "action": self.action,
            "target": self.target,
            "reason": self.reason,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }

    def is_valid(self):
        return self.action in self.ACTIONS

    @classmethod
    def from_candidate(cls, candidate):
        if not isinstance(candidate, dict):
            return None

        candidate_type = candidate.get("type")
        target = candidate.get("target")
        priority = candidate.get("priority")
        evidence = candidate.get("evidence")
        if not isinstance(evidence, dict):
            evidence = {}

        if candidate_type == "ERROR":
            if target is None:
                return None
            action = cls.CHANGE_STRATEGY if priority == "HIGH" else cls.VERIFY
            confidence = "HIGH" if priority == "HIGH" else "MEDIUM"
            reason = "Error evidence indicates that the current approach should be corrected."
            return cls.create(action, target, reason, confidence, evidence)

        if candidate_type == "DECISION":
            action = cls.CHANGE_STRATEGY if priority == "HIGH" else cls.VERIFY
            confidence = "HIGH" if priority == "HIGH" else "MEDIUM"
            reason = "Decision quality indicates that the strategy should be reviewed."
            return cls.create(action, target, reason, confidence, evidence)

        if candidate_type == "REASONING":
            action = cls.PREPARE if priority == "LOW" else cls.VERIFY
            confidence = "LOW" if priority == "LOW" else "MEDIUM"
            reason = "Reasoning quality indicates that the reasoning process should be reviewed."
            return cls.create(action, target, reason, confidence, evidence)

        return None

    @classmethod
    def safety_validate(cls, correction):
        if isinstance(correction, cls):
            data = correction.to_dict()
        elif isinstance(correction, dict):
            data = correction
        else:
            return "BLOCKED"

        # Use the existing centralized safety boundary.
        from proactive.improvement_safety import ImprovementSafety
        return ImprovementSafety.validate(data)

    @classmethod
    def apply_strategy_correction(cls, correction, available_strategies):
        if not isinstance(available_strategies, (list, set, tuple)):
            return None
        if not isinstance(correction, cls):
            return None
        if correction.action != cls.CHANGE_STRATEGY:
            return None
        if correction.target not in available_strategies:
            return None
        if cls.safety_validate(correction) != "SAFE":
            return None

        # This creates a proposal only. It does not change the active strategy.
        return {
            "strategy": correction.target,
            "status": "PROPOSED",
            "confidence": correction.confidence,
            "evidence": correction.evidence,
        }

    @staticmethod
    def confidence_score(confidence):
        return {
            "HIGH": 1.0,
            "MEDIUM": 0.67,
            "LOW": 0.33,
        }.get(confidence, 0.0)

    @classmethod
    def correction_confidence(cls, correction):
        if isinstance(correction, cls):
            confidence = correction.confidence
        elif isinstance(correction, dict):
            confidence = correction.get("confidence")
        else:
            return "LOW"

        return confidence if confidence in {"HIGH", "MEDIUM", "LOW"} else "LOW"

    @classmethod
    def preview_strategy_correction(cls, correction, current_strategy,
                                    available_strategies):
        if not isinstance(current_strategy, str):
            return None
        if not isinstance(available_strategies, (list, set, tuple)):
            return None
        if not isinstance(correction, cls):
            return None

        proposal = cls.apply_strategy_correction(
            correction, available_strategies
        )
        if proposal is None:
            return None

        return {
            "status": "PREVIEW",
            "applied": False,
            "current_strategy": current_strategy,
            "proposed_strategy": proposal["strategy"],
            "confidence": proposal["confidence"],
            "evidence": proposal["evidence"],
        }


CORRECTION_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "self_corrections.json"
)
MAX_CORRECTIONS = 500


class SelfCorrectionStore:
    def __init__(self, file=None):
        self.file = Path(file) if file else CORRECTION_FILE
        self.records = []
        self.lock = RLock()
        self._load()

    def _load(self):
        with self.lock:
            try:
                if not self.file.exists():
                    self.records = []
                    return

                with self.file.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)

                self.records = (
                    data[-MAX_CORRECTIONS:]
                    if isinstance(data, list)
                    else []
                )
            except (OSError, ValueError, TypeError):
                self.records = []

    def _save(self):
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            temp = self.file.with_suffix(self.file.suffix + ".tmp")

            with temp.open("w", encoding="utf-8") as handle:
                json.dump(
                    self.records[-MAX_CORRECTIONS:],
                    handle,
                    indent=4,
                    ensure_ascii=False,
                )

            temp.replace(self.file)
            return True
        except (OSError, TypeError, ValueError):
            return False

    def record(self, correction):
        if isinstance(correction, SelfCorrection):
            data = correction.to_dict()
        elif isinstance(correction, dict):
            data = dict(correction)
        else:
            return False

        if self.safety_validate(data) != "SAFE":
            return False

        with self.lock:
            self.records.append(data)
            self.records = self.records[-MAX_CORRECTIONS:]

            if self._save():
                return True

            self.records.pop()
            return False

    def recent(self, limit=20):
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            return []

        with self.lock:
            return list(self.records[-limit:])

    def count(self):
        with self.lock:
            return len(self.records)

    @staticmethod
    def safety_validate(correction):
        return SelfCorrection.safety_validate(correction)


self_correction = SelfCorrection()
