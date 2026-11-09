import math
from urllib.parse import urlparse


READ_ONLY_INTENTS = {
    "battery", "cpu", "ram", "disk",
    "list_habits", "habit_progress",
    "recall", "show_routine", "show_full_routine",
    "daily_briefing", "today_plan", "daily_progress",
    "list_reminders", "workflow_status", "list_workflows",
    "show_workflow", "verify_decision", "check_reasoning",
}

LOW_RISK_INTENTS = {
    "volume_up", "volume_down", "mute", "unmute",
    "brightness_up", "brightness_down",
    "open_app", "open_browser", "google_search",
    "youtube_search", "youtube_play",
    "open_file", "open_folder",
    "task_manager", "settings", "close_camera",
}

CONFIRMATION_INTENTS = {
    "add_habit", "complete_habit", "delete_habit",
    "remember",
    "add_routine", "remove_routine",
    "add_reminder", "add_weekly_reminder",
    "add_relative_reminder", "remove_reminder",
    "remove_reminder_by_match",
    "create_workflow", "add_to_workflow",
    "remove_from_workflow", "edit_workflow",
    "delete_workflow", "run_workflow",
    "stop_workflow", "resume_tasks", "retry_task",
    "create_folder", "create_file", "close_app",
    "open_camera", "take_photo",
    "take_screenshot", "analyze_screen",
    "lock_computer", "sleep", "restart", "shutdown",
    "correct_reasoning",
}

REQUIRED_FIELDS = {
    "google_search": ("query",),
    "youtube_search": ("query",),
    "youtube_play": ("query",),
    "open_file": ("path",),
    "open_folder": ("location",),
    "create_folder": ("name",),
    "create_file": ("name",),
    "add_habit": ("habit",),
    "complete_habit": ("habit",),
    "delete_habit": ("habit",),
    "habit_progress": ("habit",),
    "remember": ("text",),
    "recall": ("text",),
    "add_routine": ("period", "task"),
    "remove_routine": ("period", "task"),
    "show_routine": ("period",),
    "add_reminder": ("text", "time"),
    "add_weekly_reminder": ("text", "time", "weekday"),
    "add_relative_reminder": ("text", "amount", "unit"),
    "remove_reminder": ("id",),
    "remove_reminder_by_match": ("text",),
    "create_workflow": ("workflow", "description"),
    "add_to_workflow": ("workflow", "description"),
    "remove_from_workflow": ("workflow", "target"),
    "edit_workflow": ("workflow", "description"),
    "show_workflow": ("workflow",),
    "delete_workflow": ("workflow",),
    "run_workflow": ("workflow",),
}


def _result(status, reason):
    return {
        "status": status,
        "allowed": status == "ALLOW",
        "requires_confirmation": status == "CONFIRM",
        "reason": reason,
    }


def _valid_required_fields(name, params):
    if name == "open_app":
        value = params.get("app", params.get("name"))
        if value is None or not str(value).strip():
            return False, "Missing required parameter: app"
        return True, "Application parameter valid"

    if name == "open_browser":
        value = params.get("browser", "chrome")
        if not isinstance(value, str) or not value.strip():
            return False, "Invalid browser parameter"
        return True, "Browser parameter valid"

    for field in REQUIRED_FIELDS.get(name, ()):
        value = params.get(field)
        if value is None or not str(value).strip():
            return False, f"Missing required parameter: {field}"

    return True, "Parameters valid"


def authorize_intent(intent, confirmation=None):
    """Apply explicit default-deny authorization to a dispatcher intent."""
    if not isinstance(intent, dict):
        return _result("DENY", "Intent must be a dictionary")

    name = intent.get("intent")
    params = intent.get("parameters", {})

    if not isinstance(name, str) or not name.strip():
        return _result("DENY", "Intent name is missing")

    name = name.strip().lower()

    if not isinstance(params, dict):
        return _result("DENY", "Intent parameters must be a dictionary")

    known = READ_ONLY_INTENTS | LOW_RISK_INTENTS | CONFIRMATION_INTENTS
    if name not in known:
        return _result("DENY", f"Intent is not authorized: {name}")

    valid, reason = _valid_required_fields(name, params)
    if not valid:
        return _result("DENY", reason)

    if name in {"google_search", "youtube_search", "youtube_play"}:
        query = str(params.get("query", "")).strip()
        if len(query) > 2000:
            return _result("DENY", "Search query is too long")

    if name in {"create_file", "create_folder"}:
        value = str(params.get("name", "")).strip()
        if len(value) > 255:
            return _result("DENY", "File or folder name is too long")

    if name == "open_app":
        value = params.get("app", params.get("name"))
        if len(str(value).strip()) > 200:
            return _result("DENY", "Application name is too long")

    if name == "open_browser":
        if len(str(params.get("browser", "chrome")).strip()) > 80:
            return _result("DENY", "Browser name is too long")

        url = params.get("url")
        if url:
            parsed = urlparse(str(url).strip())
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                return _result("DENY", "Browser URL must use HTTP or HTTPS")

    if name in READ_ONLY_INTENTS or name in LOW_RISK_INTENTS:
        return _result("ALLOW", "Known intent and parameters validated")

    if name in CONFIRMATION_INTENTS:
        # Caller-supplied dictionaries are not proof of user approval.
        # Approval must be verified separately at the execution boundary.
        return _result(
            "CONFIRM",
            "This operation requires a trusted, action-bound approval"
        )

    return _result("DENY", "No authorization rule matched")


WORKFLOW_ACTIONS = {
    "open_app", "close_app", "open_url", "wait", "press", "hotkey",
    "type", "click", "double_click", "right_click",
    "scroll_up", "scroll_down",
}


def authorize_workflow_action(action):
    """Validate one stored workflow action immediately before execution."""
    if not isinstance(action, (list, tuple)) or not action:
        return _result("DENY", "Malformed workflow action")

    action_type = action[0]
    if not isinstance(action_type, str):
        return _result("DENY", "Workflow action name must be text")

    action_type = action_type.strip().lower()
    params = list(action[1:])

    if action_type not in WORKFLOW_ACTIONS:
        return _result("DENY", f"Unsupported workflow action: {action_type}")

    if action_type in {
        "click", "double_click", "right_click",
        "scroll_up", "scroll_down",
    }:
        if params:
            return _result("DENY", f"{action_type} does not accept parameters")
        return _result("ALLOW", "Workflow action validated")

    if action_type == "wait":
        if len(params) != 1:
            return _result("DENY", "Wait requires exactly one duration")
        try:
            seconds = float(params[0])
        except (TypeError, ValueError):
            return _result("DENY", "Wait duration must be numeric")
        if not math.isfinite(seconds) or seconds < 0 or seconds > 300:
            return _result("DENY", "Wait duration must be between 0 and 300 seconds")
        return _result("ALLOW", "Workflow wait validated")

    if action_type == "hotkey":
        if not 1 <= len(params) <= 5:
            return _result("DENY", "Hotkey requires between 1 and 5 keys")
        if any(not isinstance(key, str) or not key.strip() for key in params):
            return _result("DENY", "Hotkey keys must be non-empty text")
        return _result("ALLOW", "Workflow hotkey validated")

    if len(params) != 1:
        return _result("DENY", f"{action_type} requires exactly one parameter")

    value = params[0]
    if not isinstance(value, (str, int, float)) or not str(value).strip():
        return _result("DENY", f"{action_type} parameter is invalid")

    if action_type == "open_url":
        parsed = urlparse(str(value).strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return _result("DENY", "Only valid HTTP and HTTPS URLs are allowed")

    if action_type in {"open_app", "close_app"} and len(str(value)) > 200:
        return _result("DENY", "Application name is too long")

    if action_type == "type" and len(str(value)) > 10000:
        return _result("DENY", "Workflow text is too long")

    if action_type == "press" and len(str(value)) > 40:
        return _result("DENY", "Key name is too long")

    return _result("ALLOW", "Workflow action validated")

