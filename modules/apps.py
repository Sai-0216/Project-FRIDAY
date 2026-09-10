"""
Project FRIDAY
Application Controller
"""

import os
import subprocess

import psutil


class Apps:

    APPS = {

        # ========================================
        # CHROME
        # ========================================

        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
            ),
            "chrome",
        ],

        # ========================================
        # SPOTIFY
        # ========================================

        "spotify": [
            os.path.expandvars(
                r"%APPDATA%\Spotify\Spotify.exe"
            ),
            os.path.expandvars(
                r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"
            ),
            "spotify",
        ],

        # ========================================
        # VS CODE
        # ========================================

        "vscode": [
            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
            ),
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            os.path.expandvars(
                r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"
            ),
            "code.cmd",
        ],

        # ========================================
        # WINDOWS APPS
        # ========================================

        "calculator": [
            "calc"
        ],

        "cmd": [
            "cmd"
        ],

        "explorer": [
            "explorer"
        ],

        "notepad": [
            "notepad"
        ],

        "paint": [
            "mspaint"
        ],
    }

    # ========================================
    # OPEN APP
    # ========================================

    def open_app(
        self,
        app_name
    ):

        app_name = str(
            app_name
        ).lower().strip()

        # ----------------------------------------
        # Check supported application
        # ----------------------------------------

        if app_name not in self.APPS:

            return (
                f"Sorry Sir, I don't know how to open "
                f"{app_name}."
            )

        # ----------------------------------------
        # Try every configured target
        # ----------------------------------------

        for target in self.APPS[app_name]:

            try:

                target = os.path.expandvars(
                    target
                )

                # --------------------------------
                # Actual executable path
                # --------------------------------

                if (
                    os.path.isabs(target)
                    and os.path.isfile(target)
                ):

                    subprocess.Popen(
                        [target],
                        shell=False
                    )

                    return (
                        f"Opening {app_name}, Sir."
                    )

                # --------------------------------
                # Windows command / executable
                # --------------------------------

                if not os.path.isabs(target):

                    subprocess.Popen(
                        target,
                        shell=True
                    )

                    return (
                        f"Opening {app_name}, Sir."
                    )

                # --------------------------------
                # Absolute path doesn't exist
                # --------------------------------

                print(
                    f"[Apps] Target does not exist: "
                    f"{target}"
                )

            except (
                FileNotFoundError,
                OSError
            ) as e:

                print(
                    f"[Apps] Could not open "
                    f"{app_name} using "
                    f"{target}: {e}"
                )

                continue

            except Exception as e:

                print(
                    f"[Apps] Unexpected error "
                    f"opening {app_name}: "
                    f"{e}"
                )

                continue

        return (
            f"Sorry Sir, I couldn't open "
            f"{app_name}."
        )

    # ========================================
    # CLOSE APP
    # ========================================

    def close_app(
        self,
        app_name
    ):

        app_name = str(
            app_name
        ).lower().strip()

        # ========================================
        # PROCESS NAMES
        # ========================================

        process_names = {

            "chrome": [
                "chrome.exe"
            ],

            "spotify": [
                "Spotify.exe"
            ],

            "vscode": [
                "Code.exe"
            ],

            "calculator": [
                "CalculatorApp.exe",
                "calc.exe"
            ],

            "cmd": [
                "cmd.exe"
            ],

            "notepad": [
                "notepad.exe"
            ],

            "paint": [
                "mspaint.exe"
            ],

            "explorer": [
                "explorer.exe"
            ],
        }

        # ========================================
        # UNKNOWN APPLICATION
        # ========================================

        if app_name not in process_names:

            return (
                f"Sorry Sir, I don't know how to close "
                f"{app_name}."
            )

        closed = False

        # ========================================
        # FIND APPLICATION PROCESSES
        # ========================================

        for process in psutil.process_iter(
            ["name"]
        ):

            try:

                name = process.info.get(
                    "name"
                )

                if not name:
                    continue

                valid_names = [
                    p.lower()
                    for p in process_names[
                        app_name
                    ]
                ]

                if name.lower() in valid_names:

                    print(
                        f"[Apps] Closing "
                        f"{name}"
                    )

                    process.terminate()

                    closed = True

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):

                continue

        # ========================================
        # RESULT
        # ========================================

        if closed:

            return (
                f"Closed {app_name}, Sir."
            )

        return (
            f"{app_name} is not currently running."
        )

    # ========================================
    # RUNNING APPS
    # ========================================

    def running_apps(self):
        """
        Return supported applications that are
        currently running.
        """

        process_names = {

            "chrome": [
                "chrome.exe"
            ],

            "spotify": [
                "Spotify.exe"
            ],

            "vscode": [
                "Code.exe"
            ],

            "calculator": [
                "CalculatorApp.exe",
                "calc.exe"
            ],

            "cmd": [
                "cmd.exe"
            ],

            "notepad": [
                "notepad.exe"
            ],

            "paint": [
                "mspaint.exe"
            ],

            "explorer": [
                "explorer.exe"
            ],
        }

        running = set()

        for process in psutil.process_iter(
            ["name"]
        ):

            try:

                name = process.info.get(
                    "name"
                )

                if not name:
                    continue

                name = name.lower()

                for app_name, valid_names in process_names.items():

                    if name in [
                        process_name.lower()
                        for process_name in valid_names
                    ]:

                        running.add(
                            app_name
                        )

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess
            ):

                continue

        return sorted(
            running
        )


# ========================================
# APPLICATION INSTANCE
# ========================================

apps = Apps()