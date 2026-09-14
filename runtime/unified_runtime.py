"""FRIDAY V3 - Phase 31.3 Unified Runtime Coordination."""

from brain import brain
from planner import planner
from proactive.proactive_engine import proactive_engine
from proactive.proactive_system import proactive_system
from proactive.agent_coordination import agent_coordination
from proactive.execution_recovery import execution_recovery
from frontend.device_control import list_devices, send_command, broadcast_command
from frontend.control_center import FridayControlCenter


class UnifiedRuntime:

    def __init__(self):
        self.name = "FRIDAY Unified Runtime"
        self.version = "31.3"
        self.running = False

        self.brain = brain
        self.planner = planner
        self.proactive_engine = proactive_engine
        self.proactive_system = proactive_system
        self.agent_coordination = agent_coordination
        self.execution_recovery = execution_recovery
        self.device_control = {
            "list_devices": list_devices,
            "send_command": send_command,
            "broadcast_command": broadcast_command,
        }
        self.frontend_class = FridayControlCenter

    def start(self):
        if self.running:
            return self.status()

        self.running = True

        if not self.proactive_system.running:
            self.proactive_system.start()

        return self.status()

    def stop(self):
        if self.proactive_system.running:
            self.proactive_system.stop()

        self.running = False

        return self.status()

    def process_command(self, command):
        if not self.running:
            return None

        if not isinstance(command, str) or not command.strip():
            return None

        return self.brain.process(command.strip())

    def process_event(self, event):
        if not self.running:
            return None

        return self.proactive_engine.process_event(event)

    def coordinate_task(self, task):
        if not self.running:
            return None

        return self.agent_coordination.coordinate(task)

    def recover_execution(
        self,
        execution_result,
        attempt_count=1,
        max_retries=2,
    ):
        if not self.running:
            return None

        return self.execution_recovery.recover(
            execution_result,
            attempt_count=attempt_count,
            max_retries=max_retries,
        )

    def list_devices(self):
        if not self.running:
            return None

        return self.device_control["list_devices"]()

    def send_device_command(self, device_id, command):
        if not self.running:
            return None

        return self.device_control["send_command"](device_id, command)

    def broadcast_device_command(self, command):
        if not self.running:
            return None

        return self.device_control["broadcast_command"](command)

    def create_frontend(self):
        if not self.running:
            return None

        return self.frontend_class()

    def status(self):
        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "subsystems": {
                "brain": self.brain is not None,
                "planner": self.planner is not None,
                "proactive_engine": self.proactive_engine is not None,
                "proactive_system": self.proactive_system is not None,
                "agent_coordination": self.agent_coordination is not None,
                "execution_recovery": self.execution_recovery is not None,
                "device_control": all(callable(value) for value in self.device_control.values()),
                "frontend": self.frontend_class is not None,
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
