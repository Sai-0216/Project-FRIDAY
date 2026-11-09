
"""
Project FRIDAY
Phase 18.9.2

Environment Trend Analyzer

Reads historical environment snapshots and
identifies simple directional trends.

This module does NOT create events or notifications.
It only analyzes stored history.
"""

from proactive.environment_memory import (
    environment_memory
)


class EnvironmentTrendAnalyzer:

    # ========================================
    # CONFIGURATION
    # ========================================

    MIN_SAMPLES = 3

    TREND_DELTA = 5.0

    # ========================================
    # VALUE EXTRACTION
    # ========================================

    def _values(
        self,
        history,
        key
    ):
        """
        Extract numeric values for a metric.
        Invalid or missing values are ignored.
        """

        values = []

        for snapshot in history:

            value = snapshot.get(
                key
            )

            if isinstance(
                value,
                (int, float)
            ):

                values.append(
                    float(value)
                )

        return values

    # ========================================
    # TREND
    # ========================================

    def _trend(
        self,
        values
    ):
        """
        Determine the directional trend of a
        numeric sequence.
        """

        if len(values) < self.MIN_SAMPLES:

            return "INSUFFICIENT_DATA"

        first = values[0]
        last = values[-1]

        delta = last - first

        if delta >= self.TREND_DELTA:

            return "INCREASING"

        if delta <= -self.TREND_DELTA:

            return "DECREASING"

        return "STABLE"

    # ========================================
    # ANALYZE HISTORY
    # ========================================

    def analyze(
        self,
        history=None
    ):
        """
        Analyze environment history for
        CPU, RAM, disk, and battery trends.
        """

        if history is None:

            history = (
                environment_memory.history()
            )

        if not isinstance(
            history,
            list
        ):

            return {}

        metrics = {
            "cpu_percent": "CPU",
            "ram_percent": "RAM",
            "disk_percent": "DISK",
        }

        trends = {}

        for key, name in metrics.items():

            values = self._values(
                history,
                key
            )

            trends[key] = {
                "name": name,
                "samples": len(values),
                "trend": self._trend(
                    values
                ),
                "first": (
                    values[0]
                    if values
                    else None
                ),
                "last": (
                    values[-1]
                    if values
                    else None
                ),
                "delta": (
                    values[-1] - values[0]
                    if len(values) >= 2
                    else None
                ),
            }

        return trends

    # ========================================
    # SUMMARY
    # ========================================

    def summary(
        self,
        history=None
    ):
        """
        Return human-readable trend summaries.
        """

        trends = self.analyze(
            history
        )

        summaries = []

        for metric in trends.values():

            name = metric["name"]
            trend = metric["trend"]
            delta = metric["delta"]

            if trend == "INCREASING":

                summaries.append(
                    f"{name} usage is increasing."
                )

            elif trend == "DECREASING":

                summaries.append(
                    f"{name} usage is decreasing."
                )

            elif trend == "STABLE":

                summaries.append(
                    f"{name} usage is relatively stable."
                )

        return summaries


# ============================================
# ENVIRONMENT TREND INSTANCE
# ============================================

environment_trends = (
    EnvironmentTrendAnalyzer()
)