import copy
import threading

import pytest

import modules.workflows as workflows_module


PAYLOAD = [
    {
        "intent": "resume_workflow_task",
        "task_id": "task-1",
        "workflow_name": "study_flow",
        "dependencies": ["dependency-1"],
        "completed_task_id": "dependency-1",
        "current_step": 1,
    },
    {
        "workflow_snapshot": [
            ["open_app", "vscode"],
            ["wait", 2],
            ["open_url", "https://docs.python.org/3/"],
        ]
    },
    {
        "remaining_actions": [
            ["wait", 2],
            ["open_url", "https://docs.python.org/3/"],
        ]
    },
]


class FakeTaskManager:
    RUNNING = "RUNNING"

    def __init__(self):
        self.payload = copy.deepcopy(PAYLOAD)
        self.resume_calls = []
        self.fail_calls = []
        self.task = {
            "task_id": "task-1",
            "status": "RUNNING",
            "workflow_name": "study_flow",
            "current_step": 1,
            "steps": copy.deepcopy(PAYLOAD[1]["workflow_snapshot"]),
        }

    def get_resume_approval_payload(self, task_id, completed_task_id):
        if task_id != "task-1" or completed_task_id != "dependency-1":
            return None
        return copy.deepcopy(self.payload)

    def resume_waiting_task_with_approval(
        self, task_id, completed_task_id, token, approval_manager
    ):
        self.resume_calls.append(
            (task_id, completed_task_id, token, approval_manager)
        )
        return copy.deepcopy(self.task)

    def fail_task(self, task_id, error, failure_type=None):
        self.fail_calls.append((task_id, error, failure_type))
        return True


class FakeThread:
    instances = []
    fail_start = False

    def __init__(self, target, args, daemon):
        self.target = target
        self.args = args
        self.daemon = daemon
        self.started = False
        self.__class__.instances.append(self)

    def start(self):
        if self.__class__.fail_start:
            raise RuntimeError("simulated thread-start failure")
        self.started = True


def make_manager():
    manager = workflows_module.WorkflowManager.__new__(
        workflows_module.WorkflowManager
    )
    manager.state_lock = threading.Lock()
    manager.workflow_running = False
    manager.current_workflow = None
    manager.current_task_id = None
    manager.workflow_thread = None
    manager.stop_event = threading.Event()
    manager._execution_capability = object()
    return manager


@pytest.fixture(autouse=True)
def reset_thread():
    FakeThread.instances = []
    FakeThread.fail_start = False


def install(monkeypatch, fake_task_manager=None, authorization=None):
    fake = fake_task_manager or FakeTaskManager()
    monkeypatch.setattr(workflows_module, "task_manager", fake)
    monkeypatch.setattr(workflows_module.threading, "Thread", FakeThread)
    monkeypatch.setattr(
        workflows_module,
        "authorize_workflow_action",
        authorization or (lambda action: {"status": "ALLOW"}),
    )
    return fake


def test_resume_payload_requires_all_remaining_actions_authorized(monkeypatch):
    fake = install(monkeypatch)
    manager = make_manager()

    payload = manager.get_resume_approval_payload(
        "task-1", "dependency-1"
    )

    assert payload == fake.payload


def test_resume_payload_rejects_denied_remaining_action(monkeypatch):
    fake = install(
        monkeypatch,
        authorization=lambda action: {
            "status": "DENY",
            "reason": "blocked",
        },
    )
    manager = make_manager()

    payload = manager.get_resume_approval_payload(
        "task-1", "dependency-1"
    )

    assert payload is None
    assert fake.resume_calls == []


def test_resume_launches_worker_in_existing_running_mode(monkeypatch):
    fake = install(monkeypatch)
    manager = make_manager()
    approval_manager = object()

    result = manager.resume_waiting_task(
        "task-1",
        "dependency-1",
        "fresh-token",
        approval_manager,
    )

    assert "recovery started" in result.lower()
    assert len(fake.resume_calls) == 1
    assert FakeThread.instances[0].started is True
    assert FakeThread.instances[0].args[5] is True
    assert manager.workflow_running is True
    assert manager.current_task_id == "task-1"
    assert manager.current_workflow == "study_flow"


def test_busy_workflow_does_not_consume_approval(monkeypatch):
    fake = install(monkeypatch)
    manager = make_manager()
    manager.workflow_running = True
    manager.current_workflow = "coding"

    result = manager.resume_waiting_task(
        "task-1", "dependency-1", "fresh-token", object()
    )

    assert "already running" in result.lower()
    assert fake.resume_calls == []
    assert FakeThread.instances == []


def test_invalid_payload_does_not_consume_approval(monkeypatch):
    fake = FakeTaskManager()
    fake.payload[2]["remaining_actions"] = []
    install(monkeypatch, fake)
    manager = make_manager()

    result = manager.resume_waiting_task(
        "task-1", "dependency-1", "fresh-token", object()
    )

    assert "no longer eligible" in result.lower()
    assert fake.resume_calls == []
    assert FakeThread.instances == []


def test_worker_start_failure_marks_task_failed_and_cleans_state(monkeypatch):
    fake = install(monkeypatch)
    manager = make_manager()
    FakeThread.fail_start = True

    result = manager.resume_waiting_task(
        "task-1", "dependency-1", "fresh-token", object()
    )

    assert "could not start" in result.lower()
    assert len(fake.fail_calls) == 1
    assert manager.workflow_running is False
    assert manager.current_task_id is None
    assert manager.current_workflow is None
    assert manager.workflow_thread is None
