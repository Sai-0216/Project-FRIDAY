"""
Project FRIDAY
Device & Environment State
Phase 18.1
"""

from datetime import datetime

from modules.system import system
from modules.apps import apps
from modules.network import network


class DeviceState:

    # ========================================
    # DEVICE SNAPSHOT
    # ========================================

    def snapshot(self):
        """
        Return a unified snapshot of the current
        device and environment state.
        """

        # ----------------------------------------
        # BATTERY
        # ----------------------------------------

        battery = None

        try:
            import psutil

            battery_info = psutil.sensors_battery()

            if battery_info is not None:
                battery = {
                    "percent": battery_info.percent,
                    "charging": battery_info.power_plugged,
                }

        except Exception as e:

            print(
                "[DEVICE STATE] Battery error:",
                repr(e)
            )

        # ----------------------------------------
        # INITIAL STATE
        # ----------------------------------------

        state = {
            "timestamp": datetime.now().isoformat(),

            "battery": battery,

            "cpu_percent": None,

            "ram_percent": None,

            "disk_percent": None,

            "ip": None,

            "computer_name": None,

            "operating_system": None,

            "running_apps": [],

            "wifi_status": "unknown",
        }

        # ----------------------------------------
        # CPU
        # ----------------------------------------

        try:
            import psutil

            state["cpu_percent"] = psutil.cpu_percent(
                interval=0.1
            )

        except Exception as e:

            print(
                "[DEVICE STATE] CPU error:",
                repr(e)
            )

        # ----------------------------------------
        # RAM
        # ----------------------------------------

        try:
            import psutil

            state["ram_percent"] = (
                psutil.virtual_memory().percent
            )

        except Exception as e:

            print(
                "[DEVICE STATE] RAM error:",
                repr(e)
            )

        # ----------------------------------------
        # DISK
        # ----------------------------------------

        try:
            import psutil

            state["disk_percent"] = (
                psutil.disk_usage("/").percent
            )

        except Exception as e:

            print(
                "[DEVICE STATE] Disk error:",
                repr(e)
            )

        # ----------------------------------------
        # IP ADDRESS
        # ----------------------------------------

        try:
            import socket

            state["ip"] = socket.gethostbyname(
                socket.gethostname()
            )

        except Exception as e:

            print(
                "[DEVICE STATE] IP error:",
                repr(e)
            )

        # ----------------------------------------
        # COMPUTER NAME
        # ----------------------------------------

        try:
            import platform

            state["computer_name"] = (
                platform.node()
            )

        except Exception as e:

            print(
                "[DEVICE STATE] Computer name error:",
                repr(e)
            )

        # ----------------------------------------
        # OPERATING SYSTEM
        # ----------------------------------------

        try:
            import platform

            state["operating_system"] = (
                f"{platform.system()} "
                f"{platform.release()}"
            )

        except Exception as e:

            print(
                "[DEVICE STATE] OS error:",
                repr(e)
            )

        # ----------------------------------------
        # RUNNING APPLICATIONS
        # ----------------------------------------

        try:

            state["running_apps"] = (
                apps.running_apps()
            )

        except Exception as e:

            print(
                "[DEVICE STATE] Apps error:",
                repr(e)
            )

        # ----------------------------------------
        # WIFI STATUS
        # ----------------------------------------

        try:

            state["wifi_status"] = (
                network.wifi_status()
            )

        except Exception as e:

            print(
                "[DEVICE STATE] Wi-Fi error:",
                repr(e)
            )

        return state


# ========================================
# DEVICE STATE INSTANCE
# ========================================

device_state = DeviceState()