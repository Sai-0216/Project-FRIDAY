from speech import speaker
from command_manager import manager

# Import modules so they register themselves
from plugin_loader import loader
from modules.volume import volume
from modules.brightness import brightness
from modules.system import system
from modules.camera import camera
from modules.screenshot import screenshot

loader.load_plugins()


class CommandRouter:

    def route(self, command):

        print(f"Command received: '{command}'")

        response = manager.execute(command)

        if response is None:
            print("No command matched.")
            return False   # ✅ FIXED

        if response:
            speaker.speak(response)

        return True
    def execute_intent(self, intent):

        name = intent.get("intent")

        if name == "volume_up":
            speaker.speak(volume.volume_up())
            return True

        elif name == "volume_down":
            speaker.speak(volume.volume_down())
            return True

        elif name == "mute":
            speaker.speak(volume.mute())
            return True

        elif name == "unmute":
            speaker.speak(volume.unmute())
            return True

        elif name == "brightness_up":
            speaker.speak(brightness.brightness_up())
            return True

        elif name == "brightness_down":
            speaker.speak(brightness.brightness_down())
            return True

        elif name == "battery":
            speaker.speak(system.battery())
            return True

        speaker.speak("Sorry, I don't know how to do that yet.")
        return True


router = CommandRouter()