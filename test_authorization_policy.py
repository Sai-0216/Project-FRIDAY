import unittest

from security.authorization import (
    authorize_intent,
    authorize_workflow_action,
    READ_ONLY_INTENTS,
    LOW_RISK_INTENTS,
    CONFIRMATION_INTENTS,
)


class AuthorizationPolicyTests(unittest.TestCase):

    def test_every_inspected_dispatcher_intent_has_a_policy(self):
        inspected = {
            "run_workflow", "create_workflow", "add_to_workflow",
            "remove_from_workflow", "edit_workflow", "resume_tasks",
            "retry_task", "verify_decision", "correct_reasoning",
            "check_reasoning", "stop_workflow", "workflow_status",
            "list_workflows", "show_workflow", "delete_workflow",
            "volume_up", "volume_down", "mute", "unmute",
            "brightness_up", "brightness_down", "battery", "cpu",
            "ram", "disk", "task_manager", "settings",
            "lock_computer", "sleep", "restart", "shutdown",
            "open_camera", "close_camera", "take_photo",
            "take_screenshot", "analyze_screen", "open_browser",
            "google_search", "youtube_search", "youtube_play",
            "open_app", "close_app", "open_folder", "create_folder",
            "create_file", "open_file", "add_habit", "list_habits",
            "habit_progress", "delete_habit", "complete_habit",
            "remember", "recall", "add_routine", "remove_routine",
            "show_routine", "show_full_routine", "daily_briefing",
            "today_plan", "daily_progress", "add_reminder",
            "add_weekly_reminder", "add_relative_reminder",
            "list_reminders", "remove_reminder",
            "remove_reminder_by_match", "unknown",
        }
        covered = READ_ONLY_INTENTS | LOW_RISK_INTENTS | CONFIRMATION_INTENTS
        self.assertEqual(inspected - {"unknown"}, covered)

    def test_unknown_intent_is_denied(self):
        self.assertEqual(
            authorize_intent({"intent": "run_shell", "parameters": {}})["status"],
            "DENY",
        )

    def test_malformed_intent_is_denied(self):
        self.assertEqual(authorize_intent(None)["status"], "DENY")

    def test_read_only_intent_is_allowed(self):
        self.assertEqual(
            authorize_intent({"intent": "battery", "parameters": {}})["status"],
            "ALLOW",
        )

    def test_open_app_accepts_dispatcher_name_alias(self):
        self.assertEqual(
            authorize_intent({"intent": "open_app", "parameters": {"name": "notepad"}})["status"],
            "ALLOW",
        )

    def test_open_browser_uses_dispatcher_default(self):
        self.assertEqual(
            authorize_intent({"intent": "open_browser", "parameters": {}})["status"],
            "ALLOW",
        )

    def test_missing_required_parameter_is_denied(self):
        self.assertEqual(
            authorize_intent({"intent": "delete_workflow", "parameters": {}})["status"],
            "DENY",
        )

    def test_mutating_intent_requires_confirmation(self):
        self.assertEqual(
            authorize_intent({
                "intent": "delete_workflow",
                "parameters": {"workflow": "demo"},
            })["status"],
            "CONFIRM",
        )

    def test_caller_supplied_confirmation_dict_cannot_authorize(self):
        result = authorize_intent({
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        }, confirmation={
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        })
        self.assertEqual(result["status"], "CONFIRM")
        self.assertFalse(result["allowed"])


    def test_confirmation_for_different_action_is_rejected(self):
        result = authorize_intent({
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        }, confirmation={
            "intent": "restart",
            "parameters": {},
        })
        self.assertEqual(result["status"], "CONFIRM")

    def test_confirmation_for_different_parameters_is_rejected(self):
        result = authorize_intent({
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        }, confirmation={
            "intent": "delete_workflow",
            "parameters": {"workflow": "production"},
        })
        self.assertEqual(result["status"], "CONFIRM")

    def test_boolean_confirmation_is_rejected(self):
        result = authorize_intent({
            "intent": "delete_workflow",
            "parameters": {"workflow": "demo"},
        }, confirmation=True)
        self.assertEqual(result["status"], "CONFIRM")
    def test_invalid_parameters_are_denied(self):
        self.assertEqual(
            authorize_intent({
                "intent": "add_reminder",
                "parameters": {"text": "test", "time": ""},
            })["status"],
            "DENY",
        )

    def test_workflow_valid_action(self):
        self.assertEqual(
            authorize_workflow_action(["open_app", "notepad"])["status"],
            "ALLOW",
        )

    def test_workflow_unknown_action_is_denied(self):
        self.assertEqual(
            authorize_workflow_action(["run_shell", "whoami"])["status"],
            "DENY",
        )

    def test_workflow_invalid_url_is_denied(self):
        self.assertEqual(
            authorize_workflow_action(["open_url", "file:///C:/secret"])["status"],
            "DENY",
        )

    def test_workflow_excessive_wait_is_denied(self):
        self.assertEqual(
            authorize_workflow_action(["wait", 999999])["status"],
            "DENY",
        )

    def test_workflow_malformed_click_is_denied(self):
        self.assertEqual(
            authorize_workflow_action(["click", "unexpected"])["status"],
            "DENY",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

