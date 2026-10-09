import unittest

from proactive.conversation_state import ConversationState
from proactive.slot_filling import SlotFiller


class TestValidator:
    def validate(self, intent, slot, value):
        if value == "invalid":
            return {
                "valid": False,
                "value": None,
                "reason": "test rejection",
            }
        return {"valid": True, "value": value}


class TestSlotLifecycleEdgeCases(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()
        self.filler.validator = TestValidator()
        self.state = ConversationState()

    def sync_pending(self, result):
        if result.get("pending") and result.get("missing"):
            self.filler.arm(result["intent"], result["parameters"])
            self.state.update_pending_slots(
                result["intent"],
                result["parameters"],
                result["missing"],
            )
        else:
            self.state.clear_pending_slots()

    def test_cancel_after_multiple_followups_clears_both_states(self):
        self.filler.arm(
            "add_weekly_reminder",
            {"text": "submit assignment"},
        )
        self.state.update_pending_slots(
            "add_weekly_reminder",
            {"text": "submit assignment"},
            ["time", "weekday"],
        )

        first = self.filler.resolve("9 AM", "unknown", {})
        self.assertTrue(first["pending"])
        self.assertEqual(first["missing"], ["weekday"])
        self.sync_pending(first)

        result = self.filler.resolve("cancel", "unknown", {})
        self.assertTrue(result["cancelled"])
        self.assertFalse(result["pending"])
        self.filler.clear()
        self.state.clear_pending_slots()

        self.assertFalse(self.filler.has_pending())
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])

    def test_intent_switch_does_not_reuse_old_parameters(self):
        self.filler.arm(
            "create_workflow",
            {"workflow": "old-report", "old_only": "stale"},
        )
        self.state.update_pending_slots(
            "create_workflow",
            {"workflow": "old-report", "old_only": "stale"},
            ["description"],
        )

        result = self.filler.resolve(
            "remove a task",
            "remove_from_workflow",
            {"workflow": "new-report"},
        )

        self.assertTrue(result["transitioned"])
        self.assertEqual(result["intent"], "remove_from_workflow")
        self.assertEqual(result["parameters"], {"workflow": "new-report"})
        self.assertNotIn("old_only", result["parameters"])
        self.assertEqual(result["missing"], ["target"])

        self.sync_pending(result)
        self.assertEqual(self.filler.pending_intent, "remove_from_workflow")
        self.assertEqual(self.filler.pending_slots, ["target"])

        saved = self.state.snapshot()["pending_slots"]
        self.assertTrue(saved["active"])
        self.assertEqual(saved["intent"], "remove_from_workflow")
        self.assertEqual(saved["missing"], ["target"])

    def test_repeated_invalid_answers_keep_slot_pending(self):
        self.filler.arm("create_workflow", {"workflow": "reports"})
        self.state.update_pending_slots(
            "create_workflow", {"workflow": "reports"}, ["description"]
        )

        for _ in range(3):
            result = self.filler.resolve("invalid", "unknown", {})
            self.assertTrue(result["pending"])
            self.assertFalse(result["completed"])
            self.assertEqual(result["missing"], ["description"])
            self.sync_pending(result)

            saved = self.state.snapshot()["pending_slots"]
            self.assertTrue(saved["active"])
            self.assertEqual(saved["missing"], ["description"])

        self.assertTrue(self.filler.has_pending())

    def test_pending_state_can_be_rehydrated_and_completed(self):
        parameters = {"workflow": "reports"}
        self.state.update_pending_slots(
            "create_workflow", parameters, ["description"]
        )

        saved = self.state.snapshot()["pending_slots"]
        restored = SlotFiller()
        restored.validator = TestValidator()

        restored.restore_pending(
            saved["intent"],
            saved["parameters"],
            saved["missing"],
        )

        self.assertTrue(restored.has_pending())
        result = restored.resolve("daily report", "unknown", {})

        self.assertTrue(result["completed"])
        self.assertFalse(result["pending"])
        self.assertEqual(result["parameters"]["workflow"], "reports")
        self.assertEqual(result["parameters"]["description"], "daily report")
        self.assertFalse(restored.has_pending())

        self.state.clear_pending_slots()
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])

    def test_transition_discards_old_intent_specific_values(self):
        self.filler.arm(
            "create_workflow",
            {"workflow": "old"},
        )

        result = self.filler.resolve(
            "remove task",
            "remove_from_workflow",
            {"workflow": "new"},
        )

        self.assertTrue(result["transitioned"])
        self.assertEqual(result["intent"], "remove_from_workflow")
        self.assertEqual(result["parameters"], {"workflow": "new"})
        self.assertNotIn("description", result["parameters"])
        self.assertEqual(result["missing"], ["target"])


if __name__ == "__main__":
    unittest.main()
