"""FRIDAY V3 - Phase 31.5 Unified Runtime Entry Boundary."""

from dataclasses import dataclass
from brain import brain
from planner import planner
from proactive.event import Event
from proactive.proactive_engine import proactive_engine
from proactive.proactive_system import proactive_system
from proactive.agent_coordination import agent_coordination
from proactive.execution_recovery import execution_recovery
from proactive.state_manager import state_manager
from proactive.execution_state_tracking import execution_state_tracking
from frontend.device_control import list_devices, send_command, broadcast_command
from frontend.control_center import FridayControlCenter


@dataclass(frozen=True)
class RuntimeTask:
    task: object


@dataclass(frozen=True)
class RuntimeExecutionResult:
    result: object
    attempt_count: int = 1
    max_retries: int = 2


class UnifiedRuntime:

    def __init__(self):
        self.name = "FRIDAY Unified Runtime"
        self.version = "31.5"
        self.running = False
        self._started_proactive_system = False

        self.brain = brain
        self.planner = planner
        self.proactive_engine = proactive_engine
        self.proactive_system = proactive_system
        self.agent_coordination = agent_coordination
        self.execution_recovery = execution_recovery
        self.state_manager = state_manager
        self.execution_state_tracking = execution_state_tracking
        self._execution_tracking_state = None
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
            self._started_proactive_system = True
        else:
            self._started_proactive_system = False

        return self.status()

    def stop(self):
        if self._started_proactive_system and self.proactive_system.running:
            self.proactive_system.stop()

        self._started_proactive_system = False
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

    def handle(self, request):
        """Route a unified runtime request to its existing subsystem owner."""
        if not self.running:
            return None

        if isinstance(request, str):
            return self.process_command(request)

        if isinstance(request, Event):
            return self.process_event(request)

        if isinstance(request, RuntimeTask):
            return self.coordinate_task(request.task)

        if isinstance(request, RuntimeExecutionResult):
            return self.recover_execution(
                request.result,
                attempt_count=request.attempt_count,
                max_retries=request.max_retries,
            )

        return None

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

    def state_snapshot(self):
        if self.state_manager is None:
            return None

        return self.state_manager.snapshot()

    def initialize_tracking(self, dispatch_result):
        if not self.running:
            return None

        tracking = self.execution_state_tracking.initialize(
            dispatch_result
        )

        if tracking is not None:
            self._execution_tracking_state = tracking

        return tracking

    def update_tracking(self, task_id, new_state):
        if not self.running:
            return None

        if self._execution_tracking_state is None:
            return None

        tracking = self.execution_state_tracking.update(
            self._execution_tracking_state,
            task_id,
            new_state,
        )

        if tracking is not None:
            self._execution_tracking_state = tracking

        return tracking

    def runtime_state(self):
        return {
            "cognitive_state": self.state_snapshot(),
            "execution_tracking": self._execution_tracking_state,
        }

    def runtime_summary(self):
        state = self.status()

        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "overall": self.health()["overall"],
            "proactive_running": self.proactive_system.running,
            "cognitive_lifecycle": (
                self.state_manager.current()
                if self.state_manager is not None
                else None
            ),
            "execution_tracking": self._execution_tracking_state,
            "subsystems_ready": all(state["subsystems"].values()),
        }

    def health(self):
        state = self.status()
        subsystem_health = state["subsystems"]

        if not all(subsystem_health.values()):
            overall = "DEGRADED"
        elif not self.running:
            overall = "STOPPED"
        elif not self.proactive_system.running:
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return {
            "overall": overall,
            "running": self.running,
            "subsystems": dict(subsystem_health),
            "started_proactive_system": self._started_proactive_system,
            "cognitive_state": self.state_snapshot(),
            "execution_tracking": self._execution_tracking_state,
            "execution_tracking_available": self.execution_state_tracking is not None,
            "proactive_running": self.proactive_system.running,
        }

    def status(self):
        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "started_proactive_system": self._started_proactive_system,
            "subsystems": {
                "brain": self.brain is not None,
                "planner": self.planner is not None,
                "proactive_engine": self.proactive_engine is not None,
                "proactive_system": self.proactive_system is not None,
                "agent_coordination": self.agent_coordination is not None,
                "execution_recovery": self.execution_recovery is not None,
                "state_manager": self.state_manager is not None,
                "execution_state_tracking": self.execution_state_tracking is not None,
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
