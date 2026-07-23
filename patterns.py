"""
Project FRIDAY
Command Patterns
"""

class PatternRegistry:

    def __init__(self):
        self.patterns = []

    def register(self, prefix, function):
        self.patterns.append((prefix, function))

    def match(self, command):

        for prefix, function in self.patterns:

            if command.startswith(prefix):

                argument = command[len(prefix):].strip()

                return function, argument

        return None, None


patterns = PatternRegistry()