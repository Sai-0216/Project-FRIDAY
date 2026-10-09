import unittest

from proactive.conversation_state import ConversationState
from proactive.slot_filling import SlotFiller


class FakeValidator:
    def validate(self, intent, slot, value):
        return {"valid": True, "value": value}


class TestSlotLifecycleIntegration(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()
        self.filler.validator = FakeValidator()
        self.state = ConversationState()

    def test_pending_state_round_trip(self):
        missing = self.filler.arm("create_workflow", {"workflow": "daily"})
        self.state.update_pending_slots(
            "create_workflow", {"workflow": "daily"}, missing
        )

        saved = self.state.snapshot()["pending_slots"]
        self.assertTrue(saved["active"])

        restored = SlotFiller()
        restored.restore_pending(
            saved["intent"], saved["parameters"], saved["missing"]
        )
        self.assertTrue(restored.has_pending())
        self.assertEqual(restored.pending_intent, "create_workflow")
        self.assertEqual(restored.pending_slots, ["description"])

    def test_completion_clears_filler_and_persisted_state(self):
        self.filler.arm("run_workflow", {})
        self.state.update_pending_slots("run_workflow", {}, ["workflow"])

        result = self.filler.resolve("daily", "unknown", {})
        self.assertTrue(result["completed"])
        self.assertFalse(self.filler.has_pending())

        if result["completed"]:
            self.state.clear_pending_slots()

        saved = self.state.snapshot()["pending_slots"]
        self.assertFalse(saved["active"])
        self.assertIsNone(saved["intent"])
        self.assertEqual(saved["missing"], [])

    def test_transition_clears_old_intent(self):
        self.filler.arm("run_workflow", {})
        result = self.filler.resolve(
            "create folder", "create_folder", {"name": "reports"}
        )

        self.assertTrue(result["transitioned"])
        self.assertEqual(result["intent"], "create_folder")
        self.assertFalse(self.filler.has_pending())
        self.state.clear_pending_slots()

        saved = self.state.snapshot()["pending_slots"]
        self.assertFalse(saved["active"])

    def test_transition_result_can_start_new_pending_intent(self):
        self.filler.arm("run_workflow", {})
        result = self.filler.resolve(
            "create workflow", "create_workflow", {"workflow": "reports"}
        )

        self.assertTrue(result["transitioned"])
        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["intent"], "create_workflow")
        self.assertEqual(result["missing"], ["description"])

        self.state.clear_pending_slots()
        self.state.update_pending_slots(
            result["intent"], result["parameters"], result["missing"]
        )
        saved = self.state.snapshot()["pending_slots"]
        self.assertTrue(saved["active"])
        self.assertEqual(saved["intent"], "create_workflow")
        self.assertEqual(saved["missing"], ["description"])

    def test_cancel_clears_both_states(self):
        self.filler.arm("run_workflow", {})
        self.state.update_pending_slots("run_workflow", {}, ["workflow"])

        result = self.filler.resolve("cancel", "unknown", {})
        self.assertTrue(result["cancelled"])
        self.state.clear_pending_slots()

        self.assertFalse(self.filler.has_pending())
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])


if __name__ == "__main__":
    unittest.main()
