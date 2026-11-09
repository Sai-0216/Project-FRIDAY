from proactive.memory_types import MemoryType
from proactive.memory_registry import owner_for



class MemoryClassifier:

    def classify(self, memory_type, value=None):
        if not MemoryType.is_valid(memory_type):
            return None

        return {
            "type": memory_type,
            "owner": owner_for(memory_type),
            "value": value,
        }


memory_classifier = MemoryClassifier()
