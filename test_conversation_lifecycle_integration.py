import unittest
from unittest.mock import patch

from brain import Brain, _safe_process
from proactive.state_manager import StateManager
from proactive.conversation_state import ConversationState


class TestConversationLifecycleIntegration(unittest.TestCase):
    def _make_finished_brain(self, outcome):
        manager = StateManager()
        manager.begin("integration test command")
        manager.transition("EXECUTING")

        if outcome == "failed":
            manager.add_execution_result({
                "response": "Action failed",
                "error": "simulated failure",
            })
        else:
            manager.add_execution_result({
                "response": "Action completed",
                "error": None,
            })

        with patch("proactive.state_manager.episodic_memory.record"):
            manager.complete()

        self.assertEqual(manager.current().lifecycle, "IDLE")
        self.assertEqual(manager.current().outcome, outcome)

        conversation = ConversationState()
        conversation.begin_turn("integration test command")

        brain = Brain.__new__(Brain)
        brain.state_manager = manager
        brain.conversation_state = conversation

        return brain

    def test_already_idle_success_completes_conversation_turn(self):
        brain = self._make_finished_brain("completed")

        with patch("brain._original_process", return_value=True):
            result = _safe_process(brain, "integration test command")

        self.assertTrue(result)
        self.assertEqual(brain.state_manager.current().lifecycle, "IDLE")
        self.assertEqual(brain.conversation_state.status, "completed")
        self.assertIsNone(brain.conversation_state.error)

    def test_already_idle_failure_marks_conversation_turn_failed(self):
        brain = self._make_finished_brain("failed")

        with patch("brain._original_process", return_value=True):
            result = _safe_process(brain, "integration test command")

        self.assertTrue(result)
        self.assertEqual(brain.state_manager.current().lifecycle, "IDLE")
        self.assertEqual(brain.state_manager.current().outcome, "failed")
        self.assertEqual(brain.conversation_state.status, "error")
        self.assertEqual(
            brain.conversation_state.error,
            "Execution failed",
        )


    def test_processing_exception_marks_conversation_failed_when_manager_idle(self):
        manager = StateManager()
        conversation = ConversationState()
        conversation.begin_turn("integration test command")

        brain = Brain.__new__(Brain)
        brain.state_manager = manager
        brain.conversation_state = conversation

        with patch("proactive.state_manager.episodic_memory.record"), patch(
            "brain._original_process",
            side_effect=RuntimeError("simulated process failure"),
        ):
            result = _safe_process(brain, "integration test command")

        self.assertTrue(result)
        self.assertEqual(manager.current().lifecycle, "IDLE")
        self.assertEqual(manager.current().outcome, "failed")
        self.assertIn("simulated process failure", manager.current().error)
        self.assertEqual(conversation.status, "error")
        self.assertIn("simulated process failure", conversation.error)

if __name__ == "__main__":
    unittest.main(verbosity=2)
