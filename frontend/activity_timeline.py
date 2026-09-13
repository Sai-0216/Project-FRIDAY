def build_activity_entry(command, result=None):
    result = result or {}
    execution_results = result.get("execution_results", [])
    response = ""
    if execution_results:
        response = execution_results[-1].get("response", "")
    return {
        "command": str(command),
        "outcome": result.get("outcome", "pending"),
        "response": response,
        "error": result.get("error", ""),
    }


def build_timeline(istory_items, limit=10):
    items = istory_items or []
    return [
        build_activity_entry(item.get("command", ""), item.get("result", {}))
        for item in items[-max(1, int(limit)):]
    ][-1::-1]


def format_timeline(timeline):
    if not timeline:
        return "No activity recorded yet."

    lines = []
    for item in timeline:
        line = "[{}] {}".format(
            item.get("outcome", "pending"),
            item.get("command", ""),
        )
        if item.get("response"):
            line += " — " + item["response"]
        if item.get("error"):
            line += " — ERROR: " + item["error"]
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    sample = [
        {
            "command": "open calculator",
            "result": {
                "outcome": "completed",
                "execution_results": [
                    {"response": "Opening calculator, Sir."}
                ],
            },
        },
        {
            "command": "open notepad",
            "result": {
                "outcome": "completed",
                "execution_results": [
                    {"response": "Opening notepad, Sir."}
                ],
            },
        },
    ]

    timeline = build_timeline(sample)
    print("TIMELINE:", timeline)
    print("FORMATTED:")
    print(format_timeline(timeline))
