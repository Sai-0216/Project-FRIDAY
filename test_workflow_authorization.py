import threading
import unittest
from unittest.mock import patch

from modules.workflows import WorkflowManager
from security.approval_manager import ApprovalManager


class _DummyThread:
    def __init__(self, target=None, args=(), daemon=None):
        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True


class TestWorkflowAuthorization(unittest.TestCase):
    def make_manager(self, actions=None):
        manager = WorkflowManager.__new__(WorkflowManager)
        manager.workflows = {
            "demo": actions if actions is not None else [["wait", 1]]
        }
        manager.state_lock = threading.Lock()
        manager.workflow_running = False
        manager.current_workflow = None
        manager.current_task_id = None
        manager.stop_event = threading.Event()
        manager.workflow_thread = None
        manager.last_failure_reason = None
        manager._execution_capability = object()
        return manager

    def test_snapshot_is_detached_and_validated(self):
        manager = self.make_manager([["WAIT", 1]])
        snapshot = manager.get_approved_workflow_snapshot("demo")
        self.assertEqual(snapshot, [["wait", 1]])
        snapshot[0][1] = 9
        self.assertEqual(manager.workflows["demo"], [["WAIT", 1]])

    def test_invalid_action_rejects_entire_snapshot(self):
        manager = self.make_manager([["run_shell", "whoami"]])
        self.assertIsNone(manager.get_approved_workflow_snapshot("demo"))

    def test_run_without_approval_does_not_create_task(self):
        manager = self.make_manager()
        with patch("modules.workflows.task_manager.create_task") as create_task:
            response = manager.run("demo")
        create_task.assert_not_called()
        self.assertIn("requires fresh trusted approval", response)

    def test_changed_workflow_burns_approval_and_does_not_launch(self):
        manager = self.make_manager([["wait", 1]])
        approval_manager = ApprovalManager()
        intent = {"intent": "run_workflow", "parameters": {"workflow": "demo"}}
        approved_snapshot = manager.get_approved_workflow_snapshot("demo")
        token = approval_manager.issue([
            intent,
            {"workflow_actions": approved_snapshot},
        ])
        manager.workflows["demo"][0][1] = 2
        with patch("modules.workflows.task_manager.create_task") as create_task:
            response = manager.run(
                "demo",
                approval_token=token,
                approval_manager=approval_manager,
                approval_intent=intent,
            )
        create_task.assert_not_called()
        self.assertIn("did not match", response)

    def test_exact_approval_launches_only_approved_snapshot(self):
        actions = [["wait", 1]]
        manager = self.make_manager(actions)
        approval_manager = ApprovalManager()
        intent = {"intent": "run_workflow", "parameters": {"workflow": "demo"}}
        token = approval_manager.issue([
            intent,
            {"workflow_actions": [["wait", 1]]},
        ])
        task = {"task_id": "task-1"}
        with patch("modules.workflows.task_manager.create_task", return_value=task) as create_task, \
             patch("modules.workflows.threading.Thread", _DummyThread):
            response = manager.run(
                "demo",
                approval_token=token,
                approval_manager=approval_manager,
                approval_intent=intent,
            )
        create_task.assert_called_once()
        self.assertEqual(create_task.call_args.kwargs["steps"], actions)
        self.assertIn("session started", response)
        self.assertTrue(manager.workflow_thread.started)
        self.assertEqual(manager.workflow_thread.args[2], actions)

    def test_direct_action_execution_is_denied(self):
        manager = self.make_manager()
        with patch("modules.workflows.apps.open_app") as open_app:
            result = manager.execute_actions([["open_app", "notepad"]])
        self.assertFalse(result)
        open_app.assert_not_called()

    def test_action_is_revalidated_at_execution_boundary(self):
        manager = self.make_manager()
        with patch("modules.workflows.webbrowser.open") as open_url:
            result = manager.execute_actions(
                [["open_url", "javascript:alert(1)"]],
                execution_capability=manager._execution_capability,
            )
        self.assertFalse(result)
        open_url.assert_not_called()

    def test_resume_chain_and_retry_paths_fail_closed(self):
        manager = self.make_manager()
        with patch("modules.workflows.task_manager.prepare_retry") as prepare_retry:
            self.assertIn("cannot resume automatically", manager.run_task("task"))
            self.assertIn("Task-chain execution is disabled", manager.run_chain("chain"))
            self.assertIn("Failed-task resume is disabled", manager.resume_task("task"))
            with patch("modules.workflows.task_manager.get_task", return_value={"task_id": "task"}):
                self.assertFalse(manager.auto_retry_task("task"))
        prepare_retry.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
