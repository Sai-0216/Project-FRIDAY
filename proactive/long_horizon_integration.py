class LongHorizonIntegration:
    STATES = ("ready", "active", "needs_correction", "completed", "blocked")

    def __init__(self):
        self.name = "long_horizon_integration"

    def build(self, goal, decomposition, dependency, milestones, plan, monitoring, correction=None):
        if not all(isinstance(item, dict) for item in (goal, decomposition, dependency, milestones, plan, monitoring)):
            return None
        correction_data = correction if isinstance(correction, dict) else None
        state = monitoring.get("state", "on_track")
        if state == "completed":
            overall_state = "completed"
        elif correction_data and correction_data.get("state") == "corrected":
            overall_state = "needs_correction"
        else:
            overall_state = "active"
        return {
            "goal": goal,
            "decomposition": decomposition,
            "dependency": dependency,
            "milestones": milestones,
            "plan": plan,
            "monitoring": monitoring,
            "correction": correction_data,
            "state": overall_state,
        }

    def refresh(self, integration):
        if not isinstance(integration, dict):
            return None
        monitoring = integration.get("monitoring", {})
        correction = integration.get("correction")
        if monitoring.get("state") == "completed":
            integration["state"] = "completed"
        elif correction and correction.get("state") == "corrected":
            integration["state"] = "needs_correction"
        else:
            integration["state"] = "active"
        return integration

    def validate(self, integration):
        if not isinstance(integration, dict):
            return False
        required = ("goal", "decomposition", "dependency", "milestones", "plan", "monitoring", "correction", "state")
        if any(key not in integration for key in required):
            return False
        if integration["state"] not in self.STATES:
            return False
        if not all(isinstance(integration[key], dict) for key in required if key not in ("correction", "state")):
            return False
        if integration["correction"] is not None and not isinstance(integration["correction"], dict):
            return False
        return True


long_horizon_integration = LongHorizonIntegration()
