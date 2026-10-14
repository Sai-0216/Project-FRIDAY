import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from proactive.state_manager import StateManager


class TestStateManagerLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_file = Path(self.temp_dir.name) / "episodic.json"
        self.memory_patch = patch(
            "proactive.state_manager.episodic_memory"
        )
        self.memory = self.memory_patch.start()
        self.memory.record.return_value = {"saved": True}
        self.manager = StateManager()

    def tearDown(self):
        self.memory_patch.stop()
        self.temp_dir.cleanup()

    def test_empty_results_currently_complete(self):
        self.manager.begin("test command")
        self.manager.transition("EXECUTING")
        self.manager.complete()

        self.assertEqual(self.manager.current().outcome, "completed")
        self.assertEqual(self.manager.current().lifecycle, "IDLE")

    def test_repeated_complete_is_rejected_without_duplicate_learning(self):
        self.manager.begin("test command")
        self.manager.transition("EXECUTING")
        self.manager.add_execution_result({"response": "done", "error": None})

        self.manager.complete()
        with self.assertRaises(ValueError):
            self.manager.complete()

        self.assertEqual(len(self.manager.current().learning_history), 1)
        self.assertEqual(self.memory.record.call_count, 1)

    def test_repeated_fail_is_rejected_without_duplicate_learning(self):
        self.manager.begin("test command")
        self.manager.transition("EXECUTING")

        self.manager.fail("test failure")
        with self.assertRaises(ValueError):
            self.manager.fail("test failure again")

        self.assertEqual(len(self.manager.current().learning_history), 1)
        self.assertEqual(self.memory.record.call_count, 1)

    def test_learning_history_survives_next_command(self):
        self.manager.begin("first command")
        self.manager.transition("EXECUTING")
        self.manager.add_execution_result({"response": "done", "error": None})
        self.manager.complete()

        self.manager.begin("second command")

        self.assertEqual(len(self.manager.current().learning_history), 1)
        self.assertEqual(self.manager.current().command, "second command")
        self.assertEqual(self.manager.current().execution_results, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
