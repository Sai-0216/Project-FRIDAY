"""
Project FRIDAY
Frontend Performance Dashboard
"""

import time


VALID_LEVELS = {
    "FAST",
    "NORMAL",
    "SLOW",
}


def measure_operation(operation):
    if not callable(operation):
        return {
            "valid": False,
            "elapsed_ms": 0.0,
            "level": "INVALID",
        }

    started = time.perf_counter()

    try:
        operation()
    except Exception:
        return {
            "valid": False,
            "elapsed_ms": round(
                (time.perf_counter() - started) * 1000,
                3,
            ),
            "level": "ERROR",
        }

    elapsed_ms = (time.perf_counter() - started) * 1000

    if elapsed_ms < 50:
        level = "FAST"
    elif elapsed_ms < 250:
        level = "NORMAL"
    else:
        level = "SLOW"

    return {
        "valid": True,
        "elapsed_ms": round(elapsed_ms, 3),
        "level": level,
    }


def validate_performance_state(state):
    if not isinstance(state, dict):
        return {
            "valid": False,
            "elapsed_ms": 0.0,
            "level": "INVALID",
        }

    elapsed_ms = state.get("elapsed_ms")

    if not isinstance(elapsed_ms, (int, float)) or elapsed_ms < 0:
        return {
            "valid": False,
            "elapsed_ms": 0.0,
            "level": "INVALID",
        }

    level = state.get("level")

    if level not in VALID_LEVELS:
        if elapsed_ms < 50:
            level = "FAST"
        elif elapsed_ms < 250:
            level = "NORMAL"
        else:
            level = "SLOW"

    return {
        "valid": True,
        "elapsed_ms": round(float(elapsed_ms), 3),
        "level": level,
    }


def performance_check_count(state):
    result = validate_performance_state(state)

    return sum(
        1
        for key in ("valid", "elapsed_ms", "level")
        if (
            result.get(key) is True
            or (
                key == "elapsed_ms"
                and result.get(key, 0) >= 0
            )
            or (
                key == "level"
                and result.get(key) in VALID_LEVELS
            )
        )
    )


def format_performance_dashboard(state):
    result = validate_performance_state(state)

    lines = [
        "Performance Dashboard",
        "Level: {}".format(result.get("level", "INVALID")),
        "Elapsed: {} ms".format(result.get("elapsed_ms", 0.0)),
        "Valid: {}".format(result.get("valid", False)),
    ]

    return chr(10).join(lines)
