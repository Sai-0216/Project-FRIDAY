"""FRIDAY V3 - Phase 23.8 Consensus."""


class Consensus:

    @staticmethod
    def _safe_groups(groups):
        return groups if isinstance(groups, list) else []

    @classmethod
    def evaluate(cls, resolution):
        if not isinstance(resolution, dict):
            return {
                "consensus": False,
                "result": None,
                "confidence": 0.0,
                "support": 0,
                "total": 0,
            }

        groups = cls._safe_groups(resolution.get("groups"))
        majority = resolution.get("majority")

        if not isinstance(majority, dict):
            return {
                "consensus": False,
                "result": None,
                "confidence": 0.0,
                "support": 0,
                "total": 0,
            }

        support = majority.get("count", 0)
        total = majority.get("total", 0)
        ratio = majority.get("ratio", 0.0)

        # Consensus requires a strict majority.
        consensus = bool(groups) and ratio > 0.5

        return {
            "consensus": consensus,
            "result": majority.get("result") if consensus else None,
            "confidence": float(ratio),
            "support": support,
            "total": total,
        }

    @classmethod
    def build(cls, resolution):
        evaluation = cls.evaluate(resolution)

        return {
            "consensus": evaluation["consensus"],
            "result": evaluation["result"],
            "confidence": evaluation["confidence"],
            "support": evaluation["support"],
            "total": evaluation["total"],
            "finalized": evaluation["consensus"],
        }

    @classmethod
    def validate(cls, consensus):
        if not isinstance(consensus, dict):
            return False
        if not isinstance(consensus.get("consensus"), bool):
            return False
        if not isinstance(consensus.get("finalized"), bool):
            return False
        if consensus.get("finalized") != consensus.get("consensus"):
            return False
        if not isinstance(consensus.get("support"), int):
            return False
        if not isinstance(consensus.get("total"), int):
            return False
        if not isinstance(consensus.get("confidence"), (int, float)):
            return False
        if not 0.0 <= float(consensus["confidence"]) <= 1.0:
            return False
        return True


consensus = Consensus()
