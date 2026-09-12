"""FRIDAY V3 - Phase 23.4 Task Decomposition."""


class TaskDecomposition:

    @staticmethod
    def _safe_text(task):
        return str(task).strip() if task is not None else ""

    @classmethod
    def decompose(cls, task):
        text = cls._safe_text(task)
        if not text:
            return []

        normalized = text.replace(" and then ", " then ")
        normalized = normalized.replace(", then ", " then ")
        normalized = normalized.replace(";", " then ")
        normalized = normalized.replace(" and ", " then ")

        parts = normalized.split(" then ")
        subtasks = []

        for index, part in enumerate(parts, start=1):
            cleaned = part.strip(" .,")
            if cleaned:
                subtasks.append({
                    "id": index,
                    "task": cleaned,
                    "completed": False,
                })

        return subtasks

    @classmethod
    def validate(cls, subtasks):
        if not isinstance(subtasks, list) or not subtasks:
            return False

        expected = 1
        for subtask in subtasks:
            if not isinstance(subtask, dict):
                return False
            if subtask.get("id") != expected:
                return False
            if not isinstance(subtask.get("task"), str) or not subtask["task"].strip():
                return False
            if subtask.get("completed") is not False:
                return False
            expected += 1

        return True

    @classmethod
    def summary(cls, task):
        subtasks = cls.decompose(task)
        return {
            "original": cls._safe_text(task),
            "count": len(subtasks),
            "subtasks": subtasks,
            "valid": cls.validate(subtasks),
        }


task_decomposition = TaskDecomposition()
