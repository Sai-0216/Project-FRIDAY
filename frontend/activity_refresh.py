def activity_signature(items):
    signature = []
    for item in items or []:
        result = item.get("result") or {}
        signature.append((
            item.get("device_id", ""),
            item.get("command", ""),
            result.get("outcome", "pending"),
        ))
    return tuple(signature)


def detect_activity_changes(previous, current):
    previous = tuple(previous or ())
    current = tuple(current or ())
    return previous != current


def refresh_snapshot(items):
    items = list(items or [])
    return {
        "count": len(items),
        "signature": activity_signature(items),
        "valid": True,
    }


if __name__ == "__main__":
    first = [
        {"device_id": "saicharan", "command": "open notepad", "result": {"outcome": "completed"}},
    ]
    second = [
        {"device_id": "saicharan", "command": "open notepad", "result": {"outcome": "completed"}},
        {"device_id": "saicharan", "command": "open calculator", "result": {"outcome": "completed"}},
    ]
    print('FIRST:', refresh_snapshot(first))
    print('CHANGED:', detect_activity_changes(activity_signature(first), activity_signature(second)))
    print('UNCHANGED:', detect_activity_changes(activity_signature(first), activity_signature(first)))
