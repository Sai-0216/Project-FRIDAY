"""FRIDAY V3 - Phase 31.1 Unified Runtime Foundation."""

from brain import brain
from planner import planner
from proactive.proactive_engine import proactive_engine
from proactive.agent_coordination import agent_coordination
from proactive.execution_recovery import execution_recovery


class UnifiedRuntime:

    def __init__(self):
        self.name = "FRIDAY Unified Runtime"
        self.version = "31.1"
        self.running = False

        self.brain = brain
        self.planner = planner
        self.proactive_engine = proactive_engine
        self.agent_coordination = agent_coordination
        self.execution_recovery = execution_recovery

    def start(self):
        if self.running:
            return self.status()

        self.running = True
        return self.status()

    def stop(self):
        self.running = False
        return self.status()

    def status(self):
        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "subsystems": {
                "brain": self.brain is not None,
                "planner": self.planner is not None,
                "proactive_engine": self.proactive_engine is not None,
                "agent_coordination": self.agent_coordination is not None,
                "execution_recovery": self.execution_recovery is not None,
            },
        }

    def self_test(self):
        state = self.status()

        return {
            "valid": all(state["subsystems"].values()),
            "running": state["running"],
            "subsystems": state["subsystems"],
        }


unified_runtime = UnifiedRuntime()
