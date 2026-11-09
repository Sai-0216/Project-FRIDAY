def build_result(
    device_id,
    command,
    brain,
    *,
    previous_started_at=None,
):
    if not isinstance(device_id, str) or not device_id.strip():
        return None

    if not isinstance(command, str) or not command.strip():
        return None

    state_manager = getattr(brain, "state_manager", None)

    snapshot = {}
    if state_manager is not None:
        snapshot_method = getattr(state_manager, "snapshot", None)
        if callable(snapshot_method):
            candidate = snapshot_method()
            if isinstance(candidate, dict):
                snapshot = candidate

    current_command = snapshot.get("command")
    started_at = snapshot.get("started_at")
    lifecycle = snapshot.get("lifecycle", "")
    outcome = snapshot.get("outcome", "")

    command_matches = (
        isinstance(current_command, str)
        and current_command.strip() == command.strip()
    )

    fresh_execution = (
        isinstance(previous_started_at, str)
        and bool(previous_started_at)
        and isinstance(started_at, str)
        and bool(started_at)
        and started_at != previous_started_at
    )

    success = (
        fresh_execution
        and command_matches
        and lifecycle == "IDLE"
        and outcome == "completed"
    )

    error = snapshot.get("error", "")

    if not success and not error:
        if not fresh_execution:
            error = "No fresh execution lifecycle was recorded."
        elif not command_matches:
            error = "Runtime state does not match the submitted command."
        elif lifecycle != "IDLE":
            error = "Command has not reached a terminal lifecycle state."
        else:
            error = f"Command outcome was not completed: {outcome!r}."

    return {
        "type": "result",
        "device_id": device_id,
        "success": success,
        "command": command,
        "lifecycle": lifecycle,
        "outcome": outcome,
        "execution_results": snapshot.get("execution_results", []),
        "error": error,
    }
