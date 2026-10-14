import unittest

from proactive.slot_filling import SlotFiller


class TestSlotTransitionEdgeCases(unittest.TestCase):
    def setUp(self):
        self.filler = SlotFiller()

    def test_all_supported_cancel_phrases_clear_pending_state(self):
        for phrase in ("cancel", "never mind", "nevermind", "stop", "forget it"):
            with self.subTest(phrase=phrase):
                self.filler.arm("create_workflow", {"workflow": "reports"})

                result = self.filler.resolve(phrase, "unknown", {})

                self.assertTrue(result["cancelled"])
                self.assertFalse(result["pending"])
                self.assertFalse(result["completed"])
                self.assertFalse(self.filler.has_pending())

    def test_transition_to_incomplete_intent_arms_new_slots(self):
        self.filler.arm(
            "create_workflow",
            {"workflow": "old-report", "old_only": "stale"},
        )

        result = self.filler.resolve(
            "remove task",
            "remove_from_workflow",
            {"workflow": "new-report"},
        )

        self.assertTrue(result["transitioned"])
        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["intent"], "remove_from_workflow")
        self.assertEqual(result["parameters"], {"workflow": "new-report"})
        self.assertEqual(result["missing"], ["target"])

        self.filler.arm(result["intent"], result["parameters"])
        self.assertEqual(self.filler.pending_intent, "remove_from_workflow")
        self.assertEqual(self.filler.pending_parameters, {"workflow": "new-report"})
        self.assertEqual(self.filler.pending_slots, ["target"])

    def test_transition_to_new_single_slot_intent_uses_only_new_parameters(self):
        self.filler.arm(
            "create_workflow",
            {"workflow": "old-report"},
        )

        result = self.filler.resolve(
            "open browser",
            "open_browser",
            {},
        )

        self.assertTrue(result["transitioned"])
        self.assertTrue(result["pending"])
        self.assertFalse(result["completed"])
        self.assertEqual(result["intent"], "open_browser")
        self.assertEqual(result["parameters"], {})
        self.assertEqual(result["missing"], ["url"])
        self.assertNotIn("workflow", result["parameters"])
        self.assertNotIn("description", result["parameters"])

    def test_unknown_intent_followup_fills_current_pending_slot(self):
        self.filler.arm("create_workflow", {"workflow": "reports"})

        result = self.filler.resolve("daily summary", "unknown", {})

        self.assertTrue(result["completed"])
        self.assertEqual(result["intent"], "create_workflow")
        self.assertEqual(
            result["parameters"],
            {"workflow": "reports", "description": "daily summary"},
        )
        self.assertFalse(self.filler.has_pending())


if __name__ == "__main__":
    unittest.main()


