"""
Project FRIDAY
AI Planner
"""

import json
import re
from urllib.parse import quote_plus

from ai import ai


class Planner:

    # ========================================
    # SUPPORTED INTENTS
    # ========================================

    SUPPORTED_INTENTS = {
        "open_app",
        "open_browser",
        "google_search",
        "youtube_search",

        "volume_up",
        "volume_down",
        "mute",
        "unmute",

        "brightness_up",
        "brightness_down",

        "battery",
        "cpu",
        "ram",
        "disk",

        "open_camera",
        "close_camera",
        "take_photo",

        "take_screenshot",
        "analyze_screen",

        "remember",
        "recall",

        "add_habit",
        "list_habits",
        "habit_progress",
        "delete_habit",
        "complete_habit",

        "daily_briefing",
        "today_plan",
        "daily_progress",

        "add_reminder",
        "list_reminders",
        "remove_reminder",

        "run_workflow",
        "stop_workflow",
        "resume_tasks",
        "retry_task",
        "check_reasoning",
        "workflow_status",
        "list_workflows",
        "show_workflow",
        "delete_workflow",
    }

    # ========================================
    # MAIN PLANNER
    # ========================================

    def plan(self, command):

        command = str(command).strip()

        if not command:
            return None

        # ========================================
        # MULTI-TASK FIRST
        # ========================================

        multi_plan = self._multi_task_plan(
            command
        )

        if multi_plan is not None:

            print(
                "[PLANNER] Multi-task plan:",
                multi_plan
            )

            return multi_plan

        # ========================================
        # SIMPLE LOCAL COMMANDS
        # ========================================

        local_plan = self._local_plan(
            command
        )

        if local_plan is not None:

            print(
                "[PLANNER] Local plan:",
                local_plan
            )

            return local_plan

        # ========================================
        # DIRECT BROWSER SEARCH
        # ========================================

        browser_plan = self._browser_search_plan(
            command
        )

        if browser_plan is not None:

            print(
                "[PLANNER] Direct browser plan:",
                browser_plan
            )

            return browser_plan

        # ========================================
        # AI FALLBACK
        # ========================================

        prompt = f"""
You are FRIDAY's execution planner.

Convert ONLY the CURRENT USER REQUEST into
an executable JSON plan.

Return ONLY valid JSON.

Required format:

{{
    "tasks": [
        {{
            "intent": "intent_name",
            "parameters": {{}}
        }}
    ]
}}

Rules:

1. Use ONLY the current request.
2. NEVER reuse information from previous requests.
3. NEVER invent applications.
4. NEVER invent actions.
5. Preserve the order of actions.
6. Use "parameters", never "data".
7. For open_app use:
   {{"app": "spotify"}}
8. For google_search use:
   {{"query": "python tutorials"}}
9. For open_browser use:
   {{"browser": "chrome", "url": "..."}}
10. Return {{"tasks":[]}} if no executable action exists.
11. Return valid JSON only.
12. Do not return markdown.
13. Do not return explanations.

Supported intents:

open_app
open_browser
google_search
youtube_search
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
open_camera
close_camera
take_photo
take_screenshot
analyze_screen
remember
recall
add_habit
list_habits
habit_progress
delete_habit
complete_habit
daily_briefing
today_plan
daily_progress
add_reminder
list_reminders
remove_reminder
run_workflow
stop_workflow
resume_tasks
retry_task
workflow_status
list_workflows
show_workflow
delete_workflow

CURRENT USER REQUEST:

{command}
"""

        try:

            print(
                "[PLANNER] Sending request to Ollama..."
            )

            response = ai.ask(
                prompt
            )

            if not response:

                print(
                    "[PLANNER] Empty AI response."
                )

                return None

            print(
                "[PLANNER] Raw response:",
                response
            )

            # ========================================
            # CLEAN MARKDOWN
            # ========================================

            response = response.strip()

            response = re.sub(
                r"^```(?:json)?\s*",
                "",
                response,
                flags=re.IGNORECASE
            )

            response = re.sub(
                r"\s*```$",
                "",
                response
            )

            # ========================================
            # FIND JSON
            # ========================================

            match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if not match:

                print(
                    "[PLANNER] No JSON found."
                )

                return None

            json_text = match.group(
                0
            ).strip()

            # ========================================
            # PARSE
            # ========================================

            try:

                plan = json.loads(
                    json_text
                )

            except json.JSONDecodeError as e:

                print(
                    "[PLANNER] JSON error:",
                    repr(e)
                )

                return None

            # ========================================
            # NORMALIZE SINGLE TASK
            # ========================================

            if (
                isinstance(plan, dict)
                and "tasks" not in plan
                and "intent" in plan
            ):

                plan = {
                    "tasks": [
                        {
                            "intent": plan.get(
                                "intent"
                            ),
                            "parameters": plan.get(
                                "parameters",
                                {}
                            )
                        }
                    ]
                }

            if not isinstance(
                plan,
                dict
            ):

                return None

            tasks = plan.get(
                "tasks",
                []
            )

            if not isinstance(
                tasks,
                list
            ):

                return None

            # ========================================
            # VALIDATE TASKS
            # ========================================

            validated_tasks = []

            for task in tasks:

                if not isinstance(
                    task,
                    dict
                ):

                    continue

                intent = task.get(
                    "intent"
                )

                parameters = task.get(
                    "parameters",
                    {}
                )

                # ------------------------------------
                # Compatibility with old "data"
                # ------------------------------------

                if (
                    not parameters
                    and isinstance(
                        task.get("data"),
                        dict
                    )
                ):

                    parameters = task[
                        "data"
                    ]

                if not isinstance(
                    intent,
                    str
                ):

                    continue

                intent = intent.strip()

                if intent not in self.SUPPORTED_INTENTS:

                    print(
                        "[PLANNER] Rejected unsupported "
                        f"intent: {intent}"
                    )

                    continue

                if not isinstance(
                    parameters,
                    dict
                ):

                    parameters = {}

                # ------------------------------------
                # app_name → app
                # ------------------------------------

                if (
                    intent == "open_app"
                    and "app" not in parameters
                    and "app_name" in parameters
                ):

                    parameters["app"] = parameters.pop(
                        "app_name"
                    )

                validated_tasks.append(
                    {
                        "intent": intent,
                        "parameters": parameters
                    }
                )

            validated_tasks = (
                self._validate_against_command(
                    command,
                    validated_tasks
                )
            )

            final_plan = {
                "tasks": validated_tasks
            }

            print(
                "[PLANNER] Parsed plan:",
                final_plan
            )

            return final_plan

        except Exception as e:

            print(
                "[PLANNER] Error:",
                repr(e)
            )

            return None

    # ========================================
    # SIMPLE LOCAL COMMANDS
    # ========================================

    def _local_plan(
        self,
        command
    ):

        text = command.lower().strip()

        # ----------------------------------------
        # BATTERY
        # ----------------------------------------

        battery_phrases = [
            "battery",
            "what is my battery",
            "what's my battery",
            "whats my battery",
            "battery percentage",
            "battery status",
            "how much battery",
            "how much battery do i have",
            "how much battery do i have left",
            "how much battery is left",
        ]

        if any(
            phrase in text
            for phrase in battery_phrases
        ):

            return {
                "tasks": [
                    {
                        "intent": "battery",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # VOLUME UP
        # ----------------------------------------

        if self._is_volume_up(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "volume_up",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # VOLUME DOWN
        # ----------------------------------------

        if self._is_volume_down(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "volume_down",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # MUTE
        # ----------------------------------------

        if (
            text == "mute"
            or "mute the volume" in text
            or "mute volume" in text
        ):

            return {
                "tasks": [
                    {
                        "intent": "mute",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # UNMUTE
        # ----------------------------------------

        if (
            text == "unmute"
            or "unmute the volume" in text
            or "unmute volume" in text
        ):

            return {
                "tasks": [
                    {
                        "intent": "unmute",
                        "parameters": {}
                    }
                ]
            }

        # ----------------------------------------
        # SCREENSHOT
        # ----------------------------------------

        if self._is_screenshot(
            text
        ):

            return {
                "tasks": [
                    {
                        "intent": "take_screenshot",
                        "parameters": {}
                    }
                ]
            }

        return None

    # ========================================
    # VOLUME UP DETECTION
    # ========================================

    def _is_volume_up(
        self,
        text
    ):

        phrases = [
            "volume up",
            "increase volume",
            "increase the volume",
            "turn up the volume",
            "turn the volume up",
            "make the volume louder",
            "make volume louder",
            "make it louder",
            "turn it up",
            "raise the volume",
            "raise volume",
            "volume louder",
            "louder",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # VOLUME DOWN DETECTION
    # ========================================

    def _is_volume_down(
        self,
        text
    ):

        phrases = [
            "volume down",
            "decrease volume",
            "decrease the volume",
            "turn down the volume",
            "turn the volume down",
            "make the volume quieter",
            "make volume quieter",
            "make it quieter",
            "turn it down",
            "lower the volume",
            "lower volume",
            "volume quieter",
            "quieter",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # SCREENSHOT DETECTION
    # ========================================

    def _is_screenshot(
        self,
        text
    ):

        phrases = [
            "take a screenshot",
            "take screenshot",
            "capture the screen",
            "capture screen",
            "capture my screen",
            "capture the display",
            "screenshot this",
            "take a screen capture",
            "screen capture",
        ]

        return any(
            phrase in text
            for phrase in phrases
        )

    # ========================================
    # MULTI-TASK PLANNER
    # ========================================

    def _multi_task_plan(
        self,
        command
    ):

        text = command.lower().strip()

        # ----------------------------------------
        # Must contain multiple actions.
        # ----------------------------------------

        if not any(
            separator in text
            for separator in [
                ",",
                " and ",
                " then ",
                " and then "
            ]
        ):

            return None

        # ========================================
        # NORMALIZE SEPARATORS
        # ========================================

        protected = text

        # ----------------------------------------
        # and then
        # ----------------------------------------

        protected = re.sub(
            r"\s+and then\s+",
            "|||",
            protected
        )

        # ----------------------------------------
        # then
        # ----------------------------------------

        protected = re.sub(
            r"\s+then\s+",
            "|||",
            protected
        )

        # ----------------------------------------
        # Commas before actions
        # ========================================

        protected = re.sub(
            r",\s*(?=(?:"
            r"open|"
            r"launch|"
            r"start|"
            r"close|"
            r"turn|"
            r"increase|"
            r"decrease|"
            r"raise|"
            r"lower|"
            r"make|"
            r"mute|"
            r"unmute|"
            r"search|"
            r"google|"
            r"play|"
            r"take|"
            r"capture|"
            r"set"
            r")\b)",
            "|||",
            protected
        )

        # ----------------------------------------
        # "and" before a new action
        #
        # Example:
        #
        # search Google for Python tutorials
        # and capture my screen
        # ----------------------------------------

        protected = re.sub(
            r"\s+and\s+(?=(?:"
            r"open|"
            r"launch|"
            r"start|"
            r"close|"
            r"turn|"
            r"increase|"
            r"decrease|"
            r"raise|"
            r"lower|"
            r"make|"
            r"mute|"
            r"unmute|"
            r"search|"
            r"google|"
            r"play|"
            r"take|"
            r"capture|"
            r"set"
            r")\b)",
            "|||",
            protected
        )

        # ========================================
        # SPLIT
        # ========================================

        parts = [
            part.strip()
            for part in protected.split(
                "|||"
            )
            if part.strip()
        ]

        if len(parts) < 2:

            return None

        tasks = []

        # ========================================
        # PARSE EACH TASK
        # ========================================

        for part in parts:

            # ====================================
            # OPEN CHROME + SEARCH
            # ====================================

            browser_plan = (
                self._browser_search_plan(
                    part
                )
            )

            if browser_plan is not None:

                tasks.extend(
                    browser_plan["tasks"]
                )

                continue

            # ====================================
            # OPEN / LAUNCH / START APP
            # ====================================

            open_match = re.fullmatch(
                r"(?:open|launch|start)\s+(.+)",
                part
            )

            if open_match:

                app = open_match.group(
                    1
                ).strip()

                app = self._clean_argument(
                    app
                )

                if (
                    app
                    and "search" not in app
                    and "volume" not in app
                    and "brightness" not in app
                ):

                    tasks.append(
                        {
                            "intent": "open_app",
                            "parameters": {
                                "app": app
                            }
                        }
                    )

                    continue

            # ====================================
            # GOOGLE SEARCH
            # ====================================

            google_match = re.fullmatch(
                r"(?:search\s+)?google"
                r"(?:\s+for)?\s+(.+)",
                part
            )

            if google_match:

                query = google_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "google_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # EXPLICIT GOOGLE SEARCH
            # ====================================

            google_match = re.fullmatch(
                r"search\s+google\s+for\s+(.+)",
                part
            )

            if google_match:

                query = google_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "google_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # YOUTUBE SEARCH
            # ====================================

            youtube_match = re.fullmatch(
                r"search\s+youtube\s+for\s+(.+)",
                part
            )

            if youtube_match:

                query = youtube_match.group(
                    1
                ).strip()

                query = self._clean_argument(
                    query
                )

                if query:

                    tasks.append(
                        {
                            "intent": "youtube_search",
                            "parameters": {
                                "query": query
                            }
                        }
                    )

                    continue

            # ====================================
            # VOLUME UP
            # ====================================

            if self._is_volume_up(
                part
            ):

                tasks.append(
                    {
                        "intent": "volume_up",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # VOLUME DOWN
            # ====================================

            if self._is_volume_down(
                part
            ):

                tasks.append(
                    {
                        "intent": "volume_down",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # MUTE
            # ====================================

            if (
                part == "mute"
                or "mute the volume" in part
                or "mute volume" in part
            ):

                tasks.append(
                    {
                        "intent": "mute",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # UNMUTE
            # ====================================

            if (
                part == "unmute"
                or "unmute the volume" in part
                or "unmute volume" in part
            ):

                tasks.append(
                    {
                        "intent": "unmute",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BRIGHTNESS UP
            # ====================================

            if (
                "increase brightness" in part
                or "increase the brightness" in part
                or "turn up the brightness" in part
                or "turn the brightness up" in part
                or "make the brightness higher" in part
                or "make the screen brighter" in part
            ):

                tasks.append(
                    {
                        "intent": "brightness_up",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BRIGHTNESS DOWN
            # ====================================

            if (
                "decrease brightness" in part
                or "decrease the brightness" in part
                or "turn down the brightness" in part
                or "turn the brightness down" in part
                or "make the brightness lower" in part
                or "make the screen darker" in part
            ):

                tasks.append(
                    {
                        "intent": "brightness_down",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # BATTERY
            # ====================================

            if (
                "battery" in part
                or "battery status" in part
                or "battery percentage" in part
            ):

                tasks.append(
                    {
                        "intent": "battery",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # SCREENSHOT
            # ====================================

            if self._is_screenshot(
                part
            ):

                tasks.append(
                    {
                        "intent": "take_screenshot",
                        "parameters": {}
                    }
                )

                continue

            # ====================================
            # UNKNOWN PART
            # ====================================

            return None

        if not tasks:

            return None

        return {
            "tasks": tasks
        }

    # ========================================
    # CLEAN ARGUMENT
    # ========================================

    def _clean_argument(
        self,
        value
    ):

        value = str(
            value
        ).strip()

        value = value.rstrip(
            " ,."
        )

        return value.strip()

    # ========================================
    # DIRECT BROWSER SEARCH
    # ========================================

    def _browser_search_plan(
        self,
        command
    ):

        text = command.lower().strip()

        if "search" not in text:

            return None

        # ========================================
        # OPEN CHROME + SEARCH
        # ========================================

        match = re.search(
            r"(?:open|launch|start)\s+"
            r"(chrome|google chrome)"
            r"\s+and\s+search\s+"
            r"(?:for\s+)?(.+)$",
            text,
            re.IGNORECASE
        )

        if match:

            query = match.group(
                2
            ).strip()

            query = self._clean_argument(
                query
            )

            if not query:

                return None

            url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )

            return {
                "tasks": [
                    {
                        "intent": "open_browser",
                        "parameters": {
                            "browser": "chrome",
                            "url": url
                        }
                    }
                ]
            }

        return None

    # ========================================
    # VALIDATION
    # ========================================

    def _validate_against_command(
        self,
        command,
        tasks
    ):

        text = command.lower()

        validated = []

        for task in tasks:

            intent = task.get(
                "intent"
            )

            params = task.get(
                "parameters",
                {}
            )

            # ----------------------------------------
            # OPEN APP
            # ----------------------------------------

            if intent == "open_app":

                app = str(
                    params.get(
                        "app",
                        ""
                    )
                ).lower().strip()

                if not app:

                    continue

                if app not in text:

                    print(
                        "[PLANNER] Rejected unrelated "
                        f"application: {app}"
                    )

                    continue

            # ----------------------------------------
            # OPEN BROWSER
            # ----------------------------------------

            if intent == "open_browser":

                browser_name = str(
                    params.get(
                        "browser",
                        ""
                    )
                ).lower().strip()

                if (
                    browser_name
                    and browser_name not in text
                    and not (
                        browser_name == "chrome"
                        and (
                            "search" in text
                            or "google" in text
                        )
                    )
                ):

                    print(
                        "[PLANNER] Rejected unrelated "
                        f"browser: {browser_name}"
                    )

                    continue

            # ----------------------------------------
            # GOOGLE SEARCH
            # ----------------------------------------

            if intent == "google_search":

                if (
                    "google" not in text
                    and "search" not in text
                ):

                    print(
                        "[PLANNER] Rejected unrelated "
                        "Google search."
                    )

                    continue

            # ----------------------------------------
            # YOUTUBE SEARCH
            # ----------------------------------------

            if intent == "youtube_search":

                if "youtube" not in text:

                    print(
                        "[PLANNER] Rejected unrelated "
                        "YouTube search."
                    )

                    continue

            validated.append(
                task
            )

        return validated


# ========================================
# GLOBAL PLANNER
# ========================================

planner = Planner()