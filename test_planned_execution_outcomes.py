import unittest
from unittest.mock import Mock, patch

from proactive.state_manager import StateManager


class TestPlannedExecutionOutcomes(unittest.TestCase):
    def make_manager(self):
        manager = StateManager()
        manager.begin("run planned tasks")
        manager.transition("PLANNING")
        manager.transition("EXECUTING")
        return manager

    def test_all_successful_tasks_complete_as_completed(self):
        manager = self.make_manager()
        manager.add_execution_result({
            "task": {"intent": "first"},
            "response": "done",
            "error": None,
        })
        manager.add_execution_result({
            "task": {"intent": "second"},
            "response": "done",
            "error": None,
        })

        manager.complete()

        self.assertEqual(manager.state.outcome, "completed")
        self.assertEqual(manager.state.evaluation["successes"], 2)
        self.assertEqual(manager.state.evaluation["failures"], 0)

    def test_all_failed_tasks_complete_as_failed(self):
        manager = self.make_manager()
        manager.add_execution_result({
            "task": {"intent": "first"},
            "response": "friendly error",
            "error": "RuntimeError('failed')",
        })
        manager.add_execution_result({
            "task": {"intent": "second"},
            "response": "friendly error",
            "error": "RuntimeError('failed again')",
        })

        manager.complete()

        self.assertEqual(manager.state.outcome, "failed")
        self.assertEqual(manager.state.evaluation["successes"], 0)
        self.assertEqual(manager.state.evaluation["failures"], 2)

    def test_mixed_task_results_complete_as_partial(self):
        manager = self.make_manager()
        manager.add_execution_result({
            "task": {"intent": "first"},
            "response": "done",
            "error": None,
        })
        manager.add_execution_result({
            "task": {"intent": "second"},
            "response": "friendly error",
            "error": "RuntimeError('failed')",
        })

        manager.complete()

        self.assertEqual(manager.state.outcome, "partial")
        self.assertEqual(manager.state.evaluation["successes"], 1)
        self.assertEqual(manager.state.evaluation["failures"], 1)

    def test_planned_execution_records_error_for_each_task(self):
        from brain import Brain

        brain = Brain.__new__(Brain)
        brain.state_manager = self.make_manager()

        fake_dispatcher = Mock()

        def execute_task(task):
            if task.get("intent") == "second":
                fake_dispatcher.last_execution_error = "RuntimeError('second failed')"
                return "Sorry Sir, I couldn't complete that action right now."

            fake_dispatcher.last_execution_error = None
            return "first completed"

        fake_dispatcher.execute.side_effect = execute_task

        with patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("brain.conversation.add_assistant"):
            result = brain.execute_plan({
                "tasks": [
                    {"intent": "first", "parameters": {}},
                    {"intent": "second", "parameters": {}},
                ]
            })

        self.assertTrue(result)
        results = brain.state_manager.current().execution_results
        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0]["error"])
        self.assertEqual(
            results[1]["error"],
            "RuntimeError('second failed')",
        )


    def test_safe_process_preserves_failed_outcome(self):
        from brain import Brain, _safe_process

        brain = Brain.__new__(Brain)
        brain.state_manager = self.make_manager()
        brain.conversation_state = Mock()

        brain.state_manager.add_execution_result({
            "task": {"intent": "broken"},
            "response": "friendly error",
            "error": "RuntimeError('failed')",
        })
        brain.state_manager.complete()

        with patch("brain._original_process", return_value=True), \
             patch("builtins.print"):
            result = _safe_process(brain, "test command")

        self.assertTrue(result)
        self.assertEqual(brain.state_manager.current().outcome, "failed")
        self.assertEqual(brain.state_manager.current().lifecycle, "IDLE")
        brain.conversation_state.complete_turn.assert_not_called()


    def test_safe_process_classifies_mixed_plan_as_partial(self):
        from brain import Brain, _safe_process

        brain = Brain.__new__(Brain)
        brain.state_manager = self.make_manager()
        brain.conversation_state = Mock()

        fake_dispatcher = Mock()

        def execute_task(task):
            if task.get("intent") == "second":
                fake_dispatcher.last_execution_error = "RuntimeError('second failed')"
                return "Sorry Sir, I couldn't complete that action right now."

            fake_dispatcher.last_execution_error = None
            return "first completed"

        fake_dispatcher.execute.side_effect = execute_task

        plan = {
            "tasks": [
                {"intent": "first", "parameters": {}},
                {"intent": "second", "parameters": {}},
            ]
        }

        with patch("brain._original_process",
                   side_effect=lambda instance, command, source='unknown': instance.execute_plan(plan)), \
             patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("brain.conversation.add_assistant"), \
             patch("builtins.print"):
            result = _safe_process(brain, "run planned tasks")

        state = brain.state_manager.current()
        self.assertTrue(result)
        self.assertEqual(state.lifecycle, "IDLE")
        self.assertEqual(state.outcome, "partial")
        self.assertEqual(state.evaluation["successes"], 1)
        self.assertEqual(state.evaluation["failures"], 1)
        brain.conversation_state.complete_turn.assert_called_once()


if __name__ == "__main__":
    unittest.main()
