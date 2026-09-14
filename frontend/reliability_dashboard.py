"""
Project FRIDAY
Frontend Reliability Dashboard
"""

VALID_STATES = {
    "completed",
    "retry",
    "replan",
    "blocked",
    "escalate",
}


def validate_reliability_state(state):
    if not isinstance(state, dict):
        return {
            "valid": False,
            "state": "invalid",
            "recoverable": False,
            "status": "UNAVAILABLE",
        }

    recovery_state = state.get("state")

    if recovery_state not in VALID_STATES:
        return {
            "valid": False,
            "state": "invalid",
            "recoverable": False,
            "status": "INVALID",
        }

    recoverable = recovery_state in {"retry", "replan"}

    if recovery_state == "completed":
        status = "HEALTHY"
    elif recovery_state in {"retry", "replan"}:
        status = "RECOVERING"
    elif recovery_state in {"blocked", "escalate"}:
        status = "ATTENTION"
    else:
        status = "UNKNOWN"

    return {
        "valid": True,
        "state": recovery_state,
        "recoverable": recoverable,
        "status": status,
    }


def reliability_check_count(state):
    result = validate_reliability_state(state)

    return sum(
        1
        for key in ("valid", "recoverable")
        if result.get(key) is True
    )


def format_reliability_dashboard(state):
    result = validate_reliability_state(state)

    lines = [
        "Reliability Dashboard",
        "Status: {}".format(result.get("status", "UNAVAILABLE")),
        "Recovery State: {}".format(result.get("state", "invalid")),
        "Valid: {}".format(result.get("valid", False)),
        "Recoverable: {}".format(result.get("recoverable", False)),
    ]

    return chr(10).join(lines)
