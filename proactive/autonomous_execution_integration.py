class AutonomousExecutionIntegration:
    """Integrate the complete autonomous execution pipeline."""

    def integrate(self, plan, graph, readiness, dispatch, tracking, adaptation, verification):
        if not self._valid_inputs(plan, graph, readiness, dispatch, tracking, adaptation, verification):
            return None

        result = {
            "goal": plan["goal"],
            "selected_option_id": plan["selected_option_id"],
            "plan_status": plan["plan_status"],
            "graph_status": graph["graph_status"],
            "readiness_status": readiness["readiness_status"],
            "dispatch_status": dispatch["dispatch_status"],
            "tracking_status": tracking["tracking_status"],
            "adaptation_action": adaptation["action"],
            "adaptation_reason": adaptation["reason"],
            "verification_status": verification["verification_status"],
            "verification_reason": verification["reason"],
            "task_count": plan["task_count"],
            "completed_count": verification["completed_count"],
            "failed_count": verification["failed_count"],
            "remaining_count": verification["remaining_count"],
            "integration_status": "complete",
        }
        return result if self.validate(result) else None

    def _valid_inputs(self, plan, graph, readiness, dispatch, tracking, adaptation, verification):
        if not isinstance(plan, dict) or not isinstance(graph, dict):
            return False
        if not isinstance(readiness, dict) or not isinstance(dispatch, dict):
            return False
        if not isinstance(tracking, dict) or not isinstance(adaptation, dict):
            return False
        if not isinstance(verification, dict):
            return False

        goal = plan.get("goal")
        option_id = plan.get("selected_option_id")
        if not isinstance(goal, str) or not goal.strip():
            return False
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False

        if graph.get("goal") != goal or graph.get("selected_option_id") != option_id:
            return False
        if readiness.get("goal") != goal or readiness.get("selected_option_id") != option_id:
            return False
        if dispatch.get("goal") != goal or dispatch.get("selected_option_id") != option_id:
            return False
        if tracking.get("goal") != goal or tracking.get("selected_option_id") != option_id:
            return False
        if adaptation.get("goal") != goal or adaptation.get("selected_option_id") != option_id:
            return False
        if verification.get("goal") != goal or verification.get("selected_option_id") != option_id:
            return False

        if plan.get("plan_status") != "ready":
            return False
        if graph.get("graph_status") != "ready":
            return False
        if readiness.get("readiness_status") != "ready" or readiness.get("ready") is not True:
            return False
        if dispatch.get("dispatch_status") != "ready":
            return False
        if tracking.get("tracking_status") != "active":
            return False
        if adaptation.get("adaptation_status") != "ready":
            return False
        if verification.get("verification_state") != "ready":
            return False

        task_count = plan.get("task_count")
        if not isinstance(task_count, int) or isinstance(task_count, bool) or task_count <= 0:
            return False

        if graph.get("node_count") != task_count:
            return False
        if dispatch.get("dispatch_count") != task_count:
            return False
        if tracking.get("state_count") != task_count:
            return False

        return True

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False

        option_id = result.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False

        for key in ("plan_status", "graph_status", "readiness_status", "dispatch_status"):
            if result.get(key) != "ready":
                return False

        if result.get("tracking_status") != "active":
            return False
        if result.get("adaptation_action") not in ("continue", "adapt"):
            return False
        if not isinstance(result.get("adaptation_reason"), str) or not result["adaptation_reason"].strip():
            return False
        if result.get("verification_status") not in ("completed", "failed", "in_progress"):
            return False
        if not isinstance(result.get("verification_reason"), str) or not result["verification_reason"].strip():
            return False

        for key in ("task_count", "completed_count", "failed_count", "remaining_count"):
            if not isinstance(result.get(key), int) or isinstance(result.get(key), bool) or result[key] < 0:
                return False
        if result["task_count"] <= 0:
            return False

        if result.get("integration_status") != "complete":
            return False

        return True


autonomous_execution_integration = AutonomousExecutionIntegration()
