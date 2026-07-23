"""
Project FRIDAY
Command Registry
"""

class CommandRegistry:

    def __init__(self):
        self.routes = {}

    def register(self, command, function):
        self.routes[command] = function

    def get_routes(self):
        return self.routes


registry = CommandRegistry()