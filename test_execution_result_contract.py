import json
from unittest.mock import patch

from modules.execution_result import ExecutionResult
from modules.automation import Automation


def test_execution_result_preserves_string_compatibility():
    result = ExecutionResult("Done.", status="succeeded")
    assert isinstance(result, str)
    assert result == "Done."
    assert json.dumps({"response": result}) == '{"response": "Done."}'
    assert result.status == "succeeded"


def test_click_reports_success():
    with patch("modules.automation.pyautogui.click"):
        result = Automation().click()

    assert result == "Done."
    assert result.status == "succeeded"


def test_click_reports_failure():
    with patch(
        "modules.automation.pyautogui.click",
        side_effect=RuntimeError("desktop unavailable"),
    ):
        result = Automation().click()

    assert result.status == "failed"


def test_empty_press_is_not_success():
    result = Automation().press("")
    assert result.status == "failed"


def test_empty_hotkey_is_not_success():
    result = Automation().hotkey()
    assert result.status == "failed"


def test_empty_text_is_not_success():
    result = Automation().type_text("")
    assert result.status == "failed"
