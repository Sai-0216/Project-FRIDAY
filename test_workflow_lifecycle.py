import threading
import unittest
from unittest.mock import patch

from modules.workflows import WorkflowManager
from modules.workflows import task_manager
from security.approval_manager import ApprovalManager


class _FailingThread:
    def __init__(self, target=None, args=(), daemon=None):
        self.target = target
        self.args = args
        self.daemon = daemon

    def start(self):
        raise RuntimeError("simulated thread launch failure")


class TestWorkflowLifecycle(unittest.TestCase):

    def make_manager(self):
        manager = WorkflowManager.__new__(WorkflowManager)
        manager.workflows = {"demo": [["wait", 1]]}
        manager.state_lock = threading.Lock()
        manager.workflow_running = False
        manager.current_workflow = None
        manager.current_task_id = None
        manager.stop_event = threading.Event()
        manager.workflow_thread = None
        manager.last_failure_reason = None
        manager._execution_capability = object()
        return manager

    def assert_engine_clean(self, manager):
        self.assertFalse(manager.workflow_running)
        self.assertIsNone(manager.current_workflow)
        self.assertIsNone(manager.current_task_id)
        self.assertIsNone(manager.workflow_thread)

    def run_worker(self, manager, capability=None):
        with patch(
            "modules.workflows.task_manager.fail_task"
        ) as fail_task, patch.object(
            manager, "classify_failure", return_value="OTHER"
        ):
            manager._run_workflow(
                "demo",
                "task-1",
                [["wait", 1]],
                capability if capability is not None else manager._execution_capability,
            )
        return fail_task

    def test_unknown_dependency_status_fails_closed(self):
        manager = self.make_manager()
        manager.workflow_running = True
        manager.current_workflow = "demo"
        manager.current_task_id = "task-1"

        with patch(
            "modules.workflows.task_manager.dependency_status",
            return_value=None,
        ), patch.object(
            manager, "classify_failure", return_value="OTHER"
        ), patch(
            "modules.workflows.task_manager.fail_task"
        ) as fail_task:
            manager._run_workflow(
                "demo", "task-1", [["wait", 1]],
                manager._execution_capability,
            )

        fail_task.assert_called_once()
        self.assertIn("Dependency status", fail_task.call_args.args[1])
        self.assert_engine_clean(manager)

    def test_failed_dependency_fails_workflow(self):
        manager = self.make_manager()
        manager.workflow_running = True
        manager.current_workflow = "demo"
        manager.current_task_id = "task-1"

        dependency_result = {
            "failed": ["dependency-1"],
            "blocking": ["dependency-1"],
            "satisfied": False,
        }

        with patch(
            "modules.workflows.task_manager.dependency_status",
            return_value=dependency_result,
        ), patch.object(
            manager, "classify_failure", return_value="DEPENDENCY"
        ), patch(
            "modules.workflows.task_manager.fail_task"
        ) as fail_task:
            manager._run_workflow(
                "demo", "task-1", [["wait", 1]],
                manager._execution_capability,
            )

        fail_task.assert_called_once()
        self.assertIn("dependency-1", fail_task.call_args.args[1])
        self.assert_engine_clean(manager)

    def test_pending_dependency_moves_task_to_waiting(self):
        manager = self.make_manager()
        manager.workflow_running = True
        manager.current_workflow = "demo"
        manager.current_task_id = "task-1"

        dependency_result = {
            "failed": [],
            "blocking": ["dependency-1"],
            "satisfied": False,
        }

        with patch(
            "modules.workflows.task_manager.dependency_status",
            return_value=dependency_result,
        ), patch(
            "modules.workflows.task_manager.wait_for_dependencies",
            return_value={"status": "WAITING"},
        ) as wait_task, patch(
            "modules.workflows.task_manager.fail_task"
        ) as fail_task:
            manager._run_workflow(
                "demo", "task-1", [["wait", 1]],
                manager._execution_capability,
            )

        wait_task.assert_called_once_with("task-1")
        fail_task.assert_not_called()
        self.assert_engine_clean(manager)

    def test_invalid_worker_capability_fails_and_cleans_engine(self):
        manager = self.make_manager()
        manager.workflow_running = True
        manager.current_workflow = "demo"
        manager.current_task_id = "task-1"

        fail_task = self.run_worker(manager, capability=object())

        fail_task.assert_called_once()
        self.assertIn("missing execution capability", fail_task.call_args.args[1])
        self.assert_engine_clean(manager)

    def test_thread_start_failure_marks_task_failed_and_cleans_engine(self):
        manager = self.make_manager()
        approval_manager = ApprovalManager()
        intent = {
            "intent": "run_workflow",
            "parameters": {"workflow": "demo"},
        }
        actions = manager.get_approved_workflow_snapshot("demo")
        token = approval_manager.issue([
            intent,
            {"workflow_actions": actions},
        ])

        with patch(
            "modules.workflows.task_manager.create_task",
            return_value={"task_id": "task-1"},
        ), patch(
            "modules.workflows.task_manager.fail_task"
        ) as fail_task, patch(
            "modules.workflows.threading.Thread",
            _FailingThread,
        ):
            response = manager.run(
                "demo",
                approval_token=token,
                approval_manager=approval_manager,
                approval_intent=intent,
            )

        fail_task.assert_called_once()
        self.assertIn("could not start", response.lower())
        self.assert_engine_clean(manager)

    def test_missing_dependency_is_not_reported_as_satisfied(self):
        manager = object.__new__(type(task_manager))
        manager.lock = threading.RLock()
        manager.tasks = {
            "task-1": {
                "task_id": "task-1",
                "dependencies": ["missing-task"],
                "status": "PENDING",
            }
        }

        self.assertIsNone(manager.dependency_status("task-1"))
        self.assertEqual(
            manager.get_blocking_dependencies("task-1"),
            ["missing-task"],
        )

    def test_pending_dependency_is_blocking_not_failed(self):
        manager = object.__new__(type(task_manager))
        manager.lock = threading.RLock()
        manager.tasks = {
            "task-1": {
                "task_id": "task-1",
                "dependencies": ["dependency-1"],
                "status": "PENDING",
            },
            "dependency-1": {
                "task_id": "dependency-1",
                "dependencies": [],
                "status": "PENDING",
            },
        }

        result = manager.dependency_status("task-1")

        self.assertIsNotNone(result)
        self.assertFalse(result["satisfied"])
        self.assertEqual(result["blocking"], ["dependency-1"])
        self.assertEqual(result["failed"], [])

    def test_failed_dependency_is_reported_explicitly(self):
        manager = object.__new__(type(task_manager))
        manager.lock = threading.RLock()
        manager.tasks = {
            "task-1": {
                "task_id": "task-1",
                "dependencies": ["dependency-1"],
                "status": "PENDING",
            },
            "dependency-1": {
                "task_id": "dependency-1",
                "dependencies": [],
                "status": "FAILED",
            },
        }

        result = manager.dependency_status("task-1")

        self.assertIsNotNone(result)
        self.assertFalse(result["satisfied"])
        self.assertEqual(result["blocking"], ["dependency-1"])
        self.assertEqual(result["failed"], ["dependency-1"])


    def test_prestart_cancellation_cancels_before_dependency_check(self):
        manager = self.make_manager()
        manager.workflow_running = True
        manager.current_workflow = "demo"
        manager.current_task_id = "task-1"
        manager.stop_event.set()

        with patch(
            "modules.workflows.task_manager.cancel_task"
        ) as cancel_task, patch(
            "modules.workflows.task_manager.dependency_status"
        ) as dependency_status:
            manager._run_workflow(
                "demo",
                "task-1",
                [["wait", 1]],
                manager._execution_capability,
                manager.stop_event,
            )

        cancel_task.assert_called_once_with("task-1")
        dependency_status.assert_not_called()
        self.assert_engine_clean(manager)

    def test_old_worker_cannot_clear_new_worker_state(self):
        manager = self.make_manager()

        newer_event = threading.Event()
        older_event = threading.Event()
        older_event.set()
        newer_thread = object()

        manager.workflow_running = True
        manager.current_workflow = "newer"
        manager.current_task_id = "task-2"
        manager.stop_event = newer_event
        manager.workflow_thread = newer_thread

        with patch(
            "modules.workflows.task_manager.cancel_task"
        ) as cancel_task:
            manager._run_workflow(
                "demo",
                "task-1",
                [["wait", 1]],
                manager._execution_capability,
                older_event,
            )

        cancel_task.assert_called_once_with("task-1")
        self.assertTrue(manager.workflow_running)
        self.assertEqual(manager.current_workflow, "newer")
        self.assertEqual(manager.current_task_id, "task-2")
        self.assertIs(manager.stop_event, newer_event)
        self.assertIs(manager.workflow_thread, newer_thread)


if __name__ == "__main__":
    unittest.main(verbosity=2)
