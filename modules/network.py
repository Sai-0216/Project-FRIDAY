"""
Project FRIDAY
Network Controller
"""

import subprocess
from command_manager import manager
from speech import speaker

class Network:

    def wifi_on(self):
        try:
            subprocess.run(
                ["netsh", "interface", "set", "interface",
                 "Wi-Fi", "enable"],
                check=True
            )
            return "Wi-Fi enabled."
        except Exception:
            return "Couldn't enable Wi-Fi."

    def wifi_off(self):
        try:
            from speech import speaker

            speaker.speak("Turning Wi-Fi off.")

            subprocess.run(
                [
                    "netsh",
                    "interface",
                    "set",
                    "interface",
                    "Wi-Fi",
                    "disable"
                ],
                check=True
            )

            return ""

        except Exception as e:
            print(e)
            return "Couldn't disable Wi-Fi."


network = Network()

manager.register_exact("wifi on", network.wifi_on)
manager.register_exact("wi-fi on", network.wifi_on)
manager.register_exact("turn on wifi", network.wifi_on)
manager.register_exact("turn on wi-fi", network.wifi_on)

manager.register_exact("wifi off", network.wifi_off)
manager.register_exact("wi-fi off", network.wifi_off)
manager.register_exact("turn off wifi", network.wifi_off)
manager.register_exact("turn off wi-fi", network.wifi_off)