import unittest
from unittest.mock import patch

from planner import Planner


class TestPlannerValidationPaths(unittest.TestCase):
    def run_route(self, route, command, plan):
        planner = Planner()

        with (
            patch.object(
                planner, "_multi_task_plan",
                return_value=plan if route == "multi" else None,
            ),
            patch.object(
                planner, "_local_plan",
                return_value=plan if route == "local" else None,
            ),
            patch.object(
                planner, "_browser_search_plan",
                return_value=plan if route == "browser" else None,
            ),
        ):
            return planner.plan(command)

    def test_multi_task_path_rejects_unrequested_app(self):
        plan = {"tasks": [
            {"intent": "open_app", "parameters": {"app": "spotify"}}
        ]}
        result = self.run_route("multi", "open calculator", plan)
        self.assertEqual(result["tasks"], [])

    def test_local_path_rejects_unrequested_app(self):
        plan = {"tasks": [
            {"intent": "open_app", "parameters": {"app": "spotify"}}
        ]}
        result = self.run_route("local", "open calculator", plan)
        self.assertEqual(result["tasks"], [])

    def test_browser_path_rejects_unrequested_search(self):
        plan = {"tasks": [
            {"intent": "google_search", "parameters": {"query": "unrequested topic"}}
        ]}
        result = self.run_route("browser", "open calculator", plan)
        self.assertEqual(result["tasks"], [])

    def test_valid_local_plan_is_preserved(self):
        plan = {"tasks": [
            {"intent": "open_app", "parameters": {"app": "calculator"}}
        ]}
        result = self.run_route("local", "open calculator", plan)
        self.assertEqual(result, plan)


if __name__ == "__main__":
    unittest.main()
