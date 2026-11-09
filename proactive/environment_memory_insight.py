"""
Project FRIDAY
Phase 18.11.1

Environment Memory Insight

Provides a read-only view over recent environment history
and trend analysis. This module does not emit events or
execute actions.
"""

from proactive.environment_memory import environment_memory
from proactive.environment_trends import environment_trends
from proactive.environment_patterns import environment_patterns


class EnvironmentMemoryInsight:

    def recent(self, limit=None):
        history = environment_memory.history(limit)
        return {
            "samples": len(history),
            "latest": history[-1] if history else None,
            "trends": environment_trends.analyze(history),
            "summary": environment_trends.summary(history),
        }

    def interpret(self, limit=None, history=None):
        if history is None:
            insight = self.recent(limit)
        else:
            insight = {
                "samples": len(history),
                "latest": history[-1] if history else None,
                "trends": environment_trends.analyze(history),
                "summary": environment_trends.summary(history),
            }
        samples = insight["samples"]
        trends = insight["trends"]
        patterns = environment_patterns.analyze(
            history if history is not None else environment_memory.history(limit)
        )

        if samples == 0:
            status = "NO_HISTORY"

        else:
            notable = [
                metric
                for metric in trends.values()
                if metric.get("trend")
                in ("INCREASING", "DECREASING")
            ]

            if notable:
                status = "TRENDING"
            else:
                status = "INSUFFICIENT_DATA"

        notable_trends = [
            metric
            for metric in trends.values()
            if metric.get("trend")
            in ("INCREASING", "DECREASING")
        ]

        return {
            "samples": samples,
            "has_history": samples > 0,
            "status": status,
            "notable_trends": notable_trends,
            "patterns": patterns,
        }



environment_memory_insight = EnvironmentMemoryInsight()
