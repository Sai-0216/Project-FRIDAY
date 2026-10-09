import unittest

from proactive.slot_filling import SlotFiller


class FakeValidator:
    def validate(self, intent, slot, value):
        if value == "invalid":
            return {"valid": False, "value": None, "reason": "test rejection"}
        return {"valid": True, "value": value}


class TestSlotFillingLifecycle(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()
        self.filler.validator = FakeValidator()

    def test_new_intent_with_missing_slots_reports_pending(self):
        result = self.filler.resolve("run workflow", "run_workflow", {})
        self.assertEqual(result["missing"], ["workflow"])
        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])

    def test_multiturn_fill_completes_explicitly(self):
        self.filler.arm("create_workflow", {})

        first = self.filler.resolve("demo", "unknown", {})
        self.assertTrue(first["pending"])
        self.assertFalse(first["completed"])
        self.assertEqual(first["missing"], ["description"])

        second = self.filler.resolve("daily report", "unknown", {})
        self.assertFalse(second["pending"])
        self.assertTrue(second["completed"])
        self.assertFalse(self.filler.has_pending())

    def test_invalid_value_remains_pending(self):
        self.filler.arm("run_workflow", {})
        result = self.filler.resolve("invalid", "unknown", {})
        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertTrue(self.filler.has_pending())

    def test_cancel_clears_pending_lifecycle(self):
        self.filler.arm("run_workflow", {})
        result = self.filler.resolve("cancel", "unknown", {})
        self.assertTrue(result["cancelled"])
        self.assertFalse(result["pending"])
        self.assertFalse(result["completed"])
        self.assertFalse(self.filler.has_pending())

    def test_transition_reports_new_intent_lifecycle(self):
        self.filler.arm("run_workflow", {})
        result = self.filler.resolve(
            "create folder", "create_folder", {"name": "demo"}
        )
        self.assertTrue(result["transitioned"])
        self.assertEqual(result["previous_intent"], "run_workflow")
        self.assertFalse(result["pending"])
        self.assertTrue(result["completed"])
        self.assertFalse(self.filler.has_pending())


if __name__ == "__main__":
    unittest.main()
