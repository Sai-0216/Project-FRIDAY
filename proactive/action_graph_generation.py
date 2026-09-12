class ActionGraphGeneration:
    """Convert an execution plan into a validated action dependency graph."""

    def generate(self, execution_plan):
        if not self._valid_input(execution_plan):
            return None

        tasks = execution_plan["tasks"]
        nodes = []
        edges = []

        for task in tasks:
            nodes.append({
                "task_id": task["task_id"],
                "description": task["description"],
            })
            for dependency in task["depends_on"]:
                edges.append({
                    "from": dependency,
                    "to": task["task_id"],
                })

        execution_order = [task["task_id"] for task in tasks]

        result = {
            "goal": execution_plan["goal"],
            "selected_option_id": execution_plan["selected_option_id"],
            "nodes": nodes,
            "edges": edges,
            "execution_order": execution_order,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "graph_status": "ready",
        }
        return result if self.validate(result) else None

    def _valid_input(self, value):
        if not isinstance(value, dict):
            return False
        if not isinstance(value.get("goal"), str) or not value["goal"].strip():
            return False
        option_id = value.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        if value.get("plan_status") != "ready":
            return False
        tasks = value.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            return False
        for task in tasks:
            if not isinstance(task, dict):
                return False
            task_id = task.get("task_id")
            if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id <= 0:
                return False
            if not isinstance(task.get("description"), str) or not task["description"].strip():
                return False
            dependencies = task.get("depends_on")
            if not isinstance(dependencies, list):
                return False
            for dependency in dependencies:
                if not isinstance(dependency, int) or isinstance(dependency, bool) or dependency <= 0:
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

        nodes = result.get("nodes")
        edges = result.get("edges")
        order = result.get("execution_order")

        if not isinstance(nodes, list) or not nodes:
            return False
        if not isinstance(edges, list):
            return False
        if not isinstance(order, list) or not order:
            return False

        node_ids = []
        for node in nodes:
            if not isinstance(node, dict):
                return False
            node_id = node.get("task_id")
            if not isinstance(node_id, int) or isinstance(node_id, bool) or node_id <= 0:
                return False
            if not isinstance(node.get("description"), str) or not node["description"].strip():
                return False
            node_ids.append(node_id)

        if len(set(node_ids)) != len(node_ids):
            return False

        if order != node_ids:
            return False

        for edge in edges:
            if not isinstance(edge, dict):
                return False
            source = edge.get("from")
            target = edge.get("to")
            if not isinstance(source, int) or isinstance(source, bool) or source <= 0:
                return False
            if not isinstance(target, int) or isinstance(target, bool) or target <= 0:
                return False
            if source not in node_ids or target not in node_ids:
                return False
            if source == target:
                return False

        if not isinstance(result.get("node_count"), int) or isinstance(result.get("node_count"), bool):
            return False
        if result["node_count"] != len(nodes):
            return False
        if not isinstance(result.get("edge_count"), int) or isinstance(result.get("edge_count"), bool):
            return False
        if result["edge_count"] != len(edges):
            return False
        if result.get("graph_status") != "ready":
            return False
        return True


action_graph_generation = ActionGraphGeneration()
