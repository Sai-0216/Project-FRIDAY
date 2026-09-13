"""
FRIDAY Core Server - multi-device v2.

Features:
- Multiple simultaneous WebSocket device connections
- Device online/offline listing
- Send a command to a specific device
- Broadcast a command to all connected devices
"""

import json
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from network.result_store import result_store
import uvicorn

app = FastAPI(title="FRIDAY Core Server")
devices: dict[str, WebSocket] = {}


def now():
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
async def root():
    return {
        "name": "FRIDAY Core",
        "status": "online",
        "devices": list(devices.keys()),
    }


@app.get("/devices")
async def list_devices():
    return {
        "devices": [
            {"device_id": device_id, "online": True}
            for device_id in devices
        ]
    }


async def _send(device_id: str, message: dict):
    websocket = devices.get(device_id)
    if websocket is None:
        return False, f"{device_id} is offline"

    try:
        await websocket.send_text(json.dumps(message))
        return True, "sent"
    except Exception:
        if devices.get(device_id) is websocket:
            devices.pop(device_id, None)
        return False, f"{device_id} disconnected"


@app.post("/devices/{device_id}/command")
async def send_command(device_id: str, payload: dict):
    command = str(payload.get("command", "")).strip()
    if not command:
        return {"success": False, "message": "command is required"}

    ok, message = await _send(device_id, {
        "type": "command",
        "command": command,
        "timestamp": now(),
    })

    return {
        "success": ok,
        "device_id": device_id,
        "command": command,
        "message": message,
    }


@app.post("/broadcast")
async def broadcast(payload: dict):
    command = str(payload.get("command", "")).strip()
    if not command:
        return {"success": False, "message": "command is required"}

    results = {}
    for device_id in list(devices):
        ok, message = await _send(device_id, {
            "type": "command",
            "command": command,
            "timestamp": now(),
        })
        results[device_id] = {"success": ok, "message": message}

    return {
        "success": True,
        "command": command,
        "results": results,
    }


@app.get("/devices/{device_id}/results")
async def device_results(device_id: str, limit: int = 20):
    return {"device_id": device_id, "results": result_store.recent(device_id, limit)}


@app.websocket("/ws/{device_id}")
async def device_socket(websocket: WebSocket, device_id: str):
    await websocket.accept()

    old = devices.get(device_id)
    devices[device_id] = websocket

    if old is not None and old is not websocket:
        try:
            await old.close()
        except Exception:
            pass

    print(f"[FRIDAY] {device_id} connected")

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                message = {"type": "message", "data": raw}

            print(f"[{device_id}] {message}")
            if message.get("type") == "result":
                result_store.record(device_id, message)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print(f"[FRIDAY] {device_id} error: {exc}")
    finally:
        if devices.get(device_id) is websocket:
            devices.pop(device_id, None)
        print(f"[FRIDAY] {device_id} disconnected")


if __name__ == "__main__":
    uvicorn.run("network.server:app", host="0.0.0.0", port=8000, reload=False)
