import requests


def get_device_results(device_id, limit=10, base_url="http://127.0.0.1:8000"):
    response = requests.get(
        f"{base_url}/devices/{device_id}/results",
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    return results[-limit:]


def latest_device_result(device_id, base_url="http://127.0.0.1:8000"):
    results = get_device_results(device_id, limit=1, base_url=base_url)
    return results[0] if results else None


def format_execution_result(result):
    if not result:
        return "No execution result available."

    execution_results = result.get("execution_results", [])
    outcome = result.get("outcome", "unknown")
    error = result.get("error", "")

    if execution_results:
        response = execution_results[-1].get("response", "")
        if response:
            return f"{outcome}: {response}"

    if error:
        return f"{outcome}: {error}"

    return f"{outcome}: command completed without a response."


if __name__ == "__main__":
    result = latest_device_result("saicharan")
    print("LATEST:", result)
    print("FORMATTED:", format_execution_result(result))
