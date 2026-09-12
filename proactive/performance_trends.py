class PerformanceTrends:
    """Identify performance trends from weighted execution experiences."""

    TRENDS = ("improving", "declining", "stable", "insufficient")

    def analyze(self, experiences):
        if not self.validate_experiences(experiences):
            return None

        if len(experiences) < 2:
            return {
                "trend": "insufficient",
                "average_weight": self._average(experiences),
                "recent_weight": self._average(experiences),
                "change": 0.0,
                "sample_size": len(experiences),
            }

        midpoint = len(experiences) // 2
        earlier = experiences[:midpoint]
        recent = experiences[midpoint:]

        earlier_weight = self._average(earlier)
        recent_weight = self._average(recent)
        change = recent_weight - earlier_weight

        if change > 0.1:
            trend = "improving"
        elif change < -0.1:
            trend = "declining"
        else:
            trend = "stable"

        result = {
            "trend": trend,
            "average_weight": self._average(experiences),
            "recent_weight": recent_weight,
            "change": change,
            "sample_size": len(experiences),
        }

        return result if self.validate(result) else None

    def _average(self, experiences):
        if not experiences:
            return 0.0
        return sum(item["weight"] for item in experiences) / len(experiences)

    def validate_experiences(self, experiences):
        if not isinstance(experiences, list):
            return False
        for item in experiences:
            if not isinstance(item, dict):
                return False
            weight = item.get("weight")
            if not isinstance(weight, (int, float)) or not 0.0 <= weight <= 1.0:
                return False
        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if result.get("trend") not in self.TRENDS:
            return False
        for field in ("average_weight", "recent_weight", "change"):
            value = result.get(field)
            if not isinstance(value, (int, float)):
                return False
        if not isinstance(result.get("sample_size"), int) or result["sample_size"] < 0:
            return False
        return True


performance_trends = PerformanceTrends()
