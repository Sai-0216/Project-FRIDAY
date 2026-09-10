"""
Project FRIDAY
Intent Engine
"""

import json
import re

from ai import ai


class IntentEngine:

    def detect(self, command):

        command = (
            str(command)
            .lower()
            .strip()
            .rstrip("?!.,;:")
        )

        # ========================================
        # VISION COMMANDS
        # ========================================

        vision_phrases = (
            "what's on my screen",
            "what is on my screen",
            "whats on my screen",
            "describe my screen",
            "read my screen",
            "read what's on my screen",
            "read what is on my screen",
            "look at my screen",
            "look at the screen",
            "analyze my screen",
            "analyze the screen",
            "what do you see on my screen",
            "what can you see on my screen",
        )

        if any(
            phrase in command
            for phrase in vision_phrases
        ):

            result = {
                "intent": "analyze_screen",
                "parameters": {}
            }

            print(
                "Direct Vision Intent:",
                result
            )

            return result

        # ========================================
        # SCREENSHOT
        # ========================================

        if (
            "take screenshot" in command
            or "take a screenshot" in command
        ):

            result = {
                "intent": "take_screenshot",
                "parameters": {}
            }

            print(
                "Direct Screenshot Intent:",
                result
            )

            return result

        # ========================================
        # CAMERA
        # ========================================

        # ----------------------------------------
        # Open Camera
        # ----------------------------------------

        open_camera_phrases = (
            "open camera",
            "open the camera",
            "open my camera",
            "start camera",
            "start the camera",
            "launch camera",
            "launch the camera",
        )

        if command in open_camera_phrases:

            result = {
                "intent": "open_camera",
                "parameters": {}
            }

            print(
                "Direct Camera Open Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Take Photo
        # ----------------------------------------

        take_photo_phrases = (
            "take a photo",
            "take photo",
            "take a picture",
            "take picture",
            "take a pic",
            "snap a picture",
            "capture a photo",
            "capture photo",
            "capture a picture",
            "capture picture",
        )

        if command in take_photo_phrases:

            result = {
                "intent": "take_photo",
                "parameters": {}
            }

            print(
                "Direct Camera Photo Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Close Camera
        # ----------------------------------------

        close_camera_phrases = (
            "close camera",
            "close the camera",
            "close my camera",
            "stop camera",
            "stop the camera",
            "exit camera",
            "exit the camera",
        )

        if command in close_camera_phrases:

            result = {
                "intent": "close_camera",
                "parameters": {}
            }

            print(
                "Direct Camera Close Intent:",
                result
            )

            return result

        # ========================================
        # FILE & FOLDER CONTROL
        # ========================================

        # ----------------------------------------
        # Open standard folder
        # ----------------------------------------

        folder_aliases = {
            "desktop": "desktop",
            "my desktop": "desktop",
            "documents": "documents",
            "document": "documents",
            "my documents": "documents",
            "downloads": "downloads",
            "download": "downloads",
            "my downloads": "downloads",
            "pictures": "pictures",
            "picture": "pictures",
            "photos": "pictures",
            "videos": "videos",
            "video": "videos",
            "music": "music",
            "songs": "music",
        }

        open_folder_match = re.match(
            r"open\s+(?:my\s+)?(.+?)$",
            command
        )

        if open_folder_match:
            target = open_folder_match.group(1).strip()
            folder_name = folder_aliases.get(target)

            if folder_name:
                result = {
                    "intent": "open_folder",
                    "parameters": {
                        "location": folder_name
                    }
                }

                print(
                    "Direct Open Folder Intent:",
                    result
                )

                return result

        # ----------------------------------------
        # Create folder
        # ----------------------------------------

        create_folder_match = re.match(
            r"(?:create|make)\s+"
            r"(?:a\s+)?"
            r"folder\s+"
            r"(?:called\s+|named\s+)?"
            r"(.+?)"
            r"(?:\s+in\s+(.+))?$",
            command
        )

        if create_folder_match:
            folder_name = create_folder_match.group(1).strip()
            location = create_folder_match.group(2)
            location = location.strip() if location else "desktop"

            result = {
                "intent": "create_folder",
                "parameters": {
                    "name": folder_name,
                    "location": location
                }
            }

            print(
                "Direct Create Folder Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Create file
        # ----------------------------------------

        create_file_match = re.match(
            r"(?:create|make)\s+"
            r"(?:a\s+)?"
            r"file\s+"
            r"(?:called\s+|named\s+)?"
            r"(.+?)"
            r"(?:\s+in\s+(.+))?$",
            command
        )

        if create_file_match:
            file_name = create_file_match.group(1).strip()
            location = create_file_match.group(2)
            location = location.strip() if location else "desktop"

            result = {
                "intent": "create_file",
                "parameters": {
                    "name": file_name,
                    "location": location
                }
            }

            print(
                "Direct Create File Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Open file
        # ----------------------------------------

        open_file_match = re.match(
            r"open\s+file\s+(.+)$",
            command
        )

        if open_file_match:
            file_name = open_file_match.group(1).strip()

            result = {
                "intent": "open_file",
                "parameters": {
                    "path": file_name
                }
            }

            print(
                "Direct Open File Intent:",
                result
            )

            return result

        # ========================================
        # APPLICATION CONTROL
        # ========================================

        # ----------------------------------------
        # Open App
        # ----------------------------------------

        open_app_match = re.match(
            r"open\s+(.+)$",
            command
        )

        if open_app_match:

            app_name = (
                open_app_match
                .group(1)
                .strip()
            )

            supported_apps = {
                "chrome",
                "google chrome",
                "vscode",
                "vs code",
                "visual studio code",
                "spotify",
                "calculator",
                "calc",
                "notepad",
                "paint",
                "explorer",
                "cmd",
            }

            if app_name in supported_apps:

                app_aliases = {
                    "google chrome": "chrome",
                    "vs code": "vscode",
                    "visual studio code": "vscode",
                    "calc": "calculator",
                }

                app_name = app_aliases.get(
                    app_name,
                    app_name
                )

                result = {
                    "intent": "open_app",
                    "parameters": {
                        "app": app_name
                    }
                }

                print(
                    "Direct Open App Intent:",
                    result
                )

                return result

        # ----------------------------------------
        # Close App
        # ----------------------------------------

        close_app_match = re.match(
            r"close\s+(.+)$",
            command
        )

        if close_app_match:

            app_name = (
                close_app_match
                .group(1)
                .strip()
            )

            supported_apps = {
                "chrome",
                "google chrome",
                "vscode",
                "vs code",
                "visual studio code",
                "spotify",
                "calculator",
                "calc",
                "notepad",
                "paint",
                "explorer",
                "cmd",
            }

            if app_name in supported_apps:

                app_aliases = {
                    "google chrome": "chrome",
                    "vs code": "vscode",
                    "visual studio code": "vscode",
                    "calc": "calculator",
                }

                app_name = app_aliases.get(
                    app_name,
                    app_name
                )

                result = {
                    "intent": "close_app",
                    "parameters": {
                        "app": app_name
                    }
                }

                print(
                    "Direct Close App Intent:",
                    result
                )

                return result

        # ========================================
        # SYSTEM CONTROLS
        # ========================================

        # ----------------------------------------
        # Volume Up
        # ----------------------------------------

        volume_up_phrases = (
            "increase the volume",
            "increase volume",
            "volume up",
            "turn the volume up",
            "turn volume up",
            "make it louder",
            "make that louder",
            "raise the volume",
            "raise volume",
            "louder",
            "could you increase the volume?",
            "could you increase volume?",
            "raise the sound",
            "raise sound",
            "turn the sound up",
            "turn sound up",
        )

        if command in volume_up_phrases:

            result = {
                "intent": "volume_up",
                "parameters": {}
            }

            print(
                "Direct Volume Up Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Volume Down
        # ----------------------------------------

        volume_down_phrases = (
            "decrease the volume",
            "decrease volume",
            "volume down",
            "turn the volume down",
            "turn volume down",
            "make it quieter",
            "make that quieter",
            "lower the volume",
            "lower volume",
            "quieter",
            "turn the sound down",
            "turn sound down",
            "lower the sound",
            "lower sound",
            "could you decrease the volume?",
            "could you lower the volume?",
        )

        if command in volume_down_phrases:

            result = {
                "intent": "volume_down",
                "parameters": {}
            }

            print(
                "Direct Volume Down Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Mute
        # ----------------------------------------

        mute_phrases = (
            "mute",
            "mute the volume",
            "mute volume",
            "turn mute on",
            "silence",
            "silence the volume",
            "mute the sound",
            "please mute",
            "can you mute the volume",
        )

        if command in mute_phrases:

            result = {
                "intent": "mute",
                "parameters": {}
            }

            print(
                "Direct Mute Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Unmute
        # ----------------------------------------

        unmute_phrases = (
            "unmute",
            "unmute the volume",
            "unmute volume",
            "turn mute off",
            "unmute the sound",
            "please unmute",
            "can you unmute the volume",
        )

        if command in unmute_phrases:

            result = {
                "intent": "unmute",
                "parameters": {}
            }

            print(
                "Direct Unmute Intent:",
                result
            )

            return result

        # ========================================
        # BRIGHTNESS CONTROLS
        # ========================================

        # ----------------------------------------
        # Brightness Up
        # ----------------------------------------

        brightness_up_phrases = (
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
            "could you increase the brightness?",
            "could you brighten the screen?",
            "turn the screen brightness up",
        )

        if command in brightness_up_phrases:

            result = {
                "intent": "brightness_up",
                "parameters": {}
            }

            print(
                "Direct Brightness Up Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Brightness Down
        # ----------------------------------------

        brightness_down_phrases = (
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
            "could you decrease the brightness?",
            "could you dim the screen?",
            "turn the screen brightness down",
        )

        if command in brightness_down_phrases:

            result = {
                "intent": "brightness_down",
                "parameters": {}
            }

            print(
                "Direct Brightness Down Intent:",
                result
            )

            return result

        # ========================================
        # SYSTEM INFORMATION
        # ========================================

        # ----------------------------------------
        # Battery
        # ----------------------------------------

        battery_phrases = (
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
            "what is my battery level"
            "what's my battery level",
        )

        if command in battery_phrases:

            result = {
                "intent": "battery",
                "parameters": {}
            }

            print(
                "Direct Battery Intent:",
                result
            )

            return result

        # ----------------------------------------
        # CPU
        # ----------------------------------------

        cpu_phrases = (
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
        )

        if command in cpu_phrases:

            result = {
                "intent": "cpu",
                "parameters": {}
            }

            print(
                "Direct CPU Intent:",
                result
            )

            return result

        # ----------------------------------------
        # RAM
        # ----------------------------------------

        ram_phrases = (
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
        )

        if command in ram_phrases:

            result = {
                "intent": "ram",
                "parameters": {}
            }

            print(
                "Direct RAM Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Disk
        # ----------------------------------------

        disk_phrases = (
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
            "how much disk space do i have",
        )

        if command in disk_phrases:

            result = {
                "intent": "disk",
                "parameters": {}
            }

            print(
                "Direct Disk Intent:",
                result
            )

            return result

        # ========================================
        # WINDOWS SYSTEM CONTROLS
        # ========================================

        # ----------------------------------------
        # Task Manager
        # ----------------------------------------

        if command in (
            "correct your reasoning",
            "correct my reasoning",
            "correct the reasoning",
            "improve your reasoning",
            "improve my reasoning",
            "fix your reasoning",
            "fix my reasoning",
        ):
            return {"intent":"correct_reasoning","parameters":{}}

        if command in (
            "open task manager",
            "task manager",
            "open taskmanager",
            "open the task manager",
            "open the taskmanager",
        ):

            result = {
                "intent": "task_manager",
                "parameters": {}
            }

            print(
                "Direct Task Manager Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Windows Settings
        # ----------------------------------------

        if command in (
            "open settings",
            "open windows settings",
            "windows settings",
            "settings",
            "open the settings",
            "open windows setting",
        ):

            result = {
                "intent": "settings",
                "parameters": {}
            }

            print(
                "Direct Settings Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Lock Computer
        # ----------------------------------------

        if command in (
            "lock computer",
            "lock the computer",
            "lock pc",
            "lock the pc",
            "lock my computer",
            "lock my pc",
        ):

            result = {
                "intent": "lock_computer",
                "parameters": {}
            }

            print(
                "Direct Lock Computer Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Sleep
        # ----------------------------------------

        if command in (
            "sleep",
            "sleep computer",
            "sleep pc",
            "put computer to sleep",
            "put the computer to sleep",
            "put pc to sleep",
            "put the pc to sleep",
        ):

            result = {
                "intent": "sleep",
                "parameters": {}
            }

            print(
                "Direct Sleep Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Restart Computer
        # ----------------------------------------

        if command in (
            "restart",
            "restart computer",
            "restart the computer",
            "restart pc",
            "restart the pc",
            "restart my computer",
            "restart my pc",
        ):

            result = {
                "intent": "restart",
                "parameters": {}
            }

            print(
                "Direct Restart Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Shutdown Computer
        # ----------------------------------------

        if command in (
            "shutdown",
            "shut down",
            "shutdown computer",
            "shut down computer",
            "shutdown the computer",
            "shut down the computer",
            "shutdown pc",
            "shut down pc",
            "shutdown the pc",
            "shut down the pc",
            "shutdown my computer",
            "shut down my computer",
            "shutdown my pc",
            "shut down my pc",
        ):

            result = {
                "intent": "shutdown",
                "parameters": {}
            }

            print(
                "Direct Shutdown Intent:",
                result
            )

            return result

        # ========================================
        # WORKFLOWS
        # ========================================

        # ----------------------------------------
        # Stop / Cancel workflow
        # ----------------------------------------

        if command in (
            "stop workflow",
            "cancel workflow",
            "stop the workflow",
            "cancel the workflow",
            "stop current workflow",
            "cancel current workflow",
            "stop my workflow",
            "cancel my workflow",
        ):

            result = {
                "intent": "stop_workflow",
                "parameters": {}
            }

            print(
                "Direct Workflow Stop Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Workflow status
        # ----------------------------------------

        if command in (
            "workflow status",
            "what is the workflow status",
            "what's the workflow status",
            "is a workflow running",
            "is any workflow running",
            "what workflow is running",
            "which workflow is running",
            "show workflow status",
            "check workflow status",
            "status of workflow",
            "status of my workflow",
        ):

            result = {
                "intent": "workflow_status",
                "parameters": {}
            }

            print(
                "Direct Workflow Status Intent:",
                result
            )

            return result

        # ----------------------------------------
        # List workflows
        # ----------------------------------------

        if command in (
            "show my workflows",
            "show workflows",
            "list my workflows",
            "list workflows",
            "what workflows do i have",
            "what are my workflows",
        ):

            result = {
                "intent": "list_workflows",
                "parameters": {}
            }

            print(
                "Direct Workflow List Intent:",
                result
            )

            return result

        # ----------------------------------------
        # ADD TO EXISTING WORKFLOW
        # ----------------------------------------

        add_workflow_match = re.match(
            r"(?:add|append)\s+"
            r"(.+?)\s+"
            r"(?:to|into)\s+"
            r"(?:my\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+workflow$",
            command
        )

        if add_workflow_match:

            description = (
                add_workflow_match
                .group(1)
                .strip()
            )

            workflow_name = (
                add_workflow_match
                .group(2)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "add_to_workflow",
                "parameters": {
                    "workflow": workflow_name,
                    "description": description
                }
            }

            print(
                "Direct Add Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # REMOVE FROM EXISTING WORKFLOW
        # ----------------------------------------

        remove_from_workflow_match = re.match(
            r"(?:remove|delete)\s+"
            r"(.+?)\s+"
            r"from\s+"
            r"(?:my\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+workflow$",
            command
        )

        if remove_from_workflow_match:

            target = (
                remove_from_workflow_match
                .group(1)
                .strip()
            )

            workflow_name = (
                remove_from_workflow_match
                .group(2)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "remove_from_workflow",
                "parameters": {
                    "workflow": workflow_name,
                    "target": target
                }
            }

            print(
                "Direct Remove Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # EDIT EXISTING WORKFLOW
        # ----------------------------------------

        edit_workflow_match = re.match(
            r"(?:edit|modify|change|update)\s+"
            r"(?:my\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+workflow\s+"
            r"(?:to\s+)?"
            r"(.+)$",
            command
        )

        if edit_workflow_match:

            workflow_name = (
                edit_workflow_match
                .group(1)
                .strip()
            )

            description = (
                edit_workflow_match
                .group(2)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "edit_workflow",
                "parameters": {
                    "workflow": workflow_name,
                    "description": description
                }
            }

            print(
                "Direct Edit Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Show specific workflow
        # ----------------------------------------

        show_workflow_match = re.match(
            r"(?:show|view|display|describe|inspect|check)\s+"
            r"(?:my\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+workflow$",
            command
        )

        if show_workflow_match:

            workflow_name = (
                show_workflow_match
                .group(1)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "show_workflow",
                "parameters": {
                    "workflow": workflow_name
                }
            }

            print(
                "Direct Show Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Delete workflow
        # ----------------------------------------

        delete_workflow_match = re.match(
            r"(?:delete|remove)\s+"
            r"(?:my\s+)?"
            r"(?:the\s+)?"
            r"(.+?)\s+workflow$",
            command
        )

        if delete_workflow_match:

            workflow_name = (
                delete_workflow_match
                .group(1)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "delete_workflow",
                "parameters": {
                    "workflow": workflow_name
                }
            }

            print(
                "Direct Delete Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Create workflow
        # ----------------------------------------

        create_workflow_match = re.match(
            r"(?:create|add|make)\s+"
            r"(?:a\s+)?"
            r"workflow\s+"
            r"(?:called|named)\s+"
            r"(.+?)"
            r"(?:\s+that\s+(.+))?$",
            command
        )

        if create_workflow_match:

            workflow = (
                create_workflow_match
                .group(1)
                .strip()
            )

            description = (
                create_workflow_match
                .group(2)
            )

            if description:
                description = description.strip()
            else:
                description = ""

            workflow = re.sub(
                r"\s+",
                "_",
                workflow
            )

            result = {
                "intent": "create_workflow",
                "parameters": {
                    "workflow": workflow,
                    "description": description
                }
            }

            print(
                "Direct Create Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Study workflow
        # ----------------------------------------

        study_workflow_phrases = (
            "start study",
            "start my study",
            "start study session",
            "start my study session",
            "begin study",
            "begin my study",
            "begin study session",
            "begin my study session",
            "start studying",
            "start my studying",
            "start my study mode",
            "start study mode",
            "begin study mode",
            "begin my study mode",
            "run study workflow",
            "run my study workflow",
        )

        if command in study_workflow_phrases:

            result = {
                "intent": "run_workflow",
                "parameters": {
                    "workflow": "study"
                }
            }

            print(
                "Direct Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Coding workflow
        # ----------------------------------------

        coding_workflow_phrases = (
            "start coding",
            "start my coding",
            "start coding session",
            "start my coding session",
            "begin coding",
            "begin my coding",
            "begin coding session",
            "begin my coding session",
            "start programming",
            "start my programming",
            "begin coding mode",
            "begin my coding mode",
            "start coding mode",
            "start my coding mode",
            "run coding workflow",
            "run my coding workflow",
        )

        if command in coding_workflow_phrases:

            result = {
                "intent": "run_workflow",
                "parameters": {
                    "workflow": "coding"
                }
            }

            print(
                "Direct Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Work workflow
        # ----------------------------------------

        work_workflow_phrases = (
            "start work",
            "start my work",
            "start work session",
            "start my work session",
            "begin work",
            "begin my work",
            "begin work session",
            "begin my work session",
            "run work workflow",
            "run my work workflow",
            "start work mode",
            "start my work mode",
            "begin work mode",
            "begin my work mode",
        )

        if command in work_workflow_phrases:

            result = {
                "intent": "run_workflow",
                "parameters": {
                    "workflow": "work"
                }
            }

            print(
                "Direct Workflow Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Generic workflow start
        # ----------------------------------------

        run_workflow_match = re.match(
            r"(?:start|run|begin|launch|execute)\s+"
            r"(?:my\s+)?"
            r"(.+?)\s+workflow$",
            command
        )

        if run_workflow_match:

            workflow_name = (
                run_workflow_match
                .group(1)
                .strip()
            )

            workflow_name = re.sub(
                r"\s+",
                "_",
                workflow_name
            )

            result = {
                "intent": "run_workflow",
                "parameters": {
                    "workflow": workflow_name
                }
            }

            print(
                "Direct Generic Workflow Intent:",
                result
            )

            return result

        # ========================================
        # HABITS
        # ========================================

        if command.startswith(
            "add a habit called "
        ):

            habit = command.replace(
                "add a habit called ",
                "",
                1
            ).strip()

            result = {
                "intent": "add_habit",
                "parameters": {
                    "habit": habit
                }
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        if command.startswith(
            "add habit "
        ):

            habit = command.replace(
                "add habit ",
                "",
                1
            ).strip()

            result = {
                "intent": "add_habit",
                "parameters": {
                    "habit": habit
                }
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Complete habit
        # ----------------------------------------

        if command.startswith(
            "complete "
        ):

            habit = command.replace(
                "complete ",
                "",
                1
            ).strip()

            result = {
                "intent": "complete_habit",
                "parameters": {
                    "habit": habit
                }
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        # ----------------------------------------
        # List habits
        # ----------------------------------------

        if command in (
            "what are my habits",
            "show my habits",
            "show my habit",
            "what are my habits today",
            "show today's habits",
            "show my habits today",
        ):

            result = {
                "intent": "list_habits",
                "parameters": {}
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Habit progress
        # ----------------------------------------

        if command.startswith(
            "habit progress "
        ):

            habit = command.replace(
                "habit progress ",
                "",
                1
            ).strip()

            result = {
                "intent": "habit_progress",
                "parameters": {
                    "habit": habit
                }
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Delete habit
        # ----------------------------------------

        if command.startswith(
            "remove habit "
        ):

            habit = command.replace(
                "remove habit ",
                "",
                1
            ).strip()

            result = {
                "intent": "delete_habit",
                "parameters": {
                    "habit": habit
                }
            }

            print(
                "Direct Habit Intent:",
                result
            )

            return result

        # ========================================
        # ROUTINE COMMANDS
        # ========================================

        if command.startswith(
            "add morning routine "
        ):

            task = command.replace(
                "add morning routine ",
                "",
                1
            ).strip()

            result = {
                "intent": "add_routine",
                "parameters": {
                    "period": "morning",
                    "task": task
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command.startswith(
            "add evening routine "
        ):

            task = command.replace(
                "add evening routine ",
                "",
                1
            ).strip()

            result = {
                "intent": "add_routine",
                "parameters": {
                    "period": "evening",
                    "task": task
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command.startswith(
            "remove morning routine "
        ):

            task = command.replace(
                "remove morning routine ",
                "",
                1
            ).strip()

            result = {
                "intent": "remove_routine",
                "parameters": {
                    "period": "morning",
                    "task": task
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command.startswith(
            "remove evening routine "
        ):

            task = command.replace(
                "remove evening routine ",
                "",
                1
            ).strip()

            result = {
                "intent": "remove_routine",
                "parameters": {
                    "period": "evening",
                    "task": task
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command in (
            "show my morning routine",
            "what is my morning routine",
            "what's my morning routine",
            "show morning routine",
            "morning routine",
        ):

            result = {
                "intent": "show_routine",
                "parameters": {
                    "period": "morning"
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command in (
            "show my evening routine",
            "what is my evening routine",
            "what's my evening routine",
            "show evening routine",
            "evening routine",
        ):

            result = {
                "intent": "show_routine",
                "parameters": {
                    "period": "evening"
                }
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        if command in (
            "show my routine",
            "show routine",
            "what is my routine",
            "what's my routine",
            "what is my daily routine",
            "what's my daily routine",
            "show my daily routine",
            "show full routine",
            "daily routine",
        ):

            result = {
                "intent": "show_full_routine",
                "parameters": {}
            }

            print(
                "Direct Routine Intent:",
                result
            )

            return result

        # ========================================
        # DAILY BRIEFING
        # ========================================

        if command in (
            "good morning",
            "morning",
            "morning friday",
            "give me my morning briefing",
            "give me today's briefing",
            "give me my daily briefing",
            "daily briefing",
        ):

            result = {
                "intent": "daily_briefing",
                "parameters": {}
            }

            print(
                "Direct Briefing Intent:",
                result
            )

            return result

        # ========================================
        # TODAY'S PLAN
        # ========================================

        if command in (
            "what should i do today",
            "what do i have to do today",
            "what do i need to do today",
            "show my plan",
            "show today's plan",
            "what is my plan today",
            "what's my plan today",
            "show my daily plan",
        ):

            result = {
                "intent": "today_plan",
                "parameters": {}
            }

            print(
                "Direct Plan Intent:",
                result
            )

            return result

        # ========================================
        # DAILY PROGRESS
        # ========================================

        if command in (
            "how am i doing today",
            "how am i doing",
            "show my progress",
            "show today's progress",
            "what is my progress today",
            "what's my progress today",
        ):

            result = {
                "intent": "daily_progress",
                "parameters": {}
            }

            print(
                "Direct Progress Intent:",
                result
            )

            return result

        # ========================================
        # REMINDERS
        # ========================================

        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        # ========================================
        # WEEKLY RECURRING REMINDER
        # ========================================

        weekly_command = (
            command
            .replace("everyday", "every day")
            .replace("p.m.", "pm")
            .replace("a.m.", "am")
            .replace("p.m", "pm")
            .replace("a.m", "am")
        )

        weekly_result = None

        weekly_match = re.match(
            r"remind me every "
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday) "
            r"at "
            r"(\d{1,2})(?:[:](\d{2}))?\s*"
            r"(am|pm) "
            r"to (.+)",
            weekly_command
        )

        if weekly_match:

            day_name = weekly_match.group(1)

            hour = int(
                weekly_match.group(2)
            )

            minute = int(
                weekly_match.group(3) or 0
            )

            period = weekly_match.group(4)

            text = weekly_match.group(5).strip()

            if period == "pm" and hour != 12:
                hour += 12

            elif period == "am" and hour == 12:
                hour = 0

            weekly_result = (
                weekdays[day_name],
                hour,
                minute,
                text
            )

        if weekly_result is None:

            weekly_match = re.match(
                r"remind me every "
                r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday) "
                r"at (\d{1,2}):(\d{2}) "
                r"to (.+)",
                weekly_command
            )

            if weekly_match:

                day_name = weekly_match.group(1)

                weekly_result = (
                    weekdays[day_name],
                    int(weekly_match.group(2)),
                    int(weekly_match.group(3)),
                    weekly_match.group(4).strip()
                )

        if weekly_result is None:

            weekly_match = re.match(
                r"remind me every "
                r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday) "
                r"at (\d{4}) "
                r"to (.+)",
                weekly_command
            )

            if weekly_match:

                day_name = weekly_match.group(1)

                raw_time = weekly_match.group(2)

                weekly_result = (
                    weekdays[day_name],
                    int(raw_time[:2]),
                    int(raw_time[2:]),
                    weekly_match.group(3).strip()
                )

        if weekly_result is not None:

            weekday, hour, minute, text = weekly_result

            if (
                0 <= hour <= 23
                and 0 <= minute <= 59
                and text
            ):

                result = {
                    "intent": "add_weekly_reminder",
                    "parameters": {
                        "weekday": weekday,
                        "time": f"{hour:02d}:{minute:02d}",
                        "text": text
                    }
                }

                print(
                    "Direct Weekly Reminder Intent:",
                    result
                )

                return result

        # ========================================
        # DAILY RECURRING REMINDER
        # ========================================

        recurring_command = (
            command
            .replace("everyday", "every day")
            .replace("p.m.", "pm")
            .replace("a.m.", "am")
            .replace("p.m", "pm")
            .replace("a.m", "am")
        )

        recurring_result = None

        match = re.match(
            r"remind me every day at "
            r"(\d{1,2})(?:[:](\d{2}))?\s*"
            r"(am|pm) "
            r"to (.+)",
            recurring_command
        )

        if match:

            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            period = match.group(3)
            text = match.group(4).strip()

            if period == "pm" and hour != 12:
                hour += 12

            elif period == "am" and hour == 12:
                hour = 0

            recurring_result = (
                hour,
                minute,
                text
            )

        if recurring_result is None:

            match = re.match(
                r"remind me every day at "
                r"(\d{1,2}):(\d{2}) "
                r"to (.+)",
                recurring_command
            )

            if match:

                recurring_result = (
                    int(match.group(1)),
                    int(match.group(2)),
                    match.group(3).strip()
                )

        if recurring_result is None:

            match = re.match(
                r"remind me every day at "
                r"(\d{4}) "
                r"to (.+)",
                recurring_command
            )

            if match:

                raw_time = match.group(1)

                recurring_result = (
                    int(raw_time[:2]),
                    int(raw_time[2:]),
                    match.group(2).strip()
                )

        if recurring_result is not None:

            hour, minute, text = recurring_result

            if (
                0 <= hour <= 23
                and 0 <= minute <= 59
                and text
            ):

                result = {
                    "intent": "add_reminder",
                    "parameters": {
                        "time": f"{hour:02d}:{minute:02d}",
                        "text": text
                    }
                }

                print(
                    "Direct Recurring Reminder Intent:",
                    result
                )

                return result

        # ========================================
        # RELATIVE REMINDER
        # ========================================

        relative_match = re.match(
            r"remind me in "
            r"(\d+) "
            r"(minute|minutes|hour|hours) "
            r"to (.+)",
            command
        )

        if relative_match:

            result = {
                "intent": "add_relative_reminder",
                "parameters": {
                    "amount": relative_match.group(1),
                    "unit": relative_match.group(2),
                    "text": relative_match.group(3).strip()
                }
            }

            print(
                "Direct Relative Reminder Intent:",
                result
            )

            return result

        # ========================================
        # FIXED-TIME REMINDER
        # ========================================

        reminder_result = None

        match = re.match(
            r"remind me at "
            r"(\d{1,2}):(\d{2}) "
            r"to (.+)",
            command
        )

        if match:

            reminder_result = (
                int(match.group(1)),
                int(match.group(2)),
                match.group(3).strip()
            )

        if reminder_result is None:

            match = re.match(
                r"remind me at "
                r"(\d{4}) "
                r"to (.+)",
                command
            )

            if match:

                raw_time = match.group(1)

                reminder_result = (
                    int(raw_time[:2]),
                    int(raw_time[2:]),
                    match.group(2).strip()
                )

        if reminder_result is None:

            match = re.match(
                r"remind me at "
                r"(\d{1,2}) hours? "
                r"(\d{1,2}) minutes? "
                r"to (.+)",
                command
            )

            if match:

                reminder_result = (
                    int(match.group(1)),
                    int(match.group(2)),
                    match.group(3).strip()
                )

        if reminder_result is None:

            match = re.match(
                r"remind me at "
                r"(\d{1,2}) hours? "
                r"to (.+)",
                command
            )

            if match:

                reminder_result = (
                    int(match.group(1)),
                    0,
                    match.group(2).strip()
                )

        if reminder_result is None:

            match = re.match(
                r"remind me at "
                r"(\d{1,2})\s*"
                r"(am|pm) "
                r"to (.+)",
                command
            )

            if match:

                hour = int(match.group(1))

                period = match.group(2)

                if period == "pm" and hour != 12:
                    hour += 12

                elif period == "am" and hour == 12:
                    hour = 0

                reminder_result = (
                    hour,
                    0,
                    match.group(3).strip()
                )

        if reminder_result is not None:

            hour, minute, text = reminder_result

            if (
                0 <= hour <= 23
                and 0 <= minute <= 59
                and text
            ):

                result = {
                    "intent": "add_reminder",
                    "parameters": {
                        "time": f"{hour:02d}:{minute:02d}",
                        "text": text
                    }
                }

                print(
                    "Direct Reminder Intent:",
                    result
                )

                return result

        # ----------------------------------------
        # Show reminders
        # ----------------------------------------

        if command in (
            "show my reminders",
            "show reminders",
            "what are my reminders",
            "list my reminders",
        ):

            result = {
                "intent": "list_reminders",
                "parameters": {}
            }

            print(
                "Direct Reminder Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Remove reminder by natural language
        # ----------------------------------------

        natural_remove_match = re.match(
            r"(?:remove|delete) "
            r"(?:my )?"
            r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday) "
            r"(.+?) reminder$",
            command
        )

        if natural_remove_match:

            result = {
                "intent": "remove_reminder_by_match",
                "parameters": {
                    "weekday": weekdays[
                        natural_remove_match.group(1)
                    ],
                    "text": natural_remove_match.group(2).strip()
                }
            }

            print(
                "Direct Natural Reminder Removal Intent:",
                result
            )

            return result

        # ----------------------------------------
        # Remove reminder by ID
        # ----------------------------------------

        reminder_remove_match = re.match(
            r"(?:remove|delete) reminder (\d+)",
            command
        )

        if reminder_remove_match:

            result = {
                "intent": "remove_reminder",
                "parameters": {
                    "id": int(
                        reminder_remove_match.group(1)
                    )
                }
            }

            print(
                "Direct Reminder Removal Intent:",
                result
            )

            return result

        # ========================================
        # MEMORY
        # ========================================

        if command.startswith("remember "):

            text = command.replace(
                "remember ",
                "",
                1
            ).strip()

            result = {
                "intent": "remember",
                "parameters": {
                    "text": text
                }
            }

            print(
                "Direct Memory Intent:",
                result
            )

            return result

        if command.startswith("recall "):

            text = command.replace(
                "recall ",
                "",
                1
            ).strip()

            result = {
                "intent": "recall",
                "parameters": {
                    "text": text
                }
            }

            print(
                "Direct Memory Intent:",
                result
            )

            return result

        # ========================================
        # WEB SEARCH
        # ========================================

        # ----------------------------------------
        # YouTube Search / Play
        # ----------------------------------------

        youtube_match = re.match(
            r"(?:search\s+youtube(?:\s+for)?|play)\s+(.+?)(?:\s+on\s+youtube)?$",
            command
        )

        if youtube_match:

            query = youtube_match.group(1).strip()

            if query:

                result = {
                    "intent": "youtube_play",
                    "parameters": {
                        "query": query
                    }
                }

                print(
                    "Direct YouTube Search Intent:",
                    result
                )

                return result

        # ----------------------------------------
        # Google Search
        # ----------------------------------------

        google_match = re.match(
            r"search(?:\s+google)?(?:\s+for)?\s+(.+)$",
            command
        )

        if google_match:

            query = google_match.group(1).strip()

            if query:

                result = {
                    "intent": "google_search",
                    "parameters": {
                        "query": query
                    }
                }

                print(
                    "Direct Google Search Intent:",
                    result
                )

                return result

        # ========================================
        # PHASE 20 / TASK INTELLIGENCE
        # ========================================

        if command in (
            "resume my interrupted tasks",
            "resume interrupted tasks",
            "resume my interrupted task",
            "resume interrupted task",
        ):
            return {"intent": "resume_tasks", "parameters": {}}

        if command in (
            "retry the failed task",
            "retry failed task",
            "retry my failed task",
            "retry failed tasks",
        ):
            return {"intent": "retry_task", "parameters": {}}

        if command in (
            "check your reasoning",
            "check my reasoning",
            "check reasoning",
            "review your reasoning",
            "assess your reasoning",
        ):
            return {"intent": "check_reasoning", "parameters": {}}

        if command in (
            "verify your decision",
            "verify my decision",
            "verify the decision",
            "check your decision",
            "validate your decision",
        ):
            return {"intent": "verify_decision", "parameters": {}}

        # ========================================
        # AI CLASSIFICATION
        # ========================================

        prompt = f"""
You are FRIDAY's intent classifier.

Return ONLY ONE valid JSON object.

Valid intents:

create_workflow
run_workflow
stop_workflow
workflow_status
list_workflows
show_workflow
delete_workflow
add_to_workflow
remove_from_workflow
edit_workflow

open_app
close_app
open_folder
create_folder
create_file
open_file
google_search
youtube_search

task_manager
settings
lock_computer
sleep
restart
shutdown

volume_up
volume_down
mute
unmute

brightness_up
brightness_down

battery
cpu
ram
disk

take_photo
open_camera
close_camera

take_screenshot
analyze_screen

add_habit
complete_habit
list_habits
habit_progress
delete_habit

add_routine
remove_routine
show_routine
show_full_routine

daily_briefing
today_plan
daily_progress

add_reminder
add_weekly_reminder
add_relative_reminder
list_reminders
remove_reminder
remove_reminder_by_match

remember
recall

unknown

WORKFLOW RULES:

Create workflow:

User:
create workflow python new that opens vscode and chrome

Return:
{{
    "intent": "create_workflow",
    "parameters": {{
        "workflow": "python_new",
        "description": "opens vscode and chrome"
    }}
}}

Add to workflow:

User:
add github to python new workflow

Return:
{{
    "intent": "add_to_workflow",
    "parameters": {{
        "workflow": "python_new",
        "description": "github"
    }}
}}

Remove from workflow:

User:
remove chrome from python new workflow

Return:
{{
    "intent": "remove_from_workflow",
    "parameters": {{
        "workflow": "python_new",
        "target": "chrome"
    }}
}}

Edit workflow:

User:
edit python new workflow replace chrome with firefox

Return:
{{
    "intent": "edit_workflow",
    "parameters": {{
        "workflow": "python_new",
        "description": "replace chrome with firefox"
    }}
}}

Run workflow:

User:
start python new workflow

Return:
{{
    "intent": "run_workflow",
    "parameters": {{
        "workflow": "python_new"
    }}
}}

Show workflow:

User:
show python new workflow

Return:
{{
    "intent": "show_workflow",
    "parameters": {{
        "workflow": "python_new"
    }}
}}

Delete workflow:

User:
delete python new workflow

Return:
{{
    "intent": "delete_workflow",
    "parameters": {{
        "workflow": "python_new"
    }}
}}

Convert spaces in workflow names to underscores.

Examples:

python new -> python_new
my coding -> my_coding
youtube setup -> youtube_setup

Do not invent workflow names.

If the user wants to stop or cancel a running workflow:

{{
    "intent": "stop_workflow",
    "parameters": {{}}
}}

If the user asks about workflow status:

{{
    "intent": "workflow_status",
    "parameters": {{}}
}}

If the user asks to list workflows:

{{
    "intent": "list_workflows",
    "parameters": {{}}
}}

WEEKLY REMINDER RULES:

If the command is a weekly reminder:

{{
    "intent": "add_weekly_reminder",
    "parameters": {{
        "weekday": 0,
        "time": "09:00",
        "text": "study python"
    }}
}}

Weekday values:

Monday = 0
Tuesday = 1
Wednesday = 2
Thursday = 3
Friday = 4
Saturday = 5
Sunday = 6

If the command is a normal conversation question:

{{
    "intent": "unknown",
    "parameters": {{}}
}}

Do not invent an intent.

User command:

{command}
"""

        print(
            "Calling Ollama..."
        )

        try:

            response = ai.ask(
                prompt
            )

            print(
                "Returned from Ollama"
            )

            print(
                "Raw Response:",
                response
            )

            if not response:

                return {
                    "intent": "unknown",
                    "parameters": {}
                }

            response = response.strip()

            # ========================================
            # PARSE JSON
            # ========================================

            start = response.find("{")

            if start == -1:

                return {
                    "intent": "unknown",
                    "parameters": {}
                }

            decoder = json.JSONDecoder()

            result, _ = decoder.raw_decode(
                response[start:]
            )

            # ========================================
            # VALIDATE RESULT
            # ========================================

            if not isinstance(
                result,
                dict
            ):

                return {
                    "intent": "unknown",
                    "parameters": {}
                }

            if "intent" not in result:

                return {
                    "intent": "unknown",
                    "parameters": {}
                }

            if "parameters" not in result:

                result["parameters"] = {}

            # ========================================
            # NORMALIZE WORKFLOW NAME
            # ========================================

            workflow_intents = (
                "run_workflow",
                "show_workflow",
                "delete_workflow",
                "add_to_workflow",
                "remove_from_workflow",
                "edit_workflow",
                "create_workflow",
            )

            if result.get(
                "intent"
            ) in workflow_intents:

                parameters = result.get(
                    "parameters",
                    {}
                )

                if isinstance(
                    parameters,
                    dict
                ):

                    workflow_name = parameters.get(
                        "workflow"
                    )

                    if isinstance(
                        workflow_name,
                        str
                    ):

                        parameters["workflow"] = re.sub(
                            r"\s+",
                            "_",
                            workflow_name.strip()
                        )

            print(
                "Parsed Intent:",
                result
            )

            return result

        except json.JSONDecodeError as e:

            print(
                "JSON parsing failed:",
                repr(e)
            )

            return {
                "intent": "unknown",
                "parameters": {}
            }

        except Exception as e:

            print(
                "Intent Engine Error:",
                repr(e)
            )

            return {
                "intent": "unknown",
                "parameters": {}
            }


intent_engine = IntentEngine()