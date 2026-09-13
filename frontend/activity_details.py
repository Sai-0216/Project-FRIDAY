def build_activity_details(item):
    item = item or {}
    result = item.get("result") or {}
    execution_results = result.get("execution_results", [])
    response = ""
    if execution_results:
        response = execution_results[-1].get("response", "")
    return {
        "device_id": item.get("device_id", ""),
        "command": item.get("command", ""),
        "outcome": result.get("outcome", "pending"),
        "response": response,
        "error": result.get("error", ""),
    }


def format_activity_details(item):
    details = build_activity_details(item)
    lines = [
        "Device: {}".format(details["device_id"] or "unknown"),
        "Command: {}".format(details["command"] or ""),
        "Outcome: {}".format(details["outcome"]),
        "Response: {}".format(details["response"] or "none"),
        "Error: {}".format(details["error"] or "none"),
    ]
    return chr(10).join(lines)


if __name__ == "__main__":
    sample = {
        "device_id": "saicharan",
        "command": "open calculator",
        "result": {
            "outcome": "completed",
            "execution_results": [{"response": "Opening calculator, Sir."}],
            "error": "",
        },
    }
    print(format_activity_details(sample))
