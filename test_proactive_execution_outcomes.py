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

        def fail_execution(intent, *, approval_token=None):
            fake_dispatcher.last_execution_error = (
                "RuntimeError('proactive action failed')"
            )
            return "Sorry Sir, I couldn't complete that action right now."

        fake_dispatcher.execute.side_effect = fail_execution

        with patch("brain.conversation.get_last_user_message", return_value=None), \
             patch("brain.conversation.add_user"), \
             patch("brain.conversation.add_assistant"), \
             patch("brain.proactive_outcome_memory.record") as record_outcome, \
             patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.response_manager.command", side_effect=lambda value: value), \
             patch("brain.speaker.speak"), \
             patch("builtins.print"):
            result = brain.process("yes", source="local_voice")

        self.assertTrue(result)
        self.assertIsNone(brain.pending_confirmation)
        record_outcome.assert_called_once()

        results = brain.state_manager.current().execution_results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["intent"]["intent"], "test_action")
        self.assertEqual(
            results[0]["error"],
            "RuntimeError('proactive action failed')",
        )


    def test_rejected_proactive_confirmation_records_once(self):
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

        with patch("brain.conversation.get_last_user_message", return_value=None), \
             patch("brain.conversation.add_user"), \
             patch("brain.conversation.add_assistant"), \
             patch("brain.proactive_outcome_memory.record") as record_outcome, \
             patch("brain.dispatcher", fake_dispatcher), \
             patch("brain.speaker.speak"), \
             patch("builtins.print"):
            result = brain.process("no", source="local_voice")

        self.assertTrue(result)
        self.assertIsNone(brain.pending_confirmation)
        record_outcome.assert_called_once()
        self.assertEqual(record_outcome.call_args.kwargs["outcome"], "rejected")
        fake_dispatcher.execute.assert_not_called()

    def test_non_proactive_rejection_does_not_record_outcome(self):
        brain = Brain.__new__(Brain)
        brain.pending_confirmation = {
            "action": "CONFIRM",
            "intent": "test_action",
            "parameters": {},
        }
        brain.state_manager = StateManager()
        brain.conversation_state = Mock()
        brain.conversational_memory = Mock()
        brain.intent_continuity = Mock()
        brain.slot_filler = Mock()
        brain.context_fusion = None
        brain.fused_context = {}

        with patch("brain.conversation.get_last_user_message", return_value=None), \
             patch("brain.conversation.add_user"), \
             patch("brain.conversation.add_assistant"), \
             patch("brain.proactive_outcome_memory.record") as record_outcome, \
             patch("brain.speaker.speak"), \
             patch("builtins.print"):
            result = brain.process("no", source="local_voice")

        self.assertTrue(result)
        self.assertIsNone(brain.pending_confirmation)
        record_outcome.assert_not_called()

    def test_remote_yes_cannot_approve_pending_action(self):
        brain = Brain.__new__(Brain)
        brain.state_manager = StateManager()
        brain.conversation_state = Mock()
        brain.pending_confirmation = {
            "action": "CONFIRM",
            "intent": "test_action",
            "parameters": {},
        }

        with patch("builtins.print"):
            result = brain.process("yes", source="remote")

        self.assertTrue(result)
        self.assertIsNotNone(brain.pending_confirmation)

    def test_unknown_source_cannot_reject_pending_action(self):
        brain = Brain.__new__(Brain)
        brain.state_manager = StateManager()
        brain.conversation_state = Mock()
        brain.pending_confirmation = {
            "action": "CONFIRM",
            "intent": "test_action",
            "parameters": {},
        }

        with patch("builtins.print"):
            result = brain.process("no", source="unknown")

        self.assertTrue(result)
        self.assertIsNotNone(brain.pending_confirmation)

    def test_nonlocal_commands_are_blocked_while_confirmation_pending(self):
        for source in ("remote", "unknown"):
            with self.subTest(source=source):
                brain = Brain.__new__(Brain)
                brain.state_manager = StateManager()
                brain.conversation_state = Mock()
                pending = {
                    "action": "CONFIRM",
                    "intent": "test_action",
                    "parameters": {},
                }
                brain.pending_confirmation = pending

                with patch.object(
                    brain.state_manager, "begin"
                ) as begin_state, patch.object(
                    brain.conversation_state, "begin_turn"
                ) as begin_turn, patch("builtins.print"):
                    result = brain.process(
                        "open the browser",
                        source=source,
                    )

                self.assertTrue(result)
                self.assertIs(brain.pending_confirmation, pending)
                begin_state.assert_not_called()
                begin_turn.assert_not_called()


if __name__ == "__main__":
    unittest.main()
