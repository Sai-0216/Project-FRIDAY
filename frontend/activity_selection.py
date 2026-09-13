def select_activity(items, index):
    items = list(items or [])
    if not items:
        return None
    try:
        index = int(index)
    except (TypeError, ValueError):
        return None
    if index < 0 or index >= len(items):
        return None
    return items[index]


def activity_labels(items):
    labels = []
    for item in items or []:
        result = item.get("result") or {}
        outcome = result.get("outcome", "pending")
        command = item.get("command", "")
        labels.append("[{}] {}".format(outcome, command))
    return labels


if __name__ == "__main__":
    sample = [
        {"command": "open notepad", "result": {"outcome": "completed"}},
        {"command": "open calculator", "result": {"outcome": "completed"}},
    ]
    print(activity_labels(sample))
    print(select_activity(sample, 1))
    print(select_activity(sample, 9))
