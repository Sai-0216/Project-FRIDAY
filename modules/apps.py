"""
Project FRIDAY
Apps Module
"""

import subprocess
import os
from command_manager import manager


class Apps:

    APPS = {

        "chrome": [
            "chrome",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ),
        ],

        "vscode": [
            "code",
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        ],

        "calculator": ["calc"],

        "cmd": ["cmd"],

        "explorer": ["explorer"],

        "notepad": ["notepad"],

        "paint": ["mspaint"],
    }

    def open_app(self, app_name):

        app_name = app_name.lower().strip()

        if app_name not in self.APPS:
            return f"Sorry sir, I don't know how to open {app_name}."

        for target in self.APPS[app_name]:

            try:
                subprocess.Popen(target)
                return f"Opening {app_name}."

            except Exception:
                continue

        return f"Sorry sir, I couldn't open {app_name}."


apps = Apps()

manager.register_prefix("open ", apps.open_app)