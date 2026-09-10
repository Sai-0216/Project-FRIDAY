"""
Project FRIDAY
Desktop Automation
"""

import pyautogui

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
            return "Done."

        except Exception as e:
            print("Click Error:", repr(e))
            return "I couldn't click, Sir."

    # ----------------------------------------

    def double_click(self):
        try:
            pyautogui.doubleClick()
            return "Done."

        except Exception as e:
            print("Double Click Error:", repr(e))
            return "I couldn't double click, Sir."

    # ----------------------------------------

    def right_click(self):
        try:
            pyautogui.rightClick()
            return "Done."

        except Exception as e:
            print("Right Click Error:", repr(e))
            return "I couldn't right click, Sir."

    # ========================================
    # SCROLL
    # ========================================

    def scroll_up(self):
        try:
            pyautogui.scroll(500)
            return "Done."

        except Exception as e:
            print("Scroll Up Error:", repr(e))
            return "I couldn't scroll up, Sir."

    # ----------------------------------------

    def scroll_down(self):
        try:
            pyautogui.scroll(-500)
            return "Done."

        except Exception as e:
            print("Scroll Down Error:", repr(e))
            return "I couldn't scroll down, Sir."

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
                "Please tell me which "
                "key to press, Sir."
            )

        try:

            pyautogui.press(
                key
            )

            return (
                f"Pressed {key}."
            )

        except Exception as e:

            print(
                "Press Error:",
                repr(e)
            )

            return (
                f"I don't know the key "
                f"{key}, Sir."
            )

    # ========================================
    # HOTKEY
    # ========================================

    def hotkey(self, *keys):

        if not keys:

            return (
                "Please tell me which "
                "hotkey to press, Sir."
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
                    "The hotkey was empty, Sir."
                )

            print(
                "Automation Hotkey:",
                normalized_keys
            )

            pyautogui.hotkey(
                *normalized_keys
            )

            return (
                f"Pressed {' + '.join(normalized_keys)}."
            )

        except Exception as e:

            print(
                "Hotkey Error:",
                repr(e)
            )

            return (
                "I couldn't press that "
                "hotkey, Sir."
            )

    # ========================================
    # TYPE TEXT
    # ========================================

    def type_text(self, text):

        text = str(text)

        if not text:

            return (
                "There is no text to type, Sir."
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
                "Typing completed."
            )

        except Exception as e:

            print(
                "Type Error:",
                repr(e)
            )

            return (
                "I couldn't type that text, Sir."
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