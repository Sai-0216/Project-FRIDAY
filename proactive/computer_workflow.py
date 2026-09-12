"""FRIDAY V3 - Phase 24.7 Multi-Step Computer Workflows."""


class ComputerWorkflow:

    @staticmethod
    def _safe_steps(steps):
        return steps if isinstance(steps, list) else []

    @classmethod
    def create(cls, name, steps):
        steps = cls._safe_steps(steps)
        normalized = []

        for index, step in enumerate(steps, 1):
            if isinstance(step, dict):
                normalized.append({
                    "id": index,
                    "action": step.get("action", "unknown"),
                    "command": step.get("command"),
                    "target": step.get("target", step.get("application", step.get("value", ""))),
                    "completed": bool(step.get("completed", False)),
                })

        return {
            "name": str(name),
            "steps": normalized,
            "step_count": len(normalized),
            "completed_count": sum(1 for step in normalized if step["completed"]),
            "status": "ready" if normalized else "empty",
        }

    @classmethod
    def next_step(cls, workflow):
        if not isinstance(workflow, dict):
            return None

        steps = workflow.get("steps", [])
        if not isinstance(steps, list):
            return None

        for step in steps:
            if isinstance(step, dict) and not step.get("completed", False):
                return step
        return None

    @classmethod
    def complete_step(cls, workflow, step_id):
        if not isinstance(workflow, dict):
            return workflow

        steps = workflow.get("steps", [])
        if not isinstance(steps, list):
            return workflow

        for step in steps:
            if isinstance(step, dict) and step.get("id") == step_id:
                step["completed"] = True

        workflow["completed_count"] = sum(
            1 for step in steps
            if isinstance(step, dict) and step.get("completed", False)
        )
        workflow["status"] = "completed" if workflow["completed_count"] == len(steps) and steps else "ready"
        return workflow

    @classmethod
    def validate(cls, workflow):
        if not isinstance(workflow, dict):
            return False
        if not isinstance(workflow.get("name"), str):
            return False
        if not isinstance(workflow.get("steps"), list):
            return False
        if not isinstance(workflow.get("step_count"), int):
            return False
        if not isinstance(workflow.get("completed_count"), int):
            return False
        if workflow.get("step_count") != len(workflow["steps"]):
            return False
        return True


computer_workflow = ComputerWorkflow()
