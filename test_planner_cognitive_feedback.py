import json
import unittest
from unittest.mock import patch

from planner import Planner


class TestPlannerCognitiveFeedback(unittest.TestCase):
    def setUp(self):
        self.planner = Planner()

    def test_empty_history_returns_no_feedback(self):
        with patch("planner.episodic_memory.search", return_value=[]):
            self.assertEqual(self.planner._cognitive_feedback("open calculator"), "")

    def test_feedback_uses_real_newlines(self):
        history = [{
            "event": "open calculator",
            "context": {"intent": "open_app"},
            "outcome": "completed",
        }]

        with patch("planner.episodic_memory.search", return_value=history), \
             patch.object(self.planner, "_cognitive_pattern", return_value=None):
            feedback = self.planner._cognitive_feedback("open calculator")

        self.assertTrue(
            feedback.startswith("\nRELEVANT PAST EXECUTION FEEDBACK:\n")
        )
        self.assertFalse(feedback.startswith("\\nRELEVANT"))

    def test_repeated_failures_recommend_avoiding_failed_strategy(self):
        history = [
            {
                "event": "open calculator",
                "context": {"intent": "open_app"},
                "outcome": "failed",
            },
            {
                "event": "open calculator",
                "context": {"intent": "open_app"},
                "outcome": "failed",
            },
        ]

        with patch("planner.episodic_memory.recent", return_value=history):
            pattern = self.planner._cognitive_pattern("  OPEN   CALCULATOR ")

        self.assertEqual(pattern["recommendation"], "avoid_failed_strategy")
        self.assertIsNone(pattern["preferred_strategy"])
        self.assertEqual(pattern["preferred_strategy_reliability"], 0.0)
        self.assertEqual(pattern["failure_rate"], 1.0)

    def test_conflict_resolution_returns_none_when_all_strategies_fail(self):
        history = [
            {
                "event": "perform task",
                "context": {"intent": "failing_strategy_a"},
                "outcome": "failed",
            },
            {
                "event": "perform task",
                "context": {"intent": "failing_strategy_b"},
                "outcome": "failed",
            },
        ]

        with patch("planner.episodic_memory.recent", return_value=history):
            pattern = self.planner._cognitive_pattern("perform task")

        self.assertIsNone(pattern["preferred_strategy"])
        self.assertIsNone(pattern["conflict_resolution"])

    def test_preferred_strategy_uses_reliability_not_frequency(self):
        history = (
            [
                {
                    "event": "perform task",
                    "context": {"intent": "frequent_strategy"},
                    "outcome": "failed",
                }
                for _ in range(4)
            ]
            + [
                {
                    "event": "perform task",
                    "context": {"intent": "reliable_strategy"},
                    "outcome": "completed",
                }
                for _ in range(2)
            ]
        )

        with patch("planner.episodic_memory.recent", return_value=history):
            pattern = self.planner._cognitive_pattern("perform task")

        self.assertEqual(pattern["strategy_counts"]["frequent_strategy"], 4)
        self.assertEqual(pattern["strategy_counts"]["reliable_strategy"], 2)
        self.assertEqual(pattern["preferred_strategy"], "reliable_strategy")
        self.assertEqual(
            pattern["preferred_strategy_reliability"],
            1.0,
        )

    def test_feedback_prefers_reliable_strategy_and_avoids_failing_one(self):
        history = (
            [
                {
                    "event": "perform task",
                    "context": {"intent": "frequent_strategy"},
                    "outcome": "failed",
                }
                for _ in range(4)
            ]
            + [
                {
                    "event": "perform task",
                    "context": {"intent": "reliable_strategy"},
                    "outcome": "completed",
                }
                for _ in range(2)
            ]
        )

        with patch("planner.episodic_memory.search", return_value=history), \
             patch("planner.episodic_memory.recent", return_value=history):
            feedback = self.planner._cognitive_feedback("perform task")

        marker = "RELEVANT PAST EXECUTION FEEDBACK:\n"
        payload = json.loads(feedback.split(marker, 1)[1])

        self.assertEqual(
            payload["strategy_guidance"]["preferred_strategy"],
            "reliable_strategy",
        )
        self.assertTrue(payload["failure_avoidance"]["avoid"])
        self.assertEqual(
            payload["failure_avoidance"]["strategy"],
            "frequent_strategy",
        )
        self.assertEqual(payload["failure_avoidance"]["failure_rate"], 1.0)

    def test_feedback_marks_repeated_failures_for_avoidance(self):
        history = [
            {
                "event": "open calculator",
                "context": {"intent": "open_app"},
                "outcome": "failed",
            },
            {
                "event": "open calculator",
                "context": {"intent": "open_app"},
                "outcome": "failed",
            },
        ]

        with patch("planner.episodic_memory.search", return_value=history), \
             patch("planner.episodic_memory.recent", return_value=history):
            feedback = self.planner._cognitive_feedback("open calculator")

        marker = "RELEVANT PAST EXECUTION FEEDBACK:\n"
        payload = json.loads(feedback.split(marker, 1)[1])

        self.assertIsNone(payload["strategy_guidance"])
        self.assertEqual(
            payload["pattern"]["recommendation"],
            "avoid_failed_strategy",
        )
        self.assertTrue(payload["failure_avoidance"]["avoid"])
        self.assertEqual(payload["failure_avoidance"]["strategy"], "open_app")


if __name__ == "__main__":
    unittest.main()
