import unittest
from unittest.mock import Mock, patch

from brain import Brain
from proactive.state_manager import StateManager


class TestDirectIntentExecutionOutcomes(unittest.TestCase):
    def test_direct_intent_failure_is_recorded_and_state_completes_failed(self):
        brain = Brain.__new__(Brain)
        brain.pending_confirmation = None
        brain.state_manager = StateManager()
        brain.conversation_state = Mock()
        brain.conversation_state.snapshot.return_value = {"pending_slots": {}}
        brain.conversational_memory = Mock()

        brain.intent_continuity = Mock()
        brain.intent_continuity.previous_intent = None
        brain.intent_continuity.previous_parameters = {}
        brain.intent_continuity.resolve.return_value = {
            "continued": False,
            "intent": "test_action",
            "parameters": {},
        }

        brain.slot_filler = Mock()
        brain.slot_filler.has_pending.return_value = False
        brain.slot_filler.resolve.return_value = {
            "intent": "test_action",
            "parameters": {},
            "missing": [],
            "validation": {"valid": True},
            "pending": False,
            "cancelled": False,
            "transitioned": False,
        }

        brain.fused_context = {}
        brain.is_conversational = Mock(return_value=False)
        brain.is_contextual = Mock(return_value=False)

        intent = {"intent": "test_action", "parameters": {}}
        fake_dispatcher = Mock()
        fake_dispatcher.execute.return_value = (
            "Sorry Sir, I couldn't complete that action right now."
        )
        fake_dispatcher.last_execution_error = (
            "RuntimeError('direct action failed')"
        )

        with patch("brain.ContextFusion") as context_fusion_cls, \
             patch("brain.conversation.get_last_user_message", return_value=None), \
             patch("brain.conversation.add_user"), \
             patch("brain.conversation.add_assistant"), \
             patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.intent_engine.detect", return_value=intent), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"):
            context_fusion_cls.return_value.build.return_value = {}
            result = brain.process("run test action")

        self.assertTrue(result)
        fake_dispatcher.execute.assert_called_once()

        state = brain.state_manager.current()
        self.assertEqual(len(state.execution_results), 1)
        self.assertEqual(
            state.execution_results[0]["error"],
            "RuntimeError('direct action failed')",
        )
        self.assertEqual(state.outcome, "failed")
        self.assertEqual(state.lifecycle, "IDLE")
        brain.conversation_state.fail.assert_called_once()


if __name__ == "__main__":
    unittest.main()
