
import ast
import threading
import unittest
from pathlib import Path
from unittest.mock import patch


class FakeDialog:
    def __init__(self):
        self.exists = True
        self.protocol_callback = None

    def title(self, *args, **kwargs): pass
    def geometry(self, *args, **kwargs): pass
    def resizable(self, *args, **kwargs): pass
    def transient(self, *args, **kwargs): pass
    def grab_set(self): pass
    def grab_release(self): pass

    def protocol(self, name, callback):
        self.protocol_callback = callback

    def winfo_exists(self):
        return self.exists

    def destroy(self):
        self.exists = False


class FakeWidget:
    def __init__(self, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass


class FakeButton:
    def __init__(self, parent, text, command, **kwargs):
        self.text = text
        self.command = command
        FakeCTk.state["buttons"][text] = self

    def pack(self, *args, **kwargs): pass
    def focus_set(self): pass


class FakeCTk:
    state = None

    @classmethod
    def CTkToplevel(cls, root):
        dialog = FakeDialog()
        cls.state["dialog"] = dialog
        return dialog

    CTkLabel = FakeWidget
    CTkFrame = FakeWidget
    CTkButton = FakeButton


class FakeRoot:
    def __init__(self, state, action=None, fail=False):
        self.state = state
        self.action = action
        self.fail = fail
        self.calls = 0

    def after(self, delay, callback):
        if self.fail:
            raise RuntimeError("Simulated GUI scheduling failure")

        self.calls += 1
        callback()

        if self.calls == 1:
            if self.action in ("YES", "NO"):
                self.state["buttons"][self.action].command()
            elif self.action == "CLOSE":
                self.state["dialog"].protocol_callback()


class TimeoutEvent:
    def __init__(self):
        self.was_set = False

    def wait(self, timeout=None):
        return False

    def set(self):
        self.was_set = True

    def is_set(self):
        return self.was_set


def load_confirm_method():
    source_path = Path(__file__).with_name("gui.py")
    source = source_path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)

    gui_class = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "FridayGUI"
    )

    method = next(
        node for node in gui_class.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "confirm"
    )

    harness_class = ast.ClassDef(
        name="ConfirmationHarness",
        bases=[],
        keywords=[],
        body=[method],
        decorator_list=[],
        type_params=[]
    )

    module = ast.fix_missing_locations(
        ast.Module(
            body=[harness_class],
            type_ignores=[]
        )
    )

    namespace = {"ctk": FakeCTk}
    exec(compile(module, str(source_path), "exec"), namespace)

    return namespace["ConfirmationHarness"]


class TestGUIConfirmation(unittest.TestCase):

    def run_confirmation(self, action=None, timeout=False, fail=False):
        state = {
            "dialog": None,
            "buttons": {}
        }

        FakeCTk.state = state

        harness_class = load_confirm_method()
        harness = harness_class()
        harness.root = FakeRoot(state, action=action, fail=fail)

        real_event = threading.Event
        finished_event = TimeoutEvent() if timeout else real_event()
        expired_event = real_event()

        with patch(
            "threading.Event",
            side_effect=[finished_event, expired_event]
        ):
            result = harness.confirm("Approve this exact workflow?")

        return result, state

    def test_yes_approves(self):
        result, _ = self.run_confirmation(action="YES")
        self.assertTrue(result)

    def test_no_denies(self):
        result, _ = self.run_confirmation(action="NO")
        self.assertFalse(result)

    def test_window_close_denies(self):
        result, _ = self.run_confirmation(action="CLOSE")
        self.assertFalse(result)

    def test_timeout_denies_and_closes_dialog(self):
        result, state = self.run_confirmation(timeout=True)

        self.assertFalse(result)
        self.assertFalse(state["dialog"].exists)

        # A late YES must not reverse the expired decision.
        state["buttons"]["YES"].command()
        self.assertFalse(result)
        self.assertFalse(state["dialog"].exists)

    def test_gui_scheduling_failure_denies(self):
        result, _ = self.run_confirmation(fail=True)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
