from types import SimpleNamespace

import pytest

from modules.execution_result import ExecutionResult
from proactive.state_manager import StateManager


def evaluate(*results):
    manager = StateManager.__new__(StateManager)
    manager.state = SimpleNamespace(
        execution_results=list(results),
        evaluation={},
    )
    outcome = manager.evaluate_execution_results()
    return outcome, manager.state.evaluation


@pytest.mark.parametrize(
    "status",
    ["succeeded", "already_satisfied"],
)
def test_explicit_success_statuses(status):
    outcome, details = evaluate(ExecutionResult("Done.", status=status))
    assert outcome == "completed"
    assert details["successes"] == 1
    assert details["failures"] == 0


@pytest.mark.parametrize(
    "status",
    ["failed", "denied", "cancelled", "blocked", "skipped", "unknown"],
)
def test_explicit_failure_statuses(status):
    outcome, details = evaluate(ExecutionResult("Not completed.", status=status))
    assert outcome == "failed"

def test_legacy_error_status_dictionary_fails():
    outcome, details = evaluate({"response": "failed", "status": "error"})
    assert outcome == "failed"
    assert details["failures"] == 1
    assert details["successes"] == 0
    assert details["failures"] == 1


def test_legacy_success_dictionary_remains_supported():
    outcome, details = evaluate({"response": "done", "error": None})
    assert outcome == "completed"
    assert details["successes"] == 1


def test_legacy_failure_dictionary_remains_supported():
    outcome, details = evaluate({"response": "failed", "error": "RuntimeError"})
    assert outcome == "failed"
    assert details["failures"] == 1


def test_unknown_dictionary_fails_closed():
    outcome, details = evaluate({"response": "maybe"})
    assert outcome == "failed"
    assert details["failures"] == 1


def test_unknown_explicit_dictionary_status_fails_closed():
    outcome, details = evaluate({"response": "done", "error": None, "status": "mystery"})
    assert outcome == "failed"


def test_plain_string_fails_closed():
    outcome, details = evaluate("Done.")
    assert outcome == "failed"
    assert details["failures"] == 1


def test_structured_failure_is_not_counted_as_success():
    outcome, details = evaluate(
        ExecutionResult("I couldn't click.", status="failed")
    )
    assert outcome == "failed"


def test_mixed_results_are_partial():
    outcome, details = evaluate(
        ExecutionResult("Done.", status="succeeded"),
        ExecutionResult("Denied.", status="denied"),
    )
    assert outcome == "partial"
    assert details["successes"] == 1
    assert details["failures"] == 1
    assert details["total_results"] == 2
