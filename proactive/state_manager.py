from proactive.episodic_memory import episodic_memory
from proactive.cognitive_state import CognitiveState

class StateManager:
    VALID_STATES=("IDLE","UNDERSTANDING","PLANNING","EXECUTING","EVALUATING","LEARNING")
    TRANSITIONS={"IDLE":{"UNDERSTANDING"},"UNDERSTANDING":{"PLANNING","EXECUTING","EVALUATING","IDLE"},"PLANNING":{"EXECUTING","EVALUATING","LEARNING","IDLE"},"EXECUTING":{"EVALUATING","LEARNING","IDLE"},"EVALUATING":{"LEARNING","IDLE"},"LEARNING":{"IDLE","UNDERSTANDING"}}

    def __init__(self):
        self.state=CognitiveState()

    def begin(self,command=""):
        self.state.reset(command)
        self.state.transition("UNDERSTANDING")
        return self.state

    def transition(self,new_state):
        if new_state not in self.VALID_STATES:
            raise ValueError("Invalid cognitive state: "+new_state)
        current=self.state.lifecycle
        if new_state!=current and new_state not in self.TRANSITIONS.get(current,set()):
            raise ValueError("Invalid transition: "+current+" -> "+new_state)
        if new_state!=current:
            self.state.transition(new_state)
        return self.state

    def update(self,**kwargs):
        for key,value in kwargs.items():
            if hasattr(self.state,key):
                setattr(self.state,key,value)
        return self.state

    def add_execution_result(self,result):
        self.state.add_execution_result(result)
        return self.state

    def evaluate_execution_results(self):
        results = self.state.execution_results or []
        if not results:
            return "completed"

        successful_statuses = {"succeeded", "already_satisfied"}
        failed_statuses = {
            "failed", "error", "denied", "cancelled",
            "blocked", "skipped", "unknown",
        }

        failures = 0
        successes = 0

        for result in results:
            if isinstance(result, dict):
                status = result.get("status")
                error = result.get("error")

                if error:
                    failures += 1
                elif status in successful_statuses:
                    successes += 1
                elif status in failed_statuses:
                    failures += 1
                elif (
                    status is None
                    and "error" in result
                    and result.get("error") is None
                ):
                    # Backward compatibility for existing result dictionaries.
                    successes += 1
                else:
                    failures += 1
                continue

            status = getattr(result, "status", None)
            error = getattr(result, "error", None)

            if error:
                failures += 1
            elif status in successful_statuses:
                successes += 1
            else:
                # Unstructured strings and unknown result types fail closed.
                failures += 1

        if failures and successes:
            outcome = "partial"
        elif failures:
            outcome = "failed"
        else:
            outcome = "completed"

        self.state.evaluation = {
            "outcome": outcome,
            "total_results": len(results),
            "successes": successes,
            "failures": failures,
        }
        return outcome


    def record_learning(self, outcome=None):
        if outcome is None:
            outcome = self.state.outcome or self.evaluate_execution_results()
        learning = {
            "outcome": outcome,
            "command": self.state.command,
            "intent": self.state.intent,
            "execution_results": list(self.state.execution_results or []),
        }
        if not hasattr(self.state, "learning_history"):
            self.state.learning_history = []
        self.state.learning_history.append(learning)
        episodic_memory.record(
            event=self.state.command or "FRIDAY execution",
            context={
                "intent": self.state.intent,
                "resolved_command": self.state.resolved_command,
                "outcome": outcome,
            },
            outcome=outcome,
        )
        return learning

    def complete(self,outcome=None):
        if self.state.lifecycle!="EVALUATING":
            self.transition("EVALUATING")
        if outcome is None:
            outcome = self.evaluate_execution_results()
        self.state.set_outcome(outcome)
        self.transition("LEARNING")
        self.record_learning(outcome)
        self.transition("IDLE")
        return self.state

    def fail(self,error):
        self.state.set_error(error)
        if self.state.lifecycle!="EVALUATING":
            self.transition("EVALUATING")
        self.state.set_outcome("failed")
        self.transition("LEARNING")
        self.record_learning("failed")
        self.transition("IDLE")
        return self.state

    def snapshot(self):
        return self.state.snapshot()

    def current(self):
        return self.state

state_manager=StateManager()
