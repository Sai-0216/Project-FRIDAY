import contextlib
import io
import unittest
from pathlib import Path

from proactive.conversation_state import ConversationState
from proactive.slot_filling import SlotFiller


class FakeContinuity:
    previous_intent = None
    previous_parameters = {}


class FakeSpeaker:
    def __init__(self):
        self.messages = []

    def speak(self, message):
        self.messages.append(message)


class TestBrainSlotBlock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lines = Path("brain.py").read_text(
            encoding="utf-8-sig"
        ).splitlines()

        start = next(
            i for i, line in enumerate(lines)
            if "# MULTI-TURN SLOT FILLING" in line
        )
        end = next(
            i for i in range(start + 1, len(lines))
            if 'if continuity["continued"]:' in lines[i]
        )

        block = "\n".join(lines[start:end])
        cls.lifecycle_code = compile(
            "def run_lifecycle(self, command, intent_name, parameters, intent, speaker):\n"
            + "\n".join("    " + line for line in block.splitlines()),
            "brain.py:slot_lifecycle",
            "exec",
        )

    def setUp(self):
        self.filler = SlotFiller()
        self.state = ConversationState()
        self.continuity = FakeContinuity()
        self.speaker = FakeSpeaker()

        namespace = {"print": print}
        exec(self.lifecycle_code, namespace)
        self.run_lifecycle = namespace["run_lifecycle"].__get__(
            self, type(self)
        )

        self.slot_filler = self.filler
        self.conversation_state = self.state
        self.intent_continuity = self.continuity

    def run_block(self, command, detected_intent, parameters=None):
        intent = {
            "intent": detected_intent,
            "parameters": dict(parameters or {}),
        }
        with contextlib.redirect_stdout(io.StringIO()):
            result = self.run_lifecycle(
                command,
                detected_intent,
                dict(parameters or {}),
                intent,
                self.speaker,
            )
        return result, intent

    def test_initial_missing_slots_are_persisted(self):
        _, intent = self.run_block("create workflow", "create_workflow", {"workflow": "reports"})
        saved = self.state.snapshot()["pending_slots"]
        self.assertEqual(intent["intent"], "create_workflow")
        self.assertTrue(saved["active"])
        self.assertEqual(saved["missing"], ["description"])
        self.assertTrue(self.filler.has_pending())

    def test_transition_to_incomplete_intent_syncs_both_states(self):
        self.filler.arm("run_workflow", {})
        self.state.update_pending_slots("run_workflow", {}, ["workflow"])

        _, intent = self.run_block(
            "create workflow", "create_workflow", {"workflow": "reports"}
        )

        saved = self.state.snapshot()["pending_slots"]
        self.assertEqual(intent["intent"], "create_workflow")
        self.assertTrue(self.filler.has_pending())
        self.assertEqual(self.filler.pending_intent, "create_workflow")
        self.assertTrue(saved["active"])
        self.assertEqual(saved["intent"], "create_workflow")
        self.assertEqual(saved["missing"], ["description"])

    def test_cancel_clears_both_states(self):
        self.filler.arm("run_workflow", {})
        self.state.update_pending_slots("run_workflow", {}, ["workflow"])

        result, _ = self.run_block("cancel", "unknown", {})

        self.assertTrue(result)
        self.assertFalse(self.filler.has_pending())
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])
        self.assertIn("Okay, cancelled.", self.speaker.messages)

    def test_persisted_pending_state_is_restored(self):
        self.state.update_pending_slots(
            "create_workflow", {"workflow": "reports"}, ["description"]
        )

        _, intent = self.run_block("daily report", "unknown", {})

        self.assertEqual(intent["intent"], "create_workflow")
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])
        self.assertFalse(self.filler.has_pending())

    def test_completion_clears_both_states(self):
        self.filler.arm("create_workflow", {"workflow": "reports"})
        self.state.update_pending_slots(
            "create_workflow", {"workflow": "reports"}, ["description"]
        )

        _, intent = self.run_block("daily report", "unknown", {})

        self.assertEqual(intent["parameters"]["description"], "daily report")
        self.assertFalse(self.filler.has_pending())
        self.assertFalse(self.state.snapshot()["pending_slots"]["active"])


if __name__ == "__main__":
    unittest.main()
