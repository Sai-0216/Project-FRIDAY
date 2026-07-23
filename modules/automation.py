"""
Project FRIDAY
Desktop Automation
"""

import pyautogui
from command_manager import manager

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2


class Automation:

    def click(self):
        pyautogui.click()
        return "Done."

    def double_click(self):
        pyautogui.doubleClick()
        return "Done."

    def right_click(self):
        pyautogui.rightClick()
        return "Done."

    def scroll_up(self):
        pyautogui.scroll(500)
        return "Done."

    def scroll_down(self):
        pyautogui.scroll(-500)
        return "Done."

    def press(self, key):

        key = key.strip().lower()

        if not key:
            return "Please tell me which key to press."

        try:
            pyautogui.press(key)
            return f"Pressed {key}."

        except Exception as e:
            print("Press Error:", e)
            return f"I don't know the key {key}."

    def hotkey(self, *keys):
        pyautogui.hotkey(*keys)
        return "Done."

    def type_text(self, text):
        pyautogui.write(text, interval=0.04)
        return "Typing completed."


automation = Automation()
# Mouse
manager.register_exact("click", automation.click)
manager.register_exact("double click", automation.double_click)
manager.register_exact("right click", automation.right_click)

# Scroll
manager.register_exact("scroll up", automation.scroll_up)
manager.register_exact("scroll down", automation.scroll_down)

# Keyboard
manager.register_prefix("type ", automation.type_text)
manager.register_prefix("press ", automation.press)

# Hotkeys
manager.register_exact(
    "copy",
    lambda: automation.hotkey("ctrl", "c")
)

manager.register_exact(
    "paste",
    lambda: automation.hotkey("ctrl", "v")
)

manager.register_exact(
    "cut",
    lambda: automation.hotkey("ctrl", "x")
)

manager.register_exact(
    "undo",
    lambda: automation.hotkey("ctrl", "z")
)

manager.register_exact(
    "redo",
    lambda: automation.hotkey("ctrl", "y")
)

manager.register_exact(
    "select all",
    lambda: automation.hotkey("ctrl", "a")
)