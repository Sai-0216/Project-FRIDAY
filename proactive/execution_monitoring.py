class ExecutionMonitoring:
    STATES = ("on_track", "delayed", "blocked", "completed")

    def __init__(self):
        self.name = "execution_monitoring"

    def monitor(self, plan):
        if not isinstance(plan, dict):
            return None
        steps = plan.get("steps", [])
        total = len(steps)
        completed = sum(1 for step in steps if step.get("completed"))
        progress = completed / total if total else 0.0
        if total and completed == total:
            state = "completed"
        elif plan.get("status") == "paused":
            state = "blocked"
        elif total and completed == 0:
            state = "on_track"
        else:
            state = "on_track"
        current = next((step for step in steps if not step.get("completed")), None)
        return {
            "plan_id": plan.get("id"),
            "progress": progress,
            "completed_count": completed,
            "total_count": total,
            "current_step": current,
            "state": state,
        }

    def mark_delayed(self, monitoring):
        if not isinstance(monitoring, dict):
            return False
        if monitoring.get("state") == "completed":
            return False
        monitoring["state"] = "delayed"
        return True

    def validate(self, monitoring):
        if not isinstance(monitoring, dict):
            return False
        required = ("plan_id", "progress", "completed_count", "total_count", "current_step", "state")
        if any(key not in monitoring for key in required):
            return False
        if monitoring["state"] not in self.STATES:
            return False
        if not 0.0 <= float(monitoring["progress"]) <= 1.0:
            return False
        if monitoring["completed_count"] < 0 or monitoring["total_count"] < 0:
            return False
        if monitoring["completed_count"] > monitoring["total_count"]:
            return False
        return True


execution_monitoring = ExecutionMonitoring()
