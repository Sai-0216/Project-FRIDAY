import copy

import pytest

import modules.workflows as workflows_module


_DEFAULT_DEPENDENCY_RESULT = object()


class FakeTaskManager:
    WAITING = "WAITING"
    PENDING = "PENDING"

    def __init__(self, task, candidates=None, dependency_result=_DEFAULT_DEPENDENCY_RESULT):
        self.task = task
        self.candidates = candidates if candidates is not None else [
            {"task_id": "task-2", "status": self.WAITING}
        ]
        self.dependency_result = (
            {
                "blocking": [],
                "failed": [],
                "satisfied": True,
            }
            if dependency_result is _DEFAULT_DEPENDENCY_RESULT
            else dependency_result
        )

    def get_ready_dependents(self, completed_task_id):
        return self.candidates

    def get_task(self, task_id):
        if task_id != "task-2":
            return None
        return dict(self.task)

    def dependency_status(self, task_id):
        return self.dependency_result


def make_task(**overrides):
    task = {
        "task_id": "task-2",
        "status": "WAITING",
        "workflow_name": "Study Flow",
        "dependencies": ["task-1"],
        "steps": [
            ["open_app", "vscode"],
            ["wait", 2],
        ],
        "current_step": 0,
    }
    task.update(overrides)
    return task


def install_fakes(monkeypatch, task=None, candidates=None,
                  dependency_result=_DEFAULT_DEPENDENCY_RESULT, authorization=None):
    fake = FakeTaskManager(
        task or make_task(),
        candidates=candidates,
        dependency_result=dependency_result,
    )
    monkeypatch.setattr(workflows_module, "task_manager", fake)
    monkeypatch.setattr(
        workflows_module,
        "authorize_workflow_action",
        authorization or (lambda action: {"status": "ALLOW"}),
    )
    return fake


def make_manager():
    return workflows_module.WorkflowManager.__new__(
        workflows_module.WorkflowManager
    )


def test_returns_valid_read_only_recovery_proposal(monkeypatch):
    task = make_task()
    original = copy.deepcopy(task)
    install_fakes(monkeypatch, task=task)

    manager = make_manager()
    proposals = manager.get_dependency_recovery_proposals("task-1")

    assert len(proposals) == 1
    proposal = proposals[0]
    assert proposal["task_id"] == "task-2"
    assert proposal["workflow_name"] == "study_flow"
    assert proposal["current_step"] == 0
    assert proposal["total_steps"] == 2
    assert proposal["dependencies"] == ["task-1"]
    assert proposal["completed_task_id"] == "task-1"
    assert proposal["remaining_actions"] == original["steps"]
    assert task == original


def test_rejects_empty_completed_task_id(monkeypatch):
    fake = install_fakes(monkeypatch)
    proposals = make_manager().get_dependency_recovery_proposals("   ")
    assert proposals == []
    assert fake.task == make_task()


def test_rejects_non_waiting_candidate(monkeypatch):
    install_fakes(
        monkeypatch,
        candidates=[{"task_id": "task-2", "status": "PENDING"}],
    )
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


def test_rejects_task_that_is_no_longer_waiting(monkeypatch):
    install_fakes(monkeypatch, task=make_task(status="RUNNING"))
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


@pytest.mark.parametrize(
    "dependency_result",
    [
        {"blocking": ["task-3"], "failed": [], "satisfied": False},
        {"blocking": [], "failed": ["task-3"], "satisfied": False},
        {"blocking": [], "failed": [], "satisfied": False},
        None,
    ],
)
def test_rejects_unsatisfied_or_untrusted_dependencies(
    monkeypatch, dependency_result
):
    install_fakes(monkeypatch, dependency_result=dependency_result)
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


@pytest.mark.parametrize(
    "dependencies",
    [
        None,
        [],
        ["task-3"],
        ["task-1", ""],
        ["task-1", 123],
    ],
)
def test_rejects_malformed_or_unrelated_dependencies(
    monkeypatch, dependencies
):
    install_fakes(monkeypatch, task=make_task(dependencies=dependencies))
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


@pytest.mark.parametrize(
    "steps,current_step",
    [
        (None, 0),
        ([], 0),
        ([["open_app", "vscode"]], -1),
        ([["open_app", "vscode"]], 1),
        ([["open_app", "vscode"]], True),
        ([["open_app", "vscode"]], "0"),
        ([["open_app", "vscode"]], 0),
    ],
)
def test_rejects_invalid_step_snapshots(monkeypatch, steps, current_step):
    if steps == [["open_app", "vscode"]] and current_step == 0:
        steps = [["not_a_valid_action"]]

    install_fakes(
        monkeypatch,
        task=make_task(steps=steps, current_step=current_step),
    )

    if steps == [["not_a_valid_action"]]:
        monkeypatch.setattr(
            workflows_module,
            "authorize_workflow_action",
            lambda action: {"status": "DENY"},
        )

    assert make_manager().get_dependency_recovery_proposals("task-1") == []


def test_rejects_unauthorized_remaining_action(monkeypatch):
    install_fakes(
        monkeypatch,
        authorization=lambda action: {"status": "DENY"},
    )
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


def test_rejects_malformed_action(monkeypatch):
    install_fakes(
        monkeypatch,
        task=make_task(steps=[["open_app", "vscode"], ["", "bad"]]),
    )
    assert make_manager().get_dependency_recovery_proposals("task-1") == []


def test_returns_only_remaining_actions(monkeypatch):
    install_fakes(
        monkeypatch,
        task=make_task(
            steps=[
                ["open_app", "vscode"],
                ["wait", 2],
                ["open_url", "https://docs.python.org/3/"],
            ],
            current_step=1,
        ),
    )

    proposals = make_manager().get_dependency_recovery_proposals("task-1")

    assert len(proposals) == 1
    assert proposals[0]["remaining_actions"] == [
        ["wait", 2],
        ["open_url", "https://docs.python.org/3/"],
    ]


def test_rejects_non_list_candidate_result(monkeypatch):
    install_fakes(monkeypatch, candidates=None)
    monkeypatch.setattr(
        workflows_module.task_manager,
        "get_ready_dependents",
        lambda completed_task_id: None,
    )
    assert make_manager().get_dependency_recovery_proposals("task-1") == []
