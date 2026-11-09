import unittest
from unittest.mock import patch

from intent_dispatcher import IntentDispatcher
from security.approval_manager import ApprovalManager


class TestDispatcherAuthorization(unittest.TestCase):

    def setUp(self):
        self.manager = ApprovalManager()
        self.dispatcher = IntentDispatcher(
            approval_manager_instance=self.manager
        )
        self.intent = {
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        }

    def test_confirmation_intent_without_token_is_blocked(self):
        with patch.object(self.dispatcher, "_execute") as execute:
            response = self.dispatcher.execute(self.intent)

        execute.assert_not_called()
        self.assertIn("requires a fresh", response)
        self.assertEqual(
            self.dispatcher.last_authorization_result["status"],
            "CONFIRM",
        )

    def test_forged_token_is_blocked(self):
        with patch.object(self.dispatcher, "_execute") as execute:
            self.dispatcher.execute(
                self.intent,
                approval_token="not-a-real-token",
            )

        execute.assert_not_called()

    def test_valid_action_bound_token_allows_execution(self):
        token = self.manager.issue([self.intent])

        with patch.object(
            self.dispatcher,
            "_execute",
            return_value="Action completed.",
        ) as execute:
            response = self.dispatcher.execute(
                self.intent,
                approval_token=token,
            )

        execute.assert_called_once_with(self.intent)
        self.assertEqual(response, "Action completed.")
        self.assertEqual(
            self.dispatcher.last_authorization_result["status"],
            "ALLOW",
        )

    def test_token_cannot_be_replayed(self):
        token = self.manager.issue([self.intent])

        with patch.object(
            self.dispatcher,
            "_execute",
            return_value="Action completed.",
        ) as execute:
            first = self.dispatcher.execute(
                self.intent,
                approval_token=token,
            )
            second = self.dispatcher.execute(
                self.intent,
                approval_token=token,
            )

        self.assertEqual(first, "Action completed.")
        self.assertIn("requires a fresh", second)
        self.assertEqual(execute.call_count, 1)

    def test_token_for_different_action_is_rejected_and_burned(self):
        token = self.manager.issue([self.intent])
        altered = {
            "intent": "delete_workflow",
            "parameters": {"workflow": "production"},
        }

        with patch.object(self.dispatcher, "_execute") as execute:
            response = self.dispatcher.execute(
                altered,
                approval_token=token,
            )
            replay = self.dispatcher.execute(
                self.intent,
                approval_token=token,
            )

        execute.assert_not_called()
        self.assertIn("requires a fresh", response)
        self.assertIn("requires a fresh", replay)

    def test_read_only_intent_does_not_need_token(self):
        with patch.object(
            self.dispatcher,
            "_execute",
            return_value="Battery is at 80 percent.",
        ) as execute:
            response = self.dispatcher.execute({
                "intent": "battery",
                "parameters": {},
            })

        execute.assert_called_once()
        self.assertEqual(response, "Battery is at 80 percent.")

    def test_unknown_intent_is_denied(self):
        with patch.object(self.dispatcher, "_execute") as execute:
            response = self.dispatcher.execute({
                "intent": "run_shell",
                "parameters": {"command": "whoami"},
            })

        execute.assert_not_called()
        self.assertIn("authorization checks", response)
        self.assertEqual(
            self.dispatcher.last_authorization_result["status"],
            "DENY",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
