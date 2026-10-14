from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class CognitiveState:
    lifecycle: str = "IDLE"
    command: str = ""
    resolved_command: str = ""
    intent: str = ""
    parameters: dict = field(default_factory=dict)
    plan: list = field(default_factory=list)
    execution_results: list = field(default_factory=list)
    learning_history: list = field(default_factory=list)
    confidence: float = 0.0
    safety_status: str = "UNKNOWN"
    evaluation: dict = field(default_factory=dict)
    outcome: str = ""
    error: str = ""
    started_at: str = ""
    updated_at: str = ""
    transition_history: list = field(default_factory=list)

    def reset(self, command=""):
        now = datetime.now().isoformat()
        self.lifecycle = "IDLE"
        self.command = command
        self.resolved_command = ""
        self.intent = ""
        self.parameters = {}
        self.plan = []
        self.execution_results = []
        self.confidence = 0.0
        self.safety_status = "UNKNOWN"
        self.evaluation = {}
        self.outcome = ""
        self.error = ""
        self.started_at = now
        self.updated_at = now
        self.transition_history = ["IDLE"]

    def transition(self, state):
        self.lifecycle = state
        self.updated_at = datetime.now().isoformat()
        self.transition_history.append(state)

    def set_intent(self, intent, parameters=None, confidence=0.0):
        self.intent = intent or ""
        self.parameters = parameters or {}
        self.confidence = confidence
        self.updated_at = datetime.now().isoformat()

    def set_plan(self, plan):
        self.plan = plan or []
        self.updated_at = datetime.now().isoformat()

    def add_execution_result(self, result):
        self.execution_results.append(result)
        self.updated_at = datetime.now().isoformat()

    def set_evaluation(self, evaluation=None):
        self.evaluation = evaluation or {}
        self.updated_at = datetime.now().isoformat()

    def set_outcome(self, outcome):
        self.outcome = outcome or ""
        self.updated_at = datetime.now().isoformat()

    def set_error(self, error):
        self.error = error or ""
        self.updated_at = datetime.now().isoformat()

    def snapshot(self):
        return {"lifecycle": self.lifecycle, "command": self.command, "resolved_command": self.resolved_command, "intent": self.intent, "parameters": self.parameters, "plan": self.plan, "execution_results": self.execution_results, "learning_history": self.learning_history, "confidence": self.confidence, "safety_status": self.safety_status, "evaluation": self.evaluation, "outcome": self.outcome, "error": self.error, "started_at": self.started_at, "updated_at": self.updated_at, "transition_history": self.transition_history}
