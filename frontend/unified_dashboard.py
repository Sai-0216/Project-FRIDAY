"""
Project FRIDAY
Frontend Unified Dashboard
"""

try:
    from frontend.goals_dashboard import build_goals_dashboard
    from frontend.tasks_dashboard import build_tasks_dashboard
    from frontend.agents_dashboard import build_agents_dashboard
    from frontend.system_dashboard import build_system_dashboard
except ModuleNotFoundError:
    from goals_dashboard import build_goals_dashboard
    from tasks_dashboard import build_tasks_dashboard
    from agents_dashboard import build_agents_dashboard
    from system_dashboard import build_system_dashboard


def build_unified_dashboard(goals=None, tasks=None, agents=None, system=None):
    return {
        "goals": build_goals_dashboard(goals or []),
        "tasks": build_tasks_dashboard(tasks or []),
        "agents": build_agents_dashboard(agents or []),
        "system": build_system_dashboard(system or {}),
    }


def unified_dashboard_counts(dashboard):
    if not isinstance(dashboard, dict):
        return {}

    return {
        "goals": len(dashboard.get("goals", [])),
        "tasks": len(dashboard.get("tasks", [])),
        "agents": len(dashboard.get("agents", [])),
        "system": len(dashboard.get("system", {})),
    }


def format_unified_dashboard(dashboard):
    if not isinstance(dashboard, dict):
        return "Unified Dashboard is empty."

    counts = unified_dashboard_counts(dashboard)

    lines = [
        "Unified Dashboard",
        "Goals: {}".format(counts.get("goals", 0)),
        "Tasks: {}".format(counts.get("tasks", 0)),
        "Agents: {}".format(counts.get("agents", 0)),
        "System metrics: {}".format(counts.get("system", 0)),
    ]

    return chr(10).join(lines)
