import json
import urllib.error
import urllib.request

SERVER_BASE = "http://127.0.0.1:8000"


def list_devices():
    try:
        with urllib.request.urlopen(SERVER_BASE + "/devices", timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
        if isinstance(data, dict) and "devices" in data:
            return data["devices"]
        return data if isinstance(data, list) else []
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def send_command(device_id, command):
    if not isinstance(device_id, str) or not device_id.strip():
        return None
    if not isinstance(command, str) or not command.strip():
        return None
    payload = json.dumps({"command": command.strip()}).encode("utf-8")
    request = urllib.request.Request(
        SERVER_BASE + "/devices/" + device_id.strip() + "/command",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def validate_devices(devices):
    return devices is not None and isinstance(devices, list)
