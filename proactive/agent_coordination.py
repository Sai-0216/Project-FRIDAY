"""FRIDAY V3 - Phase 23.3 Agent Coordination."""

from proactive.specialist_agents import SpecialistAgents, SpecialistAgent


class AgentCoordination:

    agents = SpecialistAgents()

    @staticmethod
    def _safe_task(task):
        return dict(task) if isinstance(task, dict) else {}

    @classmethod
    def assign_role(cls, task, role):
        task = cls._safe_task(task)
        agent = cls.agents.create_agent(role)
        if not isinstance(agent, SpecialistAgent):
            return None
        return {
            "agent": agent.to_dict(),
            "task": task,
            "assigned": True,
        }

    @classmethod
    def roles_for_task(cls, task):
        task = cls._safe_task(task)
        roles = []

        if task.get("planning") or task.get("complex") or task.get("multi_step"):
            roles.append("PLANNING")

        if task.get("analysis") or task.get("complex"):
            roles.append("ANALYSIS")

        if task.get("risk") or task.get("safety"):
            roles.append("SAFETY")

        if task.get("execute") or task.get("action"):
            roles.append("EXECUTION")

        if task.get("verify") or task.get("verification"):
            roles.append("VERIFICATION")

        return list(dict.fromkeys(roles))

    @classmethod
    def validate_assignments(cls, assignments):
        if not isinstance(assignments, list) or not assignments:
            return False

        for assignment in assignments:
            if not isinstance(assignment, dict):
                return False

            if assignment.get("assigned") is not True:
                return False

            agent = assignment.get("agent")
            if not isinstance(agent, dict):
                return False

            if agent.get("role") not in SpecialistAgents.DEFINITIONS:
                return False

            if not isinstance(assignment.get("task"), dict):
                return False

        return True

    @classmethod
    def coordinate(cls, task):
        task = cls._safe_task(task)
        roles = cls.roles_for_task(task)

        if not roles:
            roles = ["ANALYSIS"]

        assignments = [
            cls.assign_role(task, role)
            for role in roles
        ]

        return {
            "task": task,
            "roles": roles,
            "assignments": assignments,
            "coordinated": cls.validate_assignments(assignments),
        }


agent_coordination = AgentCoordination()
