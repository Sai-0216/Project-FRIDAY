import copy
import threading

import pytest

from modules.task_manager import TaskManager
from security.approval_manager import ApprovalManager


def make_manager(monkeypatch):
    manager = TaskManager.__new__(TaskManager)
    manager.lock = threading.RLock()

    manager.tasks = {
        "dependency-1": {
            "task_id": "dependency-1",
            "status": TaskManager.COMPLETED,
        },
        "task-1": {
            "task_id": "task-1",
            "name": "Study",
            "goal": "Complete study workflow",
            "workflow_name": "study_flow",
            "steps": [
                ["open_app", "vscode"],
                ["wait", 2],
                ["open_url", "https://docs.python.org/3/"],
            ],
            "current_step": 1,
            "status": TaskManager.WAITING,
            "started_at": None,
            "error": "Waiting for dependency",
            "dependencies": ["dependency-1"],
        },
    }

    monkeypatch.setattr(manager, "_save_tasks", lambda: True)
    return manager


def issue_resume_approval(manager):
    approvals = ApprovalManager()
    payload = manager.get_resume_approval_payload(
        "task-1",
        "dependency-1",
    )
    assert payload is not None
    token = approvals.issue(payload)
    return approvals, token, payload


def test_payload_contains_exact_task_and_remaining_actions(monkeypatch):
    manager = make_manager(monkeypatch)
    before = copy.deepcopy(manager.tasks)

    payload = manager.get_resume_approval_payload(
        "task-1",
        "dependency-1",
    )

    assert payload is not None
    assert payload[0]["task_id"] == "task-1"
    assert payload[0]["workflow_name"] == "study_flow"
    assert payload[0]["current_step"] == 1
    assert payload[0]["completed_task_id"] == "dependency-1"
    assert payload[1]["workflow_snapshot"] == manager.tasks["task-1"]["steps"]
    assert payload[2]["remaining_actions"] == [
        ["wait", 2],
        ["open_url", "https://docs.python.org/3/"],
    ]
    assert manager.tasks == before


def test_valid_approval_transitions_waiting_to_running(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, payload = issue_resume_approval(manager)

    result = manager.resume_waiting_task_with_approval(
        "task-1",
        "dependency-1",
        token,
        approvals,
    )

    assert result is not None
    assert result["status"] == TaskManager.RUNNING
    assert result["started_at"]
    assert result["error"] is None
    assert result["current_step"] == 1
    assert approvals.consume(token, payload) is False


def test_replayed_approval_is_rejected(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, _ = issue_resume_approval(manager)

    first = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )
    second = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )

    assert first is not None
    assert second is None
    assert manager.tasks["task-1"]["status"] == TaskManager.RUNNING


def test_changed_snapshot_rejects_and_consumes_token(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, _ = issue_resume_approval(manager)

    manager.tasks["task-1"]["steps"][1][1] = 9

    result = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )

    assert result is None
    assert manager.tasks["task-1"]["status"] == TaskManager.WAITING

    manager.tasks["task-1"]["steps"][1][1] = 2
    retry = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )
    assert retry is None


def test_dependency_change_invalidates_token(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, _ = issue_resume_approval(manager)

    manager.tasks["dependency-1"]["status"] = TaskManager.WAITING

    result = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )
    assert result is None
    assert manager.tasks["task-1"]["status"] == TaskManager.WAITING

    manager.tasks["dependency-1"]["status"] = TaskManager.COMPLETED
    retry = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )
    assert retry is None


def test_wrong_completed_dependency_rejects_approval(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, _ = issue_resume_approval(manager)

    result = manager.resume_waiting_task_with_approval(
        "task-1", "another-task", token, approvals
    )

    assert result is None
    assert manager.tasks["task-1"]["status"] == TaskManager.WAITING


def test_failed_persistence_rolls_back_and_consumes_token(monkeypatch):
    manager = make_manager(monkeypatch)
    approvals, token, _ = issue_resume_approval(manager)
    before = copy.deepcopy(manager.tasks["task-1"])

    monkeypatch.setattr(manager, "_save_tasks", lambda: False)

    result = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )

    assert result is None
    assert manager.tasks["task-1"] == before

    monkeypatch.setattr(manager, "_save_tasks", lambda: True)
    retry = manager.resume_waiting_task_with_approval(
        "task-1", "dependency-1", token, approvals
    )
    assert retry is None
    assert manager.tasks["task-1"] == before


def test_rejects_malformed_step_index(monkeypatch):
    manager = make_manager(monkeypatch)

    manager.tasks["task-1"]["current_step"] = True
    assert manager.get_resume_approval_payload(
        "task-1", "dependency-1"
    ) is None

    manager.tasks["task-1"]["current_step"] = 3
    assert manager.get_resume_approval_payload(
        "task-1", "dependency-1"
    ) is None


def test_rejects_missing_dependency(monkeypatch):
    manager = make_manager(monkeypatch)
    manager.tasks["task-1"]["dependencies"] = ["missing-dependency"]

    assert manager.get_resume_approval_payload(
        "task-1", "missing-dependency"
    ) is None
