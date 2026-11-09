"""
Project FRIDAY
Natural Language Workflow Planner
"""

import json
import re

from ai import ai


class WorkflowPlanner:

    SUPPORTED_ACTIONS = {
        "open_app", "close_app", "open_url", "wait", "press", "hotkey",
        "type", "click", "double_click", "right_click",
        "scroll_up", "scroll_down",
    }

    APP_ALIASES = {
        "vs code": "vscode",
        "visual studio code": "vscode",
        "visual studio": "vscode",
        "google chrome": "chrome",
        "chrome browser": "chrome",
        "chrome": "chrome",
        "microsoft edge": "edge",
        "edge browser": "edge",
    }

    URL_ALIASES = {
        "github": "https://github.com/",
        "github website": "https://github.com/",
        "python documentation": "https://docs.python.org/3/",
        "python docs": "https://docs.python.org/3/",
    }

    def plan(self, description):
        description = str(description).strip()

        if not description:
            return {
                "success": False,
                "actions": [],
                "message": "Please tell me what the workflow should do, Sir."
            }

        prompt = f"""
You are FRIDAY's workflow planner.

Convert the user's natural-language workflow description
into a JSON action list.

Return ONLY one valid JSON object.
Do not use Markdown.
Do not use code fences.
Do not add explanations.
Do not omit closing brackets or braces.

Required structure:
{{
    "actions": [
        ["action", "parameter"]
    ]
}}

Supported actions:
open_app
close_app
open_url
wait
press
hotkey
type
click
double_click
right_click
scroll_up
scroll_down

Rules:
1. Preserve the exact requested order.
2. "open Chrome" -> ["open_app", "chrome"]
3. "open VS Code" -> ["open_app", "vscode"]
4. "open GitHub" -> ["open_url", "https://github.com/"]
5. "open Python documentation" -> ["open_url", "https://docs.python.org/3/"]
6. "wait 2 seconds" -> ["wait", 2]
7. "press enter" -> ["press", "enter"]
8. "type Python" -> ["type", "python"]
9. "type Python and press enter" must be:
   ["type", "python"],
   ["press", "enter"]
10. Do not split normal typed phrases into separate type actions.
11. Do not invent unsupported actions.
12. Every action must be an array.
13. Wait must contain a numeric number of seconds.
14. Hotkeys use multiple parameters, e.g. ["hotkey", "ctrl", "c"].

Example:
User: open chrome, open github, wait 2 seconds, type python and press enter

Return:
{{
    "actions": [
        ["open_app", "chrome"],
        ["open_url", "https://github.com/"],
        ["wait", 2],
        ["type", "python"],
        ["press", "enter"]
    ]
}}

User workflow description:
{description}
"""
        return self._ask_and_validate(prompt)

    def plan_addition(self, description):
        description = str(description).strip()

        if not description:
            return {
                "success": False,
                "actions": [],
                "message": "Please tell me what you want to add, Sir."
            }

        prompt = f"""
You are FRIDAY's workflow modification planner.

The user wants to ADD actions to an existing workflow.

Return ONLY valid JSON:
{{
    "actions": [
        ["action", "parameter"]
    ]
}}

Supported actions:
open_app
close_app
open_url
wait
press
hotkey
type
click
double_click
right_click
scroll_up
scroll_down

Rules:
- Return ONLY the NEW actions.
- Preserve requested order.
- VS Code -> vscode.
- Google Chrome -> chrome.
- GitHub -> https://github.com/
- Python documentation -> https://docs.python.org/3/
- "type python and press enter" ->
  ["type", "python"],
  ["press", "enter"]
- Wait must contain a numeric number of seconds.
- Do not use Markdown or code fences.

User request:
{description}
"""
        print("Workflow Planner: Planning addition...")
        return self._ask_and_validate(prompt)

    def plan_removal(self, description):
        description = str(description).strip()

        if not description:
            return {
                "success": False,
                "target": "",
                "message": "Please tell me what you want to remove, Sir."
            }

        prompt = f"""
You are FRIDAY's workflow modification planner.

Return ONLY valid JSON:
{{
    "target": "target description"
}}

Examples:
remove chrome -> {{"target": "chrome"}}
remove github -> {{"target": "github"}}
remove vs code -> {{"target": "vscode"}}
remove vscode -> {{"target": "vscode"}}
remove the wait -> {{"target": "wait"}}

Keep the target short and specific.
Do not return an action list.
Do not use Markdown or code fences.

User request:
{description}
"""

        try:
            print("Workflow Planner: Planning removal...")
            response = ai.ask(prompt)

            if not response:
                return {
                    "success": False,
                    "target": "",
                    "message": "I couldn't determine what to remove, Sir."
                }

            print("Workflow Planner Removal Raw Response:", response)

            data = self._extract_json(response)

            if not isinstance(data, dict):
                raise json.JSONDecodeError("Invalid removal object", response, 0)

            target = self._normalize_target(data.get("target", ""))

            if not target:
                return {
                    "success": False,
                    "target": "",
                    "message": "I couldn't determine what to remove, Sir."
                }

            print("Workflow Planner Removal Target:", target)

            return {
                "success": True,
                "target": target,
                "message": "Removal planned successfully, Sir."
            }

        except json.JSONDecodeError as e:
            print("Workflow Planner Removal JSON Error:", repr(e))
            return {
                "success": False,
                "target": "",
                "message": "I couldn't understand the removal request, Sir."
            }

        except Exception as e:
            print("Workflow Planner Removal Error:", repr(e))
            return {
                "success": False,
                "target": "",
                "message": "Something went wrong while planning the removal, Sir."
            }

    def plan_edit(self, description):
        description = str(description).strip()

        if not description:
            return {
                "success": False,
                "remove": [],
                "add": [],
                "message": "Please tell me how you want to edit it, Sir."
            }

        prompt = f"""
You are FRIDAY's workflow modification planner.

Determine what actions should be removed and what actions
should be added.

Return ONLY valid JSON:
{{
    "remove": ["target"],
    "add": [["action", "parameter"]]
}}

Supported actions:
open_app
close_app
open_url
wait
press
hotkey
type
click
double_click
right_click
scroll_up
scroll_down

Rules:
- "replace vs code with chrome" ->
  remove: ["vscode"]
  add: [["open_app", "chrome"]]
- "replace chrome with vscode" ->
  remove: ["chrome"]
  add: [["open_app", "vscode"]]
- "remove chrome and add github" ->
  remove: ["chrome"]
  add: [["open_url", "https://github.com/"]]
- "add github and wait 5 seconds" ->
  remove: []
  add: [["open_url", "https://github.com/"], ["wait", 5]]
- Normalize VS Code to vscode.
- Normalize Chrome to chrome.
- Normalize GitHub removal target to github.
- Wait must contain a numeric number of seconds.
- If nothing is removed, use [].
- If nothing is added, use [].
- Do not use Markdown or code fences.

User request:
{description}
"""

        try:
            print("Workflow Planner: Planning edit...")
            response = ai.ask(prompt)

            if not response:
                return {
                    "success": False,
                    "remove": [],
                    "add": [],
                    "message": "I couldn't understand the workflow edit, Sir."
                }

            print("Workflow Planner Edit Raw Response:", response)

            data = self._extract_json(response)

            if not isinstance(data, dict):
                raise json.JSONDecodeError("Invalid edit object", response, 0)

            remove = data.get("remove", [])
            add = data.get("add", [])

            if not isinstance(remove, list) or not isinstance(add, list):
                return {
                    "success": False,
                    "remove": [],
                    "add": [],
                    "message": "The workflow edit data was invalid, Sir."
                }

            validated_remove = [
                self._normalize_target(x)
                for x in remove
                if isinstance(x, str) and self._normalize_target(x)
            ]

            validated_add = self._validate_actions(add)

            if not validated_add["success"]:
                return {
                    "success": False,
                    "remove": [],
                    "add": [],
                    "message": validated_add["message"]
                }

            if not validated_remove and not validated_add["actions"]:
                return {
                    "success": False,
                    "remove": [],
                    "add": [],
                    "message": "I couldn't determine any workflow changes, Sir."
                }

            return {
                "success": True,
                "remove": validated_remove,
                "add": validated_add["actions"],
                "message": "Workflow edit planned successfully, Sir."
            }

        except json.JSONDecodeError as e:
            print("Workflow Planner Edit JSON Error:", repr(e))
            return {
                "success": False,
                "remove": [],
                "add": [],
                "message": "I couldn't understand the workflow edit, Sir."
            }

        except Exception as e:
            print("Workflow Planner Edit Error:", repr(e))
            return {
                "success": False,
                "remove": [],
                "add": [],
                "message": "Something went wrong while planning the workflow edit, Sir."
            }

    def _ask_and_validate(self, prompt):
        try:
            print("Workflow Planner: Calling Ollama...")
            response = ai.ask(prompt)
            print("Workflow Planner: Response received.")

            if not response:
                return {
                    "success": False,
                    "actions": [],
                    "message": "I couldn't create the workflow, Sir."
                }

            print("Workflow Planner Raw Response:", response)

            data = self._extract_json(response)

            if not isinstance(data, dict):
                return {
                    "success": False,
                    "actions": [],
                    "message": "The workflow planner returned invalid data, Sir."
                }

            actions = data.get("actions")

            if not isinstance(actions, list):
                return {
                    "success": False,
                    "actions": [],
                    "message": "The workflow actions were invalid, Sir."
                }

            validated = self._validate_actions(actions)

            if not validated["success"]:
                return validated

            if not validated["actions"]:
                return {
                    "success": False,
                    "actions": [],
                    "message": "I couldn't find any actions in that workflow, Sir."
                }

            print("Workflow Planner Actions:", validated["actions"])

            return {
                "success": True,
                "actions": validated["actions"],
                "message": "Workflow planned successfully, Sir."
            }

        except json.JSONDecodeError as e:
            print("Workflow Planner JSON Error:", repr(e))
            return {
                "success": False,
                "actions": [],
                "message": "I couldn't understand the workflow plan, Sir."
            }

        except Exception as e:
            print("Workflow Planner Error:", repr(e))
            return {
                "success": False,
                "actions": [],
                "message": "Something went wrong while creating the workflow, Sir."
            }

    def _extract_json(self, response):
        response = str(response).strip()

        response = re.sub(r"```(?:json|JSON)?", "", response)
        response = response.replace("```", "").strip()

        start = response.find("{")

        if start == -1:
            raise json.JSONDecodeError(
                "No JSON object found", response, 0
            )

        json_text = response[start:].strip()

        try:
            return json.loads(json_text)
        except json.JSONDecodeError as first_error:
            print("Workflow Planner: Initial JSON parse failed.")
            print("Attempting JSON repair...")

        # First try extracting a complete JSON object before
        # attempting structural repair.
        decoder = json.JSONDecoder()

        try:
            data, _ = decoder.raw_decode(json_text)
            return data
        except json.JSONDecodeError:
            pass

        repaired = self._repair_json(json_text)

        try:
            data = json.loads(repaired)
            print("Workflow Planner: JSON repair successful.")
            return data
        except json.JSONDecodeError:
            pass

        # Ollama commonly truncates exactly after the actions array.
        # If so, rebuild the outer object after balancing the array.
        actions_pos = re.search(r'"actions"\s*:\s*\[', repaired)

        if actions_pos:
            prefix = repaired[:actions_pos.start()]
            remainder = repaired[actions_pos.start():]
            remainder = self._repair_json(remainder)

            if not prefix.lstrip().startswith("{"):
                prefix = "{" + prefix

            candidate = prefix + remainder

            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass

        print(
            "Workflow Planner JSON Repair Failed:",
            repr(first_error)
        )
        raise first_error

    def _repair_json(self, text):
        text = text.rstrip()

        # Remove trailing commas.
        text = re.sub(r",\s*$", "", text)
        text = re.sub(r",\s*([}\]])", r"\1", text)

        stack = []
        in_string = False
        escaped = False

        for char in text:
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char in "{[":
                stack.append(char)
            elif char in "}]":
                expected = {"}": "{", "]": "["}[char]
                if stack and stack[-1] == expected:
                    stack.pop()

        if in_string:
            text += '"'

        # Remove a comma that became trailing after closing a string.
        text = re.sub(r",\s*$", "", text)

        while stack:
            opening = stack.pop()
            text += "]" if opening == "[" else "}"

        return text

    def _normalize_target(self, target):
        target = str(target).strip().lower()

        target = re.sub(r"^(?:the\s+)", "", target).strip()

        replacements = (
            ("visual studio code", "vscode"),
            ("vs code", "vscode"),
            ("google chrome", "chrome"),
            ("chrome browser", "chrome"),
            ("github website", "github"),
            ("github url", "github"),
        )

        for old, new in replacements:
            target = target.replace(old, new)

        return target.strip()

    def _validate_actions(self, actions):
        if not isinstance(actions, list):
            return {
                "success": False,
                "actions": [],
                "message": "The workflow actions were invalid, Sir."
            }

        validated_actions = []

        for action in actions:
            if not isinstance(action, list):
                return {
                    "success": False,
                    "actions": [],
                    "message": "The workflow contains an invalid action, Sir."
                }

            if not action:
                return {
                    "success": False,
                    "actions": [],
                    "message": "The workflow contains an empty action, Sir."
                }

            action_type = str(action[0]).lower().strip()

            if action_type not in self.SUPPORTED_ACTIONS:
                return {
                    "success": False,
                    "actions": [],
                    "message": (
                        f"I don't support the {action_type} action yet, Sir."
                    )
                }

            parameters = action[1:]

            if action_type == "wait":
                if len(parameters) != 1:
                    return {
                        "success": False,
                        "actions": [],
                        "message": "A wait action must have one duration, Sir."
                    }

                try:
                    seconds = float(parameters[0])
                    if seconds < 0:
                        raise ValueError

                    if seconds.is_integer():
                        seconds = int(seconds)

                    validated_actions.append(["wait", seconds])

                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "actions": [],
                        "message": (
                            "The workflow contains an invalid wait duration, Sir."
                        )
                    }

                continue

            if action_type in {
                "click",
                "double_click",
                "right_click",
                "scroll_up",
                "scroll_down",
            }:
                if parameters:
                    return {
                        "success": False,
                        "actions": [],
                        "message": (
                            f"The {action_type} action should not have "
                            "parameters, Sir."
                        )
                    }

                validated_actions.append([action_type])
                continue

            if not parameters:
                return {
                    "success": False,
                    "actions": [],
                    "message": (
                        f"The {action_type} action is missing a parameter, Sir."
                    )
                }

            if action_type == "hotkey":
                keys = []

                for parameter in parameters:
                    value = str(parameter).strip().lower()

                    if not value:
                        return {
                            "success": False,
                            "actions": [],
                            "message": (
                                "The hotkey action contains an empty key, Sir."
                            )
                        }

                    keys.append(value)

                validated_actions.append(["hotkey", *keys])
                continue

            value = str(parameters[0]).strip()

            if not value:
                return {
                    "success": False,
                    "actions": [],
                    "message": (
                        f"The {action_type} action has an empty parameter, Sir."
                    )
                }

            if action_type == "open_url":
                value = self.URL_ALIASES.get(
                    value.lower(),
                    value
                )

                if not re.match(r"^https?://", value, re.IGNORECASE):
                    return {
                        "success": False,
                        "actions": [],
                        "message": f"The URL '{value}' is invalid, Sir."
                    }

            if action_type in {"open_app", "close_app"}:
                value = self.APP_ALIASES.get(
                    value.lower().strip(),
                    value.lower().strip()
                )

            if action_type == "press":
                value = value.lower().strip()

                press_aliases = {
                    "return": "enter",
                    "escape": "esc",
                    "space bar": "space",
                    "page up": "pageup",
                    "page down": "pagedown",
                    "back space": "backspace",
                }

                value = press_aliases.get(value, value)

            validated_actions.append([action_type, value])

        return {
            "success": True,
            "actions": validated_actions,
            "message": "Actions validated successfully, Sir."
        }


workflow_planner = WorkflowPlanner()