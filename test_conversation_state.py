import unittest

from proactive.conversation_state import ConversationState


class TestConversationState(unittest.TestCase):

    def test_begin_turn(self):
        state = ConversationState()

        state.begin_turn("open chrome")

        self.assertEqual(state.status, "active")
        self.assertEqual(state.turn_count, 1)
        self.assertEqual(state.last_user_message, "open chrome")

    def test_intent_and_topic(self):
        state = ConversationState()

        state.begin_turn("open chrome")
        state.update_intent("open_application", {"application": "chrome"})
        state.update_topic("application control")

        self.assertEqual(state.last_intent, "open_application")
        self.assertEqual(
            state.last_parameters,
            {"application": "chrome"},
        )
        self.assertEqual(
            state.active_topic,
            "application control",
        )

    def test_complete_turn(self):
        state = ConversationState()

        state.begin_turn("open chrome")
        state.complete_turn("Chrome opened.")

        snapshot = state.snapshot()

        self.assertEqual(snapshot["status"], "completed")
        self.assertEqual(
            snapshot["last_assistant_message"],
            "Chrome opened.",
        )


if __name__ == "__main__":
    unittest.main()
