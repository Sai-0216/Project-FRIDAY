"""
Project FRIDAY
System Controls
"""

import os
import platform
import socket
import subprocess
from datetime import datetime

import psutil


class System:

    # ========================================
    # BATTERY
    # ========================================

    def battery(self):

        battery = psutil.sensors_battery()

        if battery is None:

            return (
                "Battery information is not available."
            )

        if battery.power_plugged:

            return (
                f"Battery is {battery.percent} "
                "percent and charging."
            )

        return (
            f"Battery is {battery.percent} percent."
        )

    # ========================================
    # CPU
    # ========================================

    def cpu(self):

        return (
            f"CPU usage is "
            f"{psutil.cpu_percent(interval=1)} percent."
        )

    # ========================================
    # RAM
    # ========================================

    def ram(self):

        ram = psutil.virtual_memory()

        return (
            f"RAM usage is "
            f"{ram.percent} percent."
        )

    # ========================================
    # DISK
    # ========================================

    def disk(self):

        disk = psutil.disk_usage("/")

        return (
            f"Disk usage is "
            f"{disk.percent} percent."
        )

    # ========================================
    # IP ADDRESS
    # ========================================

    def ip(self):

        try:

            ip = socket.gethostbyname(
                socket.gethostname()
            )

            return (
                f"Your IP address is {ip}."
            )

        except Exception:

            return (
                "Couldn't get IP address."
            )

    # ========================================
    # COMPUTER NAME
    # ========================================

    def pc_name(self):

        return (
            f"Computer name is "
            f"{platform.node()}."
        )

    # ========================================
    # OPERATING SYSTEM
    # ========================================

    def os(self):

        return (
            f"You are running "
            f"{platform.system()} "
            f"{platform.release()}."
        )

    # ========================================
    # TIME
    # ========================================

    def time(self):

        current_time = datetime.now().strftime(
            "%I:%M %p"
        )

        return (
            f"The time is {current_time}, Sir."
        )

    # ========================================
    # TASK MANAGER
    # ========================================

    def task_manager(self):

        try:

            subprocess.Popen(
                [
                    "taskmgr.exe"
                ]
            )

            return (
                "Opening Task Manager, Sir."
            )

        except Exception as e:

            print(
                "[System] Task Manager error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't open "
                "Task Manager."
            )

    # ========================================
    # WINDOWS SETTINGS
    # ========================================

    def settings(self):

        try:

            subprocess.Popen(
                [
                    "explorer.exe",
                    "ms-settings:"
                ]
            )

            return (
                "Opening Windows Settings, Sir."
            )

        except Exception as e:

            print(
                "[System] Settings error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't open "
                "Windows Settings."
            )

    # ========================================
    # LOCK COMPUTER
    # ========================================

    def lock(self):

        try:

            result = subprocess.run(
                [
                    "rundll32.exe",
                    "user32.dll,LockWorkStation"
                ],
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return (
                    "Locking the computer, Sir."
                )

            print(
                "[System] Lock failed."
            )

            print(
                "[System] Return code:",
                result.returncode
            )

            if result.stderr:

                print(
                    "[System] Error:",
                    result.stderr.strip()
                )

            return (
                "Sorry Sir, I couldn't lock "
                "the computer."
            )

        except Exception as e:

            print(
                "[System] Lock error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't lock "
                "the computer."
            )

    # ========================================
    # SLEEP
    # ========================================

    def sleep(self):

        try:

            result = subprocess.run(
                [
                    "rundll32.exe",
                    "powrprof.dll,SetSuspendState",
                    "0,1,0"
                ],
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return (
                    "Putting the computer "
                    "to sleep, Sir."
                )

            print(
                "[System] Sleep failed."
            )

            print(
                "[System] Return code:",
                result.returncode
            )

            if result.stderr:

                print(
                    "[System] Error:",
                    result.stderr.strip()
                )

            return (
                "Sorry Sir, I couldn't put "
                "the computer to sleep."
            )

        except FileNotFoundError:

            print(
                "[System] rundll32.exe was not found."
            )

            return (
                "Sorry Sir, I couldn't put "
                "the computer to sleep."
            )

        except Exception as e:

            print(
                "[System] Sleep error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't put "
                "the computer to sleep."
            )

    # ========================================
    # RESTART COMPUTER
    # ========================================

    def restart(self):

        try:

            result = subprocess.run(
                [
                    "shutdown.exe",
                    "/r",
                    "/t",
                    "0"
                ],
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return (
                    "Restarting the computer, Sir."
                )

            print(
                "[System] Restart failed."
            )

            print(
                "[System] Return code:",
                result.returncode
            )

            if result.stderr:

                print(
                    "[System] Error:",
                    result.stderr.strip()
                )

            return (
                "Sorry Sir, I couldn't restart "
                "the computer."
            )

        except FileNotFoundError:

            print(
                "[System] shutdown.exe was not found."
            )

            return (
                "Sorry Sir, I couldn't restart "
                "the computer."
            )

        except Exception as e:

            print(
                "[System] Restart error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't restart "
                "the computer."
            )

    # ========================================
    # SHUTDOWN COMPUTER
    # ========================================

    def shutdown(self):

        try:

            result = subprocess.run(
                [
                    "shutdown.exe",
                    "/s",
                    "/t",
                    "0"
                ],
                check=False,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                return (
                    "Shutting down the computer, Sir."
                )

            print(
                "[System] Shutdown failed."
            )

            print(
                "[System] Return code:",
                result.returncode
            )

            if result.stderr:

                print(
                    "[System] Error:",
                    result.stderr.strip()
                )

            return (
                "Sorry Sir, I couldn't shut down "
                "the computer."
            )

        except FileNotFoundError:

            print(
                "[System] shutdown.exe was not found."
            )

            return (
                "Sorry Sir, I couldn't shut down "
                "the computer."
            )

        except Exception as e:

            print(
                "[System] Shutdown error:",
                repr(e)
            )

            return (
                "Sorry Sir, I couldn't shut down "
                "the computer."
            )


# ========================================
# GLOBAL SYSTEM INSTANCE
# ========================================

system = System()
