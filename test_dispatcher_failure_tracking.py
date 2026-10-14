import unittest
from unittest.mock import patch

from intent_dispatcher import IntentDispatcher


class TestDispatcherFailureTracking(unittest.TestCase):
    def test_exception_sets_error_and_preserves_response(self):
        dispatcher = IntentDispatcher()

        with patch.object(
            dispatcher,
            "_execute",
            side_effect=RuntimeError("simulated failure"),
        ):
            response = dispatcher.execute(
                {"intent": "open_app", "parameters": {"app": "example"}}
            )

        self.assertEqual(
            response,
            "Sorry Sir, I couldn't complete that action right now.",
        )
        self.assertEqual(
            dispatcher.last_execution_error,
            "RuntimeError('simulated failure')",
        )

    def test_success_clears_previous_error(self):
        dispatcher = IntentDispatcher()
        dispatcher.last_execution_error = "old error"

        with patch.object(dispatcher, "_execute", return_value="Action completed."):
            response = dispatcher.execute({"intent": "battery", "parameters": {}})

        self.assertEqual(response, "Action completed.")
        self.assertIsNone(dispatcher.last_execution_error)


if __name__ == "__main__":
    unittest.main()
