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


class TestRepeatedFollowUpEdgeCase(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()
        self.filler.validator = TestValidator()
        self.state = ConversationState()

        self.filler.arm("create_workflow", {"workflow": "reports"})
        self.state.update_pending_slots(
            "create_workflow",
            {"workflow": "reports"},
            ["description"],
        )

    def test_invalid_answer_preserves_pending_slot_then_valid_answer_completes(self):
        first = self.filler.resolve("invalid", "unknown", {})

        self.assertTrue(first["pending"])
        self.assertFalse(first["completed"])
        self.assertEqual(first["missing"], ["description"])

        self.filler.arm(first["intent"], first["parameters"])
        self.state.update_pending_slots(
            first["intent"],
            first["parameters"],
            first["missing"],
        )

        saved = self.state.snapshot()["pending_slots"]
        self.assertTrue(saved["active"])
        self.assertEqual(saved["intent"], "create_workflow")
        self.assertEqual(saved["missing"], ["description"])

        second = self.filler.resolve("daily report", "unknown", {})

        self.assertTrue(second["completed"])
        self.assertFalse(second["pending"])
        self.assertEqual(
            second["parameters"]["description"],
            "daily report",
        )
        self.assertFalse(self.filler.has_pending())

        self.state.clear_pending_slots()
        saved = self.state.snapshot()["pending_slots"]
        self.assertFalse(saved["active"])


if __name__ == "__main__":
    unittest.main()
