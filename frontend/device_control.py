import json
import urllib.error
import urllib.request

SERVER_BASE = "http://127.0.0.1:8000"


def _request(path, method="GET", payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        SERVER_BASE + path,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def list_devices():
    data = _request("/devices")
    if isinstance(data, dict) and "devices" in data:
        return data["devices"]
    return data if isinstance(data, list) else None


def send_command(device_id, command):
    if not isinstance(device_id, str) or not device_id.strip():
        return None
    if not isinstance(command, str) or not command.strip():
        return None
    return _request(
        "/devices/" + device_id.strip() + "/command",
        "POST",
        {"command": command.strip()},
    )


def broadcast_command(command):
    if not isinstance(command, str) or not command.strip():
        return None
    return _request("/broadcast", "POST", {"command": command.strip()})


def validate_devices(devices):
    return devices is not None and isinstance(devices, list)


def validate_broadcast_result(result):
    return isinstance(result, dict) and result.get("success") is True
