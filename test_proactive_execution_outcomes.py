import unittest
from unittest.mock import Mock, patch

from brain import Brain
from proactive.state_manager import StateManager


class TestProactiveExecutionOutcomes(unittest.TestCase):
    def test_confirmed_proactive_execution_records_dispatcher_error(self):
        brain = Brain.__new__(Brain)
        brain.pending_confirmation = {
            "_proactive": True,
            "action": "CONFIRM",
            "intent": "test_action",
            "parameters": {},
            "event_type": "TEST",
            "reason": "Regression test",
            "context": {"attention": {"level": "LOW"}},
        }
        brain.state_manager = StateManager()
        brain.conversation_state = Mock()
        brain.conversational_memory = Mock()
        brain.intent_continuity = Mock()
        brain.slot_filler = Mock()
        brain.context_fusion = None
        brain.fused_context = {}

        fake_dispatcher = Mock()

        def fail_execution(intent):
            fake_dispatcher.last_execution_error = (
                "RuntimeError('proactive action failed')"
            )
            return "Sorry Sir, I couldn't complete that action right now."

        fake_dispatcher.execute.side_effect = fail_execution

        with patch("brain.conversation.get_last_user_message", return_value=None), \
             patch("brain.conversation.add_user"), \
             patch("brain.conversation.add_assistant"), \
             patch("brain.proactive_outcome_memory.record"), \
             patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("builtins.print"):
            result = brain.process("yes")

        self.assertTrue(result)
        self.assertIsNone(brain.pending_confirmation)

        results = brain.state_manager.current().execution_results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["intent"]["intent"], "test_action")
        self.assertEqual(
            results[0]["error"],
            "RuntimeError('proactive action failed')",
        )


if __name__ == "__main__":
    unittest.main()
