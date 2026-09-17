"""
FRIDAY Device Client - multi-device v2.

The client connects one FRIDAY installation to the central server.
Incoming commands are passed through the UnifiedRuntime command boundary.
"""

import asyncio
import json
import socket

import websockets
from network.result_protocol import build_result


class FridayDeviceClient:
    def __init__(self, server_url, device_id=None, runtime=None):
        self.server_url = server_url.rstrip("/")
        self.device_id = device_id or socket.gethostname().lower()
        self.runtime = runtime
        self.running = True

    async def run(self):
        url = f"{self.server_url}/ws/{self.device_id}"

        while self.running:
            try:
                print(f"[FRIDAY] Connecting to {url}")

                async with websockets.connect(
                    url, ping_interval=20, ping_timeout=20
                ) as websocket:
                    print(f"[FRIDAY] Connected as {self.device_id}")

                    await websocket.send(json.dumps({
                        "type": "status",
                        "device_id": self.device_id,
                        "status": "online",
                    }))

                    async for raw in websocket:
                        await self.handle_message(websocket, raw)

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as exc:
                print(f"[FRIDAY] Server connection failed: {exc}")
                if self.running:
                    await asyncio.sleep(5)

    async def handle_message(self, websocket, raw):
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            return

        if message.get("type") != "command":
            return

        command = str(message.get("command", "")).strip()
        if not command:
            return

        print(f"[FRIDAY] Remote command: {command}")

        if self.runtime is None:
            await websocket.send(json.dumps({
                "type": "result",
                "device_id": self.device_id,
                "success": False,
                "message": "Unified runtime is not attached",
            }))
            return

        try:
            self.runtime.process_command(command)
            result = build_result(self.device_id, command, self.runtime)
            await websocket.send(json.dumps(result))
        except Exception as exc:
            await websocket.send(json.dumps({
                "type": "result",
                "device_id": self.device_id,
                "success": False,
                "command": command,
                "message": str(exc),
            }))
