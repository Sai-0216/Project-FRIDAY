import unittest
from unittest.mock import Mock, patch

from brain import Brain
from proactive.state_manager import StateManager


class TestPlanStopsAfterError(unittest.TestCase):
    def make_manager(self):
        manager = StateManager()
        manager.begin("run planned tasks")
        manager.transition("PLANNING")
        manager.transition("EXECUTING")
        return manager

    def test_failure_prevents_later_tasks_from_running(self):
        brain = Brain.__new__(Brain)
        brain.state_manager = self.make_manager()

        fake_dispatcher = Mock()

        def execute_task(task):
            if task["intent"] == "second":
                fake_dispatcher.last_execution_error = (
                    "RuntimeError('second failed')"
                )
                return "Task failed"

            fake_dispatcher.last_execution_error = None
            return "Task completed"

        fake_dispatcher.execute.side_effect = execute_task

        plan = {
            "tasks": [
                {"intent": "first", "parameters": {}},
                {"intent": "second", "parameters": {}},
                {"intent": "third", "parameters": {}},
            ]
        }

        with patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("brain.conversation.add_assistant"), \
             patch("builtins.print"):
            result = brain.execute_plan(plan)

        self.assertTrue(result)
        self.assertEqual(fake_dispatcher.execute.call_count, 2)

        executed_tasks = [
            call.args[0]["intent"]
            for call in fake_dispatcher.execute.call_args_list
        ]
        self.assertEqual(executed_tasks, ["first", "second"])

        results = brain.state_manager.current().execution_results
        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0]["error"])
        self.assertEqual(
            results[1]["error"],
            "RuntimeError('second failed')",
        )


if __name__ == "__main__":
    unittest.main()
