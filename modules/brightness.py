"""
Project FRIDAY
Brightness Controller
"""

import screen_brightness_control as sbc
from command_manager import manager


class Brightness:

    def brightness_up(self):
        try:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(min(current + 10, 100))
            return "Brightness increased."
        except Exception:
            return "Couldn't change brightness."

    def brightness_down(self):
        try:
            current = sbc.get_brightness()[0]
            sbc.set_brightness(max(current - 10, 0))
            return "Brightness decreased."
        except Exception:
            return "Couldn't change brightness."

    def set_brightness(self, level):
        try:
            level = int(level)

            if level < 0 or level > 100:
                return "Brightness must be between 0 and 100."

            sbc.set_brightness(level)
            return f"Brightness set to {level} percent."

        except Exception:
            return "Invalid brightness value."


brightness = Brightness()

manager.register_exact("brightness up", brightness.brightness_up)
manager.register_exact("brightness down", brightness.brightness_down)
manager.register_prefix("brightness ", brightness.set_brightness)