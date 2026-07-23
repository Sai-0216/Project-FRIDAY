"""
Project FRIDAY
Memory Module
"""

import json
from pathlib import Path


class Memory:

    def __init__(self):
        self.file = Path("data/memory.json")

        if not self.file.exists():
            self.file.write_text("{}")

    def load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

    def remember(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)

    def recall(self, key):
        data = self.load()
        return data.get(key)


memory = Memory()