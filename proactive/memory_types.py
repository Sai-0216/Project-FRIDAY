"""
Project FRIDAY
Phase 19.2.1

Memory Type Definitions

Defines the ownership categories used by the Phase 19
learning layer. This module does not store memory.
"""


class MemoryType:

    FACT = "FACT"
    PREFERENCE = "PREFERENCE"
    EPISODIC = "EPISODIC"
    OUTCOME = "OUTCOME"
    TASK_STATE = "TASK_STATE"
    ENVIRONMENT = "ENVIRONMENT"
    LEARNED_PATTERN = "LEARNED_PATTERN"

    ALL = {
        FACT,
        PREFERENCE,
        EPISODIC,
        OUTCOME,
        TASK_STATE,
        ENVIRONMENT,
        LEARNED_PATTERN,
    }

    @classmethod
    def is_valid(cls, memory_type):
        return memory_type in cls.ALL
