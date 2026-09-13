def summarize_activity(items):
    items = list(items or [])
    summary = {
        "total": len(items),
        "completed": 0,
        "failed": 0,
        "pending": 0,
    }
    for item in items:
        result = item.get("result") or {}
        outcome = str(result.get("outcome", "pending")).lower()
        if outcome not in ("completed", "failed", "pending"):
            outcome = "pending"
        summary[outcome] += 1
    return summary


def format_activity_summary(items):
    summary = summarize_activity(items)
    return "Total: {} | Completed: {} | Failed: {} | Pending: {}".format(
        summary["total"],
        summary["completed"],
        summary["failed"],
        summary["pending"],
    )


if __name__ == "__main__":
    sample = [
        {"result": {"outcome": "completed"}},
        {"result": {"outcome": "completed"}},
        {"result": {"outcome": "failed"}},
        {"result": {"outcome": "pending"}},
        {"result": {}},
    ]
    print(summarize_activity(sample))
    print(format_activity_summary(sample))
