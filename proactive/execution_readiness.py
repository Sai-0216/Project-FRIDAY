class ExecutionReadiness:
    """Determine whether an action graph is ready for autonomous execution."""

    def assess(self, action_graph):
        if not self._valid_input(action_graph):
            return None

        nodes = action_graph["nodes"]
        edges = action_graph["edges"]
        order = action_graph["execution_order"]

        readiness_checks = {
            "graph_valid": True,
            "nodes_available": bool(nodes),
            "dependencies_valid": self._dependencies_valid(nodes, edges),
            "execution_order_valid": self._order_valid(nodes, order),
            "graph_ready": action_graph["graph_status"] == "ready",
        }

        ready = all(readiness_checks.values())

        result = {
            "goal": action_graph["goal"],
            "selected_option_id": action_graph["selected_option_id"],
            "readiness_checks": readiness_checks,
            "ready": ready,
            "readiness_status": "ready" if ready else "blocked",
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
        if value.get("graph_status") != "ready":
            return False
        nodes = value.get("nodes")
        edges = value.get("edges")
        order = value.get("execution_order")
        if not isinstance(nodes, list) or not nodes:
            return False
        if not isinstance(edges, list):
            return False
        if not isinstance(order, list) or not order:
            return False
        return True

    def _dependencies_valid(self, nodes, edges):
        node_ids = {node.get("task_id") for node in nodes}
        for edge in edges:
            if edge.get("from") not in node_ids or edge.get("to") not in node_ids:
                return False
            if edge.get("from") == edge.get("to"):
                return False
        return True

    def _order_valid(self, nodes, order):
        node_ids = [node.get("task_id") for node in nodes]
        return order == node_ids and len(order) == len(set(order))

    def validate(self, result):
        if not isinstance(result, dict):
            return False
        if not isinstance(result.get("goal"), str) or not result["goal"].strip():
            return False
        option_id = result.get("selected_option_id")
        if not isinstance(option_id, int) or isinstance(option_id, bool) or option_id <= 0:
            return False
        checks = result.get("readiness_checks")
        if not isinstance(checks, dict):
            return False
        required = {
            "graph_valid",
            "nodes_available",
            "dependencies_valid",
            "execution_order_valid",
            "graph_ready",
        }
        if set(checks) != required:
            return False
        if any(not isinstance(value, bool) for value in checks.values()):
            return False
        if not isinstance(result.get("ready"), bool):
            return False
        expected_ready = all(checks.values())
        if result["ready"] != expected_ready:
            return False
        expected_status = "ready" if expected_ready else "blocked"
        if result.get("readiness_status") != expected_status:
            return False
        return True


execution_readiness = ExecutionReadiness()
