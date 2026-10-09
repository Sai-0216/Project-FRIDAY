import unittest

from proactive.conversation_state import ConversationState
from proactive.slot_filling import SlotFiller


class TestTransitionArmingRegression(unittest.TestCase):
    def test_transition_to_incomplete_intent_syncs_both_states(self):
        filler = SlotFiller()
        state = ConversationState()

        filler.arm("run_workflow", {})
        state.update_pending_slots("run_workflow", {}, ["workflow"])

        result = filler.resolve(
            "create workflow",
            "create_workflow",
            {"workflow": "reports"},
        )

        self.assertTrue(result["transitioned"])
        self.assertTrue(result["pending"])
        self.assertEqual(result["missing"], ["description"])

        # Mirror Brain's post-resolve lifecycle synchronization.
        state.clear_pending_slots()

        if result["pending"] and result["missing"]:
            filler.arm(result["intent"], result["parameters"])
            state.update_pending_slots(
                result["intent"],
                result["parameters"],
                result["missing"],
            )
        else:
            state.clear_pending_slots()

        self.assertTrue(filler.has_pending())
        self.assertEqual(filler.pending_intent, "create_workflow")
        self.assertEqual(filler.pending_slots, ["description"])

        saved = state.snapshot()["pending_slots"]
        self.assertTrue(saved["active"])
        self.assertEqual(saved["intent"], "create_workflow")
        self.assertEqual(saved["missing"], ["description"])


if __name__ == "__main__":
    unittest.main()
