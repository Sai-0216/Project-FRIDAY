"""
Project FRIDAY
Phase 18.14.1

Environment Pattern Analyzer

Detects repeated environmental conditions from historical
snapshots. This module is analytical only and does not emit
events or execute actions.
"""

from proactive.environment_memory import environment_memory
from datetime import datetime
from modules.environment import environment


class EnvironmentPatternAnalyzer:

    MIN_OCCURRENCES = 3
    RECENT_WINDOW = 5

    def _condition_types(self, state):
        if not isinstance(state, dict):
            return set()

        cpu = state.get("cpu_percent")
        ram = state.get("ram_percent")
        disk = state.get("disk_percent")
        battery = state.get("battery")
        wifi = state.get("wifi_status")

        types = set()

        if (
            cpu is not None
            and ram is not None
            and cpu >= environment.CPU_HIGH
            and ram >= environment.RAM_HIGH
        ):
            types.add("RESOURCE_PRESSURE")

        if (
            disk is not None
            and ram is not None
            and disk >= environment.DISK_HIGH
            and ram >= environment.RAM_HIGH
        ):
            types.add("STORAGE_MEMORY_PRESSURE")

        if battery is not None:
            battery_percent = battery.get("percent")
            charging = battery.get("charging", False)

            if (
                battery_percent is not None
                and battery_percent <= environment.BATTERY_LOW
                and not charging
            ):
                types.add("BATTERY_DISCHARGE")

        if wifi in ("disconnected", "disabled"):
            types.add("NETWORK_UNAVAILABLE")

        return types

    def analyze(self, history=None):
        if history is None:
            history = environment_memory.history()

        if not isinstance(history, list):
            return []

        counts = {}

        for snapshot in history:
            for condition_type in self._condition_types(snapshot):
                counts[condition_type] = (
                    counts.get(condition_type, 0) + 1
                )

        patterns = []

        total_samples = len(history)
        recent_history = history[-self.RECENT_WINDOW:]
        recent_samples = len(recent_history)

        recent_counts = {}

        for snapshot in recent_history:
            for condition_type in self._condition_types(snapshot):
                recent_counts[condition_type] = (
                    recent_counts.get(condition_type, 0) + 1
                )

        now = datetime.now()

        for condition_type, occurrences in counts.items():
            frequency = (
                occurrences / total_samples
                if total_samples > 0
                else 0.0
            )

            recent_occurrences = recent_counts.get(
                condition_type,
                0
            )

            last_occurrence_age_seconds = None

            for snapshot in reversed(history):
                if condition_type in self._condition_types(snapshot):
                    timestamp = snapshot.get("timestamp")

                    if timestamp:
                        try:
                            observed_at = datetime.fromisoformat(
                                str(timestamp)
                            )
                            last_occurrence_age_seconds = max(
                                0.0,
                                (now - observed_at).total_seconds()
                            )
                        except (TypeError, ValueError):
                            last_occurrence_age_seconds = None
                    break

            if last_occurrence_age_seconds is None:
                recency_score = 0.0
            else:
                age_hours = last_occurrence_age_seconds / 3600.0
                recency_score = 1.0 / (1.0 + age_hours)

            recent_frequency = (
                recent_occurrences / recent_samples
                if recent_samples > 0
                else 0.0
            )

            if frequency >= 0.8:
                strength = "HIGH"
            elif frequency >= 0.5:
                strength = "MEDIUM"
            else:
                strength = "LOW"

            persistent = occurrences >= self.MIN_OCCURRENCES

            age_seconds = (
                round(last_occurrence_age_seconds)
                if last_occurrence_age_seconds is not None
                else None
            )

            recency_high = (
                age_seconds is not None
                and age_seconds <= 3600
            )

            recency_medium = (
                age_seconds is not None
                and age_seconds <= 10800
            )

            if (
                persistent
                and recent_frequency >= 0.8
                and recency_high
            ):
                confidence = "HIGH"
            elif (
                persistent
                and recent_frequency >= 0.5
                and recency_medium
            ):
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            patterns.append({
                "type": condition_type,
                "occurrences": occurrences,
                "samples": total_samples,
                "frequency": round(frequency, 3),
                "recent_occurrences": recent_occurrences,
                "recent_samples": recent_samples,
                "recent_frequency": round(recent_frequency, 3),
                "last_occurrence_age_seconds": (
                    round(last_occurrence_age_seconds, 3)
                    if last_occurrence_age_seconds is not None
                    else None
                ),
                "recency_score": round(recency_score, 3),
                "persistent": persistent,
                "strength": strength,
                "confidence": confidence,
            })

        return sorted(
            patterns,
            key=lambda pattern: pattern["type"]
        )


environment_patterns = EnvironmentPatternAnalyzer()
