from proactive.memory_types import MemoryType


MEMORY_OWNERS = {
    MemoryType.FACT: "modules.memory",
    MemoryType.PREFERENCE: "modules.memory",
    MemoryType.EPISODIC: "phase19_learning",
    MemoryType.OUTCOME: "proactive_outcome_memory",
    MemoryType.TASK_STATE: "modules.task_manager",
    MemoryType.ENVIRONMENT: "environment_memory",
    MemoryType.LEARNED_PATTERN: "phase19_learning",
}


def owner_for(memory_type):
    return MEMORY_OWNERS.get(memory_type)
