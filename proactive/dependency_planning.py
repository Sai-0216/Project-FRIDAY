class DependencyPlanning:
    def __init__(self):
        self.name = "dependency_planning"

    def create(self, tasks):
        if not isinstance(tasks, list):
            return None
        dependencies = []
        for index, task in enumerate(tasks, 1):
            if isinstance(task, str) and task.strip():
                dependencies.append({"id": index, "task": task.strip(), "depends_on": [], "ready": True, "completed": False})
        return {"tasks": dependencies, "count": len(dependencies), "status": "ready"}

    def add_dependency(self, plan, task_id, dependency_id):
        if not isinstance(plan, dict):
            return False
        tasks = plan.get("tasks", [])
        ids = {task.get("id") for task in tasks}
        if task_id not in ids or dependency_id not in ids or task_id == dependency_id:
            return False
        for task in tasks:
            if task.get("id") == task_id:
                if dependency_id not in task["depends_on"]:
                    task["depends_on"].append(dependency_id)
                task["ready"] = False
                return True
        return False

    def update_readiness(self, plan):
        if not isinstance(plan, dict):
            return None
        completed = {task.get("id") for task in plan.get("tasks", []) if task.get("completed")}
        for task in plan.get("tasks", []):
            task["ready"] = all(dep in completed for dep in task.get("depends_on", [])) and not task.get("completed", False)
        return plan

    def complete(self, plan, task_id):
        if not isinstance(plan, dict):
            return False
        self.update_readiness(plan)
        for task in plan.get("tasks", []):
            if task.get("id") == task_id and task.get("ready"):
                task["completed"] = True
                self.update_readiness(plan)
                plan["status"] = "completed" if plan.get("tasks") and all(x.get("completed") for x in plan["tasks"]) else "active"
                return True
        return False

    def ready_tasks(self, plan):
        if not isinstance(plan, dict):
            return []
        self.update_readiness(plan)
        return [task for task in plan.get("tasks", []) if task.get("ready")]

    def validate(self, plan):
        if not isinstance(plan, dict):
            return False
        tasks = plan.get("tasks")
        if not isinstance(tasks, list) or plan.get("count") != len(tasks):
            return False
        ids = {task.get("id") for task in tasks}
        for task in tasks:
            if not isinstance(task.get("task"), str) or not task["task"]:
                return False
            if not isinstance(task.get("depends_on"), list):
                return False
            if any(dep not in ids for dep in task["depends_on"]):
                return False
        return plan.get("status") in ("ready", "active", "completed")


dependency_planning = DependencyPlanning()
