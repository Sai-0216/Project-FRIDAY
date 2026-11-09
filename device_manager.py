"""FRIDAY device manager CLI.

The server must already be running.

Examples:
    python device_manager.py
    python device_manager.py list
    python device_manager.py send saicharan "open notepad"
    python device_manager.py all "say hello"
"""

import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def request(path, method="GET", payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"Could not reach FRIDAY server: {exc}")
        return None


def main():
    if len(sys.argv) == 1 or sys.argv[1] == "list":
        print(json.dumps(request("/devices"), indent=2))
        return

    if sys.argv[1] == "send" and len(sys.argv) >= 4:
        device = sys.argv[2]
        command = " ".join(sys.argv[3:])
        print(json.dumps(
            request(f"/devices/{device}/command", "POST", {"command": command}),
            indent=2,
        ))
        return

    if sys.argv[1] == "all" and len(sys.argv) >= 3:
        command = " ".join(sys.argv[2:])
        print(json.dumps(
            request("/broadcast", "POST", {"command": command}),
            indent=2,
        ))
        return

    print("Usage:")
    print("  python device_manager.py list")
    print('  python device_manager.py send <device_id> "<command>"')
    print('  python device_manager.py all "<command>"')


if __name__ == "__main__":
    main()
