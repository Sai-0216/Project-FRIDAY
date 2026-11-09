"""Backward-compatible structured execution results."""

class ExecutionResult(str):
    """String-compatible response carrying an explicit execution status."""

    VALID_STATUSES = frozenset({
        "succeeded",
        "already_satisfied",
        "failed",
        "denied",
        "cancelled",
        "blocked",
        "skipped",
        "unknown",
    })

    def __new__(cls, message, *, status="unknown", error=None):
        if status not in cls.VALID_STATUSES:
            raise ValueError(f"Invalid execution status: {status!r}")

        instance = super().__new__(cls, str(message))
        instance.status = status
        instance.error = error
        return instance
