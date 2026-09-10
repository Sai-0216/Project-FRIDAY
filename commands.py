"""
Project FRIDAY
Command Router

Handles fast commands before they reach
the intent engine / planner.
"""

import re

from speech import speaker
from command_manager import manager
from modules.memory import memory

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

        command = (
            str(command)
            .lower()
            .strip()
        )

        # ========================================
        # FAST NATURAL MEMORY UPDATES
        # ========================================
        #
        # Examples:
        #
        #   i prefer vscode
        #   i prefer vscode now
        #   i switched to cursor
        #
        #   i am learning python
        #   i am studying java
        #
        #   i am working on friday
        #   i am building friday
        #
        # ========================================

        editor_update_patterns = (

            r"^(?:i|i'm|i am)\s+"
            r"(?:prefer|use|work in|work with)\s+"
            r"(.+?)(?:\s+now)?$",

            r"^i switched to\s+(.+?)$",

        )

        language_update_patterns = (

            r"^(?:i'm|i am)\s+"
            r"(?:learning|studying)\s+"
            r"(.+?)(?:\s+now)?$",

        )

        project_update_patterns = (

            r"^(?:i'm|i am)\s+"
            r"working on\s+(.+?)$",

            r"^(?:i'm|i am)\s+"
            r"building\s+(.+?)$",

        )

        # ----------------------------------------
        # Editor
        # ----------------------------------------

        editor_value = None

        for pattern in editor_update_patterns:

            match = re.match(
                pattern,
                command
            )

            if match:

                editor_value = (
                    match.group(1)
                    .strip()
                )

                break

        if editor_value:

            previous_value = (
                memory.recall(
                    "my favourite editor"
                )
            )

            memory.remember(
                "my favourite editor",
                editor_value
            )

            if previous_value:

                speaker.speak(
                    "Got it, Sir. I updated "
                    f"your favourite editor to "
                    f"{editor_value}."
                )

            else:

                speaker.speak(
                    f"I'll remember that your "
                    f"favourite editor is "
                    f"{editor_value}, Sir."
                )

            return True

        # ----------------------------------------
        # Learning language
        # ----------------------------------------

        language_value = None

        for pattern in language_update_patterns:

            match = re.match(
                pattern,
                command
            )

            if match:

                language_value = (
                    match.group(1)
                    .strip()
                )

                break

        if language_value:

            previous_value = (
                memory.recall(
                    "my learning language"
                )
            )

            memory.remember(
                "my learning language",
                language_value
            )

            if previous_value:

                speaker.speak(
                    "Got it, Sir. I updated "
                    f"your learning language to "
                    f"{language_value}."
                )

            else:

                speaker.speak(
                    f"I'll remember that you are "
                    f"learning {language_value}, Sir."
                )

            return True

        # ----------------------------------------
        # Project
        # ----------------------------------------

        project_value = None

        for pattern in project_update_patterns:

            match = re.match(
                pattern,
                command
            )

            if match:

                project_value = (
                    match.group(1)
                    .strip()
                )

                break

        if project_value:

            previous_value = (
                memory.recall(
                    "my project"
                )
            )

            memory.remember(
                "my project",
                project_value
            )

            if previous_value:

                speaker.speak(
                    "Got it, Sir. I updated "
                    f"your project to "
                    f"{project_value}."
                )

            else:

                speaker.speak(
                    f"I'll remember that your "
                    f"project is {project_value}, Sir."
                )

            return True

        # ========================================
        # FAST PREFERENCE SUMMARY
        # ========================================

        preference_questions = (

            "what are my preferences",
            "what are my favourite things",
            "what are my favorite things",

        )

        if command in preference_questions:

            stored_memory = memory.all()

            editor = stored_memory.get(
                "my favourite editor"
            )

            language = stored_memory.get(
                "my favourite language"
            )

            learning_language = stored_memory.get(
                "my learning language"
            )

            project = stored_memory.get(
                "my project"
            )

            parts = []

            if editor:

                parts.append(
                    f"your favourite editor is {editor}"
                )

            if language:

                parts.append(
                    f"your favourite programming language is {language}"
                )

            if learning_language:

                parts.append(
                    f"you are currently learning {learning_language}"
                )

            if project:

                parts.append(
                    f"your current project is {project}"
                )

            if not parts:

                speaker.speak(
                    "I don't have any saved preferences yet, Sir."
                )

                return True

            response = (
                "Here is what I remember, Sir: "
                + "; ".join(parts)
                + "."
            )

            speaker.speak(
                response
            )

            return True

        # ========================================
        # FAST NATURAL MEMORY RECALL
        # ========================================

        # ----------------------------------------
        # Favourite editor
        # ----------------------------------------

        editor_recall_questions = (

            "what editor do i like",
            "what editor do i prefer",
            "what editor do i use",
            "what editor am i using",
            "what editor do i work in",
            "what editor do i work with",
            "which editor do i use",
            "which editor do i prefer",
            "which editor do i work in",
            "which editor do i work with",
            "what ide do i use",
            "which ide do i use",
            "which editor is my favourite",
            "which editor is my favorite",
            "what is my favourite editor",
            "what is my favorite editor",
            "what's my favourite editor",
            "what's my favorite editor",
            "whats my favourite editor",
            "whats my favorite editor",

        )

        if command in editor_recall_questions:

            value = memory.recall(
                "my favourite editor"
            )

            if value:

                speaker.speak(
                    f"Your favourite editor is {value}, Sir."
                )

            else:

                speaker.speak(
                    "I don't have a favourite editor saved yet, Sir."
                )

            return True

        # ----------------------------------------
        # Favourite programming language
        # ----------------------------------------

        favourite_language_questions = (

            "what language do i like",
            "what language do i prefer",
            "what programming language do i prefer",
            "what programming language do i like",

            "which language do i like",
            "which language do i prefer",
            "which programming language do i prefer",
            "which programming language do i like",

            "what is my favourite language",
            "what is my favorite language",
            "what's my favourite language",
            "what's my favorite language",
            "whats my favourite language",
            "whats my favorite language",

            "which language is my favourite",
            "which language is my favorite",
            "which programming language is my favourite",
            "which programming language is my favorite",

        )

        if command in favourite_language_questions:

            value = memory.recall(
                "my favourite language"
            )

            if value:

                speaker.speak(
                    f"Your favourite programming language is {value}, Sir."
                )

            else:

                speaker.speak(
                    "I don't have your favourite programming language saved yet, Sir."
                )

            return True

        # ----------------------------------------
        # Learning language
        # ----------------------------------------
        #
        # This must happen locally so questions such as:
        #
        #   which one am i learning?
        #   what language am i learning?
        #   which language am i studying?
        #
        # never reach Ollama.
        #
        # ----------------------------------------

        learning_language_questions = (

            "what language am i learning",
            "which language am i learning",

            "what programming language am i learning",
            "which programming language am i learning",

            "what language am i currently learning",
            "which language am i currently learning",

            "what programming language am i currently learning",
            "which programming language am i currently learning",

            "what language am i studying",
            "which language am i studying",

            "what programming language am i studying",
            "which programming language am i studying",

            "what programming language am i currently studying",
            "which programming language am i currently studying",

            "which one am i learning",
            "what one am i learning",

            "which one am i studying",
            "what one am i studying",

            "what am i learning",
            "what am i studying",

        )

        if command in learning_language_questions:

            value = memory.recall(
                "my learning language"
            )

            if value:

                speaker.speak(
                    f"You are currently learning {value}, Sir."
                )

            else:

                speaker.speak(
                    "I don't have a current learning language saved yet, Sir."
                )

            return True

        # ----------------------------------------
        # Project
        # ----------------------------------------

        project_recall_questions = (

            "what is my project",
            "what's my project",
            "whats my project",

            "what is my current project",
            "what's my current project",
            "whats my current project",

            "what project am i working on",
            "which project am i working on",

            "what project am i building",
            "which project am i building",

            "what am i working on",
            "what am i building",

            "remind me what my project is",
            "remind me what project i am working on",

        )

        if command in project_recall_questions:

            value = memory.recall(
                "my project"
            )

            if value:

                speaker.speak(
                    f"Your current project is {value}, Sir."
                )

            else:

                speaker.speak(
                    "I don't have your project saved yet, Sir."
                )

            return True

        # ========================================
        # FAST NATURAL MEMORY DELETION
        # ========================================

        # ----------------------------------------
        # Favourite editor
        # ----------------------------------------

        editor_delete_questions = (

            "remove my favourite editor",
            "delete my favourite editor",
            "remove my favorite editor",
            "delete my favorite editor",

            "remove my current editor",
            "delete my current editor",

            "remove my ide",
            "delete my ide",

        )

        if command in editor_delete_questions:

            memory.forget(
                "my favourite editor"
            )

            speaker.speak(
                "I've removed your favourite editor from memory, Sir."
            )

            return True

        # ----------------------------------------
        # Favourite language
        # ----------------------------------------

        language_delete_questions = (

            "remove my favourite language",
            "delete my favourite language",

            "remove my favorite language",
            "delete my favorite language",

            "remove my preferred language",
            "delete my preferred language",

        )

        if command in language_delete_questions:

            memory.forget(
                "my favourite language"
            )

            speaker.speak(
                "I've removed your favourite programming language from memory, Sir."
            )

            return True

        # ----------------------------------------
        # Learning language
        # ----------------------------------------

        learning_language_delete_questions = (

            "remove my learning language",
            "delete my learning language",

            "remove my current learning language",
            "delete my current learning language",

            "remove my study language",
            "delete my study language",

            "remove the language i'm learning",
            "delete the language i'm learning",

            "remove the language i am learning",
            "delete the language i am learning",

        )

        if command in learning_language_delete_questions:

            memory.forget(
                "my learning language"
            )

            speaker.speak(
                "I've removed your learning language from memory, Sir."
            )

            return True

        # ----------------------------------------
        # Project
        # ----------------------------------------

        project_delete_questions = (

            "remove my project",
            "delete my project",

            "remove my current project",
            "delete my current project",

            "forget my project",

        )

        if command in project_delete_questions:

            memory.forget(
                "my project"
            )

            speaker.speak(
                "I've removed your project from memory, Sir."
            )

            return True

        # ========================================
        # FAST GENERAL NATURAL MEMORY MATCHING
        # ========================================

        normalized_memory = (
            command
            .rstrip("?!.,;:")
            .strip()
        )

        memory_aliases = {

            # ------------------------------------
            # Editor
            # ------------------------------------

            "which editor do i work with":
                "my favourite editor",

            "what editor do i work with":
                "my favourite editor",

            "what editor am i using":
                "my favourite editor",

            "which ide do i use":
                "my favourite editor",

            # ------------------------------------
            # Favourite language
            # ------------------------------------

            "what language do i prefer":
                "my favourite language",

            "what programming language do i prefer":
                "my favourite language",

            "what language do i like":
                "my favourite language",

            "what programming language do i like":
                "my favourite language",

            "which language do i prefer":
                "my favourite language",

            "which programming language do i prefer":
                "my favourite language",

            # ------------------------------------
            # Learning language
            # ------------------------------------

            "what language am i learning":
                "my learning language",

            "which language am i learning":
                "my learning language",

            "what programming language am i learning":
                "my learning language",

            "which programming language am i learning":
                "my learning language",

            "what language am i studying":
                "my learning language",

            "which language am i studying":
                "my learning language",

            "what programming language am i studying":
                "my learning language",

            "which programming language am i studying":
                "my learning language",

            "which one am i learning":
                "my learning language",

            "what one am i learning":
                "my learning language",

            "which one am i studying":
                "my learning language",

            "what one am i studying":
                "my learning language",

            # ------------------------------------
            # Project
            # ------------------------------------

            "what project am i working on":
                "my project",

            "which project am i working on":
                "my project",

            "what project am i building":
                "my project",

            "which project am i building":
                "my project",

            "what am i working on":
                "my project",

            "what am i building":
                "my project",

        }

        if normalized_memory in memory_aliases:

            memory_key = (
                memory_aliases[
                    normalized_memory
                ]
            )

            value = memory.recall(
                memory_key
            )

            if value:

                if memory_key == "my favourite editor":

                    response = (
                        f"Your favourite editor is {value}, Sir."
                    )

                elif memory_key == "my favourite language":

                    response = (
                        "Your favourite programming "
                        f"language is {value}, Sir."
                    )

                elif memory_key == "my learning language":

                    response = (
                        f"You are currently learning "
                        f"{value}, Sir."
                    )

                elif memory_key == "my project":

                    response = (
                        f"Your current project is "
                        f"{value}, Sir."
                    )

                else:

                    response = (
                        f"{memory_key} is {value}, Sir."
                    )

                speaker.speak(
                    response
                )

                return True

        # ========================================
        # NATURAL PERSONAL MEMORY QUESTIONS
        # ========================================
        #
        # Let Brain/AI handle broader personal
        # questions that aren't explicit local aliases.
        #
        # ========================================

        personal_memory_markers = (

            "my favourite",
            "my favorite",

            "my preference",
            "my preferences",

            "do i like",
            "do i prefer",

            "which do i like",

            "what do i like",
            "what do i prefer",

            "what are my",

            "what is my",
            "what's my",
            "whats my",

        )

        personal_memory_question = (
            command.endswith("?")
            and any(
                marker in command
                for marker in personal_memory_markers
            )
        )

        if personal_memory_question:

            return False

        # ========================================
        # PROTECTED INTENTS
        # ========================================
        #
        # These commands must NOT be swallowed by
        # command_manager.
        #
        # They are handled by:
        #
        # Brain
        #   ↓
        # Intent Engine
        #   ↓
        # Dispatcher
        #
        # ========================================

        protected_intents = {

            # ------------------------------------
            # Personal memory questions
            # ------------------------------------

            "what is my favourite language?",
            "what's my favourite language?",
            "whats my favourite language?",

            "what is my favorite language?",
            "what's my favorite language?",
            "whats my favorite language?",

            "what is my project?",
            "what's my project?",
            "whats my project?",

            # ------------------------------------
            # Volume
            # ------------------------------------

            "mute",
            "unmute",

            "increase the volume",
            "increase volume",
            "volume up",

            "decrease the volume",
            "decrease volume",
            "volume down",

            # ------------------------------------
            # Brightness
            # ------------------------------------

            "brightness up",
            "increase brightness",
            "increase the brightness",

            "turn brightness up",
            "turn the brightness up",

            "make screen brighter",
            "make the screen brighter",

            "brighter",

            "raise brightness",
            "raise the brightness",

            "brightness down",
            "decrease brightness",
            "decrease the brightness",

            "turn brightness down",
            "turn the brightness down",

            "make screen darker",
            "make the screen darker",

            "darker",

            "lower brightness",
            "lower the brightness",

            "dim the screen",

            # ------------------------------------
            # Battery
            # ------------------------------------

            "battery",
            "battery status",

            "check battery",
            "check my battery",

            "what is my battery",
            "what's my battery",

            "how much battery do i have",
            "how much battery is left",

            "battery percentage",

            "what is my battery percentage",
            "what's my battery percentage",

            # ------------------------------------
            # CPU
            # ------------------------------------

            "cpu",
            "cpu usage",

            "check cpu",
            "check cpu usage",

            "what is my cpu usage",
            "what's my cpu usage",

            "how much cpu am i using",
            "how much cpu is being used",

            "processor usage",
            "check processor usage",

            # ------------------------------------
            # RAM
            # ------------------------------------

            "ram",
            "ram usage",

            "check ram",
            "check ram usage",

            "what is my ram usage",
            "what's my ram usage",

            "how much ram am i using",
            "how much memory am i using",

            "memory usage",
            "check memory usage",

            # ------------------------------------
            # Disk
            # ------------------------------------

            "disk",
            "disk usage",

            "check disk",
            "check disk usage",

            "disk space",
            "check disk space",

            "how much disk space is left",
            "how much storage is left",

            "storage",
            "storage usage",

            "check storage",
            "check storage usage",

            # ------------------------------------
            # Camera
            # ------------------------------------

            "open camera",
            "open the camera",

            "start camera",
            "start the camera",

            "launch camera",
            "launch the camera",

            "take photo",
            "take a photo",

            "take picture",
            "take a picture",

            "capture photo",
            "capture a photo",

            "capture picture",
            "capture a picture",

            "close camera",
            "close the camera",

            "stop camera",
            "stop the camera",

            "exit camera",
            "exit the camera",

            # ------------------------------------
            # Screenshot
            # ------------------------------------

            "take screenshot",
            "take a screenshot",

        }

        # ========================================
        # PROTECTED COMMAND
        # ========================================

        if command in protected_intents:

            return False

        # ========================================
        # FAST COMMAND
        # ========================================

        response = manager.execute(
            command
        )

        # ----------------------------------------
        # No fast command matched
        #
        # Do NOT print anything here.
        # Brain will decide whether to use the
        # planner or intent engine.
        # ----------------------------------------

        if response is None:

            return False

        # ----------------------------------------
        # Fast command succeeded
        # ----------------------------------------

        if response:

            speaker.speak(
                response
            )

        return True

    # ========================================
    # DIRECT INTENT EXECUTION
    # ========================================

    def execute_intent(
        self,
        intent
    ):

        name = intent.get(
            "intent"
        )

        # ----------------------------------------
        # Volume Up
        # ----------------------------------------

        if name == "volume_up":

            response = (
                volume.volume_up()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Volume Down
        # ----------------------------------------

        elif name == "volume_down":

            response = (
                volume.volume_down()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Mute
        # ----------------------------------------

        elif name == "mute":

            response = (
                volume.mute()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Unmute
        # ----------------------------------------

        elif name == "unmute":

            response = (
                volume.unmute()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Brightness Up
        # ----------------------------------------

        elif name == "brightness_up":

            response = (
                brightness.brightness_up()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Brightness Down
        # ----------------------------------------

        elif name == "brightness_down":

            response = (
                brightness.brightness_down()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Battery
        # ----------------------------------------

        elif name == "battery":

            response = (
                system.battery()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # CPU
        # ----------------------------------------

        elif name == "cpu":

            response = (
                system.cpu()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # RAM
        # ----------------------------------------

        elif name == "ram":

            response = (
                system.ram()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Disk
        # ----------------------------------------

        elif name == "disk":

            response = (
                system.disk()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Open Camera
        # ----------------------------------------

        elif name == "open_camera":

            response = (
                camera.open_camera()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Take Photo
        # ----------------------------------------

        elif name == "take_photo":

            response = (
                camera.take_photo()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Close Camera
        # ----------------------------------------

        elif name == "close_camera":

            response = (
                camera.close_camera()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Screenshot
        # ----------------------------------------

        elif name == "take_screenshot":

            response = (
                screenshot.take_screenshot()
            )

            if response:

                speaker.speak(
                    response
                )

            return True

        # ----------------------------------------
        # Unknown direct intent
        # ----------------------------------------

        speaker.speak(
            "Sorry, I don't know how to do that yet."
        )

        return True


router = CommandRouter()