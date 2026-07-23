"""
FRIDAY Intent Dispatcher
"""

from speech import speaker

from modules.volume import volume
from modules.brightness import brightness
from modules.system import system
from modules.camera import camera
from modules.screenshot import screenshot
from modules.browser import browser
from modules.apps import apps


class IntentDispatcher:

    def execute(self, intent):

        name = intent.get("intent")
        params = intent.get("parameters", {})

        match name:

            case "volume_up":
                return volume.volume_up()

            case "volume_down":
                return volume.volume_down()

            case "mute":
                return volume.mute()

            case "unmute":
                return volume.unmute()

            case "brightness_up":
                return brightness.brightness_up()

            case "brightness_down":
                return brightness.brightness_down()

            case "battery":
                return system.battery()

            case "cpu":
                return system.cpu()

            case "ram":
                return system.ram()

            case "disk":
                return system.disk()

            case "take_photo":
                return camera.take_photo()

            case "open_camera":
                return camera.open_camera()

            case "take_screenshot":
                return screenshot.capture()

            case "unknown":
                return "Sorry Sir, I couldn't understand."

            case _:
                return f"I don't know how to execute '{name}'."


dispatcher = IntentDispatcher()