"""Run the existing FRIDAY brain as a multi-device client.

Edit SERVER_URL if the FRIDAY Core server is on another computer.
"""
import asyncio

from runtime.unified_runtime import unified_runtime
from network.client import FridayDeviceClient

SERVER_URL = "ws://127.0.0.1:8000"
DEVICE_ID = None  # None = use this computer's hostname


if __name__ == "__main__":
    client = FridayDeviceClient(
        server_url=SERVER_URL,
        device_id=DEVICE_ID,
        runtime=unified_runtime,
    )

    unified_runtime.start()
    try:
        asyncio.run(client.run())
    finally:
        unified_runtime.stop()
