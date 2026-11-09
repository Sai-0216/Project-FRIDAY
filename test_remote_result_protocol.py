import unittest
from types import SimpleNamespace

from network.result_protocol import build_result


class TestRemoteResultProtocol(unittest.TestCase):
    DEVICE = "friday-test"
    COMMAND = "open calculator"
    PREVIOUS = "2026-11-09T10:00:00"
    CURRENT = "2026-11-09T10:00:01"

    def make_brain(self, **overrides):
        snapshot = {
            "command": self.COMMAND,
            "started_at": self.CURRENT,
            "lifecycle": "IDLE",
            "outcome": "completed",
            "execution_results": [],
            "error": "",
        }
        snapshot.update(overrides)

        manager = SimpleNamespace(snapshot=lambda: snapshot)
        return SimpleNamespace(state_manager=manager)

    def build(self, brain, previous=None):
        return build_result(
            self.DEVICE,
            self.COMMAND,
            brain,
            previous_started_at=(
                self.PREVIOUS if previous is None else previous
            ),
        )

    def test_fresh_completed_execution_reports_success(self):
        result = self.build(self.make_brain())
        self.assertTrue(result["success"])
        self.assertEqual(result["outcome"], "completed")
        self.assertEqual(result["error"], "")

    def test_failed_execution_reports_failure(self):
        result = self.build(
            self.make_brain(outcome="failed", error="Execution failed")
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Execution failed")

    def test_partial_execution_reports_failure(self):
        result = self.build(self.make_brain(outcome="partial"))
        self.assertFalse(result["success"])

    def test_stale_execution_reports_failure(self):
        result = self.build(
            self.make_brain(started_at=self.PREVIOUS)
        )
        self.assertFalse(result["success"])
        self.assertIn("fresh execution", result["error"])

    def test_mismatched_command_reports_failure(self):
        result = self.build(self.make_brain(command="different command"))
        self.assertFalse(result["success"])
        self.assertIn("does not match", result["error"])

    def test_unfinished_execution_reports_failure(self):
        result = self.build(
            self.make_brain(lifecycle="EXECUTING", outcome="running")
        )
        self.assertFalse(result["success"])

    def test_missing_state_reports_failure(self):
        brain = SimpleNamespace(state_manager=None)
        result = self.build(brain)
        self.assertFalse(result["success"])
        self.assertIn("fresh execution", result["error"])


if __name__ == "__main__":
    unittest.main()
