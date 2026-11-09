"""
Project FRIDAY
Assistant Controller
"""

import time

from brain import brain
from gui import gui
from speech import speaker
from listen import listener
from logger import logger
from modules import task_manager

from proactive.notification_manager import notification_manager
from runtime.unified_runtime import unified_runtime


class Assistant:

    def start(self):

        # ========================================
        # START FRIDAY
        # ========================================

        greeting = "Hello Sir. I am FRIDAY."

        speaker.speak(
            greeting
        )

        # ========================================
        # RECOVER INTERRUPTED TASKS
        # ========================================

        recovered_tasks = (
            task_manager.task_manager
            .recover_interrupted_tasks()
        )

        if recovered_tasks:

            print(
                "[ASSISTANT] Recovered interrupted tasks:",
                recovered_tasks
            )

        # ========================================
        # START PROACTIVE SYSTEM
        # ========================================

        unified_runtime.start()

        while True:

            # ========================================
            # WAITING FOR WAKE WORD
            # ========================================

            gui.set_status_threadsafe(
                "Listening"
            )

            command = listener.listen()

            if not command:
                continue

            command = (
                command
                .lower()
                .strip()
            )

            # ========================================
            # PROACTIVE CONFIRMATION BRIDGE
            # ========================================

            # If the Proactive NotificationManager
            # is waiting for confirmation, expose
            # that confirmation to the existing
            # brain confirmation system.

            if (
                notification_manager.has_pending_confirmation()
                and not brain.pending_confirmation
            ):

                proactive_decision = (
                    notification_manager
                    .get_pending_confirmation()
                )

                brain.pending_confirmation = (
                    proactive_decision
                )

                print(
                    "[ASSISTANT] Proactive confirmation "
                    "bridged to brain."
                )

            # ========================================
            # CONFIRMATION RESPONSES
            # ========================================

            confirmation_words = (

                # YES
                "yes",
                "yeah",
                "yep",
                "yes sir",
                "sure",
                "okay",
                "ok",
                "do it",
                "confirm",
                "go ahead",

                # NO
                "no",
                "nope",
                "no sir",
                "cancel",
                "stop",
                "don't",
                "dont",
                "never mind",
                "nevermind",
            )

            is_confirmation = (
                brain.pending_confirmation
                and command in confirmation_words
            )

            # ========================================
            # WAKE WORD REQUIRED
            # UNLESS CONFIRMATION
            # ========================================

            if (
                not command.startswith("friday")
                and not is_confirmation
            ):

                continue

            # ========================================
            # SHOW COMMAND IN GUI
            # ========================================

            gui.add_message_threadsafe(
                "🧑 You",
                command
            )

            # ========================================
            # REMOVE WAKE WORD
            # ========================================

            if command.startswith(
                "friday"
            ):

                command = command[
                    len("friday"):
                ].strip()

            # ========================================
            # WAKE WORD ONLY
            # ========================================

            if not command:

                speaker.speak(
                    "Yes Sir?"
                )

                time.sleep(
                    0.5
                )

                gui.set_status_threadsafe(
                    "Listening"
                )

                while True:

                    command = listener.listen()

                    if command:
                        break

                command = (
                    command
                    .lower()
                    .strip()
                )

                # ------------------------------------
                # REMOVE WAKE WORD AGAIN
                # ------------------------------------

                if command.startswith(
                    "friday"
                ):

                    command = command[
                        len("friday"):
                    ].strip()

                # ------------------------------------
                # SHOW FINAL COMMAND IN GUI
                # ------------------------------------

                gui.add_message_threadsafe(
                    "🧑 You",
                    command
                )

            # ========================================
            # FINAL CLEANUP
            # ========================================

            command = (
                command
                .strip()
            )

            if not command:
                continue

            logger.info(
                f"User: {command}"
            )

            # ========================================
            # EXIT COMMANDS
            # ========================================

            if command in (
                "exit",
                "quit",
                "shutdown friday",
                "goodbye",
                "stop listening"
            ):

                gui.set_status_threadsafe(
                    "Stopping"
                )

                speaker.speak(
                    "Goodbye Sir."
                )

                # ------------------------------------
                # STOP PROACTIVE SYSTEM
                # ------------------------------------

                unified_runtime.stop()

                break

            # ========================================
            # PROCESS COMMAND
            # ========================================

            gui.set_status_threadsafe(
                "Thinking"
            )

            running = unified_runtime.process_command(
                command,
                source="local_voice",
            )

            # ========================================
            # CONSUME PROACTIVE CONFIRMATION
            # ========================================

            if (
                not brain.pending_confirmation
                and notification_manager.has_pending_confirmation()
            ):

                notification_manager.consume_confirmation()

                print(
                    "[ASSISTANT] Proactive confirmation "
                    "completed."
                )

            # ========================================
            # SAFE HABIT GUI REFRESH
            # ========================================

            gui.refresh_habits_safe()

            # ========================================
            # RETURN TO IDLE
            # ========================================

            gui.set_status_threadsafe(
                "Idle"
            )

            if not running:

                # ------------------------------------
                # STOP PROACTIVE SYSTEM
                # ------------------------------------

                unified_runtime.stop()

                break


# ========================================
# ASSISTANT INSTANCE
# ========================================

assistant = Assistant()