"""FRIDAY V3 - Phase 23.2 Specialist Agents."""


class SpecialistAgent:

    TYPES = (
        "PLANNING",
        "ANALYSIS",
        "SAFETY",
        "EXECUTION",
        "VERIFICATION",
    )

    def __init__(self, name, role, description):
        self.name = str(name)
        self.role = str(role)
        self.description = str(description)

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
        }

    def is_valid(self):
        return (
            bool(self.name)
            and self.role in self.TYPES
            and bool(self.description)
        )


class SpecialistAgents:

    DEFINITIONS = {
        "PLANNING": {
            "name": "Planning Agent",
            "description": "Decomposes goals into structured steps and plans.",
        },
        "ANALYSIS": {
            "name": "Analysis Agent",
            "description": "Analyzes information, alternatives, and reasoning paths.",
        },
        "SAFETY": {
            "name": "Safety Agent",
            "description": "Evaluates risks, constraints, and unsafe actions.",
        },
        "EXECUTION": {
            "name": "Execution Agent",
            "description": "Focuses on actionable execution and task completion.",
        },
        "VERIFICATION": {
            "name": "Verification Agent",
            "description": "Checks results, assumptions, and correctness.",
        },
    }

    @classmethod
    def create_agent(cls, role):
        if role not in cls.DEFINITIONS:
            return None
        definition = cls.DEFINITIONS[role]
        return SpecialistAgent(
            definition["name"],
            role,
            definition["description"],
        )

    @classmethod
    def available_roles(cls):
        return list(cls.DEFINITIONS.keys())

    @classmethod
    def create_all(cls):
        return [cls.create_agent(role) for role in cls.DEFINITIONS]

    @classmethod
    def as_dicts(cls):
        return [agent.to_dict() for agent in cls.create_all()]

    @classmethod
    def validate_agents(cls, agents):
        if not isinstance(agents, list) or not agents:
            return False
        return all(
            isinstance(agent, SpecialistAgent) and agent.is_valid()
            for agent in agents
        )


specialist_agents = SpecialistAgents()
