"""
Project FRIDAY
Desktop Automation
"""

import pyautogui

from modules.execution_result import ExecutionResult

from command_manager import manager


# ========================================
# PYAUTOGUI CONFIGURATION
# ========================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


class Automation:

    # ========================================
    # MOUSE
    # ========================================

    def click(self):
        try:
            pyautogui.click()
            return ExecutionResult("Done.", status="succeeded")

        except Exception as e:
            print("Click Error:", repr(e))
            return ExecutionResult("I couldn't click, Sir.", status="failed")

    # ----------------------------------------

    def double_click(self):
        try:
            pyautogui.doubleClick()
            return ExecutionResult("Done.", status="succeeded")

        except Exception as e:
            print("Double Click Error:", repr(e))
            return ExecutionResult("I couldn't double click, Sir.", status="failed")

    # ----------------------------------------

    def right_click(self):
        try:
            pyautogui.rightClick()
            return ExecutionResult("Done.", status="succeeded")

        except Exception as e:
            print("Right Click Error:", repr(e))
            return ExecutionResult("I couldn't right click, Sir.", status="failed")

    # ========================================
    # SCROLL
    # ========================================

    def scroll_up(self):
        try:
            pyautogui.scroll(500)
            return ExecutionResult("Done.", status="succeeded")

        except Exception as e:
            print("Scroll Up Error:", repr(e))
            return ExecutionResult("I couldn't scroll up, Sir.", status="failed")

    # ----------------------------------------

    def scroll_down(self):
        try:
            pyautogui.scroll(-500)
            return ExecutionResult("Done.", status="succeeded")

        except Exception as e:
            print("Scroll Down Error:", repr(e))
            return ExecutionResult("I couldn't scroll down, Sir.", status="failed")

    # ========================================
    # KEY NORMALIZATION
    # ========================================

    def normalize_key(self, key):

        key = str(key).strip().lower()

        aliases = {

            # --------------------------------
            # COMMON KEYS
            # --------------------------------

            "escape": "esc",
            "return": "enter",
            "spacebar": "space",
            "back space": "backspace",
            "back-space": "backspace",

            # --------------------------------
            # ARROW KEYS
            # --------------------------------

            "left arrow": "left",
            "right arrow": "right",
            "up arrow": "up",
            "down arrow": "down",

            # --------------------------------
            # MODIFIER KEYS
            # --------------------------------

            "control": "ctrl",
            "command": "command",
            "windows": "win",

            # --------------------------------
            # PAGE KEYS
            # --------------------------------

            "page up": "pageup",
            "page down": "pagedown",

            # --------------------------------
            # DELETE
            # --------------------------------

            "delete key": "delete",
            "backspace key": "backspace",
        }

        return aliases.get(
            key,
            key
        )

    # ========================================
    # PRESS KEY
    # ========================================

    def press(self, key):

        key = self.normalize_key(key)

        if not key:

            return (
                ExecutionResult("Please tell me which "
                "key to press, Sir.", status="failed")
            )

        try:

            pyautogui.press(
                key
            )

            return (
                ExecutionResult(f"Pressed {key}.", status="succeeded")
            )

        except Exception as e:

            print(
                "Press Error:",
                repr(e)
            )

            return (
                ExecutionResult(f"I don't know the key "
                f"{key}, Sir.", status="failed")
            )

    # ========================================
    # HOTKEY
    # ========================================

    def hotkey(self, *keys):

        if not keys:

            return (
                ExecutionResult("Please tell me which "
                "hotkey to press, Sir.", status="failed")
            )

        try:

            normalized_keys = [
                self.normalize_key(key)
                for key in keys
            ]

            normalized_keys = [
                key
                for key in normalized_keys
                if key
            ]

            if not normalized_keys:

                return (
                    ExecutionResult("The hotkey was empty, Sir.", status="failed")
                )

            print(
                "Automation Hotkey:",
                normalized_keys
            )

            pyautogui.hotkey(
                *normalized_keys
            )

            return (
                ExecutionResult(f"Pressed {' + '.join(normalized_keys)}.", status="succeeded")
            )

        except Exception as e:

            print(
                "Hotkey Error:",
                repr(e)
            )

            return (
                ExecutionResult("I couldn't press that "
                "hotkey, Sir.", status="failed")
            )

    # ========================================
    # TYPE TEXT
    # ========================================

    def type_text(self, text):

        text = str(text)

        if not text:

            return (
                ExecutionResult("There is no text to type, Sir.", status="failed")
            )

        try:

            print(
                "Automation Typing:",
                repr(text)
            )

            pyautogui.write(
                text,
                interval=0.04
            )

            return (
                ExecutionResult("Typing completed.", status="succeeded")
            )

        except Exception as e:

            print(
                "Type Error:",
                repr(e)
            )

            return (
                ExecutionResult("I couldn't type that text, Sir.", status="failed")
            )


# ========================================
# GLOBAL AUTOMATION INSTANCE
# ========================================

automation = Automation()


# ========================================
# COMMAND MANAGER REGISTRATION
# ========================================

# ----------------------------------------
# Mouse
# ----------------------------------------

manager.register_exact(
    "click",
    automation.click
)

manager.register_exact(
    "double click",
    automation.double_click
)

manager.register_exact(
    "right click",
    automation.right_click
)


# ----------------------------------------
# Scroll
# ----------------------------------------

manager.register_exact(
    "scroll up",
    automation.scroll_up
)

manager.register_exact(
    "scroll down",
    automation.scroll_down
)


# ----------------------------------------
# Keyboard
# ----------------------------------------

manager.register_prefix(
    "type ",
    automation.type_text
)

manager.register_prefix(
    "press ",
    automation.press
)


# ========================================
# COMMON HOTKEY COMMANDS
# ========================================

manager.register_exact(
    "copy",
    lambda: automation.hotkey(
        "ctrl",
        "c"
    )
)

manager.register_exact(
    "paste",
    lambda: automation.hotkey(
        "ctrl",
        "v"
    )
)

manager.register_exact(
    "cut",
    lambda: automation.hotkey(
        "ctrl",
        "x"
    )
)

manager.register_exact(
    "undo",
    lambda: automation.hotkey(
        "ctrl",
        "z"
    )
)

manager.register_exact(
    "redo",
    lambda: automation.hotkey(
        "ctrl",
        "y"
    )
)

manager.register_exact(
    "select all",
    lambda: automation.hotkey(
        "ctrl",
        "a"
    )
)