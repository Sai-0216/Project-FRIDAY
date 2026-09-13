def build_result(device_id, command, brain):
    if not isinstance(device_id,str) or not device_id.strip():
        return None
    if not isinstance(command,str) or not command.strip():
        return None
    state = getattr(brain, "state_manager", None)
    snapshot = state.snapshot() if state is not None and hasattr(state, "snapshot") else {}
    return {
        "type": "result",
        "device_id": device_id,
        "success": True,
        "command": command,
        "lifecycle": snapshot.get("lifecycle", ""),
        "outcome": snapshot.get("outcome", ""),
        "execution_results": snapshot.get("execution_results", []),
        "error": snapshot.get("error", ""),
    }
