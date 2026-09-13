def filter_activity(items, query="", outcome=None):
    items = items or []
    query = str(query or "").strip().lower()
    filtered = []

    for item in items:
        command = str(item.get("command", ""))
        result = item.get("result") or {}
        item_outcome = result.get("outcome", "pending")
        response = ""
        execution_results = result.get("execution_results", [])
        if execution_results:
            response = str(execution_results[-1].get("response", ""))
        haystack = (command + " " + response).lower()

        if query and query not in haystack:
            continue
        if outcome and item_outcome != outcome:
            continue

        filtered.append(item)

    return filtered


def available_outcomes(items):
    outcomes = set()
    for item in items or []:
        result = item.get("result") or {}
        outcomes.add(result.get("outcome", "pending"))
    return sorted(outcomes)


if __name__ == "__main__":
    sample = [
        {"command": "open calculator", "result": {"outcome": "completed", "execution_results": [{"response": "Opening calculator, Sir."}]}},
        {"command": "open notepad", "result": {"outcome": "completed", "execution_results": [{"response": "Opening notepad, Sir."}]}},
        {"command": "open browser", "result": {"outcome": "failed", "error": "Browser unavailable"}},
    ]
    print("ALL:", len(filter_activity(sample)))
    print("CALCULATOR:", filter_activity(sample, query="calculator"))
    print("COMPLETED:", filter_activity(sample, outcome="completed"))
    print("OUTCOMES:", available_outcomes(sample))
