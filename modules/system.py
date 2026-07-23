"""
Project FRIDAY
System Controller
"""

import psutil
import socket
import platform
from command_manager import manager


class System:

    def battery(self):
        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information is not available."

        if battery.power_plugged:
            return f"Battery is {battery.percent} percent and charging."

        return f"Battery is {battery.percent} percent."

    def cpu(self):
        return f"CPU usage is {psutil.cpu_percent(interval=1)} percent."

    def ram(self):
        ram = psutil.virtual_memory()
        return f"RAM usage is {ram.percent} percent."

    def disk(self):
        disk = psutil.disk_usage("/")
        return f"Disk usage is {disk.percent} percent."

    def ip(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
            return f"Your IP address is {ip}."
        except:
            return "Couldn't get IP address."

    def pc_name(self):
        return f"Computer name is {platform.node()}."

    def os(self):
        return f"You are running {platform.system()} {platform.release()}."


system = System()

manager.register_exact("battery", system.battery)
manager.register_exact("battery percentage", system.battery)
manager.register_exact("cpu usage", system.cpu)
manager.register_exact("ram usage", system.ram)
manager.register_exact("memory usage", system.ram)
manager.register_exact("disk usage", system.disk)
manager.register_exact("ip address", system.ip)
manager.register_exact("computer name", system.pc_name)
manager.register_exact("operating system", system.os)