import unittest
from unittest.mock import patch

from proactive.state_manager import StateManager
from intent_dispatcher import IntentDispatcher
from security.approval_manager import ApprovalManager


class TestPlanAuthorizationStops(unittest.TestCase):
    def test_dispatcher_records_missing_confirmation_as_failure(self):
        dispatcher = IntentDispatcher(ApprovalManager())

        response = dispatcher.execute({
            "intent": "lock_computer",
            "parameters": {},
        })

        self.assertIn("confirmation", response.lower())
        self.assertEqual(
            dispatcher.last_authorization_result["status"], "CONFIRM"
        )
        self.assertTrue(
            dispatcher.last_execution_error.startswith("AuthorizationError:")
        )

    def test_plan_records_blocked_task_and_does_not_run_later_tasks(self):
        from brain import Brain

        manager = StateManager()
        manager.begin("run planned tasks")
        manager.transition("PLANNING")
        manager.transition("EXECUTING")

        class FakeDispatcher:
            def __init__(self):
                self.calls = []
                self.last_execution_error = None
                self.last_authorization_result = None

            def execute(self, task):
                self.calls.append(task["intent"])

                if task["intent"] == "blocked":
                    self.last_authorization_result = {
                        "status": "CONFIRM",
                        "allowed": False,
                        "requires_confirmation": True,
                        "reason": "Fresh confirmation required",
                    }
                    self.last_execution_error = (
                        "AuthorizationError: fresh trusted confirmation required"
                    )
                    return (
                        "That action requires a fresh, trusted "
                        "confirmation before it can run."
                    )

                self.last_authorization_result = {
                    "status": "ALLOW",
                    "allowed": True,
                    "requires_confirmation": False,
                    "reason": "Allowed",
                }
                self.last_execution_error = None
                return "completed"

        brain = Brain.__new__(Brain)
        brain.state_manager = manager
        fake_dispatcher = FakeDispatcher()

        plan = {
            "tasks": [
                {"intent": "first", "parameters": {}},
                {"intent": "blocked", "parameters": {}},
                {"intent": "must_not_run", "parameters": {}},
            ]
        }

        with patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("brain.conversation.add_assistant"):
            result = brain.execute_plan(plan)

        self.assertTrue(result)
        self.assertEqual(fake_dispatcher.calls, ["first", "blocked"])

        results = manager.current().execution_results
        self.assertEqual(len(results), 2)
        self.assertIsNone(results[0]["error"])
        self.assertTrue(
            results[1]["error"].startswith("AuthorizationError:")
        )
        self.assertEqual(
            manager.evaluate_execution_results(), "partial"
        )


if __name__ == "__main__":
    unittest.main()
