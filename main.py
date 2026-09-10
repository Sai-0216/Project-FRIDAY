"""
Project FRIDAY
Application Entry Point
"""

import os
import threading


# ============================================================
# HIDE PYGAME STARTUP BANNER
# ============================================================

# Hide pygame's startup banner in normal mode.
# The debug console can still be enabled with FRIDAY_DEBUG=1.

if os.getenv(
    "FRIDAY_DEBUG",
    "0"
).strip().lower() not in (
    "1",
    "true",
    "yes",
    "on",
):

    os.environ[
        "PYGAME_HIDE_SUPPORT_PROMPT"
    ] = "1"


# ============================================================
# DEBUG CONSOLE
# ============================================================

from debug_console import install


# Install the filter BEFORE importing FRIDAY modules.
install()


# ============================================================
# GUI FIRST
# ============================================================

# IMPORTANT:
#
# Do NOT import assistant here.
#
# assistant imports brain + speech + other heavy modules.
# Loading those before gui.run() makes FRIDAY appear slow.
#
# The GUI is lightweight enough to initialize first.

from gui import gui


# ============================================================
# BACKGROUND ASSISTANT STARTUP
# ============================================================

def start_assistant():

    try:

        # ----------------------------------------
        # Heavy FRIDAY imports happen here
        # ----------------------------------------
        #
        # These imports now happen in the background
        # instead of blocking GUI startup.
        #

        from assistant import assistant

        # ----------------------------------------
        # Start FRIDAY
        # ----------------------------------------

        assistant.start()

    except Exception as e:

        print(
            "[FRIDAY] Assistant startup error:",
            repr(e)
        )


# ============================================================
# START ASSISTANT THREAD
# ============================================================

assistant_thread = threading.Thread(
    target=start_assistant,
    name="FRIDAY-Assistant",
    daemon=True
)

assistant_thread.start()


# ============================================================
# START GUI
# ============================================================

# Tkinter / CustomTkinter must run on the main thread.

gui.run()