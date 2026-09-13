import json


def export_activity_json(items):
    items = list(items or [])
    return json.dumps(items, indent=2, ensure_ascii=False)


def export_activity_text(items):
    items = list(items or [])
    lines = []
    for index, item in enumerate(items, 1):
        result = item.get("result") or {}
        outcome = result.get("outcome", "pending")
        command = item.get("command", "")
        device_id = item.get("device_id", "")
        lines.append("{}. [{}] {} - {}".format(index, outcome, device_id or "unknown", command))
    return chr(10).join(lines) if lines else "No activity recorded."


if __name__ == "__main__":
    sample = [
        {"device_id": "saicharan", "command": "open notepad", "result": {"outcome": "completed"}},
        {"device_id": "saicharan", "command": "open calculator", "result": {"outcome": "failed"}},
    ]
    print(export_activity_text(sample))
    print(export_activity_json(sample))
