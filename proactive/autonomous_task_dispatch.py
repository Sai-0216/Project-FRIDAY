class AutonomousTaskDispatch:
    """Dispatch a ready action graph in dependency-respecting order."""

    def dispatch(self, action_graph, readiness_result):
        if not self._valid_input(action_graph, readiness_result):
            return None

        nodes = {node["task_id"]: node for node in action_graph["nodes"]}
        dispatched_tasks = []

        for position, task_id in enumerate(action_graph["execution_order"], start=1):
            node = nodes[task_id]
            dispatched_tasks.append({
                "dispatch_id": position,
                "task_id": task_id,
                "description": node["description"],
                "dispatch_status": "dispatched",
            })

        result = {
            "goal": action_graph["goal"],
            "selected_option_id": action_graph["selected_option_id"],
            "dispatched_tasks": dispatched_tasks,
            "dispatch_count": len(dispatched_tasks),
            "dispatch_status": "ready",
        }
        return result if self.validate(result) else None

    def _valid_input(self, graph, readiness):
        if not isinstance(graph, dict) or not isinstance(readiness, dict):
            return False
        if not isinstance(graph.get("goal"), str) or not graph["goal"].strip():
            return False
        option_id = graph.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if graph.get("graph_status") != "ready":
            return False
        if readiness.get("goal") != graph["goal"]:
            return False
        if readiness.get("selected_option_id") != option_id:
            return False
        if readiness.get("ready") is not True:
            return False
        if readiness.get("readiness_status") != "ready":
            return False
        nodes = graph.get("nodes")
        order = graph.get("execution_order")
        if not isinstance(nodes, list) or not nodes:
            return False
        if not isinstance(order, list) or not order:
            return False
        node_ids = [node.get("task_id") for node in nodes if isinstance(node, dict)]
        if len(node_ids) != len(nodes) or len(set(node_ids)) != len(node_ids):
            return False
        if order != node_ids:
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
        tasks = result.get("dispatched_tasks")
        if not isinstance(tasks, list) or not tasks:
            return False
        for position, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                return False
            if task.get("dispatch_id") != position:
                return False
            task_id = task.get("task_id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            if task.get("dispatch_status") != "dispatched":
                return False
        if not isinstance(result.get("dispatch_count"), int) or isinstance(result.get("dispatch_count"), bool):
            return False
        if result["dispatch_count"] != len(tasks):
            return False
        if result.get("dispatch_status") != "ready":
            return False
        return True


autonomous_task_dispatch = AutonomousTaskDispatch()
