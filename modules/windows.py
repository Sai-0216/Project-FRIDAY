"""
Project FRIDAY
Window Controller
"""

import pygetwindow as gw
from command_manager import manager


class WindowController:

    def active(self):
        return gw.getActiveWindow()

    def minimize(self):
        try:
            window = self.active()

            if window:
                window.minimize()
                return "Window minimized."

            return "No active window."

        except Exception as e:
            print(e)
            return "Couldn't minimize the window."

    def maximize(self):
        try:
            window = self.active()

            if window:
                window.maximize()
                return "Window maximized."

            return "No active window."

        except Exception as e:
            print(e)
            return "Couldn't maximize the window."

    def restore(self):
        try:
            window = self.active()

            if window:
                window.restore()
                return "Window restored."

            return "No active window."

        except Exception as e:
            print(e)
            return "Couldn't restore the window."

    def close(self):
        try:
            window = self.active()

            if window:
                title = window.title
                window.close()
                return f"Closed {title}"

            return "No active window."

        except Exception as e:
            print(e)
            return "Couldn't close the window."


windows = WindowController()

manager.register_exact("minimize window", windows.minimize)
manager.register_exact("minimise window", windows.minimize)

manager.register_exact("maximize window", windows.maximize)
manager.register_exact("maximise window", windows.maximize)

manager.register_exact("restore window", windows.restore)
manager.register_exact("close window", windows.close)